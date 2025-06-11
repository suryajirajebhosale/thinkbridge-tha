# -----------------------------------------------------
# Author: Surya Bhosale
# Date: 2025-06-11
# Project: ThinkBridge Assignment
# -----------------------------------------------------
from typing import List, TypedDict, Annotated
import operator

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel, Field


from src.config import Config
from src.agent_with_tools import create_company_research_agent, save_report_tool



llm = Config.LLM


# Properly define the state with Annotated types
class CompanyResearchState(TypedDict):
    company_name: str
    company_website: str
    final_report: str
    llm_evaluation: dict
    rewritten: bool = False
    errors: Annotated[List[str], operator.add]
    
    
class EvalSchema(BaseModel):
    score: int = Field(description="Score the report out of 10")
    rewrite: bool = Field(description="If the report should be rewritten or no")
    evaluation: str = Field(description="An evaluation of the report")
    
    
def researcher(state: CompanyResearchState):
    
    company_name, company_website, industry = state["company_name"], state["company_website"], state["industry"]
    
    agent = create_company_research_agent()
    
    prompt = f"""
    I need you to research the company {company_name} with website {company_website} operating in the {industry}.
    
    Please use the available tools to:
    1. Scrape the company website for basic information
    2. Search for recent news about the company
    3. Find financial data and performance metrics
    4. Research the company's competitors
    
    After gathering all this information, provide a comprehensive company research report with:
    - Executive Summary
    - Company Overview
    - Business Model & Products/Services  
    - Financial Performance
        - Give a summary for each resources/documents
        - Provide links to resources/documents
    - Recent News & Developments
        - Provide a brief summary for each news article
        - Provide links to each news article
    - Competitive Landscape
    - Key Insights & Analysis
    - Investment Outlook
    - Risk Factors
    
    Use all the tools available to gather comprehensive data before writing the final report in 600 to a 1000 words.
    
    Evaluation feedback if any:
    {state.get("llm_evaluation", None)}
    """
    
    
    
    result = agent.invoke({"messages": [("human", prompt)]})
    report = result["messages"][-1].content
    return {"final_report":report}


def reviewer(state: CompanyResearchState):
    report = state["final_report"]
    prompt = f"""
    
    Please use the available tools to:
        1. Save the report
    
    You are an analyst. Grade the following company report on a scale of 0–100 based on:
    - Completeness
    - Clarity
    - Factual Accuracy
    - Usefulness to an investor

    Report:
    {report}

    Give detailed scores and an overall score.
    
    If the report meets the minimum criteria save the report
    """
    llm_with_struct_output = llm.with_structured_output(EvalSchema)
    response = llm_with_struct_output.invoke([HumanMessage(content=prompt)])
    return {"llm_evaluation": response.dict()}


def to_rewrite(state: CompanyResearchState):
    try:
        eval = state["llm_evaluation"]
        rewrite = eval.get("rewrite")

        if rewrite and not state.get("rewritten", False):
            return "researcher", {"rewritten": True}
        else:
            save_report_tool.invoke({"report_content": state.get("final_report"), "company_name":state.get("company_name")})
            return END
    
    except Exception as e:
        return END, {"errors": [str(e)]}


workflow = StateGraph(CompanyResearchState)
    
# Add nodes
workflow.add_node("researcher", researcher)
workflow.add_node("reviewer", reviewer)

# Define the sequential flow
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "reviewer")
workflow.add_conditional_edges("reviewer", to_rewrite, ["researcher", END])
agentic_graph = workflow.compile()
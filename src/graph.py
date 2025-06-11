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
    industry: str
    llm_evaluation: dict
    rewritten: bool = False
    errors: Annotated[List[str], operator.add]
    
    
class EvalSchema(BaseModel):
    score: int = Field(description="Score the report out of 10")
    rewrite: bool = Field(description="If the report should be rewritten or no")
    evaluation: str = Field(description="An evaluation of the report")
    
    
def researcher(state: CompanyResearchState):
    """
    Conducts comprehensive research on a company using available tools and generates a detailed report.
    
    Args:
        state (CompanyResearchState): A dictionary containing company information including:
            - company_name: Name of the company to research
            - company_website: Website URL of the company
            - industry: Industry sector the company operates in
            - llm_evaluation: Optional evaluation feedback from previous attempts
    
    Returns:
        dict: A dictionary containing the final research report under the key 'final_report'
    """
    
    company_name, company_website, industry = state["company_name"], state["company_website"], state["industry"]
    
    agent = create_company_research_agent()
    
    prompt = f"""
I need you to research the company {company_name} with website {company_website} operating in the {industry} sector.

Please use the available tools to conduct thorough research:

**Data Collection Phase:**
1. **Website Analysis**: Scrape the company website to extract:
   - Company overview, mission, and values
   - Products/services offered
   - Target markets and customer segments
   - Leadership team and key personnel
   - Recent announcements or press releases
   - Contact information and office locations

2. **News & Market Intelligence**: Search for recent information about:
   - Latest company news and developments (past 6-12 months)
   - Industry trends affecting the company
   - Partnership announcements or strategic initiatives
   - Product launches or service expansions
   - Leadership changes or organizational updates
   - Always provide links

3. **Financial & Performance Research**: Look for:
   - Revenue figures and growth metrics
   - Funding rounds or investment news
   - Market position and company size indicators
   - Performance compared to industry benchmarks
   - Always provide links

4. **Competitive Intelligence**: Research:
   - Main competitors in their space
   - Market positioning relative to competitors
   - Unique value propositions or differentiators
   - Always provide links

**Deliverables:**

Create two comprehensive documents:

**1. EXECUTIVE FACT SHEET (Sales Rep Quick Reference)**
Format this as a concise, scannable document including:
- Company snapshot (size, revenue, locations)
- Key decision makers and contacts
- Primary products/services with brief descriptions
- Target customer profile
- Recent significant developments
- Competitive positioning
- Potential pain points or challenges
- Conversation starters and discovery questions

**2. DETAILED RESEARCH REPORT (800-1200 words)**
Structure as follows:

- **Executive Summary** (key findings for quick scanning)
- **Company Profile** (comprehensive overview)
- **Business Model & Offerings** (detailed product/service analysis)
- **Financial Health & Performance** 
  - Summarize each source with direct links
  - Include growth indicators and market position
- **Recent Developments & News**
  - Brief summary of each relevant article
  - Direct links to all news sources
- **Competitive Landscape** (market positioning analysis)
- **Sales Intelligence & Insights**
  - Potential business challenges
  - Growth opportunities
  - Recommended talking points
- **Discovery Call Preparation**
  - Suggested questions based on research
  - Potential value propositions to explore
  - Risk factors or objections to anticipate

**Research Quality Standards:**
- Prioritize recent information (within 12 months)
- Cross-reference multiple sources for accuracy
- Focus on actionable intelligence for sales conversations
- Include direct links to all sources for verification
- Highlight any data limitations or gaps found

Please gather comprehensive data using all available tools before creating the final deliverables. The fact sheet should be immediately actionable for a sales rep reviewing it 10 minutes before a discovery call.

Evaluation feedback if any: {state.get("llm_evaluation", None)}
"""
    
    
    
    result = agent.invoke({"messages": [("human", prompt)]})
    report = result["messages"][-1].content
    return {"final_report":report}


def reviewer(state: CompanyResearchState):
    """
    Evaluates the quality of the generated company research report and saves it if it meets criteria.
    
    Args:
        state (CompanyResearchState): A dictionary containing:
            - final_report: The complete research report to be evaluated
    
    Returns:
        dict: A dictionary containing the LLM evaluation results under the key 'llm_evaluation'
    """
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
    """
    Determines if the report needs to be rewritten based on the evaluation results.
    
    Args:
        state (CompanyResearchState): A dictionary containing:
            - llm_evaluation: Evaluation results from the reviewer
            - rewritten: Boolean flag indicating if the report has been rewritten before
            - final_report: The current research report
            - company_name: Name of the company being researched
    
    Returns:
        tuple: A tuple containing:
            - str: Either "researcher" to trigger a rewrite or END to finish
            - dict: Additional state updates including rewritten flag or any errors
    """
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
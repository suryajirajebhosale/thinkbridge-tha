# -----------------------------------------------------
# Author: Surya Bhosale
# Date: 2025-06-11
# Project: ThinkBridge Assignment
# -----------------------------------------------------
import json
from datetime import datetime
import requests

from bs4 import BeautifulSoup

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI



from src.config import Config

from langgraph.prebuilt import create_react_agent




# Convert your functions to tools using the @tool decorator
@tool
def scrape_company_website_tool(url: str) -> str:
    """Scrape the company's main website for basic information.
    
    Args:
        url: The company website URL to scrape
        
    Returns:
        Scraped website content including title, meta description, and main content
    """
    try:
        print(f"INVOKING SCRAPE TOOL ON: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract key information
        title = soup.find('title').get_text() if soup.find('title') else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_desc.get('content', '') if meta_desc else ""
        
        # Extract main content (remove scripts, styles, etc.)
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return f"Title: {title}\nMeta Description: {meta_desc}\nContent: {text[:3000]}..."
        
    except Exception as e:
        return f"Error scraping website: {str(e)}"

@tool
def search_company_news_tool(company_name: str, industry:str) -> str:
    """Search for recent news articles about the company.
    
    Args:
        company_name: Name of the company to search news for
        
    Returns:
        JSON string of recent news articles
    """
    try:
        print(f"FETCHING NEWS ON: {company_name}")
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_news",
            "q": f'"{company_name}" ({industry}) company news',
            "api_key": Config.SERP_API_KEY,
            "num": 8,
            "hl": "en"
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        news_results = []
        if "news_results" in data:
            for article in data["news_results"][:5]:
                news_results.append({
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "source": article.get("source", ""),
                    "date": article.get("date", ""),
                    "snippet": article.get("snippet", "")
                })
        
        return json.dumps(news_results, indent=2)
        
    except Exception as e:
        return f"Error searching news: {str(e)}"

@tool
def search_financial_data_tool(company_name: str, industry:str) -> str:
    """Search for financial information about the company.
    
    Args:
        company_name: Name of the company to search financial data for
        
    Returns:
        JSON string of financial information
    """
    try:
        print(f"FETCHING FINANCIAL DATA FOR: {company_name}")
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": f'"{company_name} ({industry})" financial data revenue earnings stock price',
            "api_key": Config.SERP_API_KEY,
            "num": 5,
            "hl": "en"
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        financial_info = {
            "search_results": [],
            "knowledge_graph": data.get("knowledge_graph", {}),
            "answer_box": data.get("answer_box", {})
        }
        
        if "organic_results" in data:
            for result in data["organic_results"][:3]:
                financial_info["search_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        return json.dumps(financial_info, indent=2)
        
    except Exception as e:
        return f"Error searching financial data: {str(e)}"
    
    
@tool
def save_report_tool(report_content: str, company_name:str) -> str:
    """
    Save the final report to a markdown file.
    
    Args:
        company_name: The name of the company being researched
        report_content: The complete report content to save
        
    Returns:
        Success message with filename or error message
    """
    try:
        
        if not report_content or not report_content.strip():
            return "Error: No report content provided to save"
            
        if not company_name or not company_name.strip():
            company_name = "unknown_company"
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company_name = company_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Remove any other problematic characters
        safe_company_name = ''.join(c for c in safe_company_name if c.isalnum() or c in '_-')
        filename = f"company_report_{safe_company_name}_{timestamp}.md"
        
                
        # Write the report to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Company Research Report: {company_name}\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write("\n" + "=" * 80 + "\n\n")
            f.write(report_content)
        
        success_msg = f"Report successfully saved to: {filename}"
        print(success_msg)
        return success_msg
        
    except Exception as e:
        error_msg = f"Error saving report: {str(e)}"
        print(error_msg)
        return error_msg

@tool
def search_competitors_tool(company_name: str, industry:str) -> str:
    """Search for competitor information.
    
    Args:
        company_name: Name of the company to search competitors for
        
    Returns:
        JSON string of competitor information
    """
    try:
        print(f"FETCHING COMPETITORS OF: {company_name}")
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": f'"{company_name} ({industry})" competitors alternatives similar companies industry',
            "api_key": Config.SERP_API_KEY,
            "num": 5,
            "hl": "en"
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        competitor_info = {
            "search_results": [],
            "related_searches": data.get("related_searches", [])
        }
        
        if "organic_results" in data:
            for result in data["organic_results"][:3]:
                competitor_info["search_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        return json.dumps(competitor_info, indent=2)
        
    except Exception as e:
        return f"Error searching competitors: {str(e)}"
    

def create_company_research_agent():
    """Create a ReAct agent with company research tools."""
    
    # Initialize LLM
    llm = Config.LLM
    
    # Define the tools list
    tools = [
        scrape_company_website_tool,
        search_company_news_tool,
        search_financial_data_tool,
        search_competitors_tool,
    ]
    
    # Create the agent
    agent = create_react_agent(llm, tools)
    
    return agent
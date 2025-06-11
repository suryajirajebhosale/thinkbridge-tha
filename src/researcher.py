# -----------------------------------------------------
# Author: Surya Bhosale
# Date: 2025-06-11
# Project: ThinkBridge Assignment
# -----------------------------------------------------
from typing import Dict, Any
from src.graph import agentic_graph
import urlparse
import os
import pandas as pd

class CompanyResearcher:
    """Class-based interface for company research."""
    def __init__(self, graph) -> None:
        self.graph = graph
        
    def research_company(self, company_name: str, company_website: str, industry:str) -> Dict[str, Any]:
        """Main function to research a company and generate a report."""
        
        
        print(f"Starting research for {company_name} ({company_website})")
        print("=" * 50)
        
        try:
            result = self.graph.invoke({"company_name":company_name, "company_website":company_website, "industry":industry})
            
            print("\nResearch completed!")
            print("=" * 50)
            
            return result
            
        except Exception as e:
            error_msg = f"Error during research: {str(e)}"
            print(error_msg)
            
    

    async def aresearch_company(self, company_name: str, company_website: str) -> Dict[str, Any]:
        """Async wrapper for company research."""
        return self.research_company(company_name, company_website)
    
if __name__ == "__main__":
    
    def fetch_company_data(path:str, count:int=1)->list[tuple[str, str]]:
        def _get_company_name(raw_url:str):
            url = raw_url.strip().split()[0]
            parsed = urlparse(url)
            company_name = parsed.netloc.replace("www.", "").split(".")[0]
            return company_name.upper()
        database = pd.read_csv(path)
        if count > 1:
            values_list = [(_get_company_name(i[0]),i[0], i[1]) for i in database.values][:count]
        else:
            values_list = [(_get_company_name(i[0]),i[0], i[1]) for i in database.values][:1]
        return values_list

    
    database = fetch_company_data(path=os.path.join(os.getcwd(), "clients.csv"))
    researcher = CompanyResearcher(graph=agentic_graph)
    for row in database:
        researcher.research_company(row[0], row[1], row[2])
    
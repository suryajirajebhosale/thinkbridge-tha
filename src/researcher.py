# -----------------------------------------------------
# Author: Surya Bhosale
# Date: 2025-06-11
# Project: ThinkBridge Assignment
# -----------------------------------------------------
from typing import Dict, Any
from src.graph import agentic_graph
from urllib.parse import urlparse
import os
import pandas as pd

class CompanyResearcher:
    """A class that provides an interface for conducting comprehensive company research.
    
    This class serves as a wrapper around the graph-based research system, providing
    both synchronous and asynchronous methods for company research.
    
    Attributes:
        graph: The graph instance used for conducting research
    """
    def __init__(self, graph) -> None:
        """Initialize the CompanyResearcher with a graph instance.
        
        Args:
            graph: The graph instance to use for conducting research
        """
        self.graph = graph
        
    def research_company(self, company_name: str, company_website: str, industry: str) -> Dict[str, Any]:
        """Conduct research on a company and generate a comprehensive report.
        
        Args:
            company_name: The name of the company to research
            company_website: The website URL of the company
            industry: The industry sector the company operates in
            
        Returns:
            Dict[str, Any]: A dictionary containing the research results
            
        Raises:
            Exception: If an error occurs during the research process
        """
        
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
        """Asynchronous wrapper for conducting company research.
        
        Args:
            company_name: The name of the company to research
            company_website: The website URL of the company
            
        Returns:
            Dict[str, Any]: A dictionary containing the research results
        """
        return self.research_company(company_name, company_website)
    


if __name__ == "__main__":
    import pandas as pd
    from urllib.parse import urlparse

    def fetch_company_data(path: str, count: int = 1) -> list[tuple[str, str]]:
        def _get_company_name(raw_url: str):
            url = raw_url.strip().split()[0]
            parsed = urlparse(url)
            company_name = parsed.netloc.replace("www.", "").split(".")[0]
            return company_name.upper()

        database = pd.read_csv(path)
        values_list = [(_get_company_name(i[0]), i[0], i[1]) for i in database.values][:count]
        return values_list

    # Get count from env
    count = int(os.getenv("COMPANY_COUNT", "1"))

    database = fetch_company_data(path=os.path.join(os.getcwd(), "companies.csv"), count=count)
    researcher = CompanyResearcher(graph=agentic_graph)

    for row in database:
        researcher.research_company(row[0], row[1], row[2])
    
import os
from typing import Literal, Dict, Any
from tavily import TavilyClient
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class DeepAgent:
    def __init__(self):
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        
        if not self.tavily_api_key or not self.groq_api_key:
            raise ValueError("Missing TAVILY_API_KEY or GROQ_API_KEY environment variables")

        self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
        self.groq_client = Groq(api_key=self.groq_api_key)

    def internet_search(
        self,
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "finance",
        include_raw_content: bool = False,
    ):
        """Run a web search"""
        try:
            return self.tavily_client.search(
                query,
                max_results=max_results,
                include_raw_content=include_raw_content,
                topic=topic,
            )
        except Exception as e:
            print(f"Error during search: {e}")
            return {"results": []}

    def analyze_asset(self, asset_name: str, asset_type: str, position_details: str) -> str:
        """
        Conducts research and generates a report for a specific asset.
        """
        query = f"Analyze {asset_name} {asset_type} financial performance news future outlook"
        print(f"Researching: {asset_name}...")
        
        search_results = self.internet_search(query, topic="finance")
        
        if not search_results.get('results'):
            return "No search results found. Unable to generate analysis."

        context = "\n\n".join([
            f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}"
            for result in search_results['results']
        ])
        
        system_prompt = """You are a senior financial analyst at a top-tier investment firm. Your task is to provide a professional, data-driven equity research report.

        **Guidelines:**
        - **Tone**: Formal, objective, and authoritative. Use professional financial terminology (e.g., "bullish divergence", "EBITDA margin expansion", "valuation headwinds").
        - **Format**: Clean Markdown. **DO NOT use emojis.**
        - **Structure**:
            1. **Investment Verdict**: Buy / Sell / Hold (with a concise rationale).
            2. **Financial Health Assessment**: Analyze key metrics (P/E, EPS growth, Debt-to-Equity) from the context.
            3. **Key Catalysts & Risks**: Recent developments, earnings reports, or macroeconomic factors.
            4. **Position Analysis**: Evaluate the user's specific holding (provided in prompt). Recommend actionable steps (e.g., "Accumulate on dips", "Trim exposure").
            5. **Outlook**: 12-month forecast based on fundamentals and sector trends.
        """

        user_prompt = f"""
        **Asset**: {asset_name} ({asset_type})
        **Client Position**: {position_details}
        
        **Market Data & News**:
        {context}
        
        Generate the research report following the strict guidelines above.
        """

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating analysis: {e}"

    def analyze_portfolio(self, portfolio_summary: str) -> str:
        """
        Generates an overall portfolio analysis based on the aggregated data.
        """
        print(f"Generating Overall Portfolio Strategy...")
        
        system_prompt = """You are a Chief Investment Officer (CIO). Your task is to review a client's total portfolio and provide a high-level strategic assessment.

        **Guidelines:**
        - **Tone**: Executive, strategic, and professional. **NO emojis.**
        - **Focus**: Asset allocation, sector exposure, risk assessment, and overall performance.
        - **Output**:
            1. **Portfolio Health Check**: Comment on diversification and performance.
            2. **Risk Assessment**: Identify concentration risks or sector over-exposure.
            3. **Strategic Recommendations**: High-level advice (e.g., "Rebalance into defensive sectors", "Increase exposure to large-caps").
        """

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"**Portfolio Summary**:\n{portfolio_summary}"}
                ],
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating portfolio analysis: {e}"


if __name__ == "__main__":
    # Test run
    agent = DeepAgent()
    print(agent.analyze_asset("TCS", "Stock", "Qty: 10, Avg: 3500, LTP: 3800"))
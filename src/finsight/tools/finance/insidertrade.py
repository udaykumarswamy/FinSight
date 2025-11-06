from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api

class InsiderTradeInput(BaseModel):
    '''
    Input schema for insider trade tool.
    This checks for the stock ticker and the limit for which the insider trades are to be retrieved.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    
    ticker: str = Field(..., description="The stock ticker symbol of the company.")
    limit: Optional[int] = Field(default=100, description="Number of records to retrieve.")
    filing_date_lt: Optional[str] = Field(default=None, description="Filing date less than.")
    filing_date_gt: Optional[str] = Field(default=None, description="Filing date greater than.")
    filing_date_lte: Optional[str] = Field(default=None, description="Filing date less than or equal to.")
    filing_date_gte: Optional[str] = Field(default=None, description="Filing date greater than or equal to.")
    
    
def create_params(ticker: str,
    limit: int,
    filing_date_gt: Optional[str],
    filing_date_gte: Optional[str],
    filing_date_lt: Optional[str],
    filing_date_lte: Optional[str]) -> dict:
    """Helper function to create params dict for API calls."""
    params = {"ticker": ticker, "limit": limit}
    if filing_date_gt is not None:
        params["filing_date_gt"] = filing_date_gt
    if filing_date_gte is not None:
        params["filing_date_gte"] = filing_date_gte
    if filing_date_lt is not None:
        params["filing_date_lt"] = filing_date_lt
    if filing_date_lte is not None:
        params["filing_date_lte"] = filing_date_lte
    return params   

@tool("get_insider_trades", args_schema=InsiderTradeInput)
def get_insider_trades(
    ticker: str,
    limit: Optional[int] = 100,
    filing_date_lt: Optional[str] = None,
    filing_date_gt: Optional[str] = None,
    filing_date_lte: Optional[str] = None,
    filing_date_gte: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Fetches insider trading activities for a specified stock ticker, 
    detailing transactions made by company insiders such as executives and directors.
    tool is used dynamically by the agent based on the query.
    documentation: https://docs.financialdatasets.ai/api-reference/endpoint/insider-trades/insider-trades
    """
    params = create_params(ticker, limit, filing_date_gt, filing_date_gte, filing_date_lt, filing_date_lte)
    data = call_api("/insider-trades/", params)
    return data.get("insider_trades", [])
from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api

class StockNewsInput(BaseModel):
    '''
    Input schema for stock news tool.
    This checks for the stock ticker and the date range for which the news are to be retrieved.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")
    start_date: Optional[str] = Field(None, description="The start date for the news articles.")
    end_date: Optional[str] = Field(None, description="The end date for the news articles.")
    limit: Optional[int] = Field(None, description="The maximum number of news articles to retrieve.")


def create_params(ticker: str,
    start_date: Optional[str],
    end_date: Optional[str],
    limit: Optional[int]) -> dict:
    
    """Helper function to create params dict for API calls."""
    params = {"ticker": ticker}
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    if limit is not None:
        params["limit"] = limit
    
    return params

@tool("stock_news", args_schema=StockNewsInput)
def stock_news(ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: Optional[int] = None) -> dict:
    """
    gets the latest news articles related to a specific stock ticker within an optional date range and limit.
    docmentation: https://docs.financialdatasets.ai/api-reference/endpoint/news/company
    Args:
        ticker (str): _description_
        start_date (Optional[str], optional): _description_. Defaults to None.
        end_date (Optional[str], optional): _description_. Defaults to None.
        limit (Optional[int], optional): _description_. Defaults to None.

    Returns:
        dict: _description_
    """
    params = create_params(ticker, start_date, end_date, limit)
    data = call_api("/news/", params)
    return data.get("news", [])
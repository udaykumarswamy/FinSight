from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api

class StockPricesInput(BaseModel):
    '''
    Input schema for stock prices tool.
    This checks for the stock ticker and the date range for which the prices are to be retrieved.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")

@tool("get_stock_prices", args_schema=StockPricesInput)
def get_stock_prices(ticker: str) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    This tool Fetches historical stock prices for a given company ticker.
    tool is used dynamically by the agent based on the query.
    """
    params = {
        "ticker": ticker
    }
    
    data = call_api("/prices/snapshot/", params)
    return data.get("snapshot", [])

class DetailedStockPricesInput(BaseModel):
    '''
    Input schema for detailed stock prices tool.
    This checks for the stock ticker and the date range for which the detailed prices are to be retrieved.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")
    interval: Literal['minute', 'day', 'week', 'month', 'year'] = Field(default='day', description="The interval of the stock prices.")
    interval_multiplier: Optional[int] = Field(default=1, description="The interval multiplier for the stock prices.")
    start_date: Optional[str] = Field(default=None, description="Start date for the stock prices (YYYY-MM-DD).")
    end_date: Optional[str] = Field(default=None, description="End date for the stock prices (YYYY-MM-DD).")
    
@tool("get_detailed_stock_prices", args_schema=DetailedStockPricesInput)
def get_detailed_stock_prices(
    ticker: str,
    interval: Literal['minute', 'day', 'week', 'month', 'year'] = 'day',
    interval_multiplier: Optional[int] = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    This tool Fetches detailed historical stock prices for a given company ticker with specified interval and date range.
    tool is used dynamically by the agent based on the query.
    """
    params = {
        "ticker": ticker,
        "interval": interval,
        "interval_multiplier": interval_multiplier
    }
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    
    data = call_api("/prices/", params)
    return data.get("prices", [])
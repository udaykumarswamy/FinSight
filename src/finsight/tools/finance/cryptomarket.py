from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api


class CryptoAnalysisInput(BaseModel):
    '''
    Input schema for crypto market analysis tool.
    This checks for the cryptocurrency symbol and the analysis type.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The cryptocurrency symbol, e.g., 'BTC-USD' for Bitcoin to USD.")
    interval: Literal['minute', 'day', 'week', 'month', 'year'] = Field(default='day', description="The interval for the market data.")
    interval_multiplier: Optional[int] = Field(default=1, description="The multiplier for the interval.")
    start_date : Optional[str] = Field(default=None, description="Start date for the data in YYYY-MM-DD format.")
    end_date : Optional[str] = Field(default=None, description="End date for the data in YYYY-MM-DD format.")
    
def create_params(ticker: str,
    interval: Literal["minute", "day", "week", "month", "year"],
    interval_multiplier: int,
    start_date: Optional[str],
    end_date: Optional[str]) -> dict:
    
    """Helper function to create params dict for API calls."""
    params = {"ticker": ticker, "interval": interval, "interval_multiplier": interval_multiplier}
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    
    return params

@tool("get_crypto_market_data", args_schema=CryptoAnalysisInput)
def get_crypto_market_data(
    ticker: str,
    interval: Literal['minute', 'day', 'week', 'month', 'year'] = 'day',
    interval_multiplier: Optional[int] = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Fetches cryptocurrency market data for a specified symbol over a given interval and date range.
    tool is used dynamically by the agent based on the query.
    """
    params = create_params(
        ticker,
        interval,
        interval_multiplier,
        start_date,
        end_date
    )
    
    data = call_api("/crypto/prices/", params)
    return data.get("prices", [])
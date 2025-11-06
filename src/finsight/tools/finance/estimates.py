from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api

class EstimateFinancialsInput(BaseModel):
    '''
    Input schema for estimating financials tool.
    This checks for the stock ticker and the period for which the estimates are to be made.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")
    period: Literal['annual', 'quarterly'] = Field(default='annual', description="Estimate financials for quaterly or yearly.")

@tool("estimate_financials", args_schema=EstimateFinancialsInput)
def estimate_financials(ticker: str, period: Literal['annual', 'quarterly'] = 'annual') -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    This is a tool that estimates financials for a given company ticker and period.
    tool is used dynamically by the agent based on the query.
    """
    params = {
        "ticker": ticker,
        "period": period
    }
    
    data = call_api("/analyst-estimates/", params)
    return data.get("analyst-estimates", [])


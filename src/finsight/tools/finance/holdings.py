from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api

class HoldingsInput(BaseModel):
    '''
    Input schema for holdings tool.
    This checks for the stock ticker and the period for which the holdings are to be retrieved.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    investor: str = Field(..., description="The stock ticker symbol of the company.")
    limit : Optional[int] = Field(default=10, description="Number of records to retrieve.")
    report_period_lt: Optional[str] = Field(default=None, description="Report period less than.")
    report_period_gt: Optional[str] = Field(default=None, description="Report period greater than.")
    report_period_lte: Optional[str] = Field(default=None, description="Report period less than or equal to.")
    report_period_gte: Optional[str] = Field(default=None, description="Report period greater than or equal to.")
    report_period : Optional[str] = Field(default=None, description="Specific report period (YYYY-MM-DD).")
    
def create_params(investor: str,
    limit: int,
    report_period_gt: Optional[str],
    report_period_gte: Optional[str],
    report_period_lt: Optional[str],
    report_period_lte: Optional[str],
    report_period: Optional[str]) -> dict:
    
    """Helper function to create params dict for API calls."""
    params = {"investor": investor, "limit": limit}
    if report_period_gt is not None:
        params["report_period_gt"] = report_period_gt
    if report_period_gte is not None:
        params["report_period_gte"] = report_period_gte
    if report_period_lt is not None:
        params["report_period_lt"] = report_period_lt
    if report_period_lte is not None:
        params["report_period_lte"] = report_period_lte 
    if report_period is not None:
        params["report_period"] = report_period
    
    return params   

@tool("get_holdings", args_schema=HoldingsInput)
def get_holdings(
    investor: str,
    limit: Optional[int] = 10,
    report_period_lt: Optional[str] = None,
    report_period_gt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
    report_period_gte: Optional[str] = None,
    report_period: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Fetches holdings information for a specified investor, 
    detailing the stocks or assets held by the investor over a reporting period.
    tool is used dynamically by the agent based on the query.
    """
    params = create_params(
        investor,
        limit,
        report_period_gt,
        report_period_gte,
        report_period_lt,
        report_period_lte,
        report_period
    )
    
    data = call_api("/institutional-ownership/", params)
    return data.get("institutional_ownership", [])
    
    
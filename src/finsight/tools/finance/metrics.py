from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api




class financialMetricsInput(BaseModel):
    '''
    Input schema for financial metrics tool.
    This checks for the stock ticker and the period for which the metrics are to be retrieved.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")
    period: Literal['annual', 'quarterly'] = Field(default='annual', description="Financial metrics for quaterly or yearly.")
    limit : Optional[int] = Field(default=100, description="Number of records to retrieve.")
    report_period_lt: Optional[str] = Field(default=None, description="Report period less than.")
    report_period_gt: Optional[str] = Field(default=None, description="Report period greater than.")
    report_period_lte: Optional[str] = Field(default=None, description="Report period less than or equal to.")
    report_period_gte: Optional[str] = Field(default=None, description="Report period greater than or equal to.")

def create_params(ticker: str,
    period: Literal["annual", "quarterly", "ttm"],
    limit: int,
    report_period_gt: Optional[str],
    report_period_gte: Optional[str],
    report_period_lt: Optional[str],
    report_period_lte: Optional[str]) -> dict:
    
    """Helper function to create params dict for API calls."""
    params = {"ticker": ticker, "period": period, "limit": limit}
    if report_period_gt is not None:
        params["report_period_gt"] = report_period_gt
    if report_period_gte is not None:
        params["report_period_gte"] = report_period_gte
    if report_period_lt is not None:
        params["report_period_lt"] = report_period_lt
    if report_period_lte is not None:
        params["report_period_lte"] = report_period_lte 
    
    return params

@tool("get_financial_metrics", args_schema=financialMetricsInput)
def get_financial_metrics(
    ticker: str,
    period: Literal['annual', 'quarterly'] = 'annual',
    limit: Optional[int] = 100,
    report_period_lt: Optional[str] = None,
    report_period_gt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
    report_period_gte: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Fetches various financial metrics of a company, 
    such as profitability ratios, liquidity ratios, and efficiency ratios, 
    which are essential for assessing the company's financial health.
    tool is used dynamically by the agent based on the query.
    """
    params = create_params(
        ticker,
        period,
        limit,
        report_period_gt,
        report_period_gte,
        report_period_lt,
        report_period_lte
    )
    
    data = call_api("/financial-metrics/", params)
    return data.get("financial_metrics", [])    




class FinancialMetricsSnapshotInput(BaseModel):
    '''
    Input schema for financial metrics snapshot tool.
    This checks for the stock ticker.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")

def create_params(ticker: str) -> dict:
    """Helper function to create params dict for API calls."""
    params = {"ticker": ticker}
    return params

@tool(args_schema=FinancialMetricsSnapshotInput)
def get_financial_metrics_snapshot(ticker: str) -> dict:
    """
    Fetches a snapshot of the most current financial metrics for a company, 
    including key indicators like market capitalization, P/E ratio, and dividend yield. 
    Useful for a quick overview of a company's financial health.
    """
    params = create_params(ticker)
    data = call_api("/financial-metrics/snapshot/", params)
    return data.get("snapshot", {})
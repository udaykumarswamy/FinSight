from langchain.tools import tool
from typing import Optional, List,Literal
from pydantic import BaseModel, Field
from finsight.tools.finance.api import call_api


class FundamentalAnalysisInput(BaseModel):
    '''
    Input schema for fundamental analysis tool.
    This checks for the stock ticker and the analysis type.
    acts as a validation layer for the inputs provided to the tool.
    
    '''
    ticker: str = Field(..., description="The stock ticker symbol of the company.")
    #analysis_type: Literal['valuation', 'profitability', 'liquidity'] = Field(default='valuation', description="Type of fundamental analysis to perform.")
    period : Literal['annual', 'quarterly'] = Field(default='annual', description="Fundamental analysis for quarterly or yearly.")
    limt : Optional[int] = Field(default=100, description="Number of records to retrieve.")
    report_period_lt : Optional[str] = Field(default=None, description="Filter reports with period less than this date (YYYY-MM-DD).")
    report_period_gt : Optional[str] = Field(default=None, description="Filter reports with period greater than this date (YYYY-MM-DD).")
    report_period_lte : Optional[str] = Field(default=None, description="Filter reports with period less than or equal to this date (YYYY-MM-DD).")
    report_period_gte : Optional[str] = Field(default=None, description="Filter reports with period greater than or equal to this date (YYYY-MM-DD).")
    
    
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


@tool("get_income_statments", args_schema=FundamentalAnalysisInput)
def get_income_statments(
    ticker: str,
    period: Literal['annual', 'quarterly'] = 'annual',
    limt: Optional[int] = 100,
    report_period_lt: Optional[str] = None,
    report_period_gt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
    report_period_gte: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Fetches a company's income statements, 
    detailing its revenues, expenses, net income, etc. over a reporting period. 
    Useful for evaluating a company's profitability and operational efficiency.
    tool is used dynamically by the agent based on the query.
    documentation: https://docs.financialdatasets.ai/api-reference/endpoint/financials/income-statements
    """
    params = create_params(
        ticker,
        period,
        limt,
        report_period_gt,
        report_period_gte,
        report_period_lt,
        report_period_lte
    )
    
    data = call_api("/financials/income-statements", params)
    return data.get("get_income_statments", {})

@tool("get_balance_sheets", args_schema=FundamentalAnalysisInput)
def get_balance_sheets(
    ticker: str,
    period: Literal['annual', 'quarterly'] = 'annual',
    limt: Optional[int] = 100,
    report_period_lt: Optional[str] = None,
    report_period_gt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
    report_period_gte: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Retrieves a company's balance sheets, 
    providing insights into its assets, liabilities, and shareholders' equity at specific points in time. 
    Useful for assessing financial stability and capital structure.
    tool is used dynamically by the agent based on the query.
    documentation: https://docs.financialdatasets.ai/api-reference/endpoint/financials/income-statements

    """
    params = create_params(
        ticker,
        period,
        limt,
        report_period_gt,
        report_period_gte,
        report_period_lt,
        report_period_lte
    )
    
    data = call_api("/financials/balance-sheets", params)
    return data.get("get_balance_sheets", {})   

@tool("get_cash_flow_statments", args_schema=FundamentalAnalysisInput)
def get_cash_flow_statments(
    ticker: str,
    period: Literal['annual', 'quarterly'] = 'annual',
    limt: Optional[int] = 100,
    report_period_lt: Optional[str] = None,
    report_period_gt: Optional[str] = None,
    report_period_lte: Optional[str] = None,
    report_period_gte: Optional[str] = None
) -> dict:
    """
    @tool --> decorator tells this function is a tool
    The args_schema links the input validation model.
    this tool Obtains a company's cash flow statements, 
    highlighting cash inflows and outflows from operating, investing, and financing activities. 
    Useful for understanding liquidity and cash management.
    tool is used dynamically by the agent based on the query.
    documentation: https://docs.financialdatasets.ai/api-reference/endpoint/financials/income-statements

    """
    params = create_params(
        ticker,
        period,
        limt,
        report_period_gt,
        report_period_gte,
        report_period_lt,
        report_period_lte
    )
    
    data = call_api("/financials/cash-flow-statements", params)
    return data.get("get_cash_flow_statments", {})
from typing import Callable, Any
from finsight.tools.finance.estimates import estimate_financials
from finsight.tools.finance.fundamentals import get_income_statments, get_balance_sheets,get_cash_flow_statments
from finsight.tools.finance.metrics import get_financial_metrics,get_financial_metrics_snapshot
from finsight.tools.finance.stocknews import stock_news
from finsight.tools.finance.stockprices import get_stock_prices,get_detailed_stock_prices
from finsight.tools.finance.insidertrade import get_insider_trades
from finsight.tools.finance.cryptomarket import get_crypto_market_data
from finsight.tools.finance.filings import get_filings, get_8K_filing_items, get_10K_filing_items, get_10Q_filing_items

from finsight.tools.search.googlenews import search_google_news



TOOLS: list[Callable[..., Any]] = [
    
    estimate_financials,
    get_cash_flow_statments,
    get_income_statments,
    get_balance_sheets,
    get_financial_metrics,
    get_financial_metrics_snapshot,
    stock_news,
    get_stock_prices,
    get_detailed_stock_prices,
    get_insider_trades,
    get_crypto_market_data,
    get_filings,
    get_8K_filing_items,
    get_10K_filing_items,
    get_10Q_filing_items,
    search_google_news,
    
     
]
import yfinance as yf
import pandas as pd

class StockFetcher:
    """
    Fetches stock data from yfinance.
    """
    def fetch(self, symbol, period="1mo"):
        """
        Fetches historical stock data for a given symbol and period.

        Args:
            symbol (str): The stock ticker symbol.
            period (str): The period for which to fetch data (e.g., "1d", "1mo", "1y").

        Returns:
            pandas.DataFrame: DataFrame containing the stock data, or empty DataFrame on error.
        """
        try:
            # Fetch data for the specified symbol and period
            # progress=False suppresses the download progress bar
            data = yf.download(symbol, period=period, progress=False)
            return data
        except Exception as e:
            # Print an error message if data fetching fails
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame() # Return an empty DataFrame on error

# Global instance to be imported by other modules
stock_fetcher = StockFetcher()
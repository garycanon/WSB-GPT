import sys
import yfinance as yf
import pandas as pd
import matplotlib.dates as mdates
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QTabWidget, QDoubleSpinBox, QSpinBox, QInputDialog,
    QAbstractItemView
)
from PyQt5.QtGui import QColor, QBrush
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StockFetcher:
    """
    Fetches stock data from yfinance.
    """
    def fetch(self, symbol, period="1mo"):
        try:
            data = yf.download(symbol, period=period, progress=False)  # Suppress progress bar
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

stock_fetcher = StockFetcher()  # Global instance

class MarketDataTab(QWidget):
    """
    Provides the main market data tab with watchlist, portfolio, and charting.
    """
    def __init__(self):
        super().__init__()
        self.tracked_symbols = []  # List of all symbols ever added to watchlist
        self.watchlist_symbols = []  # Symbols currently in the watchlist
        self.portfolio = {}  # Stores the quantity of stocks bought: {symbol: quantity}
        self.simulated_cash = 500.0  # Starting simulated money
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface.
        """
        layout = QVBoxLayout()

        # Portfolio table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels(["Stock", "Price", "Quantity", "Value", "Sell Qty", "Sell"])
        self.stock_table.setSelectionMode(QAbstractItemView.SingleSelection)  # Changed for clarity
        self.stock_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Prevent user editing
        layout.addWidget(QLabel("Portfolio"))
        layout.addWidget(self.stock_table)

        # Watchlist table
        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(8)  # Added "Owned" and "Buy" columns
        self.watchlist_table.setHorizontalHeaderLabels(["Stock", "Open", "High", "Low", "Close", "Remove", "Buy", "Owned"])
        self.watchlist_table.setSelectionMode(QAbstractItemView.SingleSelection)  # Changed for clarity
        self.watchlist_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Prevent user editing
        layout.addWidget(QLabel("Watchlist"))
        layout.addWidget(self.watchlist_table)

        # Search bar and buttons
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter stock symbol (e.g., AAPL)")
        search_layout.addWidget(self.search_bar)

        self.buy_quantity_input = QSpinBox()
        self.buy_quantity_input.setRange(1, 10000)
        self.buy_quantity_input.setValue(1)
        search_layout.addWidget(self.buy_quantity_input)

        self.buy_search_button = QPushButton("Buy Stock")
        self.buy_search_button.clicked.connect(self.buy_stock_from_search)
        search_layout.addWidget(self.buy_search_button)

        self.add_button = QPushButton("Add to Watchlist")
        self.add_button.clicked.connect(self._add_stock_to_watchlist_handler)
        search_layout.addWidget(self.add_button)

        self.clear_button = QPushButton("Clear Watchlist")
        self.clear_button.clicked.connect(self._clear_watchlist_handler)
        search_layout.addWidget(self.clear_button)

        layout.addLayout(search_layout)

        # Paper Mode Section
        self.paper_mode_layout = QVBoxLayout()
        self.cash_input = QDoubleSpinBox()
        self.cash_input.setRange(0, 1000000)
        self.cash_input.setValue(self.simulated_cash)
        self.cash_input.setPrefix("$")
        self.cash_input.valueChanged.connect(self.set_cash)
        self.paper_mode_layout.addWidget(QLabel("Simulated Cash"))
        self.paper_mode_layout.addWidget(self.cash_input)

        self.portfolio_label = QLabel("Portfolio Value: $0.00")
        self.paper_mode_layout.addWidget(self.portfolio_label)
        layout.addLayout(self.paper_mode_layout)

        # Canvas for plotting stocks
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)  # Changed to 111

        self.setLayout(layout)

    def set_cash(self, value):
        """
        Sets the simulated cash amount.
        """
        self.simulated_cash = value

    def _add_stock_to_watchlist_handler(self):
        """
        Handles adding a stock to the watchlist.
        """
        symbol = self.search_bar.text().strip().upper()
        if not symbol:
            return

        try:
            data = yf.download(symbol, period="1d", progress=False)
            if data.empty:
                QMessageBox.warning(self, "Invalid Ticker", f"Stock ticker '{symbol}' not found or data unavailable.")
            elif symbol not in self.watchlist_symbols:
                self.watchlist_symbols.append(symbol)
                self.tracked_symbols.append(symbol) # Add to tracked symbols
                self.update_watchlist_table()
                self.plot_stocks()
                self.search_bar.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while checking ticker '{symbol}': {e}")

    def _clear_watchlist_handler(self):
        """
        Clears all stocks from the watchlist that are not in the portfolio.
        """
        symbols_to_remove = [symbol for symbol in self.watchlist_symbols if symbol not in self.portfolio]
        for symbol in symbols_to_remove:
            self.watchlist_symbols.remove(symbol)
        self.update_watchlist_table()
        self.plot_stocks()

    def update_watchlist_table(self):
        """
        Updates the watchlist table with current data.
        """
        self.watchlist_table.setRowCount(0)
        self.watchlist_table.setColumnCount(8)
        self.watchlist_table.setHorizontalHeaderLabels(["Stock", "Open", "High", "Low", "Close", "Remove", "Buy", "Owned"])

        for symbol in self.watchlist_symbols:
            row_position = self.watchlist_table.rowCount()
            self.watchlist_table.insertRow(row_position)

            open_price_str = "N/A"
            high_price_str = "N/A"
            low_price_str = "N/A"
            close_price_str = "N/A"
            owned = symbol in self.portfolio  # Check if owned

            try:
                data = stock_fetcher.fetch(symbol, period="1d")
                if not data.empty:
                    latest = data.iloc[-1]
                    open_price = latest.get(('Open', symbol))
                    high_price = latest.get(('High', symbol))
                    low_price = latest.get(('Low', symbol))
                    close_price = latest.get(('Close', symbol))

                    if pd.notna(open_price):
                        open_price_str = f"{open_price:.2f}"
                    if pd.notna(high_price):
                        high_price_str = f"{high_price:.2f}"
                    if pd.notna(low_price):
                        low_price_str = f"{low_price:.2f}"
                    if pd.notna(close_price):
                        close_price_str = f"{close_price:.2f}"

            except Exception as e:
                print(f"Error processing watchlist data for {symbol}: {e}")

            self.watchlist_table.setItem(row_position, 0, QTableWidgetItem(symbol))
            self.watchlist_table.setItem(row_position, 1, QTableWidgetItem(open_price_str))
            self.watchlist_table.setItem(row_position, 2, QTableWidgetItem(high_price_str))
            self.watchlist_table.setItem(row_position, 3, QTableWidgetItem(low_price_str))
            self.watchlist_table.setItem(row_position, 4, QTableWidgetItem(close_price_str))

            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda _, s=symbol: self.remove_from_watchlist(s))
            if owned:
                remove_button.setEnabled(False)  # Disable if owned
                remove_button.setStyleSheet("color: gray;")  # Grey out
            self.watchlist_table.setCellWidget(row_position, 5, remove_button)

            buy_button = QPushButton("Buy")
            buy_button.clicked.connect(lambda _, s=symbol: self.buy_stock_from_watchlist(s))
            self.watchlist_table.setCellWidget(row_position, 6, buy_button)

            owned_indicator = QTableWidgetItem("Yes" if owned else "No")
            if owned:
                owned_indicator.setForeground(QBrush(QColor("green")))
            else:
                owned_indicator.setForeground(QBrush(QColor("red")))
            owned_indicator.setTextAlignment(4 | 12)  # Center Alignment
            self.watchlist_table.setItem(row_position, 7, owned_indicator)

    def remove_from_watchlist(self, symbol):
        """
        Removes a stock from the watchlist.
        """
        if symbol in self.watchlist_symbols and symbol not in self.portfolio: # only remove if not in portfolio
            self.watchlist_symbols.remove(symbol)
            self.update_watchlist_table()
            self.plot_stocks()

    def buy_stock_from_search(self):
        """
        Handles buying a stock from the search bar.
        """
        symbol = self.search_bar.text().strip().upper()
        quantity = self.buy_quantity_input.value()
        self._execute_buy(symbol, quantity, from_watchlist=False)
        self.search_bar.clear()

    def buy_stock_from_watchlist(self, symbol):
        """
        Handles buying a stock from the watchlist.
        """
        quantity, ok = QInputDialog.getInt(self, "Buy Stock", f"Enter quantity for {symbol}:", 1, 1, 10000, 1)
        if ok:
            self._execute_buy(symbol, quantity, from_watchlist=True)

    def _execute_buy(self, symbol, quantity, from_watchlist=False):
        """
        Executes the stock buying logic.
        """
        if not symbol:
            QMessageBox.warning(self, "Invalid Input", "Please enter a stock symbol to buy.")
            return

        try:
            data = yf.download(symbol, period="1d", progress=False)
            if data.empty:
                QMessageBox.warning(self, "Invalid Ticker", f"Stock ticker '{symbol}' not found or data unavailable.")
                return
            elif ('Close', symbol) not in data.columns:
                QMessageBox.warning(self, "Invalid Data", f"Could not retrieve closing price for '{symbol}'.")
                return

            last_close = data[('Close', symbol)].iloc[-1]
            if isinstance(last_close, pd.Series):
                last_close = last_close.squeeze()
            try:
                price = float(last_close) if pd.notna(last_close) else 0.0
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Invalid Price", f"Could not parse price for '{symbol}'.")
                return

            total_cost = price * quantity
            if self.simulated_cash >= total_cost:
                self.simulated_cash -= total_cost
                self.cash_input.setValue(self.simulated_cash)
                self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
                self.update_portfolio_and_cash()
                if symbol not in self.watchlist_symbols:
                    self.watchlist_symbols.append(symbol)
                self.update_watchlist_table()  # Refresh watchlist to show 'Owned' status
                self.plot_stocks() # update plot
            else:
                QMessageBox.warning(self, "Insufficient Funds", "You do not have enough simulated money.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while trying to buy '{symbol}': {e}")

    def sell_stock(self, symbol, row):
        """
        Handles selling a stock from the portfolio.

        Args:
            symbol (str): The symbol of the stock to sell.
            row (int): The row index in the portfolio table.
        """
        quantity_spin = self.stock_table.cellWidget(row, 4)  # 4 is the 'Sell Qty' column
        if isinstance(quantity_spin, QSpinBox):
            quantity = quantity_spin.value()
        else:
            return  # Exit if not a QSpinBox

        if symbol and symbol in self.portfolio:
            data = stock_fetcher.fetch(symbol, period="1d")
            price = 0.0

            if not data.empty and ('Close', symbol) in data.columns:
                last_close = data[('Close', symbol)].iloc[-1]
                if isinstance(last_close, pd.Series):
                    last_close = last_close.squeeze()
                try:
                    price = float(last_close) if pd.notna(last_close) else 0.0
                except (ValueError, TypeError):
                    price = 0.0

            if self.portfolio[symbol] >= quantity:
                total_sale = price * quantity
                self.portfolio[symbol] -= quantity
                self.simulated_cash += total_sale
                self.cash_input.setValue(self.simulated_cash)
                if self.portfolio[symbol] == 0:
                    del self.portfolio[symbol]
                self.update_portfolio_and_cash()
                self.update_watchlist_table()  # Refresh watchlist to update 'Owned' status
            else:
                QMessageBox.warning(self, "Insufficient Shares", "You do not have enough shares to sell.")

    def update_portfolio_and_cash(self):
        """
        Updates the portfolio table and the cash display.
        """
        self.update_portfolio_table()
        self.plot_stocks()

    def update_portfolio_table(self):
        """
        Updates the portfolio table with the current holdings.
        """
        self.stock_table.setRowCount(0)
        total_value = 0.0

        for symbol, quantity in self.portfolio.items():
            data = stock_fetcher.fetch(symbol, period="1d")
            price = 0.0

            if not data.empty and ('Close', symbol) in data.columns:
                last_close = data[('Close', symbol)].iloc[-1]
                if isinstance(last_close, pd.Series):
                    last_close = last_close.squeeze()
                try:
                    price = float(last_close) if pd.notna(last_close) else 0.0
                except (ValueError, TypeError):
                    price = 0.0

            value = price * quantity
            total_value += value

            row_position = self.stock_table.rowCount()
            self.stock_table.insertRow(row_position)
            self.stock_table.setItem(row_position, 0, QTableWidgetItem(symbol))
            self.stock_table.setItem(row_position, 1, QTableWidgetItem(f"{price:.2f}"))
            self.stock_table.setItem(row_position, 2, QTableWidgetItem(str(quantity)))
            self.stock_table.setItem(row_position, 3, QTableWidgetItem(f"${value:.2f}"))

            qty_spin = QSpinBox()
            qty_spin.setRange(1, quantity)
            qty_spin.setValue(1)
            self.stock_table.setCellWidget(row_position, 4, qty_spin)  # 4 is 'Sell Qty'

            sell_button = QPushButton("Sell")
            sell_button.clicked.connect(lambda _, s=symbol, r=row_position: self.sell_stock(s, r))
            self.stock_table.setCellWidget(row_position, 5, sell_button)  # 5 is 'Sell'

        self.portfolio_label.setText(f"Portfolio Value: ${total_value:.2f}")

    def plot_stocks(self):
        """
        Plots the stock prices of the symbols in the watchlist.
        """
        self.ax.clear()
        today = pd.Timestamp.today()
        one_month_ago = today - pd.DateOffset(months=1)

        symbols_to_plot = list(self.watchlist_symbols) # Use a copy

        if not symbols_to_plot:
            self.ax.set_title("No stocks being tracked.")
        else:
            for symbol in symbols_to_plot:
                data = stock_fetcher.fetch(symbol, period="1mo")
                if not data.empty and ('Close', symbol) in data.columns:
                    data.index = pd.to_datetime(data.index)
                    data = data.sort_index()
                    data = data[(data.index >= one_month_ago) & (data.index <= today)]
                    self.ax.plot(data.index, data[('Close', symbol)], label=symbol, linewidth=2)

            self.ax.set_title("Watchlist - Last 1 Month")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Stock Price")
            self.ax.legend()
            self.ax.grid(True)
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        self.canvas.draw_idle()

class BloombergApp(QMainWindow):
    """
    Main application window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WSB-GPT: Bloomberg Terminal Alternative")
        self.setGeometry(100, 100, 1000, 700)
        self.tabs = QTabWidget()

        self.market_tab = MarketDataTab()
        self.tabs.addTab(self.market_tab, "Market Data")

        self.setCentralWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BloombergApp()
    window.show()
    sys.exit(app.exec_())

import sys
import yfinance as yf
import pandas as pd
import matplotlib.dates as mdates
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QTabWidget, QDoubleSpinBox, QSpinBox, QInputDialog,
    QAbstractItemView, QComboBox
)
from PyQt5.QtGui import QColor, QBrush, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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

stock_fetcher = StockFetcher()  # Global instance of StockFetcher

class SettingsTab(QWidget):
    """
    Provides settings for the application, including cash and theme.
    """
    def __init__(self, main_window):
        """
        Initializes the SettingsTab.

        Args:
            main_window (QMainWindow): Reference to the main application window.
        """
        super().__init__()
        self.main_window = main_window # Reference to the main window for applying themes
        self.simulated_cash = 500.0 # Initial simulated cash
        self.init_ui() # Initialize the user interface

    def init_ui(self):
        """
        Initializes the user interface for the settings tab.
        """
        layout = QVBoxLayout() # Main vertical layout

        # Cash Input Section
        cash_layout = QHBoxLayout() # Horizontal layout for cash input
        cash_label = QLabel("Simulated Cash:") # Label for cash input
        self.cash_input = QDoubleSpinBox() # Spin box for setting cash amount
        self.cash_input.setRange(0, 1000000) # Set range for cash input
        self.cash_input.setValue(self.simulated_cash) # Set initial value
        self.cash_input.setPrefix("$") # Add '$' prefix
        # Connect value change signal to set_cash method
        self.cash_input.valueChanged.connect(self.set_cash)
        cash_layout.addWidget(cash_label) # Add label to layout
        cash_layout.addWidget(self.cash_input) # Add input to layout
        layout.addLayout(cash_layout) # Add cash layout to main layout

        # Theme Selection Section
        theme_layout = QHBoxLayout() # Horizontal layout for theme selection
        theme_label = QLabel("Theme:") # Label for theme selection
        self.theme_combo = QComboBox() # Combo box for theme selection
        # Add theme options
        self.theme_combo.addItems(["Light", "Dark", "High Contrast", "Blackout"])
        # Connect index change signal to apply_theme method
        self.theme_combo.currentIndexChanged.connect(self.apply_theme)
        theme_layout.addWidget(theme_label) # Add label to layout
        theme_layout.addWidget(self.theme_combo) # Add combo box to layout
        layout.addLayout(theme_layout) # Add theme layout to main layout

        self.setLayout(layout) # Set the main layout for the widget

    def set_cash(self, value):
        """
        Sets the simulated cash amount and updates the display in MarketDataTab.

        Args:
            value (float): The new simulated cash amount.
        """
        self.simulated_cash = value # Update the simulated cash value
        # The cash_input widget is already updated automatically by the spin box
        # When cash is changed in settings, update the display in MarketDataTab
        if hasattr(self.main_window, 'market_tab'):
             self.main_window.market_tab.update_portfolio_and_cash()


    def apply_theme(self, index):
        """
        Applies the selected theme to the main window and its widgets using stylesheets.

        Args:
            index (int): The index of the selected theme in the combo box.
        """
        theme = self.theme_combo.itemText(index) # Get the selected theme name
        if theme == "Light":
            # Clear stylesheet for default light theme
            self.main_window.setStyleSheet("")
        elif theme == "Dark":
            # Dark theme stylesheet
            self.main_window.setStyleSheet("""
                QMainWindow { background-color: #363636; color: #f0f0f0; }
                QTabWidget::pane { background-color: #363636; color: #f0f0f0; }
                QTabBar::tab { background-color: #555; color: #f0f0f0; padding: 8px; }
                QTabBar::tab:selected { background-color: #363636; border-bottom: 2px solid #f0f0f0; }
                QWidget { background-color: #363636; color: #f0f0f0; }
                QLineEdit { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; }
                QSpinBox { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; }
                QDoubleSpinBox { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; }
                QTableWidget { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; gridline-color: #666; }
                QHeaderView::section { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; }
                QPushButton { background-color: #555; color: #f0f0f0; border: 1px solid #777; padding: 5px; }
                QPushButton:hover { background-color: #666; }
                QComboBox { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; }
                QComboBox::drop-down { background-color: #4a4a4a; border: 0px; }
                QComboBox::down-arrow { color: #f0f0f0; }
                QLabel { color: #f0f0f0; }
            """)
        elif theme == "High Contrast":
            # High Contrast theme stylesheet
            self.main_window.setStyleSheet("""
                QMainWindow { background-color: black; color: yellow; }
                QTabWidget::pane { background-color: black; color: yellow; }
                QTabBar::tab { background-color: #333; color: yellow; padding: 8px; }
                QTabBar::tab:selected { background-color: black; border-bottom: 2px solid yellow; }
                QWidget { background-color: black; color: yellow; }
                QLineEdit { background-color: #333; color: yellow; border: 1px solid yellow; }
                QSpinBox { background-color: #333; color: yellow; border: 1px solid yellow; }
                QDoubleSpinBox { background-color: #333; color: yellow; border: 1px solid yellow; }
                QTableWidget { background-color: #333; color: yellow; border: 1px solid yellow; gridline-color: yellow; }
                QHeaderView::section { background-color: #333; color: yellow; border: 1px solid yellow; }
                QPushButton { background-color: #555; color: yellow; border: 1px solid yellow; padding: 5px; }
                QPushButton:hover { background-color: #777; color: black; }
                QComboBox { background-color: #333; color: yellow; border: 1px solid yellow; }
                QComboBox::drop-down { background-color: #333; border: 0px; }
                QComboBox::down-arrow { color: yellow; }
                QLabel { color: yellow; }
            """)
        elif theme == "Blackout":
            # Blackout theme stylesheet
            self.main_window.setStyleSheet("""
                QMainWindow { background-color: black; color: #ccc; }
                QTabWidget::pane { background-color: black; color: #ccc; }
                QTabBar::tab { background-color: #222; color: #ccc; padding: 8px; }
                QTabBar::tab:selected { background-color: black; border-bottom: 2px solid #ccc; }
                QWidget { background-color: black; color: #ccc; }
                QLineEdit { background-color: #222; color: #ccc; border: 1px solid #444; }
                QSpinBox { background-color: #222; color: #ccc; border: 1px solid #444; }
                QDoubleSpinBox { background-color: #222; color: #ccc; border: 1px solid #444; }
                QTableWidget { background-color: #222; color: #ccc; border: 1px solid #444; gridline-color: #444; }
                QHeaderView::section { background-color: #222; color: #ccc; border: 1px solid #444; }
                QPushButton { background-color: #333; color: #ccc; border: 1px solid #555; padding: 5px; }
                QPushButton:hover { background-color: #444; }
                QComboBox { background-color: #222; color: #ccc; border: 1px solid #444; }
                QComboBox::drop-down { background-color: #222; border: 0px; }
                QComboBox::down-arrow { color: #ccc; }
                QLabel { color: #ccc; }
            """)

class MarketDataTab(QWidget):
    """
    Provides the main market data tab with watchlist and portfolio.
    """
    def __init__(self, settings_tab):
        """
        Initializes the MarketDataTab.

        Args:
            settings_tab (SettingsTab): Reference to the settings tab.
        """
        super().__init__()
        self.settings_tab = settings_tab # Reference to the settings tab
        self.tracked_symbols = []  # List of all symbols ever added to watchlist (for plotting)
        self.watchlist_symbols = []  # Symbols currently in the watchlist table
        self.portfolio = {}  # Stores the quantity of stocks bought: {symbol: quantity}
        self.figure = Figure(figsize=(8, 6)) # Matplotlib figure for plotting
        self.canvas = FigureCanvas(self.figure) # Canvas to display the figure
        self.ax = self.figure.add_subplot(111) # Add a subplot to the figure
        self.init_ui() # Initialize the user interface
        self.update_portfolio_and_cash() # Initial update of portfolio and cash display


    def init_ui(self):
        """
        Initializes the user interface for the market data tab.
        """
        layout = QVBoxLayout() # Main vertical layout

        # Layout for Cash Available and Total Portfolio Value labels (now vertical)
        info_layout = QVBoxLayout()

        # Cash Available Label
        self.cash_label = QLabel(f"Cash Available: ${self.settings_tab.simulated_cash:.2f}")
        info_layout.addWidget(self.cash_label)

        # Portfolio Value Label
        # This label will now show the total value (cash + stocks)
        self.portfolio_label = QLabel("Total Portfolio Value: $0.00")
        info_layout.addWidget(self.portfolio_label)

        # Add the vertical info layout to the main vertical layout
        layout.addLayout(info_layout)


        # Portfolio table
        self.stock_table = QTableWidget() # Table to display portfolio holdings
        # Updated column count and headers (removed "Sell Qty")
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels(["Stock", "Price", "Quantity", "Value", "Sell"])
        # Allow only single row selection
        self.stock_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Prevent user from editing table cells
        self.stock_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(QLabel("Portfolio")) # Label for the portfolio table
        layout.addWidget(self.stock_table) # Add portfolio table to layout

        # Watchlist table
        self.watchlist_table = QTableWidget() # Table to display watchlist stocks
        # Updated column count and headers
        self.watchlist_table.setColumnCount(8)
        self.watchlist_table.setHorizontalHeaderLabels(["Stock", "Open", "High", "Low", "Close", "Buy", "Owned", " "])
        # Allow only single row selection
        self.watchlist_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Prevent user from editing table cells
        self.watchlist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(QLabel("Watchlist")) # Label for the watchlist table
        layout.addWidget(self.watchlist_table) # Add watchlist table to layout

        # Search bar and buttons layout
        search_layout = QHBoxLayout() # Horizontal layout for search and buy controls
        self.search_bar = QLineEdit() # Input field for stock symbol
        self.search_bar.setPlaceholderText("Enter stock symbol (e.g., AAPL)") # Placeholder text
        search_layout.addWidget(self.search_bar) # Add search bar to layout

        self.buy_quantity_input = QSpinBox() # Spin box for buy quantity
        self.buy_quantity_input.setRange(1, 10000) # Set range for quantity
        self.buy_quantity_input.setValue(1) # Set default quantity
        search_layout.addWidget(self.buy_quantity_input) # Add quantity input to layout

        self.buy_search_button = QPushButton("Buy Stock") # Button to buy from search
        # Connect button click to buy_stock_from_search method
        self.buy_search_button.clicked.connect(self.buy_stock_from_search)
        search_layout.addWidget(self.buy_search_button) # Add buy button to layout

        self.add_button = QPushButton("Add to Watchlist") # Button to add to watchlist
        # Connect button click to _add_stock_to_watchlist_handler method
        self.add_button.clicked.connect(self._add_stock_to_watchlist_handler)
        search_layout.addWidget(self.add_button) # Add add button to layout

        self.clear_button = QPushButton("Clear Watchlist") # Button to clear watchlist
        # Connect button click to _clear_watchlist_handler method
        self.clear_button.clicked.connect(self._clear_watchlist_handler)
        search_layout.addWidget(self.clear_button) # Add clear button to layout

        layout.addLayout(search_layout) # Add search layout to main layout

        # Add the matplotlib canvas to the layout for plotting
        layout.addWidget(self.canvas)


        self.setLayout(layout) # Set the main layout for the widget

    def open_plot_window(self):
        """
        Opens the separate plot window. - REMOVED in this version
        """
        pass # This method is no longer used as plotting is integrated

    def set_cash(self, value):
        """
        Sets the simulated cash amount (now handled by the settings tab).
        This method is not directly used in MarketDataTab anymore,
        but keeping it for clarity if needed elsewhere.
        """
        # The actual cash is stored and managed in the settings_tab
        pass


    def _add_stock_to_watchlist_handler(self):
        """
        Handles adding a stock to the watchlist.
        Fetches data to validate the ticker before adding.
        """
        symbol = self.search_bar.text().strip().upper() # Get symbol from search bar, clean and capitalize
        if not symbol:
            return # Do nothing if symbol is empty

        try:
            # Fetch 1 day of data to validate the ticker
            data = yf.download(symbol, period="1d", progress=False)
            if data.empty:
                # Show warning if ticker is not found or data is unavailable
                QMessageBox.warning(self, "Invalid Ticker", f"Stock ticker '{symbol}' not found or data unavailable.")
            elif symbol not in self.watchlist_symbols:
                # Add symbol to watchlist and tracked symbols if not already present
                self.watchlist_symbols.append(symbol)
                self.tracked_symbols.append(symbol)
                self.update_watchlist_table() # Update the watchlist table display
                self.plot_stocks() # Update the plot
                self.search_bar.clear() # Clear the search bar
        except Exception as e:
            # Show critical error message if an exception occurs
            QMessageBox.critical(self, "Error", f"An error occurred while checking ticker '{symbol}': {e}")

    def _clear_watchlist_handler(self):
        """
        Clears all stocks from the watchlist that are NOT currently in the portfolio.
        """
        # Create a list of symbols to remove (those in watchlist but not portfolio)
        symbols_to_remove = [symbol for symbol in self.watchlist_symbols if symbol not in self.portfolio]
        for symbol in symbols_to_remove:
            self.watchlist_symbols.remove(symbol) # Remove symbol from the watchlist list
        self.update_watchlist_table() # Update the watchlist table display
        self.plot_stocks() # Update the plot

    def update_watchlist_table(self):
        """
        Updates the watchlist table with current data for each symbol.
        Fetches latest price data and updates the table rows.
        """
        self.watchlist_table.setRowCount(0) # Clear existing rows
        # Updated column count and headers
        self.watchlist_table.setColumnCount(8)
        self.watchlist_table.setHorizontalHeaderLabels(["Stock", "Open", "High", "Low", "Close", "Buy", "Owned", " "])

        for symbol in self.watchlist_symbols:
            row_position = self.watchlist_table.rowCount() # Get the current row count
            self.watchlist_table.insertRow(row_position) # Insert a new row

            # Initialize price strings to N/A
            open_price_str = "N/A"
            high_price_str = "N/A"
            low_price_str = "N/A"
            close_price_str = "N/A"
            owned = symbol in self.portfolio  # Check if the stock is owned

            try:
                # Fetch 1 day of data for the symbol
                data = stock_fetcher.fetch(symbol, period="1d")
                if not data.empty:
                    latest = data.iloc[-1] # Get the latest data row
                    # Safely get price data, handling potential MultiIndex
                    open_price = latest.get(('Open', symbol))
                    high_price = latest.get(('High', symbol))
                    low_price = latest.get(('Low', symbol))
                    close_price = latest.get(('Close', symbol))

                    # Format prices if available and not NaN
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

            # Set table items with fetched data
            self.watchlist_table.setItem(row_position, 0, QTableWidgetItem(symbol))
            self.watchlist_table.setItem(row_position, 1, QTableWidgetItem(open_price_str))
            self.watchlist_table.setItem(row_position, 2, QTableWidgetItem(high_price_str))
            self.watchlist_table.setItem(row_position, 3, QTableWidgetItem(low_price_str))
            self.watchlist_table.setItem(row_position, 4, QTableWidgetItem(close_price_str))

            # Add Buy button
            buy_button = QPushButton("Buy")
            # Connect button click to buy_stock_from_watchlist method using a lambda
            buy_button.clicked.connect(lambda _, s=symbol: self.buy_stock_from_watchlist(s))
            self.watchlist_table.setCellWidget(row_position, 5, buy_button) # Add button to cell (now column 5)

            # Add Owned indicator
            owned_indicator = QTableWidgetItem("Yes" if owned else "No")
            if owned:
                # Set text color to green if owned
                owned_indicator.setForeground(QBrush(QColor("green")))
            else:
                # Set text color to red if not owned
                owned_indicator.setForeground(QBrush(QColor("red")))
            owned_indicator.setTextAlignment(4 | 12)  # Center Alignment (AlignHCenter | AlignVCenter)
            self.watchlist_table.setItem(row_position, 6, owned_indicator) # Add indicator to cell (now column 6)

            # Add Remove button (now an 'X')
            remove_button = QPushButton("X") # Changed button text to "X"
            # Connect button click to remove_from_watchlist method using a lambda
            remove_button.clicked.connect(lambda _, s=symbol: self.remove_from_watchlist(s))
            if owned:
                # Disable remove button if the stock is owned
                remove_button.setEnabled(False)
                remove_button.setStyleSheet("color: gray;") # Grey out the button
            self.watchlist_table.setCellWidget(row_position, 7, remove_button) # Add button to cell (now column 7)


    def remove_from_watchlist(self, symbol):
        """
        Removes a stock from the watchlist if it is not in the portfolio.

        Args:
            symbol (str): The symbol of the stock to remove.
        """
        # Check if the symbol is in the watchlist and NOT in the portfolio
        if symbol in self.watchlist_symbols and symbol not in self.portfolio:
            self.watchlist_symbols.remove(symbol) # Remove from the watchlist list
            self.update_watchlist_table() # Update the watchlist table display
            self.plot_stocks() # Update the plot

    def buy_stock_from_search(self):
        """
        Handles buying a stock using the symbol and quantity from the search bar.
        """
        symbol = self.search_bar.text().strip().upper() # Get symbol from search bar
        quantity = self.buy_quantity_input.value() # Get quantity from spin box
        # Execute the buy logic
        self._execute_buy(symbol, quantity, from_watchlist=False)
        self.search_bar.clear() # Clear the search bar

    def buy_stock_from_watchlist(self, symbol):
        """
        Handles buying a stock from the watchlist using an input dialog for quantity.

        Args:
            symbol (str): The symbol of the stock to buy.
        """
        # Open an input dialog to get the quantity to buy
        quantity, ok = QInputDialog.getInt(self, "Buy Stock", f"Enter quantity for {symbol}:", 1, 1, 10000, 1)
        if ok: # If the user clicked OK
            self._execute_buy(symbol, quantity, from_watchlist=True) # Execute the buy logic

    def _execute_buy(self, symbol, quantity, from_watchlist=False):
        """
        Executes the stock buying logic.
        Validates input, checks funds, updates portfolio and cash.

        Args:
            symbol (str): The stock ticker symbol.
            quantity (int): The number of shares to buy.
            from_watchlist (bool): True if the buy request came from the watchlist table.
        """
        if not symbol:
            # Show warning if no symbol is entered
            QMessageBox.warning(self, "Invalid Input", "Please enter a stock symbol to buy.")
            return

        try:
            # Fetch 1 day of data to get the current price
            data = yf.download(symbol, period="1d", progress=False)
            if data.empty:
                # Show warning if ticker is not found or data is unavailable
                QMessageBox.warning(self, "Invalid Ticker", f"Stock ticker '{symbol}' not found or data unavailable.")
                return
            # Check if the 'Close' price column exists for the symbol
            elif ('Close', symbol) not in data.columns:
                 # Show warning if closing price is not available
                QMessageBox.warning(self, "Invalid Data", f"Could not retrieve closing price for '{symbol}'.")
                return

            # Get the last closing price, handling potential MultiIndex and NaN
            last_close = data[('Close', symbol)].iloc[-1]
            if isinstance(last_close, pd.Series):
                last_close = last_close.squeeze() # Convert Series to scalar if necessary
            try:
                # Convert price to float, default to 0.0 if NaN or conversion fails
                price = float(last_close) if pd.notna(last_close) else 0.0
            except (ValueError, TypeError):
                # Show warning if price cannot be parsed
                QMessageBox.warning(self, "Invalid Price", f"Could not parse price for '{symbol}'.")
                return

            total_cost = price * quantity # Calculate the total cost of the purchase
            # Check if the user has enough simulated cash
            if self.settings_tab.simulated_cash >= total_cost:
                self.settings_tab.simulated_cash -= total_cost # Deduct cost from cash
                # Update the cash input display in the settings tab
                self.settings_tab.cash_input.setValue(self.settings_tab.simulated_cash)
                # Add the purchased quantity to the portfolio
                self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
                self.update_portfolio_and_cash() # Update portfolio table and cash display
                if symbol not in self.watchlist_symbols:
                    # Add the symbol to the watchlist if it wasn't already there
                    self.watchlist_symbols.append(symbol)
                self.update_watchlist_table()  # Refresh watchlist to show 'Owned' status
                self.plot_stocks() # Update the plot
            else:
                # Show warning if insufficient funds
                QMessageBox.warning(self, "Insufficient Funds", "You do not have enough funds.")

        except Exception as e:
            # Show critical error if an unexpected exception occurs during buying
            QMessageBox.critical(self, "Error", f"An error occurred while trying to buy '{symbol}': {e}")

    def sell_stock(self, symbol):
        """
        Handles selling a stock from the portfolio using an input dialog for quantity.

        Args:
            symbol (str): The symbol of the stock to sell.
        """
        if symbol and symbol in self.portfolio and self.portfolio[symbol] > 0:
            # Open an input dialog to get the quantity to sell
            quantity_owned = self.portfolio[symbol]
            quantity_to_sell, ok = QInputDialog.getInt(
                self, "Sell Stock", f"Enter quantity to sell for {symbol}:", 1, 1, quantity_owned, 1
            )

            if ok and quantity_to_sell > 0: # If the user clicked OK and entered a valid quantity
                # Fetch 1 day of data to get the current selling price
                data = stock_fetcher.fetch(symbol, period="1d")
                price = 0.0 # Initialize price

                if not data.empty and ('Close', symbol) in data.columns:
                    # Get the last closing price, handling potential MultiIndex and NaN
                    last_close = data[('Close', symbol)].iloc[-1]
                    if isinstance(last_close, pd.Series):
                        last_close = last_close.squeeze() # Convert Series to scalar if necessary
                    try:
                        # Convert price to float, default to 0.0 if NaN or conversion fails
                        price = float(last_close) if pd.notna(last_close) else 0.0
                    except (ValueError, TypeError):
                        price = 0.0 # Set price to 0.0 on conversion error

                # Check if the user has enough shares to sell (already checked by QInputDialog range, but good practice)
                if self.portfolio.get(symbol, 0) >= quantity_to_sell:
                    total_sale = price * quantity_to_sell # Calculate the total sale amount
                    self.portfolio[symbol] -= quantity_to_sell # Deduct sold quantity from portfolio
                    self.settings_tab.simulated_cash += total_sale # Add sale amount to cash
                    # Update the cash input display in the settings tab
                    self.settings_tab.cash_input.setValue(self.settings_tab.simulated_cash)
                    if self.portfolio[symbol] == 0:
                        # Remove the symbol from the portfolio if quantity becomes zero
                        del self.portfolio[symbol]
                    self.update_portfolio_and_cash() # Update portfolio table and cash display
                    self.update_watchlist_table()  # Refresh watchlist to update 'Owned' status
                else:
                    # This case should ideally not be reached due to QInputDialog range
                    QMessageBox.warning(self, "Insufficient Shares", "You do not have enough shares to sell.")
        elif symbol not in self.portfolio or self.portfolio[symbol] == 0:
             QMessageBox.information(self, "No Shares", f"You do not own any shares of {symbol} to sell.")


    def update_portfolio_and_cash(self):
        """
        Updates the portfolio table and the cash display in the settings tab.
        Also triggers a plot update.
        """
        self.update_portfolio_table() # Update the portfolio table
        self.plot_stocks() # Update the plot
        # Update the cash available label in the market data tab
        self.cash_label.setText(f"Cash Available: ${self.settings_tab.simulated_cash:.2f}")


    def update_portfolio_table(self):
        """
        Updates the portfolio table with the current holdings and calculates total value.
        Removed the "Sell Qty" column.
        """
        self.stock_table.setRowCount(0) # Clear existing rows
        # Updated column count and headers (removed "Sell Qty")
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels(["Stock", "Price", "Quantity", "Value", "Sell"])
        stock_value = 0.0 # Initialize total stock value

        for symbol, quantity in self.portfolio.items():
            # Fetch 1 day of data for the symbol to get the current price
            data = stock_fetcher.fetch(symbol, period="1d")
            price = 0.0 # Initialize price

            if not data.empty and ('Close', symbol) in data.columns:
                # Get the last closing price, handling potential MultiIndex and NaN
                last_close = data[('Close', symbol)].iloc[-1]
                if isinstance(last_close, pd.Series):
                    last_close = last_close.squeeze() # Convert Series to scalar if necessary
                try:
                    # Convert price to float, default to 0.0 if NaN or conversion fails
                    price = float(last_close) if pd.notna(last_close) else 0.0
                except (ValueError, TypeError):
                    price = 0.0 # Set price to 0.0 on conversion error

            value = price * quantity # Calculate the value of the holding
            stock_value += value # Add to the total stock value

            row_position = self.stock_table.rowCount() # Get the current row count
            self.stock_table.insertRow(row_position) # Insert a new row
            # Set table items with holding details
            self.stock_table.setItem(row_position, 0, QTableWidgetItem(symbol))
            self.stock_table.setItem(row_position, 1, QTableWidgetItem(f"{price:.2f}"))
            self.stock_table.setItem(row_position, 2, QTableWidgetItem(str(quantity)))
            self.stock_table.setItem(row_position, 3, QTableWidgetItem(f"${value:.2f}"))

            # Add Sell button (now in column 4)
            sell_button = QPushButton("Sell")
            # Connect button click to sell_stock method using a lambda, passing only the symbol
            sell_button.clicked.connect(lambda _, s=symbol: self.sell_stock(s))
            self.stock_table.setCellWidget(row_position, 4, sell_button) # Add button to 'Sell' column


        # Calculate total portfolio value (stocks + cash)
        total_portfolio_value = stock_value + self.settings_tab.simulated_cash
        # Update the total portfolio value label text
        self.portfolio_label.setText(f"Total Portfolio Value: ${total_portfolio_value:.2f}")


    def plot_stocks(self):
        """
        Plots the closing prices of the stocks in the watchlist for the last month.
        Uses the integrated matplotlib canvas.
        """
        self.ax.clear() # Clear the previous plot
        today = pd.Timestamp.today() # Get today's date
        one_month_ago = today - pd.DateOffset(months=1) # Calculate date one month ago

        if not self.watchlist_symbols:
            # Display a message if no stocks are being tracked
            self.ax.set_title("No stocks being tracked.")
        else:
            for symbol in self.watchlist_symbols:
                # Fetch 1 month of data for each symbol
                data = stock_fetcher.fetch(symbol, period="1mo")
                # Check if data is not empty and contains the closing price for the symbol
                if not data.empty and ('Close', symbol) in data.columns:
                    data.index = pd.to_datetime(data.index) # Ensure index is datetime
                    data = data.sort_index() # Sort data by date
                    # Filter data for the last month
                    recent_data = data[(data.index >= one_month_ago) & (data.index <= today)]

                    if not recent_data.empty:
                        # Plot the closing price for the symbol
                        self.ax.plot(recent_data.index, recent_data[('Close', symbol)], label=symbol)

            self.ax.set_title("Stock Closing Prices (Last Month)") # Set plot title
            self.ax.set_xlabel("Date") # Set x-axis label
            self.ax.set_ylabel("Closing Price") # Set y-axis label
            self.ax.legend() # Show legend with stock symbols
            self.ax.grid(True) # Add grid
            self.figure.autofmt_xdate() # Auto-format x-axis dates
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) # Format dates
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator()) # Auto-locate date ticks

        self.canvas.draw() # Redraw the canvas to show the updated plot


class MainWindow(QMainWindow):
    """
    The main application window containing tabs for market data and settings.
    """
    def __init__(self):
        """
        Initializes the MainWindow.
        """
        super().__init__()
        self.setWindowTitle("Stock Trading Simulator") # Set window title
        self.setGeometry(100, 100, 1000, 800) # Set window position and size

        self.tab_widget = QTabWidget() # Create a tab widget
        self.setCentralWidget(self.tab_widget) # Set the tab widget as the central widget

        self.settings_tab = SettingsTab(self) # Create the settings tab
        self.market_tab = MarketDataTab(self.settings_tab) # Create the market data tab, passing the settings tab

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.market_tab, "Market Data")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        # Apply the default theme from settings on startup
        self.settings_tab.apply_theme(self.settings_tab.theme_combo.currentIndex())


if __name__ == '__main__':
    # Create the application instance
    app = QApplication(sys.argv)
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    # Start the application event loop
    sys.exit(app.exec_())

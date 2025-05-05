import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QDoubleSpinBox, QSpinBox, QComboBox, QGridLayout,
    QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import QTimer

# Import the stock_fetcher instance
from stock_fetcher import stock_fetcher

class AutoTradingTab(QWidget):
    """
    Provides a tab for setting up and simulating auto trading rules.
    """
    def __init__(self, market_tab):
        """
        Initializes the AutoTradingTab.

        Args:
            market_tab (MarketDataTab): Reference to the market data tab for portfolio updates.
        """
        super().__init__()
        self.market_tab = market_tab # Reference to the market data tab
        self.auto_trade_rules = [] # List to store auto trading rules
        self.timer = QTimer(self) # Timer for simulating price checks
        self.timer.timeout.connect(self.check_auto_trade_rules) # Connect timeout signal to check rules
        self.init_ui() # Initialize the user interface


    def init_ui(self):
        """
        Initializes the user interface for the auto trading tab.
        """
        layout = QVBoxLayout() # Main vertical layout

        # Section for adding new rules
        rules_group_box = QWidget()
        rules_layout = QGridLayout() # Use grid layout for inputs

        symbol_label = QLabel("Stock Symbol:")
        self.rule_symbol_input = QLineEdit()
        self.rule_symbol_input.setPlaceholderText("e.g., GOOG")
        rules_layout.addWidget(symbol_label, 0, 0)
        rules_layout.addWidget(self.rule_symbol_input, 0, 1)

        rule_type_label = QLabel("Rule Type:")
        self.rule_type_combo = QComboBox()
        self.rule_type_combo.addItems(["Buy (Limit)", "Sell (Stop Loss)", "Sell (Take Profit)"])
        rules_layout.addWidget(rule_type_label, 1, 0)
        rules_layout.addWidget(self.rule_type_combo, 1, 1)

        price_label = QLabel("Target Price:")
        self.rule_price_input = QDoubleSpinBox()
        self.rule_price_input.setRange(0.01, 100000.00)
        self.rule_price_input.setPrefix("$")
        self.rule_price_input.setDecimals(2)
        rules_layout.addWidget(price_label, 2, 0)
        rules_layout.addWidget(self.rule_price_input, 2, 1)

        quantity_label = QLabel("Quantity:")
        self.rule_quantity_input = QSpinBox()
        self.rule_quantity_input.setRange(1, 10000)
        rules_layout.addWidget(quantity_label, 3, 0)
        rules_layout.addWidget(self.rule_quantity_input, 3, 1)

        add_rule_button = QPushButton("Add Rule")
        add_rule_button.clicked.connect(self.add_auto_trade_rule)
        rules_layout.addWidget(add_rule_button, 4, 0, 1, 2) # Span button across two columns

        rules_group_box.setLayout(rules_layout)
        layout.addWidget(QLabel("Add Auto Trading Rule:"))
        layout.addWidget(rules_group_box)

        # Section for active rules
        layout.addWidget(QLabel("Active Auto Trading Rules:"))
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels(["Stock", "Type", "Target Price", "Quantity", "Remove"])
        self.rules_table.verticalHeader().setVisible(False) # Hide row numbers
        self.rules_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Prevent editing
        self.rules_table.setSelectionMode(QAbstractItemView.SingleSelection) # Single row selection
        layout.addWidget(self.rules_table)

        # Control buttons for simulation
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Auto Trading (Simulated)")
        self.start_button.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Auto Trading (Simulated)")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False) # Disable stop button initially
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)


        self.setLayout(layout) # Set the main layout

    def add_auto_trade_rule(self):
        """
        Adds a new auto trading rule based on user input.
        """
        symbol = self.rule_symbol_input.text().strip().upper()
        rule_type = self.rule_type_combo.currentText()
        target_price = self.rule_price_input.value()
        quantity = self.rule_quantity_input.value()

        if not symbol:
            QMessageBox.warning(self, "Invalid Input", "Please enter a stock symbol.")
            return

        # Basic validation for sell rules - check if stock is in portfolio
        if "Sell" in rule_type:
            if symbol not in self.market_tab.portfolio or self.market_tab.portfolio.get(symbol, 0) < quantity:
                 QMessageBox.warning(self, "Insufficient Shares", f"You do not own {quantity} shares of {symbol} to set a sell rule.")
                 return


        rule = {
            "symbol": symbol,
            "type": rule_type,
            "target_price": target_price,
            "quantity": quantity
        }

        self.auto_trade_rules.append(rule)
        self.update_rules_table() # Update the table display
        self.clear_rule_inputs() # Clear input fields

    def remove_auto_trade_rule(self, rule_index):
        """
        Removes an auto trading rule by index.
        """
        if 0 <= rule_index < len(self.auto_trade_rules):
            del self.auto_trade_rules[rule_index]
            self.update_rules_table() # Update the table display

    def update_rules_table(self):
        """
        Updates the table displaying active auto trading rules.
        """
        self.rules_table.setRowCount(0) # Clear existing rows
        for i, rule in enumerate(self.auto_trade_rules):
            row_position = self.rules_table.rowCount()
            self.rules_table.insertRow(row_position)

            self.rules_table.setItem(row_position, 0, QTableWidgetItem(rule["symbol"]))
            self.rules_table.setItem(row_position, 1, QTableWidgetItem(rule["type"]))
            self.rules_table.setItem(row_position, 2, QTableWidgetItem(f"${rule['target_price']:.2f}"))
            self.rules_table.setItem(row_position, 3, QTableWidgetItem(str(rule["quantity"])))

            # Add Remove button
            remove_button = QPushButton("Remove")
            # Use a lambda to pass the rule index to the remove method
            remove_button.clicked.connect(lambda _, index=i: self.remove_auto_trade_rule(index))
            self.rules_table.setCellWidget(row_position, 4, remove_button)


    def clear_rule_inputs(self):
        """
        Clears the input fields for adding a new rule.
        """
        self.rule_symbol_input.clear()
        self.rule_price_input.setValue(0.01)
        self.rule_quantity_input.setValue(1)
        self.rule_type_combo.setCurrentIndex(0)

    def start_simulation(self):
        """
        Starts the simulated auto trading process.
        """
        if not self.timer.isActive():
            self.timer.start(5000) # Check rules every 5 seconds (simulate real-time)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            print("Auto trading simulation started.") # Console notification

    def stop_simulation(self):
        """
        Stops the simulated auto trading process.
        """
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            print("Auto trading simulation stopped.") # Console notification

    def check_auto_trade_rules(self):
        """
        Checks active auto trading rules against current stock prices (simulated).
        Executes simulated trades if rules are met.
        """
        print("Checking auto trade rules...") # Console notification
        executed_rules_indices = [] # Keep track of rules to remove after checking

        for i, rule in enumerate(self.auto_trade_rules):
            symbol = rule["symbol"]
            rule_type = rule["type"]
            target_price = rule["target_price"]
            quantity = rule["quantity"]

            # Simulate fetching the current price
            # In a real application, you would fetch the actual current price here.
            # For simulation, we'll fetch the latest available price from yfinance (which might be delayed)
            try:
                data = stock_fetcher.fetch(symbol, period="1d")
                if data.empty or ('Close', symbol) not in data.columns:
                    print(f"Could not fetch current price for {symbol}. Skipping rule.")
                    continue

                current_price = data[('Close', symbol)].iloc[-1]
                if isinstance(current_price, pd.Series):
                     current_price = current_price.squeeze()
                if pd.isna(current_price):
                     print(f"Current price for {symbol} is not available. Skipping rule.")
                     continue

                print(f"Checking rule for {symbol} ({rule_type}). Current Price: ${current_price:.2f}, Target Price: ${target_price:.2f}") # Console notification

                trade_executed = False

                if rule_type == "Buy (Limit)":
                    # Simulate a limit buy order: buy if current price is at or below target price
                    if current_price <= target_price:
                        print(f"Simulated Buy Order Triggered: {quantity} shares of {symbol} at ${current_price:.2f}") # Console notification
                        # Simulate the buy action
                        total_cost = current_price * quantity
                        if self.market_tab.settings_tab.simulated_cash >= total_cost:
                            self.market_tab.settings_tab.simulated_cash -= total_cost
                            self.market_tab.portfolio[symbol] = self.market_tab.portfolio.get(symbol, 0) + quantity
                            self.market_tab.update_portfolio_and_cash()
                            self.market_tab.update_watchlist_table() # Update watchlist to show owned status
                            QMessageBox.information(self, "Simulated Trade Executed",
                                                    f"Simulated Buy: {quantity} shares of {symbol} at ${current_price:.2f}")
                            trade_executed = True
                        else:
                            print(f"Simulated Buy Failed: Insufficient funds for {symbol}.") # Console notification
                            QMessageBox.warning(self, "Simulated Trade Failed",
                                                f"Simulated Buy Failed: Insufficient funds for {symbol}.")


                elif rule_type == "Sell (Stop Loss)":
                    # Simulate a stop loss order: sell if current price is at or below target price
                    # Also check if the user actually owns the stock
                    if current_price <= target_price and self.market_tab.portfolio.get(symbol, 0) >= quantity:
                        print(f"Simulated Sell (Stop Loss) Triggered: {quantity} shares of {symbol} at ${current_price:.2f}") # Console notification
                        # Simulate the sell action
                        total_sale = current_price * quantity
                        self.market_tab.portfolio[symbol] = self.market_tab.portfolio.get(symbol, 0) - quantity
                        self.market_tab.settings_tab.simulated_cash += total_sale
                        if self.market_tab.portfolio[symbol] == 0:
                             del self.market_tab.portfolio[symbol]
                        self.market_tab.update_portfolio_and_cash()
                        self.market_tab.update_watchlist_table() # Update watchlist to show owned status
                        QMessageBox.information(self, "Simulated Trade Executed",
                                                f"Simulated Sell (Stop Loss): {quantity} shares of {symbol} at ${current_price:.2f}")
                        trade_executed = True
                    elif current_price <= target_price and self.market_tab.portfolio.get(symbol, 0) < quantity:
                         print(f"Simulated Sell (Stop Loss) Failed: Insufficient shares for {symbol}.") # Console notification
                         # Rule remains active if shares are insufficient, might execute later if more shares are acquired
                         pass # Don't mark for deletion if shares are insufficient

                elif rule_type == "Sell (Take Profit)":
                    # Simulate a take profit order: sell if current price is at or above target price
                     # Also check if the user actually owns the stock
                    if current_price >= target_price and self.market_tab.portfolio.get(symbol, 0) >= quantity:
                        print(f"Simulated Sell (Take Profit) Triggered: {quantity} shares of {symbol} at ${current_price:.2f}") # Console notification
                        # Simulate the sell action
                        total_sale = current_price * quantity
                        self.market_tab.portfolio[symbol] = self.market_tab.portfolio.get(symbol, 0) - quantity
                        self.market_tab.settings_tab.simulated_cash += total_sale
                        if self.market_tab.portfolio[symbol] == 0:
                             del self.market_tab.portfolio[symbol]
                        self.market_tab.update_portfolio_and_cash()
                        self.market_tab.update_watchlist_table() # Update watchlist to show owned status
                        QMessageBox.information(self, "Simulated Trade Executed",
                                                f"Simulated Sell (Take Profit): {quantity} shares of {symbol} at ${current_price:.2f}")
                        trade_executed = True
                    elif current_price >= target_price and self.market_tab.portfolio.get(symbol, 0) < quantity:
                         print(f"Simulated Sell (Take Profit) Failed: Insufficient shares for {symbol}.") # Console notification
                         # Rule remains active if shares are insufficient, might execute later if more shares are acquired
                         pass # Don't mark for deletion if shares are insufficient

                if trade_executed:
                    executed_rules_indices.append(i) # Mark rule for removal

            except Exception as e:
                print(f"Error checking rule for {symbol}: {e}") # Console notification

        # Remove executed rules in reverse order to avoid index issues
        for index in sorted(executed_rules_indices, reverse=True):
            del self.auto_trade_rules[index]

        self.update_rules_table() # Update the table after removing executed rules

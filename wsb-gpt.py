import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

# Import the separated classes
from settings_tab import SettingsTab
from market_data_tab import MarketDataTab
from sentiment_analysis_tab import SentimentAnalysisTab
from auto_trading_tab import AutoTradingTab

class MainWindow(QMainWindow):
    """
    The main application window containing tabs for market data, settings, and sentiment analysis.
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

        # Instantiate the tabs, passing necessary references
        self.settings_tab = SettingsTab(self)
        self.market_tab = MarketDataTab(self.settings_tab)
        self.sentiment_tab = SentimentAnalysisTab()
        self.auto_trading_tab = AutoTradingTab(self.market_tab)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.market_tab, "Market Data")
        self.tab_widget.addTab(self.sentiment_tab, "Sentiment Analysis")
        self.tab_widget.addTab(self.auto_trading_tab, "Auto Trading")
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

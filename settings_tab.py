from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QComboBox
)
from PyQt5.QtGui import QColor, QBrush, QPalette

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
        self.theme_combo.addItems(["Blackout", "Light", "Dark", "High Contrast"])
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
        # Access the market_tab through the main_window reference
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
                QHeaderView::section { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; } /* Added styling for header sections */
                QPushButton { background-color: #555; color: #f0f0f0; border: 1px solid #777; padding: 5px; }
                QPushButton:hover { background-color: #666; }
                QComboBox { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; }
                QComboBox::drop-down { background-color: #4a4a4a; border: 0px; }
                QComboBox::down-arrow { color: #f0f0f0; }
                QLabel { color: #f0f0f0; }
                QTextEdit { background-color: #4a4a4a; color: #f0f0f0; border: 1px solid #666; } /* Added styling for QTextEdit */
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
                QHeaderView::section { background-color: #333; color: yellow; border: 1px solid yellow; } /* Added styling for header sections */
                QPushButton { background-color: #555; color: yellow; border: 1px solid yellow; padding: 5px; }
                QPushButton:hover { background-color: #777; color: black; }
                QComboBox { background-color: #333; color: yellow; border: 1px solid yellow; }
                QComboBox::drop-down { background-color: #333; border: 0px; }
                QComboBox::down-arrow { color: yellow; }
                QLabel { color: yellow; }
                QTextEdit { background-color: #333; color: yellow; border: 1px solid yellow; } /* Added styling for QTextEdit */
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
                QHeaderView::section { background-color: #222; color: #ccc; border: 1px solid #444; } /* Added styling for header sections */
                QPushButton { background-color: #333; color: #ccc; border: 1px solid #555; padding: 5px; }
                QPushButton:hover { background-color: #444; }
                QComboBox { background-color: #222; color: #ccc; border: 1px solid #444; }
                QComboBox::drop-down { background-color: #222; border: 0px; }
                QComboBox::down-arrow { color: #ccc; }
                QLabel { color: #ccc; }
                QTextEdit { background-color: #222; color: #ccc; border: 1px solid #444; } /* Added styling for QTextEdit */
            """)

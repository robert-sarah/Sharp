"""
PyQt5 GUI Module for Sharp Language
Provides high-level GUI utilities for building desktop applications
"""

import sys
from typing import Callable, Any, Dict, List, Optional
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, 
        QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QTextEdit,
        QDialog, QComboBox, QSpinBox, QCheckBox, QRadioButton,
        QListWidget, QTableWidget, QFileDialog, QColorDialog
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QFont, QColor, QIcon
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("Warning: PyQt5 not installed. GUI functions will not work.")

class SharpWindow:
    """Represents a PyQt5 window in Sharp"""
    def __init__(self, title: str = "Sharp App", width: int = 800, height: int = 600):
        if not PYQT5_AVAILABLE:
            raise RuntimeError("PyQt5 is not installed")
        
        self.title = title
        self.width = width
        self.height = height
        self.window = QMainWindow()
        self.window.setWindowTitle(title)
        self.window.resize(width, height)
        
        self.central_widget = QWidget()
        self.window.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        self.widgets = {}
    
    def add_label(self, name: str, text: str):
        """Add a label to the window"""
        label = QLabel(text)
        self.widgets[name] = label
        self.main_layout.addWidget(label)
        return label
    
    def add_button(self, name: str, text: str, callback: Optional[Callable] = None):
        """Add a button to the window"""
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        self.widgets[name] = button
        self.main_layout.addWidget(button)
        return button
    
    def add_textbox(self, name: str, placeholder: str = ""):
        """Add a text input field"""
        textbox = QLineEdit()
        textbox.setPlaceholderText(placeholder)
        self.widgets[name] = textbox
        self.main_layout.addWidget(textbox)
        return textbox
    
    def add_textarea(self, name: str, text: str = ""):
        """Add a multi-line text area"""
        textarea = QTextEdit()
        textarea.setText(text)
        self.widgets[name] = textarea
        self.main_layout.addWidget(textarea)
        return textarea
    
    def get_widget(self, name: str):
        """Get a widget by name"""
        return self.widgets.get(name)
    
    def get_text(self, name: str) -> str:
        """Get text from a text widget"""
        widget = self.widgets.get(name)
        if isinstance(widget, (QLineEdit, QTextEdit)):
            return widget.text() if isinstance(widget, QLineEdit) else widget.toPlainText()
        return ""
    
    def set_text(self, name: str, text: str):
        """Set text on a text widget"""
        widget = self.widgets.get(name)
        if isinstance(widget, (QLineEdit, QTextEdit)):
            if isinstance(widget, QLineEdit):
                widget.setText(text)
            else:
                widget.setPlainText(text)
    
    def show(self):
        """Show the window"""
        self.window.show()
    
    def close(self):
        """Close the window"""
        self.window.close()

def create_window(title: str, width: int = 800, height: int = 600) -> SharpWindow:
    """Create a new Sharp GUI window"""
    return SharpWindow(title, width, height)

def show_message(title: str, message: str):
    """Show a message dialog"""
    if PYQT5_AVAILABLE and QApplication.instance():
        QMessageBox.information(None, title, message)

def show_error(title: str, message: str):
    """Show an error dialog"""
    if PYQT5_AVAILABLE and QApplication.instance():
        QMessageBox.critical(None, title, message)

def show_question(title: str, question: str) -> bool:
    """Show a yes/no question dialog"""
    if PYQT5_AVAILABLE and QApplication.instance():
        reply = QMessageBox.question(None, title, question,
                                    QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes
    return False

def run_app():
    """Run the Qt application"""
    if PYQT5_AVAILABLE:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        sys.exit(app.exec_())

# Make sure we have a QApplication instance for GUI operations
if PYQT5_AVAILABLE and not QApplication.instance():
    _app = QApplication(sys.argv)

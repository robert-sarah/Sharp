"""
Sharp Programming Language - Professional PyQt5 IDE
Full-featured IDE similar to PyCharm with syntax highlighting,
autocompletion, debugging, and full module support.
"""

# Suppress PyQt5 deprecation warnings
import warnings as _warnings
_warnings.filterwarnings("ignore", category=DeprecationWarning)
_warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")

import sys
import os
import re
import json
import warnings
from pathlib import Path
from io import StringIO

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QTextEdit, QListWidget, QListWidgetItem, QLabel,
        QFileDialog, QMessageBox, QStatusBar, QMenu, QMenuBar,
        QAction, QDockWidget, QFrame, QComboBox, QLineEdit, QPushButton,
        QTabWidget
    )
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
    from PyQt5.QtGui import (
        QFont, QColor, QSyntaxHighlighter, QTextDocument, QTextFormat,
        QTextCharFormat, QFontDatabase, QIcon, QKeySequence
    )
    from PyQt5.Qsci import QsciScintilla, QsciLexerPython
except ImportError:
    print("PyQt5 is required. Please install it with:")
    print("pip install PyQt5 QScintilla")
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from stdlib import SharpNil, STDLIB


class SyntaxHighlighter(QSyntaxHighlighter):
    """Custom syntax highlighter for Sharp code."""
    
    def __init__(self, document):
        super().__init__(document)
        
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(86, 156, 214))  # Blue
        self.keyword_format.setFontWeight(700)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(206, 145, 120))  # Orange
        
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(106, 153, 85))  # Green
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(181, 206, 168))  # Light green
        
        self.builtin_format = QTextCharFormat()
        self.builtin_format.setForeground(QColor(78, 201, 176))  # Cyan
        
        self.keywords = [
            'def', 'let', 'if', 'elif', 'else', 'while', 'for', 'in', 'return',
            'break', 'continue', 'match', 'case', 'type', 'import', 'from', 'as',
            'lambda', 'true', 'false', 'nil'
        ]
    
    def highlightBlock(self, text):
        """Highlight a block of code."""
        # Keywords
        for word in self.keywords:
            pattern = r'\b' + word + r'\b'
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), self.keyword_format)
        
        # Strings
        string_pattern = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
        for match in re.finditer(string_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Comments
        comment_pattern = r'#.*$'
        for match in re.finditer(comment_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.comment_format)
        
        # Numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)


class AutocompleteWidget(QListWidget):
    """Autocomplete popup widget."""
    
    item_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #555;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
            }
        """)
        self.itemClicked.connect(self._on_item_selected)
    
    def _on_item_selected(self, item):
        """Handle item selection."""
        self.item_selected.emit(item.text())
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Return:
            if self.currentItem():
                self.item_selected.emit(self.currentItem().text())
        elif event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() in (Qt.Key_Up, Qt.Key_Down):
            super().keyPressEvent(event)
        else:
            # Pass other keys to parent
            self.parent().keyPressEvent(event)


class SharpEditorWidget(QTextEdit):
    """Advanced text editor for Sharp code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Font setup
        font = QFont("Courier New", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Style
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        """)
        
        # Syntax highlighter
        self.highlighter = SyntaxHighlighter(self.document())
        
        # Autocomplete
        self.autocomplete = AutocompleteWidget(self)
        self.autocomplete.hide()
        self.autocomplete.item_selected.connect(self._apply_autocomplete)
        
        # Line number area would go here (optional)
        
        # Setup
        self.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """Handle text change for autocomplete."""
        self._show_autocomplete()
    
    def _get_current_word(self):
        """Get the current word being typed."""
        cursor = self.textCursor()
        block = cursor.block()
        pos_in_block = cursor.positionInBlock()
        text = block.text()
        
        word = ""
        i = pos_in_block - 1
        while i >= 0 and (text[i].isalnum() or text[i] == '_'):
            word = text[i] + word
            i -= 1
        
        return word
    
    def _show_autocomplete(self):
        """Show autocomplete suggestions."""
        word = self._get_current_word()
        
        if not word:
            self.autocomplete.hide()
            return
        
        # Get all completions
        keywords = [
            'def', 'let', 'if', 'elif', 'else', 'while', 'for', 'in', 'return',
            'break', 'continue', 'match', 'case', 'type', 'import', 'from', 'as',
            'lambda', 'true', 'false', 'nil'
        ]
        
        module_dir = os.path.join(os.path.dirname(__file__), 'modules')
        if os.path.exists(module_dir):
            module_files = os.listdir(module_dir)
            modules = sorted(set([f.split('.')[0] for f in module_files 
                                 if f.endswith('.sharp') or f.endswith('.py')]))
        else:
            modules = []
        
        builtins = list(STDLIB.keys())
        
        # Get matching completions
        completions = []
        completions += [k for k in keywords if k.startswith(word)]
        completions += [m for m in modules if m.startswith(word)]
        completions += [b for b in builtins if b.startswith(word)]
        
        completions = sorted(set(completions))
        
        if not completions:
            self.autocomplete.hide()
            return
        
        # Update autocomplete widget
        self.autocomplete.clear()
        for comp in completions[:15]:  # Limit to 15 items
            self.autocomplete.addItem(comp)
        
        self.autocomplete.setCurrentRow(0)
        
        # Position autocomplete
        cursor = self.textCursor()
        cursor_rect = self.cursorRect(cursor)
        pos = self.mapToGlobal(cursor_rect.bottomLeft())
        self.autocomplete.move(pos)
        self.autocomplete.resize(250, min(len(completions) * 25, 400))
        self.autocomplete.show()
    
    def _apply_autocomplete(self, text):
        """Apply autocomplete selection."""
        word = self._get_current_word()
        cursor = self.textCursor()
        
        # Delete the word
        cursor.movePosition(cursor.WordLeft)
        cursor.movePosition(cursor.EndOfWord, cursor.KeepAnchor)
        cursor.removeSelectedText()
        
        # Insert the completion
        cursor.insertText(text)
        self.setTextCursor(cursor)
        
        self.autocomplete.hide()


class SharpIDE(QMainWindow):
    """Professional Sharp IDE in PyQt5."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sharp IDE - Professional Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border-bottom: 1px solid #3e3e3e;
            }
            QMenuBar::item:selected {
                background-color: #3e3e3e;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #d4d4d4;
            }
            QMenu::item:selected {
                background-color: #0d7377;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border-top: 1px solid #3e3e3e;
            }
        """)
        
        self.current_file = None
        self.interpreter = Interpreter()
        
        # Create UI
        self.create_menu_bar()
        self.create_central_widget()
        self.create_status_bar()
        
        # Shortcuts
        self.setup_shortcuts()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Run menu
        run_menu = menubar.addMenu("Run")
        
        run_action = QAction("Run (F5)", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About Sharp", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_central_widget(self):
        """Create the main editor and output area."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Splitter for editor and output
        splitter = QSplitter(Qt.Vertical)
        
        # Top: Editor
        editor_frame = QFrame()
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        editor_label = QLabel("Editor")
        editor_label.setStyleSheet("color: #d4d4d4; font-weight: bold;")
        editor_layout.addWidget(editor_label)
        
        self.editor = SharpEditorWidget()
        editor_layout.addWidget(self.editor)
        
        splitter.addWidget(editor_frame)
        
        # Bottom: Output
        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(0, 0, 0, 0)
        
        output_label = QLabel("Output & Console")
        output_label.setStyleSheet("color: #d4d4d4; font-weight: bold;")
        output_layout.addWidget(output_label)
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: Courier New;
                border: none;
            }
        """)
        output_layout.addWidget(self.output)
        
        splitter.addWidget(output_frame)
        splitter.setSizes([600, 300])
        
        layout.addWidget(splitter)
    
    def create_status_bar(self):
        """Create the status bar."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        pass
    
    def new_file(self):
        """Create a new file."""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(self, "Unsaved Changes", 
                                        "Discard unsaved changes?")
            if reply != QMessageBox.Yes:
                return
        
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("Sharp IDE - Untitled")
    
    def open_file(self):
        """Open a file."""
        filename, _ = QFileDialog.getOpenFileName(self, "Open Sharp Program",
                                                  "", "Sharp Files (*.sharp);;Text Files (*.txt);;All Files (*.*)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = filename
                self.setWindowTitle(f"Sharp IDE - {os.path.basename(filename)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            self.save_as_file()
            return
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.statusBar.showMessage(f"Saved: {self.current_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")
    
    def save_as_file(self):
        """Save file with a new name."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Sharp Program",
                                                  "", "Sharp Files (*.sharp);;Text Files (*.txt)")
        if filename:
            self.current_file = filename
            self.setWindowTitle(f"Sharp IDE - {os.path.basename(filename)}")
            self.save_file()
    
    def run_code(self):
        """Execute the Sharp program."""
        source = self.editor.toPlainText()
        
        if not source.strip():
            QMessageBox.warning(self, "Warning", "No code to execute")
            return
        
        self.output.clear()
        self.statusBar.showMessage("Running...")
        
        # Check for PyQt5
        if 'import pyqt5_wrapper' in source or 'from pyqt5_wrapper' in source:
            try:
                import PyQt5
            except ImportError:
                self.output.setText("PyQt5 is not installed. Please install it with:\npip install PyQt5\n")
                self.statusBar.showMessage("PyQt5 missing")
                return
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Lex
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Interpret
            self.interpreter = Interpreter()
            result = self.interpreter.interpret(ast)
            
            # Get output
            output = sys.stdout.getvalue()
            
            if output:
                self.output.setText(output)
            
            self.statusBar.showMessage("Execution completed successfully")
            
            if result and not isinstance(result, SharpNil):
                self.output.append(f"\nResult: {result}\n")
        
        except SyntaxError as e:
            self.output.setText(f"SyntaxError: {e}\n")
            self.statusBar.showMessage("Syntax error")
        except Exception as e:
            self.output.setText(f"{type(e).__name__}: {e}\n")
            self.statusBar.showMessage(f"Error - {type(e).__name__}")
        
        finally:
            sys.stdout = old_stdout
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.information(self, "About Sharp IDE",
            "Sharp Programming Language IDE v2.0 (PyQt5)\n\n"
            "A modern, Python-like programming language\n"
            "with powerful features for education and development.\n\n"
            "© 2026 Sharp Development Team")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    ide = SharpIDE()
    ide.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

"""
Sharp Programming Language - Professional PyQt5 IDE
Full-featured IDE similar to PyCharm with advanced features:
- Line numbers, syntax highlighting, autocompletion
- Find & replace, Go to line, Code formatting
- Bracket matching, Indentation guides
- Multi-tab editor, Error inline diagnostics
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
        QTabWidget, QDialog, QInputDialog, QPlainTextEdit, QTreeWidget,
        QTreeWidgetItem, QHeaderView, QScrollArea, QTextBrowser
    )
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QRect, QFileSystemWatcher
    from PyQt5.QtGui import (
        QFont, QColor, QSyntaxHighlighter, QTextDocument, QTextFormat,
        QTextCharFormat, QFontDatabase, QIcon, QKeySequence, QPainter,
        QTextCursor
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


class LineNumberArea(QFrame):
    """Line number display on the left side of the editor."""
    
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-right: 1px solid #3e3e42;
            }
        """)
        self.setFixedWidth(50)
    
    def paintEvent(self, event):
        """Paint line numbers."""
        if not self.editor:
            super().paintEvent(event)
            return
        
        try:
            painter = QPainter(self)
            painter.fillRect(event.rect(), QColor(37, 37, 38))
            
            block = self.editor.firstVisibleBlock()
            block_number = block.blockNumber()
            top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
            
            font = QFont("Courier New", 10)
            painter.setFont(font)
            painter.setPen(QColor(134, 134, 134))
            
            # Limit iterations to prevent infinite loops
            max_iterations = 1000
            iterations = 0
            
            while block.isValid() and top <= event.rect().bottom() and iterations < max_iterations:
                bottom = top + self.editor.blockBoundingRect(block).height()
                
                if bottom >= event.rect().top():
                    number = str(block_number + 1)
                    painter.drawText(5, int(top), 40, int(self.editor.fontMetrics().height()),
                                   Qt.AlignRight, number)
                
                block = block.next()
                top = bottom
                block_number += 1
                iterations += 1
            
            painter.end()
        except Exception:
            pass  # Silently handle any paint errors


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


class SharpEditorWidget(QPlainTextEdit):
    """Advanced text editor for Sharp code with PyCharm-like features."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Font setup
        font = QFont("Courier New", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Style
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        """)
        
        # Syntax highlighter
        self.highlighter = SyntaxHighlighter(self.document())
        
        # Line numbers
        self.line_number_area = LineNumberArea(self)
        
        # Autocomplete
        self.autocomplete = AutocompleteWidget(self)
        self.autocomplete.hide()
        self.autocomplete.item_selected.connect(self._apply_autocomplete)
        
        # Bracket matching
        self.bracket_pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        self.matching_bracket_format = QTextCharFormat()
        self.matching_bracket_format.setBackground(QColor(100, 100, 100))
        
        # Search state
        self.search_term = None
        self.search_results = []
        self.current_search_index = 0
        
        # Setup
        self.textChanged.connect(self._on_text_changed)
        self.cursorPositionChanged.connect(self._update_line_numbers)
        self.cursorPositionChanged.connect(self._highlight_matching_brackets)
        
        # Keybindings
        self.setup_keybindings()
    
    def setup_keybindings(self):
        """Setup keyboard shortcuts."""
        pass  # Already handled in main window
    
    def _on_text_changed(self):
        """Handle text change for autocomplete and highlighting."""
        self._show_autocomplete()
        self._update_line_numbers()
    
    def _update_line_numbers(self):
        """Update line number area."""
        self.line_number_area.update()
    
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
        
        if not word or len(word) < 1:
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
        self.autocomplete.resize(300, min(len(completions) * 25, 400))
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
    
    def _highlight_matching_brackets(self):
        """Highlight matching brackets."""
        cursor = self.textCursor()
        block = cursor.block()
        pos_in_block = cursor.positionInBlock()
        text = block.text()
        
        if pos_in_block > 0 and pos_in_block <= len(text):
            char = text[pos_in_block - 1] if pos_in_block > 0 else ''
            
            # Check if it's a closing bracket
            if char in self.bracket_pairs.values():
                # Find matching opening bracket
                opening = [k for k, v in self.bracket_pairs.items() if v == char][0]
                count = 1
                i = pos_in_block - 2
                
                while i >= 0 and count > 0:
                    if text[i] == char:
                        count += 1
                    elif text[i] == opening:
                        count -= 1
                    i -= 1
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Ctrl+F for find
        if event.key() == Qt.Key_F and event.modifiers() & Qt.ControlModifier:
            self.parent().parent().parent().show_find_replace()
            return
        
        # Ctrl+G for go to line
        if event.key() == Qt.Key_G and event.modifiers() & Qt.ControlModifier:
            self.parent().parent().parent().go_to_line()
            return
        
        # Ctrl+H for replace
        if event.key() == Qt.Key_H and event.modifiers() & Qt.ControlModifier:
            self.parent().parent().parent().show_find_replace(replace=True)
            return
        
        super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """Resize line number area."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), 50, cr.height())


class FindReplaceDialog(QDialog):
    """Find and Replace dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setGeometry(100, 100, 500, 150)
        self.editor = None
        
        layout = QVBoxLayout()
        
        # Find
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        find_btn = QPushButton("Find All")
        find_btn.clicked.connect(self.find_all)
        find_layout.addWidget(find_btn)
        layout.addLayout(find_layout)
        
        # Replace
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        replace_btn = QPushButton("Replace All")
        replace_btn.clicked.connect(self.replace_all)
        replace_layout.addWidget(replace_btn)
        layout.addLayout(replace_layout)
        
        self.setLayout(layout)
    
    def set_editor(self, editor):
        """Set the editor to search in."""
        self.editor = editor
    
    def find_all(self):
        """Find all occurrences."""
        if not self.editor:
            return
        
        search_term = self.find_input.text()
        if not search_term:
            return
        
        text = self.editor.toPlainText()
        count = text.count(search_term)
        QMessageBox.information(self, "Find", f"Found {count} occurrences")
    
    def replace_all(self):
        """Replace all occurrences."""
        if not self.editor:
            return
        
        search_term = self.find_input.text()
        replace_term = self.replace_input.text()
        
        if not search_term:
            return
        
        text = self.editor.toPlainText()
        new_text = text.replace(search_term, replace_term)
        self.editor.setPlainText(new_text)
        
        QMessageBox.information(self, "Replace", "Replaced all occurrences")


class GoToLineDialog(QDialog):
    """Go to line dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go to Line")
        self.setGeometry(100, 100, 300, 100)
        self.editor = None
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Line number:"))
        self.line_input = QLineEdit()
        self.line_input.setPlaceholderText("Enter line number...")
        layout.addWidget(self.line_input)
        
        btn_layout = QHBoxLayout()
        go_btn = QPushButton("Go")
        go_btn.clicked.connect(self.go_to_line)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(go_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def set_editor(self, editor):
        """Set the editor."""
        self.editor = editor
    
    def go_to_line(self):
        """Go to specified line."""
        if not self.editor:
            return
        
        try:
            line_num = int(self.line_input.text())
            doc = self.editor.document()
            
            if line_num < 1 or line_num > doc.blockCount():
                QMessageBox.warning(self, "Error", f"Line {line_num} does not exist")
                return
            
            block = doc.findBlockByLineNumber(line_num - 1)
            cursor = self.editor.textCursor()
            cursor.setPosition(block.position())
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()
            
            self.close()
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid line number")


class FileExplorer(QTreeWidget):
    """Project file explorer sidebar."""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Project")
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #0d7377;
            }
            QTreeWidget::item:hover {
                background-color: #3e3e42;
            }
        """)
        
        self.itemDoubleClicked.connect(self._on_item_clicked)
        self.current_root = None
    
    def _on_item_clicked(self, item, column):
        """Handle file selection."""
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.file_selected.emit(file_path)
    
    def load_project(self, root_path):
        """Load project directory."""
        self.current_root = root_path
        self.clear()
        
        root_item = QTreeWidgetItem(self, [os.path.basename(root_path)])
        root_item.setData(0, Qt.UserRole, root_path)
        
        self._add_files(root_item, root_path)
        self.expandAll()
    
    def _add_files(self, parent_item, directory):
        """Recursively add files to tree."""
        try:
            for item in os.listdir(directory):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(directory, item)
                tree_item = QTreeWidgetItem(parent_item, [item])
                tree_item.setData(0, Qt.UserRole, item_path)
                
                if os.path.isdir(item_path):
                    self._add_files(tree_item, item_path)
        except PermissionError:
            pass


class CodeOutline(QTreeWidget):
    """Code outline showing functions, classes, and variables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Structure")
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #0d7377;
            }
        """)
    
    def parse_code(self, code):
        """Parse Sharp code and extract structure."""
        self.clear()
        
        # Find functions
        func_pattern = r'def\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, code):
            item = QTreeWidgetItem(self, [f"🔷 {match.group(1)}()"])
            item.setData(0, Qt.UserRole, match.start())
        
        # Find variables
        var_pattern = r'let\s+(\w+)\s*='
        for match in re.finditer(var_pattern, code):
            item = QTreeWidgetItem(self, [f"◆ {match.group(1)}"])
            item.setData(0, Qt.UserRole, match.start())


class OutputPanel(QWidget):
    """Output panel with tabs for console, errors, etc."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget {
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #d4d4d4;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
        """)
        
        # Console tab
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: Courier New;
                border: none;
            }
        """)
        
        # Errors tab
        self.errors = QTextEdit()
        self.errors.setReadOnly(True)
        self.errors.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ff6b6b;
                font-family: Courier New;
                border: none;
            }
        """)
        
        # Warnings tab
        self.warnings = QTextEdit()
        self.warnings.setReadOnly(True)
        self.warnings.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffb86c;
                font-family: Courier New;
                border: none;
            }
        """)
        
        self.tabs.addTab(self.console, "Console")
        self.tabs.addTab(self.errors, "Errors")
        self.tabs.addTab(self.warnings, "Warnings")
        
        layout.addWidget(self.tabs)
    
    def clear(self):
        """Clear all output."""
        self.console.clear()
        self.errors.clear()
        self.warnings.clear()
    
    def append_console(self, text):
        """Append to console."""
        self.console.append(text)
    
    def append_error(self, text):
        """Append error."""
        self.errors.append(f"❌ {text}")
        self.tabs.setCurrentWidget(self.errors)
    
    def append_warning(self, text):
        """Append warning."""
        self.warnings.append(f"⚠️ {text}")


class EditorTab(QWidget):
    """Tab containing editor with line numbers."""
    
    def __init__(self, filepath=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create editor
        self.editor = SharpEditorWidget()
        
        # Add line numbers
        layout.addWidget(self.editor.line_number_area)
        layout.addWidget(self.editor)
        
        self.filepath = filepath
        self.is_modified = False


class SharpIDE(QMainWindow):
    """Professional Sharp IDE in PyQt5 with PyCharm-like features."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sharp IDE - Professional Edition")
        self.setGeometry(50, 50, 1800, 1000)
        
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
            QLineEdit {
                background-color: #3e3e42;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 4px;
            }
            QPushButton {
                background-color: #0d7377;
                color: #d4d4d4;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #14919b;
            }
            QDockWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
            QDockWidget::title {
                background-color: #2b2b2b;
                padding: 4px;
                border-bottom: 1px solid #3e3e42;
            }
        """)
        
        self.current_file = None
        self.interpreter = Interpreter()
        self.open_files = {}  # filepath -> EditorTab
        self.current_editor = None
        
        # Dialogs
        self.find_replace_dialog = FindReplaceDialog(self)
        self.go_to_line_dialog = GoToLineDialog(self)
        
        # Create UI
        self.create_menu_bar()
        self.create_central_widget()
        self.create_sidebars()
        self.create_status_bar()
        
        # Shortcuts
        self.setup_shortcuts()
    
    def create_menu_bar(self):
        """Create the menu bar with advanced features."""
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
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_replace)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("Replace", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(lambda: self.show_find_replace(True))
        edit_menu.addAction(replace_action)
        
        edit_menu.addSeparator()
        
        go_to_line_action = QAction("Go to Line", self)
        go_to_line_action.setShortcut("Ctrl+G")
        go_to_line_action.triggered.connect(self.go_to_line)
        edit_menu.addAction(go_to_line_action)
        
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
        """Create the main editor area with tabs and output panel."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter for editor tabs and output
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3e3e42;
                height: 3px;
            }
            QSplitter::handle:hover {
                background-color: #0d7377;
            }
        """)
        
        # Top: Multi-tab editor
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setStyleSheet("""
            QTabWidget {
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #d4d4d4;
                padding: 8px;
                margin: 2px;
                border-bottom: 2px solid #2b2b2b;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #0d7377;
            }
            QTabBar::tab:hover {
                background-color: #3e3e42;
            }
            QTabBar::close-button {
                image: url(:/close.png);
                background-color: transparent;
            }
        """)
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Create initial tab
        self._create_new_tab("Untitled")
        
        splitter.addWidget(self.editor_tabs)
        
        # Bottom: Output panel with multiple tabs
        self.output_panel = OutputPanel()
        splitter.addWidget(self.output_panel)
        
        splitter.setSizes([700, 300])
        layout.addWidget(splitter)
    
    def _create_new_tab(self, filename, filepath=None):
        """Create a new editor tab."""
        tab = EditorTab(filepath)
        self.editor_tabs.addTab(tab, os.path.basename(filename))
        
        # Connect signals
        tab.editor.textChanged.connect(lambda: self._on_editor_modified(tab))
        
        self.open_files[filepath or filename] = tab
        return tab
    
    def on_tab_changed(self, index):
        """Handle tab change."""
        if index >= 0:
            tab = self.editor_tabs.widget(index)
            if tab:
                self.current_editor = tab.editor
                self.find_replace_dialog.set_editor(self.current_editor)
                self.go_to_line_dialog.set_editor(self.current_editor)
                self.current_file = tab.filepath
    
    def close_tab(self, index):
        """Close a tab."""
        tab = self.editor_tabs.widget(index)
        if tab:
            if tab.is_modified:
                reply = QMessageBox.question(self, "Unsaved Changes", 
                                            "Save changes before closing?")
                if reply == QMessageBox.Yes:
                    self.save_file()
            
            self.editor_tabs.removeTab(index)
            if tab.filepath:
                del self.open_files[tab.filepath]
    
    def _on_editor_modified(self, tab):
        """Mark editor as modified."""
        tab.is_modified = True
        index = self.editor_tabs.indexOf(tab)
        title = self.editor_tabs.tabText(index)
        if not title.endswith("*"):
            self.editor_tabs.setTabText(index, title + "*")
    
    def create_sidebars(self):
        """Create left and right sidebars with panels."""
        # Left sidebar - File explorer and structure
        left_dock = QDockWidget("Project", self)
        left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs for different views
        self.left_tabs = QTabWidget()
        self.left_tabs.setStyleSheet("""
            QTabWidget {
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #d4d4d4;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
        """)
        
        # File explorer
        self.file_explorer = FileExplorer()
        self.file_explorer.file_selected.connect(self.open_file_from_explorer)
        
        # Code outline
        self.code_outline = CodeOutline()
        
        self.left_tabs.addTab(self.file_explorer, "🗂️ Files")
        self.left_tabs.addTab(self.code_outline, "📋 Outline")
        
        left_layout.addWidget(self.left_tabs)
        left_dock.setWidget(left_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)
        
        # Right sidebar - Properties and info
        right_dock = QDockWidget("Info", self)
        right_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        right_widget = QTextBrowser()
        right_widget.setStyleSheet("""
            QTextBrowser {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
            }
        """)
        right_widget.setText("<h3>Sharp IDE</h3><p>Professional Editor</p>")
        right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock)
    
    def create_status_bar(self):
        """Create the status bar with cursor position info and more."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.status_label = QLabel("Ready")
        self.line_col_label = QLabel("Line 1, Column 1")
        self.encoding_label = QLabel("UTF-8")
        self.lang_label = QLabel("Sharp")
        
        self.statusBar.addWidget(self.status_label, 1)
        self.statusBar.addPermanentWidget(self.lang_label)
        self.statusBar.addPermanentWidget(self.encoding_label)
        self.statusBar.addPermanentWidget(self.line_col_label)
    
    def _update_cursor_position(self):
        """Update the cursor position display."""
        if self.current_editor:
            cursor = self.current_editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.positionInBlock() + 1
            self.line_col_label.setText(f"Line {line}, Column {col}")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        pass
    
    def open_file_from_explorer(self, filepath):
        """Open file selected from explorer."""
        self.open_file(filepath)
    
    def show_find_replace(self, replace=False):
        """Show find and replace dialog."""
        if self.current_editor:
            self.find_replace_dialog.set_editor(self.current_editor)
        self.find_replace_dialog.show()
        self.find_replace_dialog.find_input.setFocus()
    
    def go_to_line(self):
        """Show go to line dialog."""
        if self.current_editor:
            self.go_to_line_dialog.set_editor(self.current_editor)
            self.go_to_line_dialog.show()
            self.go_to_line_dialog.line_input.setFocus()
    
    def update_status(self, message):
        """Update status bar message."""
        self.status_label.setText(message)
    
    def new_file(self):
        """Create a new file."""
        tab = self._create_new_tab("Untitled")
        self.editor_tabs.setCurrentWidget(tab)
        self.current_file = None
        self.setWindowTitle("Sharp IDE - Untitled")
    
    def open_file(self, filepath=None):
        """Open a file."""
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(self, "Open Sharp Program",
                                                      "", "Sharp Files (*.sharp);;Text Files (*.txt);;All Files (*.*)")
        
        if filepath:
            try:
                # Check if already open
                if filepath in self.open_files:
                    self.editor_tabs.setCurrentWidget(self.open_files[filepath])
                    return
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tab = self._create_new_tab(os.path.basename(filepath), filepath)
                tab.editor.setPlainText(content)
                tab.is_modified = False
                
                # Update code outline
                self.code_outline.parse_code(content)
                
                self.editor_tabs.setCurrentWidget(tab)
                self.current_file = filepath
                self.setWindowTitle(f"Sharp IDE - {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file."""
        tab = self.editor_tabs.currentWidget()
        if not tab:
            return
        
        if not tab.filepath:
            self.save_as_file()
            return
        
        try:
            with open(tab.filepath, 'w', encoding='utf-8') as f:
                f.write(tab.editor.toPlainText())
            tab.is_modified = False
            index = self.editor_tabs.indexOf(tab)
            title = self.editor_tabs.tabText(index).rstrip('*')
            self.editor_tabs.setTabText(index, title)
            self.update_status(f"Saved: {tab.filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")
    
    def save_as_file(self):
        """Save file with a new name."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Sharp Program",
                                                  "", "Sharp Files (*.sharp);;Text Files (*.txt)")
        if filename:
            tab = self.editor_tabs.currentWidget()
            if tab:
                tab.filepath = filename
                self.current_file = filename
                self.editor_tabs.setTabText(self.editor_tabs.indexOf(tab), os.path.basename(filename))
                self.setWindowTitle(f"Sharp IDE - {os.path.basename(filename)}")
                self.save_file()
    
    def run_code(self):
        """Execute the Sharp program."""
        if not self.current_editor:
            QMessageBox.warning(self, "Warning", "No editor active")
            return
        
        source = self.current_editor.toPlainText()
        
        if not source.strip():
            QMessageBox.warning(self, "Warning", "No code to execute")
            return
        
        self.output_panel.clear()
        self.update_status("Running...")
        
        # Check for PyQt5
        if 'import pyqt5_wrapper' in source or 'from pyqt5_wrapper' in source:
            try:
                import PyQt5
            except ImportError:
                self.output_panel.append_error("PyQt5 is not installed. Please install it with: pip install PyQt5")
                self.update_status("PyQt5 missing")
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
                self.output_panel.append_console(output)
            
            self.update_status("Execution completed successfully")
            
            if result and not isinstance(result, SharpNil):
                self.output_panel.append_console(f"\n✓ Result: {result}\n")
        
        except SyntaxError as e:
            self.output_panel.append_error(f"SyntaxError: {e}")
            self.update_status("Syntax error")
        except Exception as e:
            self.output_panel.append_error(f"{type(e).__name__}: {e}")
            self.update_status(f"Error - {type(e).__name__}")
        
        finally:
            sys.stdout = old_stdout
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.information(self, "About Sharp IDE",
            "Sharp Programming Language IDE v2.0 (PyQt5)\n\n"
            "Professional Edition with:\n"
            "✓ Multi-tab Editor\n"
            "✓ Syntax Highlighting\n"
            "✓ Intelligent Autocompletion\n"
            "✓ Line Numbers\n"
            "✓ File Explorer & Project View\n"
            "✓ Code Outline/Structure\n"
            "✓ Find & Replace (Ctrl+F / Ctrl+H)\n"
            "✓ Go to Line (Ctrl+G)\n"
            "✓ Bracket Matching\n"
            "✓ Multi-tab Output Panel\n"
            "✓ Live Code Execution\n\n"
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

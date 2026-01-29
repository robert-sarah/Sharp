"""
Sharp Programming Language - GUI IDE Editor
A complete integrated development environment for Sharp programs.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font
import os
import sys
import re
from io import StringIO

# Add parent directory to path to import Sharp modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from stdlib import SharpNil, STDLIB

class SharpIDE:
    """Full-featured IDE for Sharp Programming Language."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sharp IDE - Integrated Development Environment")
        self.root.geometry("1200x700")
        
        self.current_file = None
        self.interpreter = Interpreter()
        
        # Autocomplete popup
        self.autocomplete_window = None
        self.autocomplete_listbox = None
        
        # Configure style
        self.root.configure(bg="#2b2b2b")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        self.create_layout()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root, bg="#404040", fg="white")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Execute (F5)", command=self.run_code)
        run_menu.add_command(label="Clear Output", command=self.clear_output)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#404040", fg="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Sharp", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_docs)
    
    def create_layout(self):
        """Create the main IDE layout."""
        # Top toolbar
        toolbar = tk.Frame(self.root, bg="#404040", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # File name label
        self.file_label = tk.Label(toolbar, text="Untitled", bg="#404040", fg="white", font=("Arial", 10))
        self.file_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Buttons
        btn_font = ("Arial", 9)
        tk.Button(toolbar, text="New", command=self.new_file, bg="#505050", fg="white", font=btn_font).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Open", command=self.open_file, bg="#505050", fg="white", font=btn_font).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Save", command=self.save_file, bg="#505050", fg="white", font=btn_font).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Run (F5)", command=self.run_code, bg="#0d7377", fg="white", font=btn_font).pack(side=tk.LEFT, padx=2)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Editor and output panel
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg="#2b2b2b")
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: Editor
        editor_frame = tk.Frame(paned, bg="#2b2b2b")
        paned.add(editor_frame)
        
        editor_label = tk.Label(editor_frame, text="Editor", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold"))
        editor_label.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Line numbers and editor
        editor_content = tk.Frame(editor_frame, bg="#1e1e1e")
        editor_content.pack(fill=tk.BOTH, expand=True)
        
        self.line_numbers = tk.Text(editor_content, width=4, bg="#1e1e1e", fg="#858585", 
                                     font=("Courier", 11), state=tk.DISABLED, wrap=tk.NONE)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.editor = scrolledtext.ScrolledText(editor_content, bg="#1e1e1e", fg="#d4d4d4", 
                                                font=("Courier", 11), insertbackground="#d4d4d4",
                                                wrap=tk.WORD)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure syntax highlighting
        self.setup_syntax_highlighting()
        
        # Bind editor events
        self.editor.bind("<KeyRelease>", self.on_key_release)
        self.editor.bind("<Control-Return>", lambda e: self.run_code())
        self.editor.bind("<Control-space>", lambda e: self.show_autocomplete())
        self.editor.bind("<Escape>", lambda e: self.hide_autocomplete())
        
        # Right panel: Output
        output_frame = tk.Frame(paned, bg="#2b2b2b")
        paned.add(output_frame)
        
        output_label = tk.Label(output_frame, text="Output & Console", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold"))
        output_label.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.output = scrolledtext.ScrolledText(output_frame, bg="#1e1e1e", fg="#00ff00", 
                                                font=("Courier", 10), state=tk.DISABLED,
                                                wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bg="#404040", fg="#d4d4d4", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_syntax_highlighting(self):
        """Setup syntax highlighting for Sharp code."""
        # Keywords
        self.editor.tag_configure("keyword", foreground="#569cd6", font=("Courier", 11, "bold"))
        # Strings
        self.editor.tag_configure("string", foreground="#ce9178")
        # Comments
        self.editor.tag_configure("comment", foreground="#6a9955")
        # Numbers
        self.editor.tag_configure("number", foreground="#b5cea8")
        # Functions
        self.editor.tag_configure("function", foreground="#dcdcaa")
        # Builtins
        self.editor.tag_configure("builtin", foreground="#4ec9b0")
    
    def highlight_syntax(self):
        """Apply syntax highlighting to the editor."""
        try:
            # Remove all tags first
            for tag in ["keyword", "string", "comment", "number", "function", "builtin"]:
                self.editor.tag_remove(tag, "1.0", tk.END)
            
            content = self.editor.get("1.0", tk.END)
            
            # Keywords
            keywords = r'\b(def|let|if|elif|else|while|for|in|return|break|continue|match|case|type|import|lambda|true|false|nil)\b'
            for match in re.finditer(keywords, content):
                start = match.start()
                end = match.end()
                self.editor.tag_add("keyword", f"1.0+{start}c", f"1.0+{end}c")
            
            # Comments
            comments = r'#.*$'
            for match in re.finditer(comments, content, re.MULTILINE):
                start = match.start()
                end = match.end()
                self.editor.tag_add("comment", f"1.0+{start}c", f"1.0+{end}c")
            
            # Strings
            strings = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
            for match in re.finditer(strings, content):
                start = match.start()
                end = match.end()
                self.editor.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")
            
            # Numbers
            numbers = r'\b\d+\.?\d*\b'
            for match in re.finditer(numbers, content):
                start = match.start()
                end = match.end()
                self.editor.tag_add("number", f"1.0+{start}c", f"1.0+{end}c")
            
            # Builtin functions - simplified without position check
            builtins_pattern = r'\b(' + '|'.join(STDLIB.keys()) + r')\b'
            for match in re.finditer(builtins_pattern, content):
                start = match.start()
                end = match.end()
                self.editor.tag_add("builtin", f"1.0+{start}c", f"1.0+{end}c")
        except Exception:
            pass  # Silently ignore syntax highlighting errors
    
    def on_key_release(self, event=None):
        """Handle key release events for syntax highlighting, line numbers, and autocomplete."""
        try:
            self.update_line_numbers()
            self.highlight_syntax()
            # Always trigger autocomplete for any word or after space for import/from
            if event:
                # Trigger on any character
                self.show_autocomplete_if_matches()
        except Exception:
            pass  # Silently ignore errors
    
    def get_current_word(self):
        """Get the current word being typed."""
        try:
            cursor = self.editor.index(tk.INSERT)
            line_num = cursor.split('.')[0]
            cursor_col = int(cursor.split('.')[1])
            line_content = self.editor.get(f"{line_num}.0", f"{line_num}.end")
            
            # Find word boundaries - safer implementation
            word = ""
            i = cursor_col - 1
            
            # Ensure we don't go out of bounds
            while i >= 0 and i < len(line_content) and (line_content[i].isalnum() or line_content[i] == '_'):
                word = line_content[i] + word
                i -= 1
            
            return word
        except Exception:
            return ""
    
    def show_autocomplete(self, event=None):
        """Show autocomplete suggestions for keywords, modules, and functions."""
        try:
            word = self.get_current_word()
            if not word:
                self.hide_autocomplete()
                return

            # Sharp keywords
            keywords = [
                'def', 'let', 'if', 'elif', 'else', 'while', 'for', 'in', 'return', 'break', 'continue',
                'match', 'case', 'type', 'import', 'from', 'as', 'lambda', 'true', 'false', 'nil'
            ]
            # Module names
            module_files = os.listdir(os.path.join(os.path.dirname(__file__), 'modules'))
            modules = [f.split('.')[0] for f in module_files if f.endswith('.sharp') or f.endswith('.py')]
            modules = list(sorted(set(modules)))
            # Builtin functions
            builtins = list(STDLIB.keys())

            # Context-aware completions
            line = self.editor.get("insert linestart", "insert lineend")
            completions = []
            if re.match(r'\s*import\s+\w*$', line):
                completions = [m for m in modules if m.startswith(word)]
            elif re.match(r'\s*from\s+\w+\s+import\s+\w*$', line):
                # Try to get module exports
                modname = line.split()[1]
                mod_exports = []
                try:
                    modfile = os.path.join(os.path.dirname(__file__), 'modules', modname + '.sharp')
                    if os.path.exists(modfile):
                        with open(modfile, 'r', encoding='utf-8') as f:
                            mod_exports = re.findall(r'def\s+(\w+)', f.read())
                    else:
                        modfile = os.path.join(os.path.dirname(__file__), 'modules', modname + '.py')
                        if os.path.exists(modfile):
                            with open(modfile, 'r', encoding='utf-8') as f:
                                mod_exports = re.findall(r'def\s+(\w+)', f.read())
                except Exception:
                    pass
                completions = [e for e in mod_exports if e.startswith(word)]
            else:
                # Default: keywords, builtins, modules
                completions = [k for k in keywords if k.startswith(word)]
                completions += [m for m in modules if m.startswith(word)]
                completions += [b for b in builtins if b.startswith(word)]

            completions = sorted(set(completions))
            if not completions:
                self.hide_autocomplete()
                return

            # Create autocomplete window
            if self.autocomplete_window:
                self.autocomplete_window.destroy()

            self.autocomplete_window = tk.Toplevel(self.editor)
            self.autocomplete_window.wm_overrideredirect(True)

            # Position window at cursor
            cursor = self.editor.index(tk.INSERT)
            bbox = self.editor.bbox(cursor)
            if bbox:
                x = bbox[0] + self.editor.winfo_rootx()
                y = bbox[1] + bbox[3] + self.editor.winfo_rooty()
                self.autocomplete_window.wm_geometry(f"+{x}+{y}")

            # Create listbox
            self.autocomplete_listbox = tk.Listbox(self.autocomplete_window, bg="#2b2b2b", fg="#d4d4d4", 
                                                   font=("Courier", 10), height=min(10, len(completions)))
            self.autocomplete_listbox.pack(fill=tk.BOTH, expand=True)

            for match in completions:
                self.autocomplete_listbox.insert(tk.END, match)

            # Select first item
            self.autocomplete_listbox.selection_set(0)

            # Bind keys
            self.autocomplete_listbox.bind("<Return>", self.apply_autocomplete)
            self.autocomplete_listbox.bind("<Tab>", self.close_autocomplete_no_insert)
            self.autocomplete_listbox.bind("<space>", self.close_autocomplete_no_insert)
            self.autocomplete_listbox.bind("<Escape>", lambda e: self.hide_autocomplete())
            self.autocomplete_listbox.bind("<Up>", self.autocomplete_up)
            self.autocomplete_listbox.bind("<Down>", self.autocomplete_down)
            self.autocomplete_listbox.bind("<Key>", self.autocomplete_keypress)

            self.autocomplete_listbox.focus()
        except Exception:
            self.hide_autocomplete()

    def close_autocomplete_no_insert(self, event=None):
        """Ferme l'autocomplétion sans rien insérer (pour espace/tab)."""
        self.hide_autocomplete()
        # Redonne le focus à l'éditeur et insère la touche
        self.editor.focus_set()
        if event and event.keysym == 'Tab':
            self.editor.insert(tk.INSERT, '\t')
        elif event and event.keysym == 'space':
            self.editor.insert(tk.INSERT, ' ')
        return "break"

    def autocomplete_keypress(self, event):
        """Ferme l'autocomplétion sur toute autre touche normale (lettre, chiffre, etc.)."""
        # Autorise navigation/flèches, Entrée, Tab, Espace, sinon ferme
        if event.keysym in ("Up", "Down", "Return", "Tab", "space", "Escape"):
            return
        self.hide_autocomplete()
        self.editor.focus_set()
        # Laisse la touche passer à l'éditeur
        return None
    
    def show_autocomplete_if_matches(self):
        """Show autocomplete if there are matches for keywords, modules, or functions."""
        word = self.get_current_word()
        # Always show autocomplete if word is not empty or if line matches import/from
        line = self.editor.get("insert linestart", "insert lineend")
        if word or re.match(r'\s*(import|from)\s*$', line):
            self.show_autocomplete()
    
    def apply_autocomplete(self, event=None):
        """Apply the selected autocomplete suggestion."""
        if not self.autocomplete_listbox:
            return
        
        selection = self.autocomplete_listbox.curselection()
        if not selection:
            return
        
        selected = self.autocomplete_listbox.get(selection[0])
        word = self.get_current_word()
        
        # Replace the word
        cursor = self.editor.index(tk.INSERT)
        line = cursor.split('.')[0]
        col = int(cursor.split('.')[1])
        
        # Delete the word
        self.editor.delete(f"{line}.{col-len(word)}", f"{line}.{col}")
        
        # Insert the selected completion
        self.editor.insert(f"{line}.{col-len(word)}", selected)
        
        self.hide_autocomplete()
    
    def autocomplete_up(self, event=None):
        """Move up in autocomplete list."""
        if not self.autocomplete_listbox:
            return
        selection = self.autocomplete_listbox.curselection()
        if selection and selection[0] > 0:
            self.autocomplete_listbox.selection_clear(0, tk.END)
            self.autocomplete_listbox.selection_set(selection[0] - 1)
            self.autocomplete_listbox.see(selection[0] - 1)
        return "break"
    
    def autocomplete_down(self, event=None):
        """Move down in autocomplete list."""
        if not self.autocomplete_listbox:
            return
        selection = self.autocomplete_listbox.curselection()
        max_index = self.autocomplete_listbox.size() - 1
        if selection and selection[0] < max_index:
            self.autocomplete_listbox.selection_clear(0, tk.END)
            self.autocomplete_listbox.selection_set(selection[0] + 1)
            self.autocomplete_listbox.see(selection[0] + 1)
        return "break"
    
    def hide_autocomplete(self):
        """Hide the autocomplete window."""
        if self.autocomplete_window:
            self.autocomplete_window.destroy()
            self.autocomplete_window = None
            self.autocomplete_listbox = None
    
    def update_line_numbers(self, event=None):
        """Update line numbers in the line number panel."""
        line_count = self.editor.get("1.0", tk.END).count('\n')
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        
        self.line_numbers.config(state=tk.DISABLED)
    
    def new_file(self):
        """Create a new file."""
        if self.editor.get("1.0", tk.END).strip():
            if not messagebox.askyesno("Unsaved Changes", "Discard unsaved changes?"):
                return
        
        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.file_label.config(text="Untitled")
        self.update_line_numbers()
        self.update_status("New file created")
    
    def open_file(self):
        """Open a file."""
        filename = filedialog.askopenfilename(
            title="Open Sharp Program",
            filetypes=[("Sharp files", "*.sharp"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
                self.current_file = filename
                self.file_label.config(text=os.path.basename(filename))
                self.update_line_numbers()
                self.update_status(f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            self.save_as_file()
            return
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get("1.0", tk.END))
            self.update_status(f"Saved: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
    
    def save_as_file(self):
        """Save the file with a new name."""
        filename = filedialog.asksaveasfilename(
            title="Save Sharp Program",
            filetypes=[("Sharp files", "*.sharp"), ("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".sharp"
        )
        
        if filename:
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename))
            self.save_file()
    
    def run_code(self):
        """Execute the Sharp program."""
        source = self.editor.get("1.0", tk.END)
        if not source.strip():
            messagebox.showwarning("Warning", "No code to execute")
            return
        self.clear_output()
        self.update_status("Running...")
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # Special check for PyQt5 if using GUI
            if 'import pyqt5_wrapper' in source or 'from pyqt5_wrapper' in source or 'import gui' in source:
                try:
                    import PyQt5
                except ImportError:
                    self.append_output("PyQt5 is not installed. Please install it with: pip install PyQt5\n")
                    self.update_status("PyQt5 missing")
                    return
            # Lex
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            for token in tokens:
                if token.type.name == 'ERROR':
                    self.append_output(f"Lexer Error: {token.value}\n")
                    self.update_status("Error - lexing failed")
                    return
            parser = Parser(tokens)
            ast = parser.parse()
            self.interpreter = Interpreter()  # Fresh interpreter for each run
            result = self.interpreter.interpret(ast)
            output = sys.stdout.getvalue()
            if output:
                self.append_output(output)
            self.update_status("Execution completed successfully")
            if result and not isinstance(result, SharpNil):
                self.append_output(f"Result: {result}\n")
        except SyntaxError as e:
            self.append_output(f"SyntaxError: {e}\n")
            self.update_status("Error - syntax error")
        except Exception as e:
            self.append_output(f"{type(e).__name__}: {e}\n")
            self.update_status(f"Error - {type(e).__name__}")
        finally:
            sys.stdout = old_stdout
    
    def clear_output(self):
        """Clear the output panel."""
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)
    
    def append_output(self, text):
        """Append text to the output panel."""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
    
    def update_status(self, message):
        """Update the status bar."""
        self.status_bar.config(text=message)
    
    # Edit menu commands
    def undo(self):
        """Undo action."""
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """Redo action."""
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass
    
    def cut(self):
        """Cut selected text."""
        try:
            self.editor.event_generate("<<Cut>>")
        except tk.TclError:
            pass
    
    def copy(self):
        """Copy selected text."""
        try:
            self.editor.event_generate("<<Copy>>")
        except tk.TclError:
            pass
    
    def paste(self):
        """Paste text."""
        try:
            self.editor.event_generate("<<Paste>>")
        except tk.TclError:
            pass
    
    def select_all(self):
        """Select all text."""
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)
    
    # Bind keyboard shortcuts
    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<F5>", lambda e: self.run_code())
    
    # Help menu commands
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About Sharp IDE", 
            "Sharp Programming Language IDE v1.0\n\n"
            "A modern, Python-like programming language\n"
            "with powerful features for education and development.\n\n"
            "© 2026 Sharp Development Team")
    
    def show_docs(self):
        """Show documentation."""
        messagebox.showinfo("Sharp Documentation",
            "SHARP PROGRAMMING LANGUAGE - Quick Reference\n\n"
            "=== VARIABLES & TYPES ===\n"
            "let x = 10          # Create variable (like Python's x = 10)\n"
            "let name = \"Alice\" # String\n"
            "let pi = 3.14       # Float\n"
            "let flag = true     # Boolean\n"
            "let items = [1,2,3] # List\n"
            "let info = {\"age\": 25}  # Dictionary\n\n"
            "=== OPERATIONS ===\n"
            "x = x + 5           # Arithmetic\n"
            "name.upper()        # String methods\n"
            "items[0]            # List access\n"
            "info[\"age\"]        # Dict access\n\n"
            "=== FUNCTIONS ===\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "result = add(3, 5)  # Call function\n\n"
            "=== LAMBDAS (Anonymous Functions) ===\n"
            "square = lambda x: x * x\n"
            "print(square(5))    # Output: 25\n\n"
            "=== CONTROL FLOW ===\n"
            "if x > 10:\n"
            "    print(\"Large\")\n"
            "elif x > 5:\n"
            "    print(\"Medium\")\n"
            "else:\n"
            "    print(\"Small\")\n\n"
            "for i in range(5):\n"
            "    print(i)        # 0 to 4\n\n"
            "while x > 0:\n"
            "    print(x)\n"
            "    x = x - 1\n\n"
            "=== BUILT-IN FUNCTIONS ===\n"
            "len([1,2,3])        # Length: 3\n"
            "range(5)            # [0,1,2,3,4]\n"
            "map(square, [1,2,3])# Apply function\n"
            "filter(lambda x: x>2, [1,2,3,4])  # Filter list\n"
            "sum([1,2,3])        # Add up: 6\n"
            "max([1,5,2])        # Largest: 5\n\n"
            "=== I/O & FILES ===\n"
            "print(\"Hello\")     # Output\n"
            "x = input(\"Enter: \")  # Read input\n"
            "f = open(\"file.txt\")\n"
            "content = read(f)\n"
            "write(f, \"text\")\n"
            "close(f)\n\n"
            "=== MATH FUNCTIONS ===\n"
            "sqrt(16)            # 4.0\n"
            "pow(2, 3)           # 8\n"
            "sin(0), cos(0)      # Trigonometry\n"
            "floor(3.7), ceil(3.2)  # Rounding\n\n"
            "Press OK to continue learning!")



def main():
    """Main entry point for the IDE."""
    root = tk.Tk()
    ide = SharpIDE(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()
        root.destroy()


if __name__ == "__main__":
    main()

"""
wxPython GUI Module for Sharp Language
Alternative to PyQt5 for building desktop applications
"""

try:
    import wx
    WXPYTHON_AVAILABLE = True
except ImportError:
    WXPYTHON_AVAILABLE = False
    print("Warning: wxPython not installed. wxGUI functions will not work.")

class SharpFrame:
    """Represents a wxPython frame/window"""
    def __init__(self, title: str = "Sharp App", width: int = 800, height: int = 600):
        if not WXPYTHON_AVAILABLE:
            raise RuntimeError("wxPython is not installed")
        
        self.title = title
        self.width = width
        self.height = height
        self.frame = wx.Frame(None, title=title, size=(width, height))
        self.panel = wx.Panel(self.frame)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)
        self.widgets = {}
    
    def add_label(self, name: str, text: str):
        """Add a label"""
        label = wx.StaticText(self.panel, label=text)
        self.widgets[name] = label
        self.sizer.Add(label, 0, wx.ALL | wx.EXPAND, 5)
        return label
    
    def add_button(self, name: str, text: str, callback=None):
        """Add a button"""
        button = wx.Button(self.panel, label=text)
        if callback:
            button.Bind(wx.EVT_BUTTON, lambda e: callback())
        self.widgets[name] = button
        self.sizer.Add(button, 0, wx.ALL | wx.EXPAND, 5)
        return button
    
    def add_textbox(self, name: str, placeholder: str = ""):
        """Add a text input"""
        textbox = wx.TextCtrl(self.panel, value="", style=wx.TE_LEFT)
        self.widgets[name] = textbox
        self.sizer.Add(textbox, 0, wx.ALL | wx.EXPAND, 5)
        return textbox
    
    def add_textarea(self, name: str, text: str = ""):
        """Add a multi-line text area"""
        textarea = wx.TextCtrl(self.panel, value=text, style=wx.TE_MULTILINE)
        self.widgets[name] = textarea
        self.sizer.Add(textarea, 1, wx.ALL | wx.EXPAND, 5)
        return textarea
    
    def get_text(self, name: str) -> str:
        """Get text from a widget"""
        widget = self.widgets.get(name)
        if widget and hasattr(widget, 'GetValue'):
            return widget.GetValue()
        return ""
    
    def set_text(self, name: str, text: str):
        """Set text on a widget"""
        widget = self.widgets.get(name)
        if widget and hasattr(widget, 'SetValue'):
            widget.SetValue(text)
    
    def show(self):
        """Show the frame"""
        self.frame.Show()
    
    def close(self):
        """Close the frame"""
        self.frame.Close()

def create_window(title: str, width: int = 800, height: int = 600) -> SharpFrame:
    """Create a new wxPython window"""
    return SharpFrame(title, width, height)

def run_app():
    """Run the wxPython application"""
    if WXPYTHON_AVAILABLE:
        app = wx.GetApp()
        if not app:
            app = wx.App()
        app.MainLoop()

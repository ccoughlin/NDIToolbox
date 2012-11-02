"""ui.py - user interface for the ColormapCreator app

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'ccoughlin'

import ui_defaults
from controllers.colormapcreator_ctrl import ColormapCreatorController
import wx
import wx.gizmos
import wx.aui
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class ColormapCreatorUI(wx.Frame):
    """Basic wxPython user interface for a matplotlib colormap editor"""

    def __init__(self, parent, *args, **kwargs):
        wx.Frame.__init__(self, parent=parent, title="Create Colormap", *args, **kwargs)
        if parent is not None:
            self.SetIcon(parent.GetIcon())
        self.controller = ColormapCreatorController(self)
        self.init_ui()
        self.controller.set_colormap()

    def init_ui(self):
        """Creates the user interface"""
        self.MinSize = (800, 300)
        self.SetSize(wx.Size(900, 600))
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.init_menu()

        # Color Management panel
        self.c_panel = wx.Panel(self)
        self.c_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        cmap_lbl = wx.StaticText(self.c_panel, wx.ID_ANY, "Type Of Colormap:")
        self.c_panel_sizer.Add(cmap_lbl, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags, ui_defaults.widget_margin)
        self.cmap_choices = ["Linear Gradient", "Simple List"]
        self.cmap_cb = wx.Choice(self.c_panel, wx.ID_ANY, choices=self.cmap_choices)
        self.cmap_cb.SetToolTipString("Sets the colormap to use gradients or a simple list of colors")
        self.Bind(wx.EVT_CHOICE, self.controller.on_preview, self.cmap_cb)
        self.c_panel_sizer.Add(self.cmap_cb, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                               ui_defaults.widget_margin)
        self.colors_lb = wx.gizmos.EditableListBox(self.c_panel, wx.ID_ANY, "Colors:", wx.DefaultPosition,
                                                   wx.DefaultSize,
                                                   style=wx.gizmos.EL_ALLOW_NEW|wx.gizmos.EL_ALLOW_DELETE)
        self.colors_lb.SetToolTipString("Add, delete, and reorder colors in the colormap")
        self.c_panel_sizer.Add(self.colors_lb, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                               ui_defaults.widget_margin)
        self.addcolor_btn = self.colors_lb.GetNewButton()
        self.addcolor_btn.Bind(wx.EVT_BUTTON, self.controller.on_add_color)
        self.c_panel.SetSizerAndFit(self.c_panel_sizer)
        self._mgr.AddPane(self.c_panel, wx.aui.AuiPaneInfo().Name("colors").Caption("Colormap").Left().
        CloseButton(False).MinimizeButton(True).MaximizeButton(True).Floatable(True).Dockable(True).
        MinSize(wx.Size(200, 100)))

        # Preview Panel
        self.preview_panel = wx.Panel(self)
        self.preview_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.preview_btn = wx.Button(self.preview_panel, wx.ID_ANY, "Preview Colormap", wx.DefaultPosition,
                                     wx.DefaultSize)
        self.preview_btn.SetToolTipString("Redraws the plot to demonstrate the current colormap")
        self.Bind(wx.EVT_BUTTON, self.controller.on_preview, self.preview_btn)
        self.preview_panel_sizer.Add(self.preview_btn, ui_defaults.lbl_pct, ui_defaults.lblsizer_flags,
                                     ui_defaults.widget_margin)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.preview_panel, wx.ID_ANY, self.figure)
        self.axes = self.figure.add_subplot(111)
        self.preview_panel_sizer.Add(self.canvas, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                     ui_defaults.widget_margin)
        self.preview_panel.SetSizerAndFit(self.preview_panel_sizer)
        self._mgr.AddPane(self.preview_panel, wx.aui.AuiPaneInfo().Name("preview").Caption("Preview").Center().
        CloseButton(False).MinimizeButton(True).MaximizeButton(True).Floatable(True).Dockable(True).
        MinSize(wx.Size(600, 100)))
        self._mgr.Update()

    def init_menu(self):
        """Creates the main menu"""
        self.menubar = wx.MenuBar()
        self.file_mnu = wx.Menu()
        self.load_cmap_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Load Colormap...", help="Loads a colormap")
        self.Bind(wx.EVT_MENU, self.controller.on_load_cmap, id=self.load_cmap_mnui.GetId())
        self.file_mnu.AppendItem(self.load_cmap_mnui)
        self.save_cmap_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Save Colormap...",
                                          help="Saves current colormap")
        self.Bind(wx.EVT_MENU, self.controller.on_save_cmap, id=self.save_cmap_mnui.GetId())
        self.file_mnu.AppendItem(self.save_cmap_mnui)
        close_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Close Window", help="Closes the colormap editor")
        self.Bind(wx.EVT_MENU, self.controller.on_close, id=close_mnui.GetId())
        self.file_mnu.AppendItem(close_mnui)
        self.menubar.Append(self.file_mnu, "&File")
        self.SetMenuBar(self.menubar)

    def get_cmap_type(self):
        """Returns one of 'linear' or 'list' for linearly-interpolated colormap or simple list of colors,
        respectively."""
        idx = self.cmap_cb.GetCurrentSelection()
        if idx == 0: # Linear
            return "linear"
        return "list"

    def set_cmap_type(self, cmap_type):
        """Sets the current selection in the choice box according to the specified colormap type.
        Uses 'linear' or 'list'."""
        if cmap_type == 'linear':
            self.cmap_cb.SetSelection(0)
        elif cmap_type == 'list':
            self.cmap_cb.SetSelection(1)

    def add_color(self, rgb_list):
        """Adds the list of RGB components [R,G,B] to the list of colors.  Each component should be a floating-point
        number between 0 and 1."""
        colors_lc = self.colors_lb.GetListCtrl()
        color_idx = colors_lc.GetFocusedItem()
        if color_idx == -1:
            color_idx = colors_lc.GetItemCount()-1
        colors_lc.InsertStringItem(color_idx, ','.join([str(el) for el in rgb_list]))

def main():
    app = wx.PySimpleApp()
    ui = ColormapCreatorUI()
    ui.Show(True)
    app.MainLoop()

if __name__ == "__main__":
    main()
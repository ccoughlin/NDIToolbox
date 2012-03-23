"""podtk.py - UI for the Probability Of Detection (POD) Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import podtk_ctrl
from views import wxspreadsheet
from views import wxmodeltree
from views import ui_defaults
import matplotlib
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg, \
    FigureCanvasWxAgg as FigureCanvas
import matplotlib.figure
import wx
import wx.aui

class PODWindow(wx.Frame):
    """Primary interface for POD Toolkit"""

    def __init__(self, parent):
        _size = wx.Size(1024, 800)
        self.parent = parent
        wx.Frame.__init__(self, id=wx.ID_ANY, name='', parent=self.parent,
                          size=_size, title="POD Toolkit")
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.version = "03.02.11"
        self.controller = podtk_ctrl.PODWindowController(self)
        self.input_sheet_page = 0 # Input data on first notebook page
        self.output_sheet_page = 1 # Output data on second notebook page
        self.txtoutput_sheet_page = 2 # Text output on third notebook page
        self.MinSize = wx.Size(600, 800)
        self.init_menu()
        self.init_ui()
        self.SetIcon(parent.GetIcon())

    def init_menu(self):
        """Creates the POD Toolkit application menu"""
        self.menubar = wx.MenuBar()

        self.file_mnu = wx.Menu() # File menu
        quit_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Close Window\tCTRL+W",
                                help="Exits PODToolkit")
        self.file_mnu.AppendItem(quit_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_quit, quit_mnui)
        self.menubar.Append(self.file_mnu, "&File")

        self.models_mnu = wx.Menu() # Models menu
        addmodel_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY, text="Add A Model\tCTRL+A",
                                    help="Adds a POD model to the available models")
        self.Bind(wx.EVT_MENU, self.controller.on_add_model, addmodel_mnui)
        self.models_mnu.AppendItem(addmodel_mnui)
        savemodel_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY,
                                     text="Save Model Configuration",
                                     help="Saves the current model configuration to disk\tCTRL+W")
        self.Bind(wx.EVT_MENU, self.controller.on_save_model, savemodel_mnui)
        self.models_mnu.AppendItem(savemodel_mnui)
        deletemodel_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY, text="Remove Current Model",
                                       help="Removes the currently selected POD model from the " \
                                            "workspace")
        self.Bind(wx.EVT_MENU, self.controller.on_delete_model, deletemodel_mnui)
        self.models_mnu.AppendItem(deletemodel_mnui)
        self.menubar.Append(self.models_mnu, "&Models")

        self.ops_mnu = wx.Menu() # Operations menu
        run_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Run\tCTRL+R",
                               help="Runs the current model")
        self.ops_mnu.AppendItem(run_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_runmodel, run_mnui)

        self.menubar.Append(self.ops_mnu, "&Operation")

        self.help_mnu = wx.Menu() # Basic Help menu
        about_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="About POD Toolkit",
                                 help="About this program")
        self.help_mnu.AppendItem(about_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about, about_mnui)
        help_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="Usage Basics",
                                help="A rundown of how to use POD Toolkit to get you started")
        self.Bind(wx.EVT_MENU, self.controller.on_help, help_mnui)
        self.help_mnu.AppendItem(help_mnui)
        self.menubar.Append(self.help_mnu, "&Help")

        self.SetMenuBar(self.menubar)

    def init_ui(self):
        """Generates the user interface"""
        self.init_ctrls()
        self.init_spreadsheets()
        self.init_plots()

        # LH of UI - ModelTree pane (upper) and ModelProperty editor pane (lower).
        # Resizable and dockable on left and right of UI.
        self._mgr.AddPane(self.ctrl_panel, wx.aui.AuiPaneInfo().
        Name("ctrl_panel").Caption("Models").MinSize(wx.Size(260, 450)).
        Left().CloseButton(False).MinimizeButton(True).MaximizeButton(True).MinimizeButton(True).
        Floatable(True).Dockable(False).LeftDockable(True).RightDockable(True))

        self._mgr.AddPane(self.modelprops_panel, wx.aui.AuiPaneInfo().
        Name("modelprops_panel").Caption("Model Properties").MinSize(wx.Size(260, 100)).
        Bottom().Left().CloseButton(False).MinimizeButton(True).MaximizeButton(True)
        .MinimizeButton(
            True).
        Floatable(True).Dockable(False).LeftDockable(True).RightDockable(True))

        # Center of UI - Input/Output Notebook pane.  Resizable but not dockable.
        self._mgr.AddPane(self.spreadsheet_panel, wx.aui.AuiPaneInfo().
        Name("spreadsheet_panel").Caption("Inputs And Outputs").MinSize(wx.Size(300, 900)).
        Center().CloseButton(False).MinimizeButton(True).MaximizeButton(True).
        Floatable(False).Dockable(False))

        # RH of UI - Plot 1 (above) and Plot 2 (below).  Resizable and dockable on
        # left and right of UI.
        self._mgr.AddPane(self.plot_panel, wx.aui.AuiPaneInfo().
        Name("plot_panel").Caption("Plots").MinSize(wx.Size(424, 900)).
        Right().CloseButton(False).MinimizeButton(True).MaximizeButton(True).
        Dockable(False).LeftDockable(True).RightDockable(True))

        self._mgr.Update()
        self.status_bar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.status_bar)

    def init_ctrls(self):
        """Builds the ModelTree and ModelProperty editor panes (LH of UI)."""
        self.ctrl_panel = wx.Panel(self)
        self.ctrl_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.init_modeltree()
        self.init_modelpropertiesgrid()
        self.ctrl_panel.SetSizer(self.ctrl_panel_sizer)

    def init_modeltree(self):
        """Builds the ModelTree"""
        self.modeltree = wxmodeltree.ModelTree(self.ctrl_panel, wx.ID_ANY,
                                               style=wx.WANTS_CHARS | wx.TR_DEFAULT_STYLE)
        self.modeltree.Expand(self.modeltree.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.controller.on_selection_change, self.modeltree)
        self.Bind(wx.EVT_TREE_SET_INFO, self.controller.on_modeltree_change, self.modeltree)
        self.modeltree.Bind(wx.EVT_RIGHT_DOWN, self.controller.on_right_click_modeltree)
        self.ctrl_panel_sizer.Add(self.modeltree, ui_defaults.ctrl_pct,
                                  ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.controller.get_models()

    def init_spreadsheets(self):
        """Builds the spreadsheet panels and the text output panel"""
        self.spreadsheet_panel = wx.Panel(self)
        self.spreadsheet_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Notebook control - first page is input data spreadsheet,
        # second page is output data spreadsheet, third is generic text control for text output.
        self.spreadsheet_nb = wx.Notebook(self.spreadsheet_panel, wx.ID_ANY,
                                          wx.DefaultPosition, wx.DefaultSize, 0)

        self.input_sheet = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
                                    wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        input_sheet_panelsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_grid = self.creategrid(self.input_sheet)
        self.input_tb = self.creategrid_toolbar(self.input_sheet)
        self.input_tb.Realize()
        input_sheet_panelsizer.Add(self.input_tb, 0, wx.EXPAND,
                                   border=ui_defaults.widget_margin)
        input_sheet_panelsizer.Add(self.input_grid, 1, wx.TOP | wx.LEFT | wx.GROW)
        self.input_sheet.SetSizer(input_sheet_panelsizer)
        self.input_sheet.Layout()
        self.spreadsheet_nb.AddPage(self.input_sheet, "Input Worksheet", False)

        self.output_sheet = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
                                     wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        output_sheet_panelsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output_grid = self.creategrid(self.output_sheet)
        self.output_tb = self.creategrid_toolbar(self.output_sheet)
        self.output_tb.Realize()
        output_sheet_panelsizer.Add(self.output_tb, 0, wx.EXPAND,
                                    border=ui_defaults.widget_margin)
        output_sheet_panelsizer.Add(self.output_grid, 1, wx.TOP | wx.LEFT | wx.GROW)
        self.output_sheet.SetSizer(output_sheet_panelsizer)
        self.output_sheet.Layout()
        self.spreadsheet_nb.AddPage(self.output_sheet, "Output Worksheet", False)

        self.txtoutput_sheet = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
                                        wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        txtoutput_sheet_panelsizer = wx.BoxSizer(wx.VERTICAL)
        self.txtoutput_tc = wx.TextCtrl(self.txtoutput_sheet, wx.ID_ANY,
                                        u'', wx.DefaultPosition, wx.DefaultSize,
                                        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        txtoutput_sheet_panelsizer.Add(self.txtoutput_tc, 1, wx.TOP | wx.LEFT | wx.GROW)
        self.txtoutput_sheet.SetSizer(txtoutput_sheet_panelsizer)
        self.spreadsheet_nb.AddPage(self.txtoutput_sheet, "Text Summary", False)

        self.spreadsheet_panel_sizer.Add(self.spreadsheet_nb, 1,
                                         wx.TOP | wx.LEFT | wx.GROW, ui_defaults.widget_margin)
        self.spreadsheet_panel.SetSizer(self.spreadsheet_panel_sizer)

    def init_modelpropertiesgrid(self):
        """Builds the ModelProperty editor"""
        self.modelprops_panel = wx.Panel(self)
        self.modelprops_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.mp_lbl = wx.StaticText(self.modelprops_panel, wx.ID_ANY,
                                    u"No Property Selected", wx.DefaultPosition, wx.DefaultSize, 0)
        self.modelprops_panel_sizer.Add(self.mp_lbl, ui_defaults.lbl_pct,
                                        ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.mp_grid = wxspreadsheet.Spreadsheet(self.modelprops_panel)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.controller.on_property_change)
        self.mp_grid.SetNumberRows(1)
        self.mp_grid.SetNumberCols(2)
        self.mp_grid.SetRowLabelSize(1)
        ro_attrib = wx.grid.GridCellAttr()
        ro_attrib.SetReadOnly()
        self.mp_grid.SetColAttr(0, ro_attrib)
        self.mp_grid.SetColSize(0, 125)
        self.mp_grid.SetColSize(1, 125)
        self.mp_grid.SetColMinimalAcceptableWidth(100)
        self.mp_grid.SetColLabelValue(0, "Property")
        self.mp_grid.SetColLabelValue(1, "Value")
        self.mp_grid.EnableEditing(True)
        self.modelprops_panel_sizer.Add(self.mp_grid, ui_defaults.ctrl_pct,
                                        ui_defaults.sizer_flags | wx.GROW,
                                        ui_defaults.widget_margin)
        self.modelprops_panel.SetSizer(self.modelprops_panel_sizer)

    def init_plots(self):
        """Builds the two plot windows"""
        self.plot_panel = wx.Panel(self)
        self.plot_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.figure1 = matplotlib.figure.Figure((5, 4), 75)
        self.figure2 = matplotlib.figure.Figure((5, 4), 75)
        self.canvas1 = FigureCanvas(self.plot_panel, -1, self.figure1)
        self.canvas2 = FigureCanvas(self.plot_panel, -1, self.figure2)
        self.toolbar1 = NavigationToolbar2WxAgg(self.canvas1)

        self.toolbar2 = NavigationToolbar2WxAgg(self.canvas2)

        self.axes1 = self.figure1.add_subplot(111, navigate=True)
        self.axes1.grid(True)
        self.axes2 = self.figure2.add_subplot(111, navigate=True)
        self.axes2.grid(True)
        plot1_lbl = wx.StaticText(self.plot_panel, wx.ID_ANY, u"Plot 1",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        plot1_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
                                  70, 90, 92, False, wx.EmptyString))
        plot2_lbl = wx.StaticText(self.plot_panel, wx.ID_ANY, u"Plot 2",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        plot2_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
                                  70, 90, 92, False, wx.EmptyString))
        self.plot_panel_sizer.Add(plot1_lbl, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.canvas1, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.toolbar1, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.toolbar1.Realize()
        self.plot_panel_sizer.Add(plot2_lbl, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.canvas2, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.toolbar2, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.toolbar2.Realize()
        self.plot_panel.SetSizer(self.plot_panel_sizer)

    def creategrid(self, parent, numcols=None, numrows=None):
        """Builds and returns a new Spreadsheet with the specified
        number of columns and rows."""
        newgrid = wxspreadsheet.Spreadsheet(parent)
        if numcols is not None:
            newgrid.SetNumberCols(numcols)
        if numrows is not None:
            newgrid.SetNumberRows(numrows)
        newgrid.ForceRefresh()
        newgrid.EnableEditing(True)
        newgrid.EnableGridLines(True)
        newgrid.EnableDragGridSize(False)
        newgrid.EnableDragColMove(True)
        newgrid.EnableDragColSize(True)
        newgrid.EnableDragRowSize(True)
        newgrid.EnableDragGridSize(True)
        newgrid.SetMargins(0, 0)
        newgrid.SetColLabelSize(30)
        newgrid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        return newgrid

    def creategrid_toolbar(self, parent):
        """Creates a toolbar for a Spreadsheet control - includes open
        and save functions."""
        toolbar = wx.ToolBar(parent,
                             style=wx.TB_VERTICAL | wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        tsize = (16, 16)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize)

        toolbar.SetToolBitmapSize(tsize)
        toolbar.AddLabelTool(20, "Open", open_bmp, shortHelp="Open ")
        toolbar.AddSimpleTool(30, save_bmp, "Save", "Long help for 'Save'")
        self.Bind(wx.EVT_TOOL, self.controller.on_sheet_tool_click, id=20)
        self.Bind(wx.EVT_TOOL, self.controller.on_sheet_tool_click, id=30)
        return toolbar

    def tree_popup(self, click_position):
        """Generates a contextual (popup) menu for the ModelTree"""
        self.PopupMenu(wxmodeltree.ModelTreeContextMenu(self), click_position)

    def close(self):
        """Correctly handles UI shutdown"""
        self._mgr.UnInit()
        self.Destroy()
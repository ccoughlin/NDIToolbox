"""
wxspreadsheet.py: single-file extension of wxPython's CSheet (grid) with basic spreadsheet
functionality.  Original code:  https://bitbucket.org/ccoughlin/wxspreadsheet/overview
"""

__author__ = 'Chris R. Coughlin'

import wx.lib.sheet
import wx.grid
import csv

class ContextMenu(wx.Menu):
    '''Basic right-click popup menu for CSheet controls.  Currently
    implements copy-paste selected cell(s), insert row / column, delete
    row / column.'''

    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        insertrow = wx.MenuItem(self, wx.NewId(), 'Insert Row(s)')
        self.AppendItem(insertrow)
        self.Bind(wx.EVT_MENU, self.OnInsertRow, id=insertrow.GetId())
        deleterow = wx.MenuItem(self, wx.NewId(), 'Delete Row(s)')
        self.AppendItem(deleterow)
        self.Bind(wx.EVT_MENU, self.OnDeleteRow, id=deleterow.GetId())
        insertcol = wx.MenuItem(self, wx.NewId(), 'Insert Column(s)')
        self.AppendItem(insertcol)
        self.Bind(wx.EVT_MENU, self.OnInsertCol, id=insertcol.GetId())
        deletecol = wx.MenuItem(self, wx.NewId(), 'Delete Column(s)')
        self.AppendItem(deletecol)
        self.Bind(wx.EVT_MENU, self.OnDeleteCol, id=deletecol.GetId())
        self.AppendSeparator()
        copy = wx.MenuItem(self, wx.NewId(), 'Copy')
        self.AppendItem(copy)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=copy.GetId())
        paste = wx.MenuItem(self, wx.NewId(), 'Paste')
        self.AppendItem(paste)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=paste.GetId())
        clear = wx.MenuItem(self, wx.NewId(), 'Clear Selected Cells')
        self.AppendItem(clear)
        self.Bind(wx.EVT_MENU, self.OnClear, id=clear.GetId())

    def OnInsertRow(self, event):
        '''Basic "Insert Row(s) Here" function'''
        self.parent.SelectRow(self._getRow())
        self.parent.InsertRows(self._getRow(), self._getSelectionRowSize())

    def OnDeleteRow(self, event):
        '''Basic "Delete Row(s)" function'''
        self.parent.DeleteRows(self._getRow(), self._getSelectionRowSize())

    def OnInsertCol(self, event):
        '''Basic "Insert Column(s) Here" function'''
        self.parent.InsertCols(self._getCol(), self._getSelectionColSize())

    def OnDeleteCol(self, event):
        '''Basic "Delete Column(s)" function'''
        self.parent.DeleteCols(self._getCol(), self._getSelectionColSize())

    def OnClear(self, event):
        '''Erases the contents of the currently selected cell(s).'''
        self.parent.Clear()

    def OnCopy(self, event):
        '''Copies the contents of the currently selected cell(s)
        to the clipboard.'''
        self.parent.Copy()

    def OnPaste(self, event):
        '''Pastes the clipboard's contents to the currently
        selected cell(s).'''
        self.parent.Paste()

    def _getRow(self):
        '''Returns the first (top) row in the selected row(s) if any,
        otherwise returns the row of the current cursor position.'''
        selected_row = self.parent.GetSelectedRows()
        if  selected_row != []:
            return selected_row[0]
        else:
            return self.parent.GetGridCursorRow()

    def _getCol(self):
        '''Returns the first (left) row in the selected column(s) if any,
        otherwise returns the column of the current cursor position.'''
        selected_col = self.parent.GetSelectedCols()
        if  selected_col != []:
            return selected_col[0]
        else:
            return self.parent.GetGridCursorCol()

    def _getSelectionRowSize(self):
        '''Returns the number of selected rows, number of rows in the
        current selection, or 1 in order of preference.'''
        numrows = 1
        if self.parent.GetSelectionBlockTopLeft() != []:
            numrows = self.parent.GetSelectionBlockBottomRight()[0][0] -\
                      self.parent.GetSelectionBlockTopLeft()[0][0] + 1
        else:
            numrows = len(self.parent.GetSelectedRows())
        return numrows

    def _getSelectionColSize(self):
        '''Returns the number of selected columns, number of columns in the
        current selection, or 1 in order of preference.'''
        numcols = 1
        if self.parent.GetSelectionBlockTopLeft() != []:
            numcols = self.parent.GetSelectionBlockBottomRight()[0][1] -\
                      self.parent.GetSelectionBlockTopLeft()[0][1] + 1
        else:
            numcols = len(self.parent.GetSelectedCols())
        return numcols


class SpreadsheetTextCellEditor(wx.TextCtrl):
    """ Custom text control for cell editing """

    def __init__(self, parent, id, grid):
        wx.TextCtrl.__init__(self, parent, id, "",
                             style=wx.NO_BORDER | wx.TE_PROCESS_ENTER)
        self._grid = grid                           # Save grid reference
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def OnChar(self, evt):                          # Hook OnChar for custom behavior
        """Customizes char events """
        key = evt.GetKeyCode()
        if key == wx.WXK_DOWN or key == wx.WXK_RETURN:
            self._grid.DisableCellEditControl()     # Commit the edit
            self._grid.MoveCursorDown(False)        # Change the current cell
        elif key == wx.WXK_UP:
            self._grid.DisableCellEditControl()     # Commit the edit
            self._grid.MoveCursorUp(False)          # Change the current cell
        elif key == wx.WXK_LEFT:
            self._grid.DisableCellEditControl()     # Commit the edit
            self._grid.MoveCursorLeft(False)        # Change the current cell
        elif key == wx.WXK_RIGHT:
            self._grid.DisableCellEditControl()     # Commit the edit
            self._grid.MoveCursorRight(False)       # Change the current cell

        evt.Skip()                                  # Continue event


class SpreadsheetCellEditor(wx.lib.sheet.CCellEditor):
    """ Custom cell editor """

    def __init__(self, grid):
        super(SpreadsheetCellEditor, self).__init__(grid)

    def Create(self, parent, id, evtHandler):
        """ Create the actual edit control.  Must derive from wxControl.
            Must Override
        """
        self._tc = SpreadsheetTextCellEditor(parent, id, self._grid)
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)


class Spreadsheet(wx.lib.sheet.CSheet):
    '''Child class of CSheet (child of wxGrid) that implements a basic
    right-click popup menu.'''

    def __init__(self, parent):
        self.parent = parent
        super(Spreadsheet, self).__init__(self.parent)

    def OnRightClick(self, event):
        '''Defines the right click popup menu for the spreadsheet'''

        '''Move the cursor to the cell clicked'''
        self.SetGridCursor(event.GetRow(), event.GetCol())
        self.PopupMenu(ContextMenu(self), event.GetPosition())

    def ReadCSV(self, csvfile, _delimiter=',', _quotechar='#'):
        '''Reads a CSV file into the current spreadsheet, replacing
        existing contents (if any).'''
        self.ClearGrid()
        with open(csvfile, 'rU') as inputfile:
            csv_reader = csv.reader(inputfile,
                                    delimiter=_delimiter, quotechar=_quotechar)
            try:
                self.SetNumberRows(0)
                self.SetNumberCols(0)

                rownum = 0
                for row in csv_reader:
                    self.AppendRows(1)
                    numcols = len(row)
                    if self.GetNumberCols() < numcols:
                        self.SetNumberCols(numcols)
                    colnum = 0
                    for cell in row:
                        self.SetCellValue(rownum, colnum, str(cell))
                        colnum = colnum + 1
                    rownum = rownum + 1
            except csv.Error as err:
                print("Skipping line {0}: {1}".format(csv_reader.line_num, err))

    def WriteCSV(self, csvfile, _delimiter=',', _quotechar='#', _quoting=csv.QUOTE_MINIMAL):
        '''Writes the current contents of the spreadsheet to a CSV file'''
        csv_writer = csv.writer(open(csvfile, 'wb'), delimiter=_delimiter, quotechar=_quotechar, quoting=_quoting)
        for rownum in range(self.GetNumberRows()):
            rowdata = []
            for colnum in range(self.GetNumberCols()):
                rowdata.append(self.GetCellValue(rownum, colnum))
            csv_writer.writerow(rowdata)
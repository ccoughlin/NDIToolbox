"""uicontroller.py - controller for the main user interface

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'ccoughlin'

from models.colormapcreator_model import ColormapCreatorModel
import pathfinder
import wx

class ColormapCreatorController(object):
    """Controller for the ColormapCreator user interface"""

    def __init__(self, view):
        self.view = view
        self.model = ColormapCreatorModel(self)
        self.init_colormap_dict()
        self.sample_data = self.model.generate_sample_data()

    def init_colormap_dict(self):
        """Sets the colormap_dict to a sane starting point"""
        self.colormap_dict = {'name':'default',
                              'type':'linear',
                              'colors':[[0,0,0],
                                        [0.5,0.5,0.5],
                                        [1,1,1]]}

    @property
    def colormap(self):
        """Returns the current colormap, or 'bone' if not specified."""
        if self.colormap_dict is not None:
            return self.model.create_cmap(self.colormap_dict)
        return self.model.get_cmap("bone")

    def preview_colormap(self):
        """Previews the current colormap in an image plot"""
        cmap_type = self.view.get_cmap_type()
        colours = self.get_colors()
        if colours != []:
            self.colormap_dict['type'] = cmap_type
            self.colormap_dict['colors'] = colours
        self.view.axes.cla()
        self.view.img = self.view.axes.imshow(self.sample_data, aspect='equal', origin='lower', cmap=self.colormap)
        if hasattr(self.view, "colorbar"):
            # Need to completely erase plot if colorbar already exists
            self.view.figure.delaxes(self.view.figure.axes[1])
            self.view.figure.subplots_adjust(right=0.90)
        self.view.colorbar = self.view.figure.colorbar(self.view.img)
        if self.colormap_dict is not None:
            self.view.colorbar.set_label(self.colormap_dict.get('name', None))
        self.refresh_plot()

    def refresh_plot(self):
        """Forces plot to redraw itself"""
        self.view.canvas.draw()

    def set_colormap(self):
        """Sets the UI's colormap according to the current colormap dict"""
        self.view.set_cmap_type(self.colormap_dict.get('type', 'linear'))
        self.set_colors(self.colormap_dict['colors'])
        self.preview_colormap()

    def get_colors(self):
        """Returns a list of the colors in the UI"""
        raw_color_strs = self.view.colors_lb.GetStrings()
        colors = []
        for raw_str in raw_color_strs:
            els = raw_str.split(',')
            if len(els) == 3:
                try:
                    new_color = []
                    for el in els:
                        color_component = float(el)
                        if color_component > 1:
                            color_component /= 255
                        elif color_component < 0:
                            color_component = 0
                        new_color.append(color_component)
                    colors.append(new_color)
                except ValueError: # couldn't convert to floating-point number
                    pass
        return colors

    def set_colors(self, color_list):
        """Sets the list of colors in the UI to the specified list"""
        str_colors = []
        for color in color_list:
            new_color_str = ','.join([str(el) for el in color])
            str_colors.append(new_color_str)
        self.view.colors_lb.SetStrings(str_colors)

    # Event handlers
    def on_preview(self, evt):
        """Handles request to preview the current colormap"""
        self.preview_colormap()

    def on_close(self, evt):
        """Handles request to close app"""
        self.close()

    def close(self):
        """Closes the app"""
        self.view.Destroy()

    def on_load_cmap(self, evt):
        """Handles request to load a colormap"""
        file_dlg = wx.FileDialog(parent=self.view, message="Please specify a colormap file",
                                 defaultDir=pathfinder.colormaps_path(), style=wx.FD_OPEN)
        if file_dlg.ShowModal() == wx.ID_OK:
            try:
                self.colormap_dict = self.model.get_cmap_dict(file_dlg.GetPath())
                self.set_colormap()
            finally:
                file_dlg.Destroy()

    def on_save_cmap(self, evt):
        """Handles request to save current colormap"""
        file_dlg = wx.FileDialog(parent=self.view, message="Please specify a filename",
                                 defaultDir=pathfinder.colormaps_path(),
                                 style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if file_dlg.ShowModal() == wx.ID_OK:
            try:
                self.model.save_cmap_dict(self.colormap_dict, file_dlg.GetPath())
                self.colormap_dict = self.model.get_cmap_dict(file_dlg.GetPath())
                self.set_colormap()
            finally:
                file_dlg.Destroy()

    def on_add_color(self, evt):
        """Handles request to add a new color to the colormap"""
        color_dlg = wx.ColourDialog(self.view)
        color_dlg.GetColourData().SetChooseFull(True)
        if color_dlg.ShowModal() == wx.ID_OK:
            color_data = color_dlg.GetColourData()
            normalized_color_data = [component/255. for component in color_data.GetColour().Get()]
            self.view.add_color(normalized_color_data)
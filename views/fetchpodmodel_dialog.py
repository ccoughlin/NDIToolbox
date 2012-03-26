"""fetchpodmodel_dialog.py - wxPython dialogs for installing PODModel archives

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from views import fetchplugin_dialog
from controllers import fetchpodmodel_dialog_ctrl

class FetchPODModelDialog(fetchplugin_dialog.FetchPluginDialog):
    """wxPython dialog for installing POD Models from the local filesystem"""

    def __init__(self, parent, plugin_path=None):
        self.plugin_type = "POD Model"
        super(FetchPODModelDialog, self).__init__(parent, plugin_path, self.plugin_type)

    def init_controller(self):
        """Creates the view's controller"""
        self.controller = fetchpodmodel_dialog_ctrl.FetchPODModelDialogController(self)


class FetchRemotePODModelDialog(fetchplugin_dialog.FetchRemotePluginDialog):
    """wxPython dialog for downloading and installing POD Models"""

    def __init__(self, parent):
        self.plugin_type = "POD Model"
        super(FetchRemotePODModelDialog, self).__init__(parent, self.plugin_type)

    def init_controller(self):
        """Creates the view's controller"""
        self.controller = fetchpodmodel_dialog_ctrl.FetchRemotePODModelDialogController(self)
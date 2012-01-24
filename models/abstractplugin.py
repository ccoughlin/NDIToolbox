"""abstractplugin.py - defines the abstract plugin for the A7117 project

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from abc import ABCMeta, abstractmethod, abstractproperty

class AbstractPlugin(object):
    """Abstract base class definition for A7117 plugins.  Plugins must
    be a subclass of AbstractPlugin and must define the following members.

    data - getter and setter - NumPy array
    description - getter - str
    authors - getter - str
    copyright - getter - str
    name - getter - str
    version - getter - str
    url - getter - str
    run() method

    For more concrete examples, consult the TRIPlugin, ComputationalToolsPlugin,
    and CompanyPluginTemplate modules.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def data(self):
        pass
    @data.setter
    def data(self, newdata):
        pass

    @abstractproperty
    def description(self):
        pass

    @abstractproperty
    def authors(self):
        pass

    @abstractproperty
    def copyright(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def version(self):
        pass

    @abstractproperty
    def url(self):
        pass

    @abstractmethod
    def run(self):
        pass
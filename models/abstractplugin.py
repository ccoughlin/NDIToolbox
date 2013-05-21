"""abstractplugin.py - defines the abstract plugin for NDIToolbox

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from abc import ABCMeta, abstractmethod, abstractproperty

class AbstractPlugin(object):
    """Abstract base class definition for NDIToolbox plugins.  Plugins must
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
    and CompanyPlugin modules.
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


class CompanyPlugin(AbstractPlugin):
    """Basic template for NDIToolbox plugins for an institution.  Subclasses
    should overload the placeholder plugin fields and the run() method."""

    name = "Generic Company Plugin"
    description = "NDIToolbox Plugin By Company Name"
    authors = "Company Inc."
    version = "1.0"
    url = "www.company_url.com"
    copyright = "Copyright (C) 2012 Company Name.  All rights reserved."

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.name)
        self.description = kwargs.get('description', self.description)
        self.authors = kwargs.get('authors', self.authors)
        self.version = kwargs.get('version', self.version)
        self.url = kwargs.get('url', self.url)
        self.copyright = kwargs.get('copyright', self.copyright)
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data

    def run(self):
        """Executes the plugin"""
        pass


class TRIPlugin(CompanyPlugin):
    """Basic template for NDIToolbox plugins for TRI/Austin personnel"""

    name = "TRI/Austin Plugin"
    description = "Basic template for creating NDIToolbox plugins for TRI/Austin personnel."
    authors = "TRI/Austin, Inc."
    version = "1.0"
    url = "www.tri-austin.com"
    copyright = "Copyright (C) 2013 TRI/Austin, Inc.  All rights reserved."

    def __init__(self, **kwargs):
        CompanyPlugin.__init__(self, **kwargs)


class ComputationalToolsPlugin(CompanyPlugin):
    """Basic template for NDIToolbox plugins for Computational Tools personnel"""

    name = "Computational Tools Plugin"
    description = "Basic template for creating NDIToolbox plugins for Computational Tools personnel."
    authors = "John C. Aldrin (Computational Tools, Inc.)"
    version = "1.0"
    url = "www.computationaltools.com"
    copyright = "Copyright (C) 2012 Computational Tools.  All rights reserved."

    def __init__(self, **kwargs):
        CompanyPlugin.__init__(self, **kwargs)
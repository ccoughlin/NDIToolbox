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
    """Basic template for A7117 plugins for an institution.  Subclasses
    should overload the placeholder plugin fields and the run() method."""

    name = "Generic Company Plugin"
    description = "A7117 Plugin By Company Name"
    authors = "Company Inc."
    version = "1.0"
    url = "www.company_url.com"
    copyright = "Copyright (C) 2012 Company Name.  All rights reserved."

    def __init__(self, name, description, authors=None, version=None,
                 url=None, copyright=None):
        self.name = name
        self.description = description
        if authors is not None:
            self.authors = authors
        if version is not None:
            self.version = version
        if url is not None:
            self.url = url
        if copyright is not None:
            self.copyright = copyright
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
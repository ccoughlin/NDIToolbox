"""computationaltoolsplugin.py - basic template for creating a plugin for A7117
for Computational Tools personnel.

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from abstractplugin import CompanyPlugin

class ComputationalToolsPlugin(CompanyPlugin):
    """Basic template for A7117 plugins for Computational Tools personnel"""

    name = "Computational Tools Plugin"
    description = "Basic template for creating A7117 plugins for Computational Tools personnel."
    authors = "John C. Aldrin (Computational Tools, Inc.)"
    version = "1.0"
    url = "www.computationaltools.com"
    copyright = "Copyright (C) 2012 Computational Tools.  All rights reserved."

    def __init__(self, name=None, description=None, authors=None, version=None,
                 url=None, copyright=None):
        super(ComputationalToolsPlugin, self).__init__(name, description, authors, version,
                                        url, copyright)
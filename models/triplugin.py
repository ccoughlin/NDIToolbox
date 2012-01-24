"""triplugin.py - basic template for creating a plugin for A7117
for TRI/Austin personnel.

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from abstractplugin import CompanyPlugin

class TRIPlugin(CompanyPlugin):
    """Basic template for A7117 plugins for TRI/Austin personnel"""

    name = "TRI/Austin Plugin"
    description = "Basic template for creating A7117 plugins for TRI/Austin personnel."
    authors = "TRI/Austin, Inc."
    version = "1.0"
    url = "www.tri-austin.com"
    copyright = "Copyright (C) 2012 TRI/Austin, Inc.  All rights reserved."

    def __init__(self, name=None, description=None, authors=None, version=None,
                 url=None, copyright=None):
        super(TRIPlugin, self).__init__(name, description, authors, version,
                                        url, copyright)
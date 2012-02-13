"""config.py - implements configuration options for the appplication

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import ConfigParser

class Configure(object):
    """Wrapper for ConfigParser SafeConfigParser"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser.SafeConfigParser()
        # Default section name for application-wide configuration
        self.app_section = "Application"

    def set(self, section, options):
        """Given a dict options, sets key=val configuration
        options in specified section for each item.  If the
        section does not already exist it is created."""
        self.config.read(self.config_file)
        if not self.config.has_section(section):
            self.config.add_section(section)
        for key, val in options.items():
            if isinstance(val, list) or isinstance(val, tuple):
                option_val = ','.join([str(el) for el in val])
            else:
                option_val = str(val)
            self.config.set(section, str(key), option_val)
        with open(self.config_file, 'wb') as config_file:
            self.config.write(config_file)

    def set_app_option(self, options):
        """Sets the specified options dict under the
        default 'Application' section"""
        self.set(self.app_section, options)

    def has_option(self, section, option):
        """Returns True if the specified section
        exists and has the specified option"""
        self.config.read(self.config_file)
        return self.config.has_option(section, option)

    def has_app_option(self, option):
        """Returns True if the 'Application' section
        contains the specified option"""
        return self.has_option(self.app_section, option)

    def get(self, section, option_key):
        """Returns a string instance of the specified option_key
        from the specified section if found, otherwise returns
        None."""
        option_val = None
        self.config.read(self.config_file)
        if self.has_option(section, option_key):
                option_val = self.config.get(section, option_key)
        return option_val

    def get_app_option(self, option_key):
        """Returns a string instance of the specified option_key
        from the default Application section, or None if not
        found."""
        return self.get(self.app_section, option_key)

    def get_boolean(self, section, option_key):
        """Returns a Boolean instance of the specified option_key
        from the specified section if found, otherwise returns
        None."""
        option_val = None
        self.config.read(self.config_file)
        try:
            if self.has_option(section, option_key):
                option_val = self.config.getboolean(section, option_key)
        except ValueError: # didn't recognize the option value as a Boolean
            pass
        finally:
            return option_val

    def get_int(self, section, option_key):
        """Returns an integer instance of the specified option_key
        from the specified section if found, otherwise returns None."""
        option_val = None
        self.config.read(self.config_file)
        try:
            if self.has_option(section, option_key):
                option_val = self.config.getint(section, option_key)
        except ValueError: # Couldn't convert option to int
            pass
        finally:
            return option_val

    def get_float(self, section, option_key):
        """Returns a float instance of the specified option_key
        from the specified section if found, otherwise returns None."""
        option_val = None
        self.config.read(self.config_file)
        try:
            if self.has_option(section, option_key):
                option_val = self.config.getfloat(section, option_key)
        except ValueError: # Couldn't convert option to float
            pass
        finally:
            return option_val

    def get_list(self, section, option_key, split_char=','):
        """Returns a list of strings of the specified option_key,
        splitting the elements by the specified split_char (comma
        by default).  Returns None if the option_key was not found."""
        option = self.get(section, option_key)
        if option is not None:
            return option.split(split_char)
        return None

    def get_app_option_boolean(self, option_key):
        """Returns a Boolean value of the specified option_key
        from the default Application section if found, or None
        if not found / not converted."""
        return self.get_boolean(self.app_section, option_key)

    def get_app_option_int(self, option_key):
        """Returns an int value of the specified option_key
        from the default Application section if found, or None
        if not found / not converted."""
        return self.get_int(self.app_section, option_key)

    def get_app_option_float(self, option_key):
        """Returns a float value of the specified option_key
        from the default Application section if found, or None
        if not found / not converted."""
        return self.get_float(self.app_section, option_key)

    def get_app_option_list(self, option_key):
        """Returns a list of the specified option_key's settings
        from the default Application section if found, or None
        if not found."""
        return self.get_list(self.app_section, option_key)

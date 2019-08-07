import configparser
import os

DEBUGCFG = False

class jmConfig:
    """
    A class to represent general jm configuration

    Methods
    -------
    load()
        Load global configuration file to memory structure
    save()
        Save memory structure to global configuration file
    jaillist() : list of strings
        List of existing jails
    bootlist() : list of strings
        List of bootable jails
    bootorder() : list of strings
        List of bootable jails in boot order
    shutorder() : list of strings
        List of existing jails in shutdown order (non-bootable first)

    """

    def __init__(self):
        """Initialize configuration object"""

        self.configfile = "/usr/local/etc/jm.conf"
        self.exists = os.path.exists(self.configfile)
        self.params = configparser.ConfigParser()

    def load(self):
        """Load configuration from file"""
        self.params.read(self.configfile)

    def save(self):
        """Save configuration to file"""
        with open(self.configfile, 'w') as f:
            self.params.write(f)

    def __noint(self, value):
        """Internal method to make "no" sortable as integer

        Parameters
        ----------
        value : string
            Value to process

        Returns
        -------
        string
            Sortable integer representation
        """

        if value == 'no':
            return '99999'

        return value


    def jaillist(self):
        """Get list of jail sections existing in configuration

        Returns
        -------
        list of strings
            List of jail names in config
        """

        """Everything but service entries is a jail name"""
        return list(
                filter(
                    lambda x: not x in ['DEFAULTS', 'MAIN'],
                    self.params.sections()))

    def bootlist(self):
        """Get list of bootable jails

        Returns
        -------
        list of strings
            List of jails which are marked as bootable in config
        """

        return list(
                filter(
                    lambda x: not self.params[x]['boot'] == 'no',
                    self.jaillist()))

    def bootorder(self):
        """Get list of bootable jails sorted by boot order

        Returns
        -------
        list of strings
            Sorted list of bootable jails
        """

        return sorted(
                self.bootlist(),
                key = lambda x: int(self.params[x]['boot']))

    def shutorder(self):
        """Get list of all jails sorted in reverse boot order.

        All non-bootable jails are stopped first

        Returns
        -------
        list of strings
            List of all jails sorted in shutdown order
        """
        
        return sorted(
                self.jaillist(),
                key = lambda x: int(self.__noint(self.params[x]['boot'])),
                reverse = True)




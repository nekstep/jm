import configparser
import os

DEBUGCFG = False

class jmConfig:

    def __init__(self):
        if DEBUGCFG:
            self.configfile = "/home/kst/jm/jm.conf"
        else:
            self.configfile = "/usr/local/etc/jm.conf"

        self.exists = os.path.exists(self.configfile)
        self.params = configparser.ConfigParser()

    def load(self):
        self.params.read(self.configfile)

    def save(self):
        with open(self.configfile, 'w') as f:
            self.params.write(f)

    def __noint(self, value):
        if value == 'no':
            return '99999'

        return value


    def jaillist(self):
        return list(
                filter(
                    lambda x: not x in ['DEFAULTS', 'MAIN'],
                    self.params.sections()))

    def bootlist(self):
        return list(
                filter(
                    lambda x: not self.params[x]['boot'] == 'no',
                    self.jaillist()))

    def bootorder(self):
        return sorted(
                self.bootlist(),
                key = lambda x: int(self.params[x]['boot']))

    def shutorder(self):
        return sorted(
                self.jaillist(),
                key = lambda x: int(self.__noint(self.params[x]['boot'])),
                reverse = True)




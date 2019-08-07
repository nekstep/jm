import os
import jm_lib.zfs as zfs
import jailconf
import json

"""List of filesystems to be mounted from base system"""
FSLIST = [ 'bin',
           'boot',
           'lib',
           'libexec',
           'rescue',
           'sbin',
           'usr/sbin',
           'usr/include',
           'usr/lib',
           'usr/libexec',
           'usr/bin',
           'usr/share',
           'usr/src',
           'usr/libdata']

class jmJail:
    """
    A class to represent jail

    Methods
    -------
    create(args)
        Create new jail from command line arguments
    destroy()
        Destroy this jail on filesystem
    load(config)
        Load jail from global configuration
    create_jailconf()
        Create jail.conf for this jail object
    get_config(key) : string
        Get value for configuration key
    status() : integer
        Get jail status (stopped/running/crashed)
    jid_exists() : boolean
        Check if jid file exists
    getid_jls() : string
        Get id of current jail from jls
    start()
        Start jail
    console()
        Provide console for jail
    exec(cmd)
        Execute command in jail
    stop()
        Stop jail
    zfs_jid_path() : string
        Get jid path
    zfs_fstab_path() : string
        Get fstab path
    zfs_jailconf_path() : string
        Get jail.conf path
    zfs_jail_pool() : string
        Get jail ZFS pool
    zfs_jail_mountpoint() : string
        Get jail ZFS mountpoint
    zfs_root_pool() : string
        Get jail ZFS root pool
    zfs_root_mountpoint() : string
        Get jail ZFS root mountpoint
    destroy_pools()
        Destroy jail ZFS pools
    create_pools()
        Create jail ZFS pools
    sync_defaults()
        Sync default filesystem structure
    create_fstab()
        Create fstab for jail

    """

    def __init__(self, name, config):
        """Initialize jail object

        Parameters
        ----------
        name : string
            Name of jail to initialize in object
        config : jmConfig
            Global configuration object
        """

        self.config = {}
        self.name = name
        self.jconf = None
        self.__zfspool = config['MAIN']['zfspool']
        self.__mountpoint = config['MAIN']['mountpoint']

    def create(self, args):
        """Create new jail

        Paramters
        ---------
        args : namespace
            Arguments passed from command line
        """

        """Copy allowed attributes from command line options to object"""
        for attr in ['interface', 'addr', 'hostname', 'boot']:
            if attr in vars(args):
                if not vars(args)[attr] is None:
                    self.config[attr] = vars(args)[attr]

        """Create new jail on filesystem"""
        self.create_pools()
        self.sync_defaults()
        self.create_fstab()

    def destroy(self):
        """Destroy this jail"""

        """Destroy pool and remove mountpoints"""
        self.destroy_pools()
        os.rmdir(self.zfs_jail_mountpoint())

    def load(self, config):
        """Load jail configuration from global config

        Parameters
        ----------
        config : jmConfig
            Global configuration file to load from
        """

        """Copy relevant global config section to local config"""
        self.config = config[self.name]

    def create_jailconf(self):
        """Create jail.conf for current jail"""

        """Create jailconf object and populate default parameters"""
        self.jconf = jailconf.JailConf()
        self.jconf[self.name] = jailconf.JailBlock([
            ('path', self.zfs_root_mountpoint()),
            ('mount.fstab', self.zfs_fstab_path()),
            ('allow.raw_sockets', '1'),
            ('allow.sysvipc', '1'),
            ('allow.set_hostname', '1'),
            ('mount.devfs', '1'),
            ('mount.fdescfs', '1'),
            ('exec.start', '"/bin/sh /etc/rc"'),
            ('exec.stop', '"/bin/sh /etc/rc.shutdown"')
            ])

        """Populate optional parameters"""
        if 'interface' in self.config:
            self.jconf[self.name]['interface'] = self.config['interface']

        if 'addr' in self.config:
            self.jconf[self.name]['ip4.addr'] = self.config['addr']

        if 'hostname' in self.config:
            self.jconf[self.name]['host.hostname'] = self.config['hostname']

        """Dump jailconf object to file"""
        zfs.write_to_file(self.zfs_jailconf_path(), self.jconf.dumps())

    def get_config(self, key):
        """Get a key from config or '-' if there is no such entry

        Parameters
        ----------
        key : string
            Key to get

        Returns
        -------
        string
            Key value or '-'
        """

        if key in self.config:
            return self.config[key]
        else:
            return '-'

    def status(self):
        """Get jail status

        Returns
        -------
        integer
            0 - stopped
            1 - running correctly
            2 - pid exists but not running (crashed)
        """

        if self.jid_exists():
            if self.getid_jls() == None:
                return 2
            else:
                return 1
        else:
            return 0

    def jid_exists(self):
        """Check if relevant jid file exists

        Returns
        -------
        boolean
            True if jid exists
        """

        return os.path.exists(self.zfs_jid_path())

    def getid_jls(self):
        """Get id of running jail from jls

        Returns
        -------
        string
            Jail id if running, None if not
        """

        jailid = None

        """Load all jails from jls output into JSON object"""
        jlist = json.load(os.popen("jls -v --libxo json"))

        """Try to find entry with current name and save jail id if found"""
        for jent in jlist["jail-information"]["jail"]:
            if jent["name"] == self.name:
                jailid = jent["jid"]

        return jailid

    def getid_jid(self):
        """Get id of jail from jid file or '-' if not

        Returns
        -------
        string
            Jail id
        """

        jailid = "-"

        if self.jid_exists():
            with open(self.zfs_jid_path(), 'r') as f:
                jailid = f.read().replace('\n','')

        return jailid

    def start(self):
        """Start current jail"""

        """Attempt to create jail in system"""
        zfs.run_command(f"jail -c -f {self.zfs_jailconf_path()}")

        """See if it is running so we can get an id"""
        jailid = self.getid_jls()

        """If it is not running - it has failed to start"""
        if jailid is None:
            print(f"Jail {self.name} failed to start!")
            return -1

        """Save id to jid file"""
        with open(self.zfs_jid_path(), 'w') as f:
            f.write(str(jailid))

    def console(self):
        """Provide console for jail"""

        """Execute shell"""
        self.exec("/bin/csh -l") 

    def exec(self, cmd):
        """Execute command in jail

        Parameters
        ----------
        cmd : array of string
            Command from command line
        """
            

        """Get id of running jail"""
        jailid = self.getid_jls()

        """See if it is not running"""
        if jailid is None:
            return

        """Run specified command in jail"""
        cmdline = " ".join(cmd)
        zfs.run_command(f"jexec {jailid} {cmdline}")

    def stop(self):
        """Stop jail"""

        if self.getid_jid() == "-":
            return

        """Shutdown jail if running"""
        jailid = self.getid_jls()
        if jailid is not None:
            zfs.run_command(
                    f"jexec {jailid} /bin/sh /etc/rc.shutdown")
            zfs.run_command(
                    f"jail -r {jailid}")

        """Remove jid and jail.conf"""
        os.remove(self.zfs_jid_path())
        os.remove(self.zfs_jailconf_path())

        """Unmount devfs"""
        zfs.run_command(f"umount {self.zfs_root_mountpoint()}/dev/fd")
        zfs.run_command(f"umount {self.zfs_root_mountpoint()}/dev")

        """Unmount all other nullfs filesystems"""
        for fs in FSLIST:
            zfs.run_command(f"umount {self.zfs_root_mountpoint()}/{fs}")

    def zfs_jid_path(self):
        """Get jid path"""
        return self.zfs_jail_mountpoint() + '/jail.pid'

    def zfs_fstab_path(self):
        """Get fstab path"""
        return self.zfs_jail_mountpoint() + '/fstab'

    def zfs_jailconf_path(self):
        """Get jail.conf path"""
        return self.zfs_jail_mountpoint() + '/jail.conf'

    def zfs_jail_pool(self):
        """Get jail ZFS pool"""
        return self.__zfspool + '/jails/' + self.name

    def zfs_jail_mountpoint(self):
        """Get jail ZFS mountpoint"""
        return self.__mountpoint + '/jails/' + self.name

    def zfs_root_pool(self):
        """Get jail ZFS root pool"""
        return self.zfs_jail_pool() + '/root'

    def zfs_root_mountpoint(self):
        """Get jail ZFS root mountpoint"""
        return self.zfs_jail_mountpoint() + '/root'

    def destroy_pools(self):
        """Destroy jail ZFS pools"""
        zfs.destroy(self.zfs_root_pool())
        zfs.destroy(self.zfs_jail_pool())

    def create_pools(self):
        """Create jail ZFS pools"""
        zfs.create(self.zfs_jail_pool(), self.zfs_jail_mountpoint())
        zfs.create(self.zfs_root_pool(), self.zfs_root_mountpoint())

    def sync_defaults(self):
        """Sync default filesystem structure"""

        zfs.run_command(f"rsync -av {self.__mountpoint}/defaults/ {self.zfs_root_mountpoint()}")

    def create_fstab(self):
        """Create fstab for jail"""
        s = ''

        for fs in FSLIST:
            s += f"/{fs} {self.zfs_root_mountpoint()}/{fs} nullfs ro 0 0\n"

        zfs.write_to_file(self.zfs_fstab_path(),s)




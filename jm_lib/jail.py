import os
import jm_lib.zfs as zfs
import jailconf
import json

DEBUGCFG = True
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

    def __init__(self, name, config):
        self.config = {}
        self.name = name
        self.jconf = None
        self.__zfspool = config['MAIN']['zfspool']
        self.__mountpoint = config['MAIN']['mountpoint']

    def create(self, args):
        for attr in ['interface', 'addr', 'hostname', 'boot']:
            if attr in vars(args):
                if not vars(args)[attr] is None:
                    self.config[attr] = vars(args)[attr]

        self.create_pools()
        self.sync_defaults()
        self.create_fstab()

    def destroy(self):
        self.destroy_pools()
        os.rmdir(self.zfs_jail_mountpoint())

    def load(self, config):
        self.config = config[self.name]

    def create_jailconf(self):
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

        if 'interface' in self.config:
            self.jconf[self.name]['interface'] = self.config['interface']

        if 'addr' in self.config:
            self.jconf[self.name]['ip4.addr'] = self.config['addr']

        if 'hostname' in self.config:
            self.jconf[self.name]['host.hostname'] = self.config['hostname']

        zfs.write_to_file(self.zfs_jailconf_path(), self.jconf.dumps())

    def get_config(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return '-'

    def status(self):
        if self.jid_exists():
            if self.jls_getid() == None:
                return 2
            else:
                return 1
        else:
            return 0

    def jid_exists(self):
        return os.path.exists(self.zfs_jid_path())

    def jls_getid(self):
        jailid = None

        jlist = json.load(os.popen("jls -v --libxo json"))

        for jent in jlist["jail-information"]["jail"]:
            if jent["name"] == self.name:
                jailid = jent["jid"]

        return jailid

    def start(self):
        zfs.run_command(f"jail -c -f {self.zfs_jailconf_path()}")

        jailid = self.jls_getid()

        if jailid is None:
            print(f"Jail {self.name} failed to start!")
            return -1

        with open(self.zfs_jid_path(), 'w') as f:
            f.write(str(jailid))

    def console(self):
        if self.jid() == "-":
            return

        zfs.run_command(f"jexec {self.jid()} /bin/csh -l")

    def exec(self, cmd):
        if self.jid() == "-":
            return

        cmdline = " ".join(cmd)

        zfs.run_command(f"jexec {self.jid()} {cmdline}")

    def stop(self):
        if self.jid() == "-":
            return

        zfs.run_command(f"jexec {self.jid()} /bin/sh /etc/rc.shutdown")
        zfs.run_command(f"jail -r {self.jid()}")

        os.remove(self.zfs_jid_path())
        os.remove(self.zfs_jailconf_path())

        zfs.run_command(f"umount {self.zfs_root_mountpoint()}/dev/fd")
        zfs.run_command(f"umount {self.zfs_root_mountpoint()}/dev")

        for fs in FSLIST:
            zfs.run_command(f"umount {self.zfs_root_mountpoint()}/{fs}")


    def jid(self):
        rv = "-"

        if self.jid_exists():
            with open(self.zfs_jid_path(), 'r') as f:
                rv = f.read().replace('\n','')

        return rv

    def zfs_jid_path(self):
        return self.zfs_jail_mountpoint() + '/jail.pid'

    def zfs_fstab_path(self):
        return self.zfs_jail_mountpoint() + '/fstab'

    def zfs_jailconf_path(self):
        return self.zfs_jail_mountpoint() + '/jail.conf'

    def zfs_jail_pool(self):
        return self.__zfspool + '/jails/' + self.name

    def zfs_jail_mountpoint(self):
        return self.__mountpoint + '/jails/' + self.name

    def zfs_root_pool(self):
        return self.zfs_jail_pool() + '/root'

    def zfs_root_mountpoint(self):
        return self.zfs_jail_mountpoint() + '/root'

    def destroy_pools(self):
        zfs.destroy(self.zfs_root_pool())
        zfs.destroy(self.zfs_jail_pool())

    def create_pools(self):
        zfs.create(self.zfs_jail_pool(), self.zfs_jail_mountpoint())
        zfs.create(self.zfs_root_pool(), self.zfs_root_mountpoint())

    def sync_defaults(self):
        zfs.run_command(f"rsync -av {self.__mountpoint}/defaults/ {self.zfs_root_mountpoint()}")

    def create_fstab(self):
        s = ''

        for fs in FSLIST:
            s += f"/{fs} {self.zfs_root_mountpoint()}/{fs} nullfs ro 0 0\n"

        zfs.write_to_file(self.zfs_fstab_path(),s)




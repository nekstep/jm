import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig

args = None
cfg = None

def parser(p):
    p.add_argument('zfspool')
    p.add_argument('mountpoint')

def validate():
    if os.path.exists(args.mountpoint):
        print(f"Mountpoint {args.mountpoint} already exists!")
        return False

    if args.zfspool in zfs.list():
        print(f"ZFS pool {args.zfspool} already exists!")
        return False

    return True


def run(in_args):
    global args
    global config

    args = in_args
    cfg = jmConfig()

    if cfg.exists:
        print (f"Config {cfg.configfile} already present!")
        return -1

    if not validate():
        return -1

    zfs.create(args.zfspool, args.mountpoint)
    zfs.create(args.zfspool + '/jails', args.mountpoint + '/jails')
    zfs.create(args.zfspool + '/defaults', args.mountpoint + '/defaults')

    cfg.params['MAIN'] = {
            'zfspool': args.zfspool,
            'mountpoint': args.mountpoint }

    cfg.save()


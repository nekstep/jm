import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

args = None
cfg = None

def parser(p):
    p.add_argument('name')

def validate():
    if not args.name in cfg.params.sections():
        print(f"Jail {args.name} does not exist!")
        return False

    return True

def start_jail(name):
    jail = jmJail(name, cfg.params)
    jail.load(cfg.params)

    status = jail.status()

    if status == 1:
        print (f"Jail {jail.name} is already running as {jail.jid()}")
        return -1

    if status == 2:
        jail.stop()

    jail.create_jailconf()

    jail.start()

    print("Started: %s" % jail.jid())


def run(in_args):
    global args
    global cfg

    args = in_args
    cfg = jmConfig()

    if not cfg.exists:
        print (f"Config {cfg.configfile} absent!")
        return -1

    cfg.load()

    if args.name == "ALL":
        order = cfg.bootorder()

        for name in order:
            start_jail(name)

    else:
        if not validate():
            return -1

        start_jail(args.name)



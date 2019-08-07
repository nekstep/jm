import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

args = None
cfg = None

def parser(p):
    p.add_argument('name')
    p.add_argument('-a', '--addr')
    p.add_argument('-i', '--interface')
    p.add_argument('-n', '--hostname')
    p.add_argument('-b', '--boot', default="no")

def validate():
    if args.name in cfg.params.sections():
        print(f"Jail {args.name} already exists!")
        return False

    return True


def run(in_args):
    global args
    global cfg

    args = in_args
    cfg = jmConfig()

    if not cfg.exists:
        print (f"Config {cfg.configfile} absent!")
        return -1

    cfg.load()

    if not validate():
        return -1

    jail = jmJail(args.name, cfg.params)
    jail.create(args)

    cfg.params[jail.name] = jail.config
    cfg.save()

    print(f"Created {jail.name}")


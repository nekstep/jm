import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

args = None
cfg = None

def parser(p):
    p.add_argument('-b', '--boot', action='store_true')
    p.add_argument('-r', '--running', action='store_true')
    p.add_argument('-s', '--shutdown', action='store_true')

def validate():
    return True

def run_str(value):
    if value:
        return "running"
    else:
        return "stopped"

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

    print("R %-15s %-15s %4s %4s %s" % ('NAME', 'IP', 'JID', 'BOOT', 'HOSTNAME'))
    jlist = []

    if args.boot:
        jlist = cfg.bootorder()
    elif args.shutdown:
        jlist = cfg.shutorder()
    else:
        jlist = cfg.jaillist()

    for name in jlist:
        jail = jmJail(name, cfg.params)
        jail.load(cfg.params)

        if args.running and not jail.jid_exists():
            continue

        print("%s %-15s %-15s %4s %4s %s" % (
            (' ', '*')[jail.jid_exists()],
            name,
            jail.get_config('addr'),
            jail.jid(),
            jail.get_config('boot').replace('no','-'),
            jail.get_config('hostname')
            ));



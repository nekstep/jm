import os

DEBUG_ZFS = False

def run_command(cmd):
    if DEBUG_ZFS:
        print("DEBUGZFS: %s" % cmd)
    else:
        os.system(cmd)

def write_to_file(filename, s):
    if DEBUG_ZFS:
        print("DEBUGZFS: write to %s" % filename)
        print(s)
    else:
        f = open(filename, "w")
        f.write(s)
        f.close()

def list():
    zfslist = {}

    for str in os.popen('zfs list'):
        arr = str.split()
        zfslist[arr[0]] = arr[4]

    return zfslist

def create(pool, mount):
    run_command(f"zfs create -o mountpoint={mount} {pool}");

def destroy(pool):
    run_command(f"zfs destroy {pool}");


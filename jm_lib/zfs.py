import os

DEBUG_ZFS = False

def run_command(cmd):
    """Run os command

    Parameters
    ----------
    cmd : string
        Command to run
    """

    if DEBUG_ZFS:
        print("DEBUGZFS: %s" % cmd)
    else:
        os.system(cmd)

def write_to_file(filename, s):
    """Write to file

    Parameters
    ----------
    filename : string
        File to write
    s : string
        Data to write
    """

    if DEBUG_ZFS:
        print("DEBUGZFS: write to %s" % filename)
        print(s)
    else:
        f = open(filename, "w")
        f.write(s)
        f.close()

def list():
    """Get list of ZFS pools with mountpoints

    Returns
    -------
    map
        All ZFS pools in system with mountpoints
    """

    zfslist = {}

    for str in os.popen('zfs list'):
        arr = str.split()
        zfslist[arr[0]] = arr[4]

    return zfslist

def create(pool, mount):
    """Create ZFS pool

    Parameters
    ----------
    pool : string
        ZFS pool name
    mount : string
        ZFS pool mountpoint
    """

    run_command(f"zfs create -o mountpoint={mount} {pool}");

def destroy(pool):
    """Destroy ZFS pool

    Parameters
    ----------
    pool : string
        ZFS pool name
    """

    run_command(f"zfs destroy {pool}");


'''module to get system stats'''
import os
import platform

import psutil

# Ignore the following FS name
IGNORE_FSNAME = ('', 'none', 'gvfs-fuse-daemon', 'fusectl', 'cgroup')

# Ignore the following FS type
IGNORE_FSTYPE = ('binfmt_misc', 'devpts', 'iso9660', 'none', 'proc', 'sysfs',
                    'usbfs', 'rootfs', 'autofs', 'devtmpfs')

def get_fs_delta(old, new):
    '''return the delta between two fs interface readings'''
    return _calculate_delta(old, new, "size", "used", "avail")

def get_fs_stats_delta(old, new):
    '''return the delta between two stats from get_fs_stats'''
    delta = {}

    for name in new:
        if name in old:
            delta[name] = get_fs_delta(old[name], new[name])
            delta[name]["type"] = new[name]["type"]
            delta[name]["mnt_point"] = new[name]["mnt_point"]

    return delta

def get_fs_stats(ignore_fsname=IGNORE_FSNAME, ignore_fstype=IGNORE_FSTYPE):
    '''get file system stats'''
    # Reset the list
    filesystems = {}

    # Open the current mounted FS
    fs_stats = psutil.disk_partitions(True)
    for fs_stat in fs_stats:
        if fs_stat.device in ignore_fsname or fs_stat.fstype in ignore_fstype:
            continue

        fs_current = {}
        fs_current['type'] = fs_stat.fstype
        fs_current['mnt_point'] = fs_stat.mountpoint

        try:
            fs_usage = psutil.disk_usage(fs_stat.mountpoint)

            fs_current['size']  = fs_usage.total
            fs_current['used']  = fs_usage.used
            fs_current['avail'] = fs_usage.free

        except OSError:
            fs_current['size']  = -1
            fs_current['used']  = -1
            fs_current['avail'] = -1

        filesystems[fs_stat.device] = fs_current

    return filesystems

def get_platform_info():
    '''return platform information'''
    host = {}
    host['os'] = platform.system()
    host['hostname'] = platform.node()
    host['platform'] = platform.architecture()[0]

    is_archlinux = os.path.exists(os.path.join("/", "etc", "arch-release"))

    if host['os'] == "Linux":
        if is_archlinux:
            host['distro'] = "Arch Linux"
        else:
            distro = platform.linux_distribution()
            host['distro'] = " ".join(distro[:2])

        host['version'] = platform.release()
    elif host['os'] == "FreeBSD":
        host['version'] = platform.release()
    elif host['os'] == "Darwin":
        host['version'] = platform.mac_ver()[0]
    elif host['os'] == "Windows":
        version = platform.win32_ver()
        host['version'] = " ".join(version[::2])
    else:
        host['version'] = ""

    return host

def _calculate_cpu_stats(cputime):
    '''return stats for a cpu'''
    base = {
        'kernel': cputime.system,
        'user': cputime.user,
        'idle': cputime.idle
    }

    if hasattr(cputime, 'nice'):
        base['nice'] = cputime.nice

    return base

def _calculate_delta(old, new, *names):
    '''calculate the delta between old and new field *names*'''
    delta = {}

    for name in names:
        if name in old and name in new:
            delta[name] = new[name] - old[name]

    return delta

def get_cpu_delta(old, new):
    '''calculate the delta for cpu stats of a single cpu'''
    return _calculate_delta(old, new, "kernel", "user", "idle", "nice")

def get_cpu_stats_delta(old, new):
    '''calculate the delta for the value returned by get_cpu_stats'''
    delta = {}

    delta["global"] = get_cpu_delta(old["global"], new["global"])
    delta["percpu"] = [get_cpu_delta(oldcpu, newcpu) for oldcpu, newcpu in
            zip(old["percpu"], new["percpu"])]

    return delta

def get_cpu_stats():
    '''return cpu stats'''
    cputime = psutil.cpu_times()

    cpu = _calculate_cpu_stats(cputime)

    percpu = [_calculate_cpu_stats(val) for val in
                psutil.cpu_times(percpu=True)]

    return {
        "global": cpu,
        "percpu": percpu
    }

def get_load_stats():
    '''return load stats'''
    avg1m, avg5m, avg15m = os.getloadavg()

    return {
        'avg1m': avg1m,
        'avg5m': avg5m,
        'avg15m': avg15m
    }

def get_mem_delta(old, new):
    '''return the delta between two mem readings'''
    return _calculate_delta(old, new, "cache", "total", "used", "free",
                            "percent")

def get_mem_stats_delta(old, new):
    '''return the delta between two get_mem_stats values'''
    delta = {}

    delta["mem"] = get_mem_delta(old["mem"], new["mem"])
    delta["swap"] = get_mem_delta(old["swap"], new["swap"])
    delta["cache"] = new["cache"] - old["cache"]

    return delta

def get_mem_stats():
    '''return mem stats'''

    if hasattr(psutil, 'cached_phymem') and hasattr(psutil, 'phymem_buffers'):
        cachemem = psutil.cached_phymem() + psutil.phymem_buffers()
    else:
        cachemem = -1

    phymem = psutil.phymem_usage()
    mem = {
        'cache': cachemem,
        'total': phymem.total,
        'used': phymem.used,
        'free': phymem.free,
        'percent': phymem.percent
    }

    virtmem = psutil.virtmem_usage()
    memswap = {
        'total': virtmem.total,
        'used': virtmem.used,
        'free': virtmem.free,
        'percent': virtmem.percent
    }

    return {
        "cache": cachemem,
        "mem": mem,
        "swap": memswap
    }

def get_net_delta(old, new):
    '''return the delta between two net interface readings'''
    return _calculate_delta(old, new, "rb", "tb", "rc", "tc")

def get_net_stats_delta(old, new):
    '''return the delta between two stats from get_net_stats'''
    delta = {}

    for name in new:
        if name in old:
            delta[name] = get_net_delta(old[name], new[name])

    return delta

def get_net_stats():
    '''return network stats'''
    network = {}

    network_new = psutil.network_io_counters(True)

    for name, iface in network_new.items():
        netstat = {}
        netstat['rb'] = iface.bytes_recv
        netstat['tb'] = iface.bytes_sent
        netstat['rc'] = iface.packets_recv
        netstat['tc'] = iface.packets_sent

        network[name] = netstat

    return network

def get_disk_delta(old, new):
    '''return the delta between two disk interface readings'''
    return _calculate_delta(old, new, "rb", "wb", "rc", "wc", "rt", "wt")

def get_disk_stats_delta(old, new):
    '''return the delta between two stats from get_disk_stats'''
    delta = {}

    for name in new:
        if name in old:
            delta[name] = get_disk_delta(old[name], new[name])

    return delta

def get_disk_stats():
    '''return diskio stats'''
    diskios = {}

    diskio = psutil.disk_io_counters(True)

    for name, diskio in diskio.items():
        diskstat = {}

        diskstat['rb'] = diskio.read_bytes
        diskstat['wb'] = diskio.write_bytes
        diskstat['rc'] = diskio.read_count
        diskstat['wc'] = diskio.write_count
        diskstat['rt'] = diskio.read_time
        diskstat['wt'] = diskio.write_time

        diskios[name] = diskstat

    return diskios

TITLE_LEVELS = ["=", "-", ".", ":", "+"]

def print_title(title, underline="-"):
    '''print a title'''
    print title
    print underline * len(title)

def pretty_print(title, data, level=0):
    '''pretty print a generic stas dict'''
    underline = TITLE_LEVELS[level] if level < len(TITLE_LEVELS) else "/"

    print_title(title, underline)
    print

    for key, value in data.items():
        if isinstance(value, dict):
            pretty_print(key, value, level + 1)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                pretty_print("%s %d" % (key, i), item, level + 1)
        else:
            print key + ":", value

    print

def main():
    '''main function that displays the current values and deltas'''
    import time

    cpu  = get_cpu_stats()
    mem  = get_mem_stats()
    net  = get_net_stats()
    disk = get_disk_stats()
    fst  = get_fs_stats()

    platinfo = get_platform_info()

    pretty_print("Platform", platinfo)
    pretty_print("CPU", cpu)
    pretty_print("Memory", mem)
    pretty_print("Net", net)
    pretty_print("Disk", disk)
    pretty_print("File System", fst)

    while True:
        time.sleep(5)

        new_cpu  = get_cpu_stats()
        new_mem  = get_mem_stats()
        new_net  = get_net_stats()
        new_disk = get_disk_stats()
        new_fst  = get_fs_stats()

        cpu_diff  = get_cpu_stats_delta(cpu, new_cpu)
        mem_diff  = get_mem_stats_delta(mem, new_mem)
        net_diff  = get_net_stats_delta(net, new_net)
        disk_diff = get_disk_stats_delta(disk, new_disk)
        fst_diff  = get_fs_stats_delta(fst, new_fst)

        pretty_print("CPU diff", cpu_diff)
        pretty_print("Memory diff", mem_diff)
        pretty_print("Net diff", net_diff)
        pretty_print("Disk diff", disk_diff)
        pretty_print("File System diff", fst_diff)

        cpu  = new_cpu
        mem  = new_mem
        net  = new_net
        disk = new_disk
        fst  = new_fst

if __name__ == "__main__":
    main()

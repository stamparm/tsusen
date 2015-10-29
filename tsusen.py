import datetime
import os
import re
import socket
import struct
import subprocess
import time

try:
    import pcapy
except ImportError:
    if subprocess.mswindows:
        exit("[!] please install Pcapy (e.g. 'https://breakingcode.wordpress.com/?s=pcapy') and WinPcap (e.g. 'http://www.winpcap.org/install/')")
    else:
        exit("[!] please install Pcapy (e.g. 'apt-get install python-pcapy')")

_auxiliary = {}
_cap = None
_datalink = None
_traffic = {}

CAPTURE_FILTER = "(tcp[13] == 2) or not tcp"  # SYN or not TCP
MONITOR_INTERFACE = "any"
SNAP_LEN = 100
IPPROTO = 8
ETH_LENGTH = 14
LAST_FILENAME = None
LAST_WRITE = None
WRITE_PERIOD = 60 * 15
IPPROTO_LUT = dict(((getattr(socket, _), _.replace("IPPROTO_", "")) for _ in dir(socket) if _.startswith("IPPROTO_")))
LOCAL_ADDRESSES = []
BLACKLISTED_ADDRESSES = ("255.255.255.255", "127.0.0.1", "0.0.0.0")
DATE_FORMAT = "%Y-%m-%d"
RESULTS_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(__file__), "./results"))

def _log_write(force=False, filename=None):
    global LAST_FILENAME
    global LAST_WRITE

    current = time.time()
    filename = filename or os.path.join(RESULTS_DIRECTORY, "%s.csv" % datetime.date.today().strftime(DATE_FORMAT))

    if LAST_WRITE is None:
        LAST_WRITE = current

    if LAST_FILENAME is None:
        LAST_FILENAME = filename

    if force or (current - LAST_WRITE) > WRITE_PERIOD:
        if not os.path.isdir(RESULTS_DIRECTORY):
            os.makedirs(RESULTS_DIRECTORY)

        with open(filename, "w+b") as f:
            results = []
            f.write("proto dst_port src_ip dst_ip timestamp\n")

            for key in _traffic:
                proto, dst_ip, dst_port = key.split(":")
                for src_ip in sorted(_traffic[key]):
                    sec = _auxiliary["%s:%s" % (key, src_ip)]
                    results.append((sec, (proto, dst_port, src_ip, dst_ip)))

            for sec, entry in sorted(results):
                f.write("%s %s\n" % (" ".join(str(_) for _ in entry), sec))

        LAST_WRITE = current

    if LAST_FILENAME != filename:
        if not force and LAST_WRITE != current:
            _log_write(True, LAST_FILENAME)

        LAST_FILENAME = filename

        _traffic.clear()
        _auxiliary.clear()

def _process_packet(packet, sec, usec):
    try:
        if _datalink == pcapy.DLT_LINUX_SLL:
            packet = packet[2:]

        eth_header = struct.unpack("!HH8sH", packet[:ETH_LENGTH])
        eth_protocol = socket.ntohs(eth_header[3])

        if eth_protocol == IPPROTO:  # IP
            ip_header = struct.unpack("!BBHHHBBH4s4s", packet[ETH_LENGTH:ETH_LENGTH + 20])
            ip_length = ip_header[2]
            packet = packet[:ETH_LENGTH + ip_length]  # truncate
            iph_length = (ip_header[0] & 0xF) << 2
            protocol = ip_header[6]
            src_ip = socket.inet_ntoa(ip_header[8])
            dst_ip = socket.inet_ntoa(ip_header[9])

            proto = IPPROTO_LUT.get(protocol)

            if proto is None:
                return

            # only process SYN packets
            if protocol == socket.IPPROTO_TCP:  # TCP
                i = iph_length + ETH_LENGTH
                src_port, dst_port, _, _, doff_reserved, flags = struct.unpack("!HHLLBB", packet[i:i + 14])
                if flags == 2:  # SYN set (only)
                    local_src = False
                    for prefix, mask in LOCAL_ADDRESSES:
                        if addr_to_int(src_ip) & mask == prefix:
                            local_src = True
                            break
                    if not local_src and dst_ip not in BLACKLISTED_ADDRESSES:
                        key = "%s:%s:%s" % (proto, dst_ip, dst_port)
                        if key not in _traffic:
                            _traffic[key] = set()
                        _traffic[key].add(src_ip)
                        _auxiliary["%s:%s" % (key, src_ip)] = sec

            else:
                if protocol == socket.IPPROTO_UDP:  # UDP
                    i = iph_length + ETH_LENGTH
                    _ = packet[i:i + 4]
                    if len(_) < 4:
                        return

                    src_port, dst_port = struct.unpack("!HH", _)
                else:                               # non-TCP/UDP (e.g. ICMP)
                    src_port, dst_port = '-', '-'

                flow = tuple(sorted((addr_to_int(src_ip), src_port, addr_to_int(dst_ip), dst_port)))
                if flow not in _auxiliary:
                    _auxiliary[flow] = True
                    local_src = False
                    for prefix, mask in LOCAL_ADDRESSES:
                        if addr_to_int(src_ip) & mask == prefix:
                            local_src = True
                            break
                    if not local_src and dst_ip not in BLACKLISTED_ADDRESSES:
                        key = "%s:%s:%s" % (proto, dst_ip, dst_port)
                        if key not in _traffic:
                            _traffic[key] = set()
                        _traffic[key].add(src_ip)
                        _auxiliary["%s:%s" % (key, src_ip)] = sec

    except KeyboardInterrupt:
        raise

    except Exception:
        pass

    finally:
        _log_write()

def packet_handler(header, packet):
    try:
        sec, usec = header.getts()
        _process_packet(packet, sec, usec)
    except socket.timeout:
        pass

def addr_to_int(value):
    _ = value.split('.')
    return (long(_[0]) << 24) + (long(_[1]) << 16) + (long(_[2]) << 8) + long(_[3])

def int_to_addr(value):
    return '.'.join(str(value >> n & 0xFF) for n in (24, 16, 8, 0))

def make_mask(bits):
    return 0xffffffff ^ (1 << 32 - bits) - 1

def local_addresses():
    items = []

    for cmd, regex in (("ifconfig", r"inet addr:([\d.]+) .*Mask:([\d.]+)"), ("ipconfig", r"IPv4 Address[^\n]+([\d.]+)\s+Subnet Mask[^\n]+([\d.]+)")):
        try:
            items = re.findall(regex, subprocess.check_output(cmd))
            break
        except:
            pass

    for ip, mask in items:
        LOCAL_ADDRESSES.append((addr_to_int(ip) & addr_to_int(mask), addr_to_int(mask)))

def main():
    global _cap
    global _datalink

    local_addresses()

    print "[i] opening interface '%s'" % MONITOR_INTERFACE
    try:
        _cap = pcapy.open_live(MONITOR_INTERFACE, SNAP_LEN, True, 0)
    except socket.error, ex:
        if "permitted" in str(ex):
            exit("\n[x] please run with sudo/Administrator privileges")
        elif "No such device" in str(ex):
            exit("\n[x] no such device '%s'" % MONITOR_INTERFACE)
        else:
            raise

    if CAPTURE_FILTER:
        print "[i] setting filter '%s'" % CAPTURE_FILTER
        _cap.setfilter(CAPTURE_FILTER)

    _datalink = _cap.datalink()
    if _datalink not in (pcapy.DLT_EN10MB, pcapy.DLT_LINUX_SLL):
        exit("[x] datalink type '%s' not supported" % _datalink)

    try:
        _cap.loop(-1, packet_handler)
    except KeyboardInterrupt:
        print "\r[x] Ctrl-C pressed"
        _log_write(True)

if __name__ == "__main__":
    main()

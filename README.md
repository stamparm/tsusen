# tsusen [![Python 2.6|2.7](https://img.shields.io/badge/python-2.6|2.7-blue.svg)](https://www.python.org/) [![Dependencies pcapy](https://img.shields.io/badge/dependencies-pcapy-yellow.svg)](https://github.com/CoreSecurity/pcapy) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/stamparm/maltrail#license-mit)

![Logo](http://i.imgur.com/hH1cr49.png)

**tsusen** (&#27941;&#27874;&#12475;&#12531;&#12469;&#12540;) is a standalone network sensor made for gathering information from the regular traffic coming from the outside (i.e. Internet) on a daily basis (e.g. mass-scans, service-scanners, etc.). Any disturbances should be closely watched for as those can become a good prediction base of forthcoming events. For example, exploitation of a newly found web service vulnerability (e.g. [Heartbleed](http://heartbleed.com/)) should generate a visible "spike" of total number of (potential) attackers on affected network port.

Sensor's results are stored locally in CSV files on a daily basis (e.g. `2015-10-27.csv`) with periodic (flush) write of current day's data (e.g. every 15 minutes). Sample results are as follows:

```
TCP 1080 192.165.67.186 222.186.56.107 1446188056 1446188056 1
TCP 1080 192.165.67.186 64.125.239.78 1446191096 1446191096 1
TCP 1081 192.165.67.186 111.248.100.185 1446175412 1446175412 1
TCP 1081 192.165.67.186 111.248.102.150 1446183374 1446183374 1
TCP 1081 192.165.67.186 36.225.254.129 1446170512 1446170512 1
TCP 1095 192.165.67.186 36.229.233.199 1446177047 1446177047 1
TCP 111 192.165.67.186 80.82.65.219 1446181028 1446181028 1
TCP 111 192.165.67.186 94.102.52.44 1446181035 1446181035 1
TCP 11122 192.165.67.186 222.186.56.39 1446198391 1446198391 1
TCP 11211 192.165.67.186 74.82.47.43 1446200598 1446200598 1
TCP 135 192.165.67.186 1.160.12.156 1446163293 1446163294 3
TCP 135 192.165.67.186 104.174.148.124 1446178211 1446178212 3
TCP 135 192.165.67.186 106.242.5.179 1446180063 1446180064 3
TCP 135 192.165.67.186 173.30.55.76 1446184279 1446195229 6
TCP 135 192.165.67.186 174.100.28.2 1446179470 1446202911 9
TCP 135 192.165.67.186 218.253.225.163 1446174945 1446195646 9
TCP 135 192.165.67.186 219.114.66.114 1446169303 1446183947 6
TCP 135 192.165.67.186 222.186.56.43 1446165515 1446202626 5
...
```

where `proto` (e.g. in first entry this is `TCP`) represents the protocol that has been used by initiator coming from `src_ip` (e.g. in first entry this is `115.231.222.40`) toward our `<dst_ip:dst_port>` (e.g. in first entry this is `192.165.57.46:8080`) service, while the `timestamp` represents the time of (that day's first) connection attempt represented in Unix [timestamp](http://www.onlineconversion.com/unix_time.htm) format (e.g. in first entry this is `1446042553`, which stands for `Wed, 28 Oct 2015 14:29:13 GMT`).

# tsusen [![Python 2.6|2.7](https://img.shields.io/badge/python-2.6|2.7-blue.svg)](https://www.python.org/) [![Dependencies pcapy](https://img.shields.io/badge/dependencies-pcapy-yellow.svg)](https://github.com/CoreSecurity/pcapy) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/stamparm/maltrail#license-mit)

![Logo](http://i.imgur.com/hH1cr49.png)

**tsusen** is a standalone sensor made for gathering information from the regular network traffic coming from the outside on a daily basis (e.g. mass-scans, service-scanners, etc.). Any disturbances should be closely watched for as those can become a good prediction base of forthcoming events. For example, exploitation of a newly found web service vulnerability (e.g. [Heartbleed](http://heartbleed.com/)) should generate a visible "spike" of total number of (potential) attackers on affected network port.

Sensor's results are stored locally in CSV files on a daily basis (e.g. `2015-10-27.csv`) with periodic (flush) write of current day's data (e.g. every 15 minutes). File's structure is as follows:

```
proto dst_port src_ip dst_ip timestamp
...
TCP 80 89.233.107.5 192.166.17.63 1446040782   # just a sample record
...
```

where `proto` represents the protocol that has been used by initiator coming from `src_ip` (in this case `89.233.107.5`) toward our `<dst_ip:dst_port>` (in this case `192.166.17.63:80`) service, while the `timestamp` represents the time of (that day's first) connection attempt represented in Unix [timestamp](http://www.onlineconversion.com/unix_time.htm) format (in this case `1446040782` stands for `Wed, 28 Oct 2015 13:59:42 GMT`).

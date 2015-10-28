# tsusen [![Python 2.6|2.7](https://img.shields.io/badge/python-2.6|2.7-blue.svg)](https://www.python.org/) [![Dependencies pcapy](https://img.shields.io/badge/dependencies-pcapy-yellow.svg)](https://github.com/CoreSecurity/pcapy) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/stamparm/maltrail#license-mit)

![Logo](http://i.imgur.com/hH1cr49.png)

**tsusen** is a standalone sensor made for gathering information from the regular network traffic coming from the outside on a daily basis (e.g. mass-scans, service-scanners, etc.). Any disturbances should be closely watched for as those can become a good prediction base of forthcoming events. For example, exploitation of a newly found web service vulnerability (e.g. [Heartbleed](http://heartbleed.com/)) should generate a visible "spike" of total number of (potential) attackers on affected network port.

Sensor's results are stored locally in CSV files on a daily basis (e.g. `2015-10-27.csv`) with periodic (flush) write of current day's data (e.g. every 15 minutes). Sample results are as follows:

```
proto dst_port src_ip dst_ip timestamp
TCP 8080 115.231.222.40 192.165.57.46 1446042553
ICMP - 172.15.206.3 192.165.57.46 1446042324
ICMP - 177.38.33.166 192.165.57.46 1446042667
ICMP - 198.210.119.35 192.165.57.46 1446041727
ICMP - 208.104.81.34 192.165.57.46 1446040945
ICMP - 212.234.83.216 192.165.57.46 1446043137
ICMP - 24.249.35.22 192.165.57.46 1446043333
ICMP - 46.161.40.37 192.165.57.46 1446042429
ICMP - 66.112.205.3 192.165.57.46 1446043347
ICMP - 68.150.97.129 192.165.57.46 1446040871
ICMP - 70.29.19.14 192.165.57.46 1446041791
ICMP - 74.41.223.144 192.165.57.46 1446041698
TCP 119 85.25.103.50 192.165.57.46 1446043192
TCP 135 24.249.35.22 192.165.57.46 1446043334
TCP 135 66.112.205.3 192.165.57.46 1446043348
TCP 135 68.150.97.129 192.165.57.46 1446040873
TCP 135 70.29.19.14 192.165.57.46 1446041793
UDP 161 15.76.167.176 192.165.57.46 1446041530
UDP 161 185.94.111.1 192.165.57.46 1446043430
TCP 1433 222.186.56.43 192.165.57.46 1446040887
TCP 1433 222.186.61.8 192.165.57.46 1446042842
TCP 22 43.229.53.19 192.165.57.46 1446042659
TCP 22 85.114.40.90 192.165.57.46 1446042392
TCP 23 120.60.203.19 192.165.57.46 1446041664
TCP 23 121.11.56.100 192.165.57.46 1446041421
TCP 23 46.161.40.37 192.165.57.46 1446042429
TCP 23 5.141.213.109 192.165.57.46 1446041983
TCP 23 78.165.174.63 192.165.57.46 1446041152
TCP 23 93.172.149.191 192.165.57.46 1446042997
TCP 3389 89.248.174.117 192.165.57.46 1446043378
TCP 8102 188.138.75.83 192.165.57.46 1446043238
TCP 80 115.239.248.245 192.165.57.46 1446042251
TCP 80 184.105.247.207 192.165.57.46 1446041108
TCP 80 85.114.40.90 192.165.57.46 1446042452
...
...
```

where `proto` represents the protocol that has been used by initiator coming from `src_ip` (in first entry `115.231.222.40`) toward our `<dst_ip:dst_port>` (in first entry `192.165.57.46:8080`) service, while the `timestamp` represents the time of (that day's first) connection attempt represented in Unix [timestamp](http://www.onlineconversion.com/unix_time.htm) format (in first entry `1446042553` stands for `Wed, 28 Oct 2015 14:29:13 GMT`).

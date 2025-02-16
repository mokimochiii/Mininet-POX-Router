# Mininet-POX-Router
## USAGE
ONLY RUN THESE FILES IN MININET
Save topo.py in the root directory
Save controller.py in ~/pox/pox/misc
Start the topology with:
```bash
  sudo python topo.py
```
Start the controller with:
```bash
  sudo ~pox/pox.py log.level --packet=WARN misc.controller
```

## FIREWALL RULES
Rule 1: ICMP traffic is forwarded only between:
 - IT Department subnets and the Faculty LAN
 - IT Department subnets and  the Student Housing LAN
 - devices that are on the same subnet

Rule 2: TCP traffic is forwarded only between:
 - the University Data Center, IT Department and Faculty LAN
 - the University Data Center, Student Housing LAN, the trustedPCs, guest
 - Devices that are on the same subnet
 - The printer only prints using TCP.
 - Exception: Only the Faculty LAN may access the Faculty Exam Server

Rule 3: UDP traffic is forwarded only between:
 - The University Data Center, IT Department, Faculty LAN and the Student Housing LAN
 - devices that are on the same subnet

Rule 4: Guest hosts (“guest”) are allowed to use the printer
 - Think about the protocol behind file uploading and printer info in Rule 2.

Rule 5: All other traffic should be dropped.

Added Rule 6:
 - Only Student Housing LAN can communicate with the Discord Server (dServer)


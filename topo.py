#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController

class MyTopology(Topo):
  def __init__(self):
    Topo.__init__(self)

    #Faculty LAN
    facultyWS = self.addHost('facultyws', ip='169.233.3.10/24', defaultRoute='facultyws-eth1')
    printer = self.addHost('printer', ip='169.233.3.20/24', defaultRoute='printer-eth1')
    facultyPC = self.addHost('facultypc', ip='169.233.3.30/24', defaultRoute='facultypc-eth1')
    facultySwitch = self.addSwitch('s2')

    self.addLink(facultyWS, facultySwitch, port1=1, port2=4)
    self.addLink(printer, facultySwitch, port1=1, port2=3)
    self.addLink(facultyPC, facultySwitch, port1=1, port2=1)

    #Student Housing LAN
    studentPC1 = self.addHost('studentpc1', ip='169.233.4.1/24', defaultRoute='studentpc1-eth1')
    studentPC2 = self.addHost('studentpc2', ip='169.233.4.2/24', defaultRoute='studentpc2-eth1')
    labWS = self.addHost('labws', ip='169.233.4.100/24', defaultRoute='labws-eth1')
    studentSwitch = self.addSwitch('s3')

    self.addLink(studentPC1, studentSwitch, port1=1, port2=1)
    self.addLink(studentPC2, studentSwitch, port1=1, port2=4)
    self.addLink(labWS, studentSwitch, port1=1, port2=2)

    #IT Department LAN
    itBackup = self.addHost('itbackup', ip='169.233.1.30/24', defaultRoute='itbackup-eth1')
    itWS = self.addHost('itws', ip='169.233.1.10/24', defaultRoute='itws-eth1')
    itPC = self.addHost('itpc', ip='169.233.1.20/24', defaultRoute='itpc-eth1')
    itSwitch = self.addSwitch('s4')

    self.addLink(itBackup, itSwitch, port1=1, port2=3)
    self.addLink(itWS, itSwitch, port1=1, port2=2)
    self.addLink(itPC, itSwitch, port1=1, port2=1)

    #University Data Center
    examServer = self.addHost('examserver', ip='169.233.2.1/24', defaultRoute='examserver-eth1')
    webServer = self.addHost('webserver', ip='169.233.2.2/24', defaultRoute='webServer-eth1')
    dnsServer = self.addHost('dnsserver', ip='169.233.2.3/24', defaultRoute='dnsServer-eth1')
    dataCenterSwitch = self.addSwitch('s5')

    self.addLink(examServer, dataCenterSwitch, port1=1, port2=1)
    self.addLink(webServer, dataCenterSwitch, port1=1, port2=2)
    self.addLink(dnsServer, dataCenterSwitch, port1=1, port2=3)

    #Core Network
    coreSwitch = self.addSwitch('s1')

    self.addLink(facultySwitch, coreSwitch, port1=2, port2=2)
    self.addLink(studentSwitch, coreSwitch, port1=3, port2=3)
    self.addLink(itSwitch, coreSwitch, port1=4, port2=4)
    self.addLink(dataCenterSwitch, coreSwitch, port1=5, port2=5)

    #Internet Devices
    trustedPC1 = self.addHost('trustedpc1', ip='212.26.59.102/32', defaultRoute='trustedpc1-eth1')
    trustedPC2 = self.addHost('trustedpc2', ip='10.100.198.6/32', defaultRoute='trustedpc2-eth1')
    guest = self.addHost('guest', ip='10.100.198.10/32', defaultRoute='guest-eth1')
    dServer = self.addHost('dserver', ip='3.21.20.4/32', defaultRoute='dserver-eth1')

    self.addLink(trustedPC1, coreSwitch, port1=1, port2=6)
    self.addLink(trustedPC2, coreSwitch, port1=1, port2=7)
    self.addLink(guest, coreSwitch, port1=1, port2=8)
    self.addLink(dServer, coreSwitch, port1=1, port2=9)

if __name__ == '__main__':
  #This part of the script is run when the script is executed
  topo = MyTopology() #Creates a topology
  c0 = RemoteController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633) #Creates a remote controller
  net = Mininet(topo=topo, controller=c0) #Loads the topology
  net.start() #Starts mininet
  CLI(net) #Opens a command line to run commands on the simulated topology
  net.stop() #Stops mininet

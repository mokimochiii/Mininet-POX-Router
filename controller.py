from pox.core import core

import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Routing (object):
    
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_routing (self, packet, packet_in, port_on_switch, switch_id):
    # port_on_swtich - the port on which this packet was received
    # switch_id - the switch which received this packet

    def accept(output_port):
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.data = packet_in
      msg.idle_timeout = 60
      msg.hard_timeout = 300
      msg.buffer_id = packet_in.buffer_id

      msg.actions.append(of.ofp_action_output(port=output_port))

      self.connection.send(msg)
      print(f"Packet Accepted\r\n")
    
    def drop():
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet, packet_in.in_port)
      msg.buffer_id = packet_in.buffer_id
      self.connection.send(msg)
      print(f"Packet Dropped\r\n")

    def subnet(ipaddr):
      subnetmask_32 = ["212.26.59.102", "10.100.198.6", "10.100.198.10", "3.21.20.4"]
      if ipaddr in subnetmask_32:
        return ipaddr
      #24 bit subnet mask
      return ipaddr[:ipaddr.rfind(".")] + ".0"


    def is_same_subnet(srcaddr, dstaddr):
      subnetmask_32 = ["212.26.59.102", "10.100.198.6", "10.100.198.10", "3.21.20.4"]
      if srcaddr in subnetmask_32 or dstaddr in subnetmask_32:
        return False
      return srcaddr[:srcaddr.rfind(".")] == dstaddr[:dstaddr.rfind(".")]
    
    #subnet naming conventions
    it_subnet = "169.233.1.0"
    data_center_subnet = "169.233.2.0"
    faculty_subnet = "169.233.3.0"
    student_subnet = "169.233.4.0"
    trusted_pcs = ["212.26.59.102", "10.100.198.6"]
    guest = "10.100.198.10"
    exam_server = "169.233.2.1"
    printer = "169.233.3.20"
    dserver = "3.21.20.4"

    # IP/Subnet Mapping
    coreSwitch_mapping = {"169.233.3.0":2, "169.233.4.0":3, "169.233.1.0":4, "169.233.2.0":5, "212.26.59.102": 6, "10.100.198.6":7, "10.100.198.10":8, "3.21.20.4":9}
    coreSwitch_mapping_I = {value: key for key, value in coreSwitch_mapping.items()}
    it_mapping = {"169.233.1.20":1, "169.233.1.10":2, "169.233.1.30":3}
    data_center_mapping = {"169.233.2.1":1, "169.233.2.2":2, "169.233.2.3":3}
    faculty_mapping = {"169.233.3.30":1, "169.233.3.20":3, "169.233.3.10":4}
    student_mapping = {"169.233.4.1":1, "169.233.4.100":2, "169.233.4.2":4}

    #Switch naming conventions
    switch1 = 1
    switch2 = 2
    switch3 = 3
    switch4 = 4
    switch5 = 5

    #packet protocol headers
    arp_h = packet.find('arp')
    icmp_h = packet.find('icmp')
    ipv4_h = packet.find('ipv4')
    tcp_h = packet.find('tcp')
    udp_h = packet.find('udp')

    #flood all ARP 
    if arp_h:
      msg = of.ofp_packet_out()
      msg.data = packet_in
      msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
      self.connection.send(msg)
      return

    #the rest of the packets we will check should have ipv4
    if ipv4_h is None:
      drop()
      return
    
    srcaddr = str(ipv4_h.srcip)
    dstaddr = str(ipv4_h.dstip)

    #current subnet that the packet is in
    subnet_ip = coreSwitch_mapping_I.get(switch_id)
    if switch_id == switch1:
      output_port = coreSwitch_mapping[subnet(dstaddr)]
      if output_port is None:
        drop()
        return
    elif subnet_ip != subnet(dstaddr):
      output_port = coreSwitch_mapping[subnet_ip]
    else:
      if switch_id == switch2:
        output_port = faculty_mapping[dstaddr]
      if switch_id == switch3:
        output_port = student_mapping[dstaddr]
      if switch_id == switch4:
        output_port = it_mapping[dstaddr]
      if switch_id == switch5:
        output_port = data_center_mapping[dstaddr]

    if (dstaddr == dserver and subnet(srcaddr) == student_subnet) or \
      (srcaddr == dserver and subnet(dstaddr) == student_subnet):
      accept(output_port)
      return

    #Rule 1: ICMP traffic is forwarded only between:
    #        IT Department subnets and the Faculty LAN
    #        IT Department subnets and the Student Housing LAN
    #        Devices that are on the same subnet
    if icmp_h:
      if (subnet(srcaddr) == it_subnet and subnet(dstaddr) == faculty_subnet) or \
        (subnet(srcaddr) == it_subnet and subnet(dstaddr) == student_subnet):
         accept(output_port)
         return
      
      if (subnet(srcaddr) == faculty_subnet and subnet(dstaddr) == it_subnet) or \
        (subnet(srcaddr) == student_subnet and subnet(dstaddr) == it_subnet):
         accept(output_port)
         return
      
      if is_same_subnet(srcaddr, dstaddr):
        accept(output_port)
        return

    #Rule 2: TCP traffic is forwarded only between
    #        The University Data Center, IT Department and Faculty LAN
    #        The University Data Center, Student Housing LAN, the trustedPCs, guest
    #        Devices that are on the same subnet
    #        The printer only prints using TCP
    #        Exception: Only the Faculty LAN may access the Faculty Exam Server
    if tcp_h:
      if dstaddr == exam_server:
        if subnet(srcaddr) == faculty_subnet:
          accept(output_port)
        else:
          drop()

      if ((subnet(srcaddr) == it_subnet or subnet(srcaddr) == faculty_subnet or subnet(srcaddr) == data_center_subnet) and
          (subnet(dstaddr) == it_subnet or subnet(dstaddr) == faculty_subnet or subnet(dstaddr) == data_center_subnet)):
        accept(output_port)
        return
      
      if ((subnet(srcaddr) == student_subnet or subnet(srcaddr) == data_center_subnet or srcaddr in trusted_pcs or srcaddr == guest) and 
          (subnet(dstaddr) == student_subnet or subnet(dstaddr) == data_center_subnet or dstaddr in trusted_pcs or dstaddr == guest)):
        accept(output_port)
        return
      
      if is_same_subnet(srcaddr, dstaddr):
        accept(output_port)
        return

    #Rule 3: UDP traffic is forwarded only between
    #        The University Data Center, IT Department, Faculty LAN and the Student Housing LAN
    #        Devices that are on the same subnet
    if udp_h:
      if ((subnet(srcaddr) == it_subnet or subnet(srcaddr) == faculty_subnet  or subnet(srcaddr) == student_subnet  or subnet(srcaddr) == data_center_subnet ) and 
          (subnet(dstaddr) == it_subnet or subnet(dstaddr) == faculty_subnet or subnet(dstaddr) == student_subnet or subnet(dstaddr) == data_center_subnet)):
        accept(output_port)
        return
      
      if is_same_subnet(srcaddr, dstaddr):
        accept(output_port)
        return

    #Rule 4: Guest hosts are allowed to use the printer
    #        Think about the protocol behind file uploading and printer info in Rule 2
    if tcp_h:
      if (srcaddr == guest and dstaddr == printer) or \
         (srcaddr == printer and dstaddr == guest):
        accept(output_port)
        return

    #Rule 5: All other traffic should be dropped
    drop()

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_routing(packet, packet_in, event.port, event.dpid)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Routing(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)

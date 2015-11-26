"""
A skeleton POX component

You can customize this to do whatever you like.  Don't forget to
adjust the Copyright above, and to delete the Apache license if you
don't want to release under Apache (but consider doing so!).

Rename this file to whatever you like, .e.g., mycomponent.py.  You can
then invoke it with "./pox.py mycomponent" if you leave it in the
ext/ directory.

Implement a launch() function (as shown below) which accepts commandline
arguments and starts off your component (e.g., by listening to events).

Edit this docstring and your launch function's docstring.  These will
show up when used with the help component ("./pox.py help --mycomponent").
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
log = core.getLogger()

s1_dpid=0
s2_dpid=0
matrix=0 #2 cols for switchs and 3 rows for bandwidth r1 = bw 1, r2 = bw 5, r3 = bw10
#	s1	s2
#q1	0	0
#q2	0	0
#q3	0	0
switch_count = 2 
queue_count = 3
MAX_BANDWIDTH = 10

def _handle_ConnectionUp (event):
	global s1_dpid, s2_dpid, matrix
	print "ConnectionUp: ",dpidToStr(event.connection.dpid)
	#remember the connection dpid for switch
	for m in event.connection.features.ports:
		if m.name == "s1-eth1":
			s1_dpid = event.connection.dpid
			print "s1_dpid=", s1_dpid
		elif m.name == "s2-eth1":
			s2_dpid = event.connection.dpid
			print "s2_dpid=", s2_dpid
	matrix = [[0 for x in range(queue_count)]for i in range(switch_count)]

inTable = {}
all_ports = of.OFPP_FLOOD

def _handle_PacketIn (event):
	global s1_dpid, s2_dpid
	packet = event.parsed
	inTable[(event.connection,packet.src)] = event.port
	dst_port = inTable.get((event.connection,packet.dst))
	print('came into handle_packetin')
	if dst_port is None:
	    # We don't know where the destination is yet.  So, we'll just
	    # send the packet out all ports (except the one it came in on!)
	    # and hope the destination is out there somewhere. :)
	    msg = of.ofp_packet_out(data = event.ofp)
	    msg.actions.append(of.ofp_action_output(port = all_ports))
	    event.connection.send(msg)
	else:
		# Since we know the switch ports for both the source and dest
		# MACs, we can install rules for both directions.
		msg = of.ofp_flow_mod()
		msg.match.dl_dst = packet.src
		msg.match.dl_src = packet.dst
		msg.actions.append(of.ofp_action_output(port = event.port))
		event.connection.send(msg)

		# This is the packet that just came in -- we want to
		# install the rule and also resend the packet.
		msg = of.ofp_flow_mod()
		msg.data = event.ofp # Forward the incoming packet
		msg.match.dl_src = packet.src
		msg.match.dl_dst = packet.dst
		msg.actions.append(of.ofp_action_output(port = dst_port))
		event.connection.send(msg)

		log.debug("Installing %s <-> %s" % (packet.src, packet.dst))
	pass

def new_Connection(src_ip, dstn_ip, bandwidth,event):
	print("in new connection")
	if bandwidth<=MAX_BANDWIDTH:
		minQIndex = getMinQueue(bandwidth) #gives queue number . index 0 - 1 mbps, 1 - 5mbps, 2 - 10mbps
		qIds = []
		pathPresent = True
		for i in range(0,switch_count):
			if matrix[minQIndex][i]!=0:
				pathPresent = False
				break
		if pathPresent==False:
			return False
		else:
			print('path present')
	else:
		return False;

def getOutputPortOfSwitch(switch,dstn_ip):
	if dstn_ip=="10.0.0.4":
		if switch == 0: #switch 1
			return 4
		elif switch == 1:	#switch 2
			return 2
	else:
		if switch == 1:
			return 1
		elif dstn_ip=="10.0.0.3":
			return 3
		elif dstn_ip=="10.0.0.2":
			return 2
		else:
			return 1


def getMinQueue(bandwidth):
	if bandwidth <=1:
		return 0
	elif bandwidth<=5:
		return 1
	else:
		return 2

def getQidFromMatrix(srcip,switch):
	for i in range(0,queue_count):
		if(str(matrix[i][switch-1]) is srcip):
			return i
	return 0
	pass



def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
	core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

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
import BaseHTTPServer
import SocketServer
import json
import threading
from BaseHTTPServer import BaseHTTPRequestHandler

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
log = core.getLogger()

s1_dpid=0
s2_dpid=0
reservation_matrix=[]
#	q1	 q2	  q3
#s1	FREE FREE FREE
#s2	FREE FREE FREE
#.
#.
#s6	FREE FREE FREE

switch_count = 6 
queue_count = 3
MAX_BANDWIDTH = 10
FREE = "free"

def _handle_ConnectionUp (event):

    print "starting the reservation http service"
    reservationService = ReservationServiceThread()
    reservationService.setDaemon(True);
    reservationService.start();


	print("Connection Up!")
	pass

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
	    pathpres = new_Connection(str(packet.src),str(packet.dst),2)
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
		#msg.actions.append(of.ofp_action_output(port = dst_port))
		msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id=getQidFromMatrix(str(packet.src))))
		print("Msg has Port"+str(dst_port)+","+str(getQidFromMatrix(str(packet.src))))
		event.connection.send(msg)
		log.debug("Installing %s <-> %s" % (packet.src, packet.dst))
	pass

def new_Connection(src_ip, dstn_ip, bandwidth):
	pathPresent = True
	print("in new connection")
	if bandwidth<=MAX_BANDWIDTH:
		minQIndex = getMinQueue(bandwidth) #gives queue number . index 0 - 1 mbps, 1 - 5mbps, 2 - 10mbps
		qIds = []
		for i in range(0,switch_count):
			#print("val:"+str(i)+","+str(minQIndex))
			if reservation_matrix[i][minQIndex] == FREE:
				pass
			else:
				pathPresent = False
				break
		if pathPresent==True:
			print('path present')
			for i in range(0,switch_count):
				reservation_matrix[i][minQIndex] = src_ip
	else:
		pathPresent = False
	print("new conn:")
	print("reservation matrix is")
	for i in range(switch_count):
		print("s"+str(i)+":"+reservation_matrix[i][0]+","+reservation_matrix[i][1]+","+reservation_matrix[i][2])
	return pathPresent
"""
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
"""

def getMinQueue(bandwidth):
	if bandwidth <=1:
		return 0
	elif bandwidth<=5:
		return 1
	elif bandwidth<=10:
		return 2

def getQidFromMatrix(srcip):
	qid = 0
	for i in range(queue_count):
		if reservation_matrix[0][i] == srcip:
			qid = i
	print("get qid from matrix returns "+str(qid)+" for "+srcip)
	return qid
	pass

def launch ():
	global reservation_matrix
	reservation_matrix = [[FREE for x in range(0,queue_count)] for j in range(0,switch_count)]
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
	core.openflow.addListenerByName("PacketIn", _handle_PacketIn)


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # Handler for the GET request
    def do_POST(self):

        response={}
        #get the body of POST request
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        request = json.loads(post_body);
        src_ip = request['src_ip']
        dst_ip = request['dst_ip']
        bandwidth = request['bandwidth']

        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if src_ip == None | dst_ip == None | bandwidth | None:
            #we give an eror response back
            response['reservation'] = 'BAD_REQUEST'
            str = json.dumps(response)
            print str
            self.send_response(200)
            self.wfile.write(str)
            return

        bandwidth = int(bandwidth)
        bool_value = new_Connection(src_ip,dst_ip,bandwidth)

        if(bandwidth):
             response['reservation'] = 'OK'

        else:
             response['reservation'] = 'FAILED'


        str = json.dumps(response)
        print str
        self.send_response(200)
        self.wfile.write(str)
        return


"""
The class is responsible for hosting the reservation
service for clients.
"""


class ReservationServiceThread(threading.Thread):
    SERVER_PORT = 6060

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(ReservationServiceThread, self).__init__(group, target, name, args, kwargs, verbose)

    def run(self):
        print "starting reservation service. Listening on port %s",self.SERVER_PORT
        httpd = BaseHTTPServer.HTTPServer(("", self.SERVER_PORT), MyHandler)
        httpd.serve_forever();
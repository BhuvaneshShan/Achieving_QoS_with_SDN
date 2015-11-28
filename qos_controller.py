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
import json
import threading

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
log = core.getLogger()

reservation_matrix=[]
avail_matrix=[]
qbw = [1,1,5,10] #q0 is the default queue for any unreserved traffic
#     q0    q1   q2   q3
#s1 DEFAULT FREE FREE FREE
#s2 DEFAULT FREE FREE FREE
#.
#.
#s6 DEFAULT FREE FREE FREE

switch_count = 6 
queue_count = 3
MAX_BANDWIDTH = 10
FREE = "free"
TEST = 1

inTable = {}
all_ports = of.OFPP_FLOOD

def _handle_ConnectionUp(event):
    pass

def getSrcIPandARP (packet):
    #Gets source IPv4 address for packets that have one (IPv4 and ARP)
    #Returns (ip_address, has_arp).  If no IP, returns (None, False).
    if isinstance(packet, ipv4):
        log.debug("IP %s => %s",str(packet.srcip),str(packet.dstip))
        #print("IPv4:src"+str(packet.srcip)+",dstn:"+str(packet.dstip))
        return ( packet.dstip, False )
    elif isinstance(packet, arp):
        log.debug("ARP %s %s => %s",
                {arp.REQUEST:"request",arp.REPLY:"reply"}.get(packet.opcode,
                    'op:%i' % (packet.opcode,)),
               str(packet.protosrc), str(packet.protodst))
        #print("ARP:src"+str(packet.protosrc)+",dstn:"+str(packet.protodst))
        if (packet.hwtype == arp.HW_TYPE_ETHERNET and
          packet.prototype == arp.PROTO_TYPE_IP and
          packet.protosrc != 0):
            return ( packet.protodst, True )
    return ( None, False )


def _handle_PacketIn (event):
    global s1_dpid, s2_dpid
    #print("payload:"+str(dir(event.parsed.payload)))
    #print("hwsrc:"+str(event.parsed.payload.hwsrc))
    #print("hwdst:"+str(event.parsed.payload.hwdst))
    packet = event.parsed
    (pckt_srcip, hasARP) = getSrcIPandARP(packet.next)
    if pckt_srcip is None:
        pckt_srcip = "10.0.0.0"
        #print("Pckt_srcip:"+str(pckt_srcip))
        #self.updateIPInfo(pckt_srcip,macEntry,hasARP)
        print("pckt_srcip is NONE and is set to 10.0.0.0!")
    inTable[(event.connection,packet.src)] = event.port
    dst_port = inTable.get((event.connection,packet.dst))
    #print('came into handle_packetin')
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
        #msg.actions.append(of.ofp_action_output(port = dst_port))
        #ipv4_packet = event.parsed.find("ipv4")
        #if ipv4_packet is None:
        #    print("ipv4 none")
        #ipv4_src_ip = ipv4_packet.srcip
        #print("ipv4 src ip :"+str(ipv4_src_ip))
        msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id=getQidFromMatrix(str(pckt_srcip))))
        print("Msg sent to Switch "+str(event.connection.dpid)+": Port"+str(dst_port)+", Queue"+str(getQidFromMatrix(str(pckt_srcip))))
        #print("srcip:"+str(packet.src))
        event.connection.send(msg)
        log.debug("Installing %s <-> %s" % (packet.src, packet.dst))
    pass

def new_Connection(src_ip, dstn_ip, bandwidth):
    pathPresent = True
    print("in new connection")
    if bandwidth<=MAX_BANDWIDTH:
        minQIndex = getCorrectQueue(bandwidth) #gives queue number . index 0 - 1 mbps, 1 - 5mbps, 2 - 10mbps
        qIds = []
        if minQIndex == -1:
            pathPresent = False
        else:
            for i in range(0,switch_count):
                if reservation_matrix[i][minQIndex] == FREE:
                    reservation_matrix[i][minQIndex] = src_ip
                else:
                    reservation_matrix[i][minQIndex] = reservation_matrix[i][minQIndex] + "," + src_ip
            #should not assign to all switch queus. but rather only to the switches involved in the connection
            for i in range(0,switch_count):
                avail_matrix[i][minQIndex] -= bandwidth
    else:
        pathPresent = False
    print("new conn:")
    printResMatrix()
    return pathPresent

def printResMatrix():
    print("reservation matrix is")
    for i in range(switch_count):
        print("s"+str(i)+": "+reservation_matrix[i][0]+";"+reservation_matrix[i][1]+";"+reservation_matrix[i][2]+";"+reservation_matrix[i][3])

def getCorrectQueue(bandwidth):
    que = getMinQueue(bandwidth)
    val = 1
    for i in range(switch_count):
        if avail_matrix[i][que] < bandwidth:
            val = 0
            break
    if val == 1:
        return que
    else:
        return -1

def getMinQueue(bandwidth):
    if bandwidth <=1:
        return 1
    elif bandwidth<=5:
        return 2
    elif bandwidth<=10:
        return 3

def getQidFromMatrix(srcip):
    qid = 0
    #print("checking Qid for srcip :"+str(srcip))
    for i in range(1,queue_count+1):
        #print("Res matrix entry chekcing:"+str(reservation_matrix[0][i]))
        if srcip in reservation_matrix[0][i]:
            qid = i
    #print("get qid from matrix returns "+str(qid)+" for "+srcip)
    return qid

def launch ():

    print "starting the reservation http service inside launch method"
    reservationService = ReservationServiceThread()
    reservationService.setDaemon(True)
    reservationService.start()

    global reservation_matrix, avail_matrix
    reservation_matrix = [[FREE for x in range(0,queue_count+1)] for j in range(0,switch_count)] #+1 for default queue fro normal convo
    avail_matrix = [[0 for x in range(0,queue_count+1)] for j in range(0,switch_count)]
    for i in range(0,switch_count):
        for j in range(0,queue_count+1):
            avail_matrix[i][j] = qbw[j]
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)


#curl -H "Content-Type: application/json" -X POST -d '{"bandwidth":5}' http://localhost:6060
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # Handler for the GET request
    def do_POST(self):



        src_ip = None
        dst_ip = None
        bandwidth = None

        response={}
        try:
            #get the body of POST request
            post_body = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
            request = json.loads(post_body);
            src_ip = request.get('source_ip')
            dst_ip = request.get('dest_ip')
            bandwidth = request.get('bandwidth')
        except Exception:
            print "internal server error happened"
            return



        if (src_ip is None) | (dst_ip is None) | (bandwidth is None):
            #we give an eror response back
            print 'src_ip, dst_ip, bandwidth cannot be null'
            response['reservation'] = 'BAD_REQUEST'
            json_str = json.dumps(response)

            content = bytes(json_str)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        bandwidth = int(bandwidth)
        bool_value = new_Connection(src_ip,dst_ip,bandwidth)
        if(bool_value):
             response['reservation'] = 'OK'

        else:
             response['reservation'] = 'FAILED'


        json_str = json.dumps(response)
        content = bytes(json_str)
        self.send_response(200)
        self.send_header("Content-type","application/json")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)
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
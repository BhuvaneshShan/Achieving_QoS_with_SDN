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
log = core.getLogger()

reservation_matrix=[]
avail_matrix=[]
qbw = [1,5,10]
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
TEST = 1

inTable = {}
all_ports = of.OFPP_FLOOD

def _handle_ConnectionUp(event):
    pass



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
        #msg.actions.append(of.ofp_action_output(port = dst_port))
        msg.actions.append(of.ofp_action_enqueue(port = dst_port, queue_id=getQidFromMatrix(str(packet.src))))
        print("Msg sent to"+str(event.connection.dpid)+": Port"+str(dst_port)+","+str(getQidFromMatrix(str(packet.src))))
        event.connection.send(msg)
        log.debug("Installing %s <-> %s" % (packet.src, packet.dst))
    pass

def new_Connection(src_ip, dstn_ip, bandwidth):
    pathPresent = True
    print("in new connection, with src_ip: " + src_ip)
    if bandwidth<=MAX_BANDWIDTH:
        qIds = []
        questr = getCorrectQueue(src_ip, bandwidth)
        if questr == "FALSE" or questr == "":
            pathPresent = False
        else:
            questrlist = questr.split(",")
            qIndex = [0 for x in range(len(questrlist))]
            print questrlist
            i=0
            for q in questrlist:
                qIndex[i] = int(q)
                i +=1
            #check for starting and ending indices, assuming unidrectional
            for i in range(switch_count):
                if src_ip == "10.0.0." + str(i+1):
                    source =i
                if dstn_ip == "10.0.0." + str(i+1):
                    destination = i
                    break
            for i in range(source, destination+1):
                if reservation_matrix[i][qIndex[i]]== FREE:
                    reservation_matrix[i][qIndex[i]] = src_ip
                else:
                    reservation_matrix[i][qIndex[i]] = reservation_matrix[i][qIndex[i]] + "," + src_ip
            for i in range(source, destination+1):
                avail_matrix[i][qIndex[i]] -= bandwidth
    else:
        pathPresent = False
    print("new conn:")
    printResMatrix()
    return pathPresent

def printResMatrix():
    print("reservation matrix is")
    for i in range(switch_count):
        print("s"+str(i)+": "+reservation_matrix[i][0]+";"+reservation_matrix[i][1]+";"+reservation_matrix[i][2])

def getCorrectQueue(src_ip, bandwidth):
    que = getMinQueue(src_ip, bandwidth)
    print "start with queue: " + str(que)
    if que == -1:
        return "FALSE"
    val = 1
    questr = ""
    for i in range(switch_count):
        if avail_matrix[i][que] >= bandwidth:
            if questr == "":
                questr = str(que)
            else:
                questr = questr + " , " + str(que)
        elif avail_matrix[i][((que+1)%3)] >= bandwidth:
            if questr == "":
                questr = str((que+1)%3)
            else:
                questr = questr + " , " + str((que+1)%3)
            que = (que+1)%3
        elif avail_matrix[i][((que+2)%3)] >= bandwidth:
            if questr == "":
                questr = str((que+2)%3)
            else:
                questr = questr + " , " + str((que+2)%3)
            que = (que+1)%3
        else:
            val = 0
            break
    if val == 1:
        return questr
    else:
        return "FALSE"

def getMinQueue(src_ip, bandwidth):
    for i in range(switch_count):
        #check which queue to start with for that particular switch
        if src_ip == ("10.0.0."+str(i+1)):
            for j in range(3):
                print avail_matrix[i][j]
                if avail_matrix[i][j] >= bandwidth:
                    return j
    return -1

def getQidFromMatrix(srcip):
    qid = 0
    for i in range(queue_count):
        #should not check in switch1 but rather the concerned switches in the middle of the connection
        #also srcip looks like  real MAC address "09:f3:87:d3:ab:3e" while res matrix has simple ip addr like "10.0.0.1", so qid 0 is returned.
        if srcip in reservation_matrix[0][i]:
            qid = i
    #print("get qid from matrix returns "+str(qid)+" for "+srcip)
    return qid
    pass

def launch ():

    print "starting the reservation http service inside launch method"
    reservationService = ReservationServiceThread()
    reservationService.setDaemon(True)
    reservationService.start()

    global reservation_matrix, avail_matrix
    reservation_matrix = [[FREE for x in range(0,queue_count)] for j in range(0,switch_count)]
    avail_matrix = [[0 for x in range(0,queue_count)] for j in range(0,switch_count)]
    for i in range(0,switch_count):
        for j in range(0,queue_count):
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

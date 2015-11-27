# Import socket module
import getopt
import json

import sys
import urllib2


def main(argv):
    CONTROLLER_IP = '127.0.0.1'
    CONTROLLER_SERVICE_PORT = 6060

    bandwidth = None
    source_ip = None
    destination_ip = None


    #first get the program commandline params
    try:
        opts, args = getopt.getopt(argv,"hb:s:d:",["bandwidth=","sourceip=","destip="])
        for opt,arg in opts:
            if opt in ("-b","--bandwidth"):
                bandwidth = arg
            elif opt in ("-s","--sourceip"):
                source_ip = arg
            elif opt in ("-d","--destip"):
                destination_ip = arg;

    except getopt.GetoptError:
        print "usage:  client.py -b <bandwidth>  -s <souce_ip> -d <destination_ip>"

    #send the reservation request to the controller reservation service
    request = {}
    request['source_ip'] = source_ip
    request['dest_ip'] = destination_ip
    request['bandwidth'] = int(bandwidth)

    request_str = json.dumps(request);
    reservation_endpoint = 'http://'+ CONTROLLER_IP + ":" + str(CONTROLLER_SERVICE_PORT)
    print 'contacting reservation server : ' + reservation_endpoint

    req = urllib2.Request(reservation_endpoint)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req,request_str)
    data = response.read()
    response_dict = json.loads(data)


    if response_dict['reservation'] == 'BAD_REQUEST':
        print "bad request params.."
        return;
    elif response_dict['reservation'] == 'FAILED':
        print "reservation failed, try again"
        return;
    elif response_dict['reservation'] == 'OK':
        print "reservation granted"
        #if reservation granted, go ahead and send the retuest, else abort
        #execute the file download command

        return



if __name__ == '__main__':
    main(sys.argv[1:])



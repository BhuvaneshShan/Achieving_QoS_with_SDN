# Achieving_QoS_with_SDN
computer networks project - software defined networking

###iperf for data collection
1. I found a way to get data. No change in code. just pull the latest from repo
2. in mininet xterm window, open window for each host using 

xterm h1 h2 h3 h4 h5 h6

3. reserve a path using client.py

eg: sudo python client.py -b 3 -s 10.0.0.1 -d 10.0.0.4

4. Now data needs to be sent from h1 to h4
5. In h1 (server sending data) xterm window type,

iperf -s

6. In h4 (client receiving data) xterm window type,

iperf -c <src/server ip addrs>

eg: iperf -c 10.0.0.1

Now h4 starts hearing from h1.

7. I think we need to add -p <port number> to the above commands to get the actual bandwindth the network allows.
8. check other options using iperf --help


### Quickstart Steps


1. First start the mininet totpology
sudo python -m gatech.main

2. Then copy the qos_controller.py script found at the root of the git repo to 'pox/ext' directory.
3. Start the pox controller

sudo pox.py qos_controller

4. At this point, we have mininet talking to our pox controller. Reservation service is up on port '6060' of the
in the same machine node as the controller.

5. Running the client - open a xterm windown in client host.
within the xterm terminal run the our client code.

give bandwidth (-b) source ip (-s) and destination ip (-d) . controller IP and port is hardcoded in
the script. change it accordingly before running.

python client.py -b 5 -s 10.0.0.1 -d 10.0.0.4

###Changes
####Nov 30, 2015 12.21am
1. Dumb and Smart controllers integrated into one file
2. change the MODE variable to DUMB or SMART to use as per need.
3. debugged. still edge cases are to be debugged.
4. iperf pending


####Nov 28, 2015 11.09am

1. Default queue (index 0) has been added so that unreserved traffic can use it

2. Queues (1Mbps, 5Mbps and 10Mbps) are indexed as 1,2 and 3 in the reservation and availabilty matrices

3. IPvsMAC addressing problem resolved. 






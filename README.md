# Achieving_QoS_with_SDN
computer networks project - software defined networking

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







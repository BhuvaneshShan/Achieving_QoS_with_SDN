#controller logic using pyratic controller
# Dumb controller
# Smart controller
import os

from mininet.node import Controller


class PoxBridge(Controller):

    pox_file = None;

    def __init__(self,pox_script_name):
        self.pox_file = pox_script_name

    def start(self):
        "Start POX learning switch"
        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd( self.pox, self.pox_file % ' &' )


    def stop(self, *args, **kwargs):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )




def testController():
    pass

if __name__ == '__main__':
    #test function goes here
    testController()


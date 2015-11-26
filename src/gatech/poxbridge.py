#controller logic using pyratic controller
# Dumb controller
# Smart controller
import os

from mininet.node import Controller


class PoxBridge(Controller):
    def start(self):
        "Start POX learning switch"
        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd( self.pox, 'forwarding.l2_learning &' )


    def stop(self, *args, **kwargs):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )




def testController():
    pass

if __name__ == '__main__':
    #test function goes here
    testController()


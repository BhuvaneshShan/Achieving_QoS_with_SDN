#controller logic using pyratic controller
# Dumb controller
# Smart controller
import os

from mininet.node import Controller

from gatech.util import create_queues


class PoxBridge(Controller):
    def start(self):

        "create the queues using the convenience util function"
        create_queues()
        "Start POX learning switch"
        #self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        #self.cmd( self.pox, 'qos_controller &' )


    def stop(self, *args, **kwargs):
        "Stop POX"
        #self.cmd( 'kill %' + self.pox )




def testController():
    pass

if __name__ == '__main__':
    #test function goes here
    testController()


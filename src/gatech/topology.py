import logging

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections

LOG = logging.getLogger(__name__);

class ExpTopo(Topo):
    # override the super class abstract method
    def build(self, *args, **kwargs):
        # create hosts
        h1 = self.addHost('h1',cpu=0.25)
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        # create switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        # add links
        self.addLink(s1, h1,bw=10,delay='5ms')
        self.addLink(s2, h2,bw=20,delay='5ms')
        self.addLink(s3, h3,bw=30,delay='5ms')
        self.addLink(s4, h4,bw=40,delay='5ms')
        self.addLink(s5, h5,bw=50,delay='5ms')
        self.addLink(s6, h6,bw=60,delay='5ms')

        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)
        self.addLink(s4, s5)
        self.addLink(s5, s6)


def startTopology():
    net = None
    try:
        # Create and test a simple network
        topo = ExpTopo()
        net = Mininet(topo = topo)
        net.start()
        print "Dumping host connections"
        dumpNodeConnections(net.hosts)
        print "Testing network connectivity"
        net.pingAll()
        CLI(net)
        print "cleaning up.."
        net.stop()

    except Exception as e:
        LOG.error(e.message)
        #net.stop()



if __name__ == '__main__':
    setLogLevel('info')
    startTopology()
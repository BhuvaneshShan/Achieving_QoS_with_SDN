import logging
import logging.config

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink

from gatech.Settings import LOG_SETTINGS
from gatech.poxbridge import PoxBridge
from topology import ExpTopo

logging.config.dictConfig(LOG_SETTINGS)
LOG = logging.getLogger('gatech.main')

if __name__ == '__main__':
        LOG.info("starting minient environement")
        setLogLevel('info')
        topo = ExpTopo()
        net = Mininet(topo = topo, controller=PoxBridge, link=TCLink, host=CPULimitedHost)
        net.start()
        CLI(net)
        LOG.info('shutting down mininet')
        net.stop();

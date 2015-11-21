import logging
import logging.config

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink

from gatech.Settings import LOG_SETTINGS
from gatech.controller import SmartControlelr
from topology import ExpTopo

logging.config.dictConfig(LOG_SETTINGS)
LOG = logging.getLogger(__name__)

if __name__ == '__main__':
        topo = ExpTopo()
        net = Mininet(topo = topo,controller=SmartControlelr,link=TCLink,host=CPULimitedHost)
        net.start()
        CLI(net)

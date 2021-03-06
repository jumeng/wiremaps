from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.internet import defer

from wiremaps.collector.icollector import ICollector
from wiremaps.collector.helpers.port import PortCollector
from wiremaps.collector.helpers.arp import ArpCollector
from wiremaps.collector.helpers.lldp import LldpCollector, LldpSpeedCollector

class Linux:
    """Collector for Linux.

    It is assumed that they are running an LLDP agent. This agent will
    tell us which ports to use.
    """

    implements(ICollector, IPlugin)

    def handleEquipment(self, oid):
        return (oid in ['.1.3.6.1.4.1.8072.3.2.10', # Net-SNMP Linux
                        ])

    def collectData(self, equipment, proxy):
        ports = PortCollector(equipment, proxy)
        arp = ArpCollector(equipment, proxy, self.config)
        lldp = LldpCollector(equipment, proxy)
        speed = LldpSpeedCollector(equipment, proxy)
        d = ports.collectData()
        d.addCallback(lambda x: arp.collectData())
        d.addCallback(lambda x: lldp.collectData())
        d.addCallback(lambda x: speed.collectData())
        d.addCallback(lambda x: lldp.cleanPorts())
        return d

linux = Linux()

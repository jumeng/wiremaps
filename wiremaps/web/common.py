import re

from twisted.names import client
from nevow import rend
from nevow import tags as T, entities as E

class RenderMixIn:
    """Helper class that provide some builtin fragments"""

    def render_ip(self, ctx, ip):
        d = self.dbpool.runQuery("SELECT ip FROM equipment WHERE ip=%(ip)s",
                                 {'ip': ip})
        d.addCallback(lambda x: T.invisible[
                x and
                T.a(href="equipment/%s/" % ip) [ ip ] or
                T.a(href="search/%s/" % ip) [ ip ],
                T.invisible(data=self.data_solvedip, # Dunno why we can't use T.directive here
                            render=T.directive("solvedip"))])
        return d

    def data_solvedip(self, ctx, ip):
        ptr = '.'.join(ip.split('.')[::-1]) + '.in-addr.arpa'
        d = client.lookupPointer(ptr)
        d.addErrback(lambda x: None)
        return d

    def render_solvedip(self, ctx, name):
        try:
            return ctx.tag[" ", E.harr, " ",
                           str(name[0][0].payload.name),
                           ]
        except:
            return ctx.tag

    def render_mac(self, ctx, mac):
        return T.a(href="search/%s/" % mac) [ mac ]

    def render_hostname(self, ctx, name):
        d = self.dbpool.runQuery("SELECT name FROM equipment "
                                 "WHERE lower(name)=lower(%(name)s)",
                                 {'name': name})
        d.addCallback(lambda x: x and
                      T.a(href="equipment/%s/" % name) [ name ] or
                      T.a(href="search/%s/" % name) [ name ])
        return d    

    def render_vlan(self, ctx, vlan):
        return T.a(href="search/%s/" % vlan) [ vlan ]

    def render_sonmpport(self, ctx, port):
        if port < 64:
            return ctx.tag[port]
        if port < 65536:
            return ctx.tag[int(port/64)+1, "/", port%64]
        return ctx.tag["%02x:%02x:%02x" % (port >> 16, (port & 0xffff) >> 8,
                                           (port & 0xff))]

    lastdigit = re.compile("^(.*?)(\d+-)?(\d+)$")
    def render_ports(self, ctx, ports):
        results = []
        for p in ports:
            if not results:
                results.append(p)
                continue
            lmo = self.lastdigit.match(results[-1])
            if not lmo:
                results.append(p)
                continue
            cmo = self.lastdigit.match(p)
            if not cmo:
                results.append(p)
                continue
            if int(lmo.group(3)) + 1 != int(cmo.group(3)) or \
                    lmo.group(1) != cmo.group(1):
                results.append(p)
                continue
            if lmo.group(2):
                results[-1] = "%s%s%s" % (lmo.group(1),
                                          lmo.group(2),
                                          cmo.group(3))
            else:
                results[-1] = "%s%s-%s" % (lmo.group(1),
                                           lmo.group(3),
                                           cmo.group(3))
        return ctx.tag[", ".join(results)]

class FragmentMixIn(rend.Fragment, RenderMixIn):
    def __init__(self, dbpool, *args, **kwargs):
        self.dbpool = dbpool
        rend.Fragment.__init__(self, *args, **kwargs)

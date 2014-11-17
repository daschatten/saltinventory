#!/usr/bin/python

#
# Requirements:
#
# * salt
# * python-netaddr
#

import salt.client
from netaddr import *
from jinja2 import Template, BaseLoader, TemplateNotFound, FileSystemLoader, Environment

# settings

config = {
'base_path': 'www/',
'host_page_path': 'www/hosts/',
'network_page_path': 'www/networks/',
'template_path': 'templates/',
}

# class definitions

class Inventorizer:
  config = None

  saltcmd = None

  host_list = {}
  network_list = {}

  def __init__(self, config):
    self.config = config
    self.saltcmd = salt.client.LocalClient()
    self.process()

  def process(self):
    self.collectHostData()
    self.createHostList()
    self.collectNetworkData()
    self.createHostPages()
    self.createNetworkList()
    self.createNetworkPages()

  def collectHostData(self):
    self.host_list = self.saltcmd.cmd('*', 'grains.items')

  def collectNetworkData(self):
    result = self.saltcmd.cmd('*', 'network.interfaces')
    for hostname, hostdata in result.iteritems():
      for interface, interfacedata in hostdata.iteritems():

        if interfacedata.has_key('inet'):
          for netdata in interfacedata['inet']:
            ip = IPNetwork(netdata['address'] + '/' + netdata['netmask'])
            host = {'hostname': hostname, 'address': netdata['address'], 'netobj': ip}
            self.addNetworkHost(ip, host)

        if interfacedata.has_key('secondary'):
          for netdata in interfacedata['secondary']:
            ip = IPNetwork(netdata['address'] + '/' + netdata['netmask'])
            host = {'hostname': hostname, 'address': netdata['address'], 'netobj': ip}
            self.addNetworkHost(ip, host)

        if interfacedata.has_key('inet6'):
          for netdata in interfacedata['inet6']:
            ip = IPNetwork(netdata['address'] + '/' + netdata['prefixlen'])
            host = {'hostname': hostname, 'address': netdata['address'], 'netobj': ip}
            self.addNetworkHost(ip, host)


  def addNetworkHost(self, ip, host):
    if self.network_list.has_key(ip.cidr):
      self.network_list[ip.cidr].append(host)
    else:
      self.network_list[ip.cidr] = [host]

  def createHostList(self):
    fo = open(self.config['base_path'] + "hostlist.html", "wb")
    env = Environment(loader = FileSystemLoader(config['template_path']))
    template = env.get_template('hostlist_template.html')
    fo.write(template.render({'hostlist': self.host_list}))
    fo.close
   
  def createHostPages(self):
    for hostname, hostdata in self.host_list.iteritems():
      self.createHostPage(hostname, hostdata)

  def createHostPage(self, hostname, hostdata):
    fo = open(self.config['host_page_path'] + hostname + ".html", "wb")
    env = Environment(loader = FileSystemLoader(config['template_path']))
    template = env.get_template('host_template.html')
    fo.write(template.render(hostdata))
    fo.close

  def createNetworkList(self):
    fo = open(self.config['base_path'] + "networklist.html", "wb")
    env = Environment(loader = FileSystemLoader(config['template_path']))
    env.filters['len'] = self.lenFilter
    template = env.get_template('networklist_template.html')
    fo.write(template.render({'networklist': self.network_list}))
    fo.close

  def createNetworkPages(self):
    for network, networkdata in self.network_list.iteritems():
      self.createNetworkPage(network, networkdata)

  def createNetworkPage(self, network, networkdata):
    fo = open(self.config['network_page_path'] + str(network.cidr).replace('/', '_') + ".html", "wb")
    env = Environment(loader = FileSystemLoader(config['template_path']))
    env.filters['replace'] = self.replaceFilter
    template = env.get_template('network_template.html')
    fo.write(template.render({'network': network, 'data': networkdata}))
    fo.close

  def lenFilter(self, list):
    return len(list)

  def replaceFilter(self, str, old, new):
    return str(str).replace(old, new)

# main program

inv = Inventorizer(config)


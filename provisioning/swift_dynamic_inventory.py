#! /usr/bin/python

import argparse
import json


class Inventory:

    '''
    Ansible inventory , generated from config file
    '''
    def __init__(self, fname):
        self.__load_config__(fname)

    def __load_config__(self, name):
        with open(name) as f:
            # this function is a bit ugly and should be rewritten
            self.conf = json.loads(f.read())

    def build_devices_dict(self):
        # Devices dict should be of the form:
        # {
        #   "object_devices": [ { "type": "object", "dev": "vdb", "region": "regionOne", "zone": "1", "weight": "100"   },...]
        #   "container_devices": [ { "type": "container",... },... ]
        #   "account_devices": [ { "type": "account",... },... ]
        # }
        def add_device_to_list(d, l):
            #if not d['name'] in [dev['name'] for dev in l]:
            #    l.append(d)
            l.append(d)

        def iterate_devices_in_node(device_type, node):
            for d in node['swift_devices'][device_type]:
                yield d

        def append_ring_info_to_device(d,n):
            device['ip'] = n['ip']
            device['zone'] = n['zone']
            device['region'] = n['region']

        object_devices = list()
        container_devices = list()
        account_devices = list()

        for node in self.conf['groups']['swift-object']:
            node_conf = self.conf[node]
            for device in iterate_devices_in_node('object_devices', node_conf):
                device['type'] = 'object'
                append_ring_info_to_device(device, node_conf['rings_info'])
                add_device_to_list(device, object_devices)

        for node in self.conf['groups']['swift-md']:
            node_conf = self.conf[node]
            for device in iterate_devices_in_node('container_devices', node_conf):
                device['type'] = 'container'
                append_ring_info_to_device(device, node_conf['rings_info'])
                add_device_to_list(device, container_devices)
            for device in iterate_devices_in_node('account_devices', node_conf):
                device['type'] = 'account'
                append_ring_info_to_device(device, node_conf['rings_info'])
                add_device_to_list(device, account_devices)

        res = dict()
        res['object_devices'] = object_devices
        res['container_devices'] = container_devices
        res['account_devices'] = account_devices
        return res

    def show_list(self):
        g = {}
        for group in ['keystone', 'swift-proxy', 'swift-md', 'swift-object',
                      'swift-ring-builder']:
            g[group] = dict()
            g[group]['hosts'] = self.conf['groups'][group]
            g[group]['vars'] = dict()
            if group == 'keystone':
                g[group]['vars'] = self.conf[group]['vars']
            if group == 'swift-ring-builder':
                g[group]['vars'] = self.conf[group]
            if group.startswith('swift'):
                 g[group]['vars'].update(self.conf['swift']['vars'])

        return g

    def show_host(self, name):
        res = self.conf[name]
        # For the swift-ring-builder host we
        # need to dynamically construct:
        # object_devices, container_devices, account_devices
        # See swift-create-rings role
        if name in self.conf['groups']['swift-ring-builder']:
            res.update(self.build_devices_dict())
        #for group_vars in ['keystone', 'swift']:
        #    res.update(self.conf[group_vars]['vars'])
        return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host')
    args = parser.parse_args()
    inventory = Inventory('cluster_config.json')
    out = {}
    if args.list:
        out = inventory.show_list()

    if args.host:
        out = inventory.show_host(args.host)

    print json.dumps(out)


if __name__ == '__main__':
    main()


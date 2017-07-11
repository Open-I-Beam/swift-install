#!/usr/bin/env python
# --------------------------------------------------------------------------
# Copyright IBM Corp. 2015, 2015 All Rights Reserved
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# Limitations under the License.
# --------------------------------------------------------------------------
# Written By George Goldberg (georgeg@il.ibm.com)

import argparse
import json
import yaml

class Inventory:

    '''
    Ansible inventory , generated from config file
    '''
    host_group_names = ['swift-proxy',
                        'swift-storage',
                        'swift-client',
                        'swift-ring-builder',
                        'keystone']

    def __init__(self, fname):
        self.__load_config__(fname)

    def __load_config__(self, name):
        def ip_string(ip_suffix):
            return '%s.%d' % (self.conf['vagrant']['ip_prefix'], ip_suffix)

        def ip_range(ip_range):
            return [ip_string(x) for x in ip_range]

        with open(name) as f:
            # this function is a bit ugly and should be rewritten
            self.conf = yaml.load(f)
            machines = self.conf['vagrant']['machines']
            self.proxy_storage_unified =\
                machines['proxy']['num'] == 0
            if not self.proxy_storage_unified:
                proxy_ip_range = range(2, machines['proxy']['num'] + 2)
                storage_ip_range = range(
                    machines['proxy']['num'] + 2,
                    machines['proxy']['num'] + 2 + machines['storage']['num'])
            else:
                proxy_ip_range = range(2, machines['storage']['num'] + 2)
                storage_ip_range = proxy_ip_range

            mc = max(storage_ip_range) + 1
            client_ip_range = []
            if machines['client']['num'] > 0:
                client_ip_range = range(mc, mc + machines['client']['num'])
                mc = max(client_ip_range) + 1

            self.ips = dict(
                proxy_ips=ip_range(proxy_ip_range),
                storage_ips=ip_range(storage_ip_range),
                keystone_ip=ip_string(proxy_ip_range[0]),
                client_ips=ip_range(client_ip_range),
                docker_ip=ip_string(mc),
            )

    def __host_group__(self, group):
        if group == 'proxy' and self.proxy_storage_unified:
            group = 'storage'
        g = {}
        g['hosts'] = [
            '%s%d' % (group,x) 
            for x in range(
                self.conf['vagrant']['machines'][group]['num'])]
        return g
    
    def __get_host_or_group_conf_vars__(self, host_group_section, host_group):
        '''
        retrieves hostvars's or groupvars's 
        section element from config file
        '''
        ansible = self.conf['ansible']
        if (host_group_section in ansible) and\
            (host_group in ansible[host_group_section]):
              return ansible[host_group_section][host_group]
        return {}


    def __conf_group_vars__(self, group):
        return self.__get_host_or_group_conf_vars__('groupvars', group)
    
    def __conf_host_vars__(self, host):
        return self.__get_host_or_group_conf_vars__('hostvars', host)

    def __all_group_vars__(self):
        conf = self.conf
        ips = self.ips
        out = dict(
            keystone_endpoint_host=ips['keystone_ip'],
            keystone_internal_url='http://%s:5000/v2.0' % (ips['keystone_ip']),
            keystone_admin_url='http://%s:35357/v2.0' % (ips['keystone_ip']),
            keystone_public_url='http://%s:5000/v2.0' % (ips['keystone_ip']),
        )

        out.update(self.__conf_group_vars__('all'))

        return out

    def show_host(self, name):
        def proxy_vars(ip, ind):
            return dict(
                proxy_internal_ip=ip,
                proxy_public_ip=ip,
                proxy_admin_ip=ip
            )

        def client():
            ipind = int(name[6:])
            return ({}, self.ips['client_ips'][ipind])

        def proxy():
            ipind = int(name[5:])
            ip = self.ips['proxy_ips'][ipind]
            out = proxy_vars(ip, ipind)
            return (out, ip)

        def storage():
            ipind = int(name[7:])
            ip = self.ips['storage_ips'][ipind]
            out = dict(rings_info=dict(
                ip=ip,
                zone=ipind + 1,
                region=1)
            )
            if self.proxy_storage_unified:
                out.update(proxy_vars(ip, ipind))
            return (out, ip)

        out = {}
        ip = ''
        try:
            if name.startswith('client'):
                out, ip = client()
            if name.startswith('proxy'):
                out, ip = proxy()
            if name.startswith('storage'):
                out, ip = storage()

            if len(ip) > 0:
                out['ansible_ssh_host'] = ip
        except:
            pass
        
        out.update(self.__conf_host_vars__('all'))
        out.update(self.__conf_host_vars__(name))
        return out

    def __add_host_group__(self, name):

        def proxy():
            return self.__host_group__('proxy')

        def storage():
            def list_n_disks(n, fs):
                return [dict(name='sd%c' % (chr(x)),
                             weight=100, fs=fs) for x in range(98, 98 + n)]

            out = self.__host_group__('storage')
            device_list = list_n_disks(
                self.conf['vagrant']['machines']['storage']['disk'],
                self.conf['ansible']['fstype'])
            out['vars'] = dict(
                swift_object_devices=device_list,
                swift_container_devices=device_list,
                swift_account_devices=device_list
            )
            return out

        def client():
            if self.conf['vagrant']['machines']['client']['num'] > 0:
                return self.__host_group__('client')
            return {}

        def keystone():
            if self.proxy_storage_unified:
                return dict(hosts=['storage0'])
            return dict(hosts=['proxy0'])

        def ring_builder():
            if self.proxy_storage_unified:
                return dict(hosts=['storage0'])
            return dict(hosts=['proxy0'])

        if name == 'swift-proxy':
            return proxy()
        elif name == 'swift-storage':
            return storage()
        elif name == 'swift-client':
            return client()
        elif name == 'swift-ring-builder':
            return ring_builder()
        elif name == 'keystone':
            return keystone()
        return {}

    def show_list(self):
        out = {}
        all_group_vars = self.__all_group_vars__()
        out['all'] = dict(vars=all_group_vars)
        for group_name in Inventory.host_group_names:
            res = self.__add_host_group__(group_name)
            if 'hosts' in res:
                out[group_name] = res
                if 'vars' not in res:
                    out[group_name]['vars'] = {}
                out[group_name]['vars'].update(self.__conf_group_vars__(group_name))    
        return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host')
    parser.add_argument('--ips', action='store_true')
    args = parser.parse_args()
    inventory = Inventory('vagrant_config.yaml')
    out = {}
    if args.list:
        out = inventory.show_list()

    if args.host:
        out = inventory.show_host(args.host)

    if args.ips:
        out = inventory.ips
    print(json.dumps(out))


if __name__ == '__main__':
    main()

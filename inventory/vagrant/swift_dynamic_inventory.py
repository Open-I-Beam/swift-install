#!/usr/bin/env python
#---------------------------------------------------------------------------
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
#---------------------------------------------------------------------------
# Written By George Goldberg (georgeg@il.ibm.com)

import argparse
import json


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
            self.conf = json.loads(f.read())
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
        g['hosts'] = ['%s%d' % (group, x)
                      for x in range(self.conf['vagrant']['machines'][group]['num'])]
        g['vars'] = {}
        return g

    def __all_group_vars__(self):
        conf = self.conf
        ips = self.ips
        out = dict(
            keystone_admin_token='ADMIN',
            keystone_admin_password='passw0rd',
            swift_hash_path_prefix='d55ca1881f1e09b1',
            swift_hash_path_suffix='a3f3c381c916a198',
            swift_identity_password='passw0rd',
            openstack_region=1,
            global_log_verbose=False,
            global_log_debug=False,
            keystone_endpoint_host=ips['keystone_ip'],
            keystone_internal_url='http://%s:5000/v2.0' % (ips['keystone_ip']),
            keystone_admin_url='http://%s:35357/v2.0' % (ips['keystone_ip']),
            keystone_public_url='http://%s:5000/v2.0' % (ips['keystone_ip']),
            openstack_version=self.conf['openstack_version'],
        )

        if 'groupvars' in conf:
            out.update(conf['groupvars'])

        return out

    def show_host(self, name):
        def proxy_vars(ip, ind):
            return dict(
                  internal_ip=ip,
                  public_ip=ip,
                  admin_ip=ip
            )

        def client():
            ipind = int(name[6:])
            out = {}
            out['cosbench_controller'] = False
            if ipind == 0:
                out['cosbench_controller'] = True
            return (out, self.ips['client_ips'][ipind])

        def proxy():
            ipind = int(name[5:])
            ip = self.ips['proxy_ips'][ipind]
            out = proxy_vars(ip , ipind)
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
                out.update(self.conf['credentials'])
        except:
            pass 
        
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
                self.conf['vagrant']['machines']['storage']['disk'], self.conf['fstype'])
            out['vars']['swift_devices'] = dict(
                object_devices=device_list,
                container_devices=device_list,
                account_devices=device_list
            )
            return out

        def client():
            if self.conf['vagrant']['machines']['client']['num'] > 0:
                out = self.__host_group__('client')
                out['vars']['cosbench_driver_ips'] =\
                    self.ips['client_ips']
                return out
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
        return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host')
    parser.add_argument('--ips', action='store_true')
    args = parser.parse_args()
    inventory = Inventory('vagrant_config.json')
    out = {}
    if args.list:
        out = inventory.show_list()

    if args.host:
        out = inventory.show_host(args.host)

    if args.ips:
        out = inventory.ips
    print json.dumps(out)


if __name__ == '__main__':
    main()

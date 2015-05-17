#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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

DOCUMENTATION = '''
---
author: George Goldberg
module:
short_description: Swift ring builder command
description:
  - This module calls to swift-ring-builder to build and rebalance rings
version_added: "1"
options:
  op:
    description:
    - operaion to perform.
    choices: ["add" , "rebalance" , "create"]
    required: true
  type:
    description:
    - the class of the ring.
    choices: ["container" , "object" , "account"]
    required: true
  chdir:
    default: "/etc/swift"
    description:
    - Where to perform the command / type.builder is located
    required: false
  dev:
    description:
    - required if op == add , device , for example sdb
    required: false
  ip:
    description:
    - required if op == add , ip of the device type server
    required: false
  port:
    description:
    - required if op == add , port of the device type server
    required: false
  region:
    description:
    - required if op == add , region of the device , a number
    required: false
  zone:
    description:
    - required if op == add , zone of a device , a number
    required: false
  weight:
    description:
    - required if op == add , weigh of the device >0 and <=100
    required: false
  part_power:
    default: "18"
    description:
    - used in create command , 2^part_power --> number of partiotions in a ring
    required: false
  replicas:
    default: "3"
    description:
    - used in create command , number of replicas for each part
    required: false
  min_part_hour:
    default: "1"
    description:
    - used in create command
    required: false
notes:
  - uses swift-ring-builder command
'''

EXAMPLES = '''
'''
import os


class RingBuilder:

    def __init__(self, module):
        self.module = module

    def builder_file_exists(self):
        module = self.module
        chdir = module.params['chdir']
        type = module.params['type']
        return os.path.exists('%s/%s.builder' % (chdir, type))

    def __create__(self):
        module = self.module
        type = module.params['type']
        chdir = module.params['chdir']
        part_power = module.params['part_power']
        replicas = module.params['replicas']
        min_part_hours = module.params['min_part_hours']
        cmd = 'swift-ring-builder %s.builder create %s %s %s' % (
            type, part_power, replicas, min_part_hours)
        rc, out, err = module.run_command(cmd, cwd=chdir, check_rc=True)

    def create(self):
        module = self.module
        if not self.builder_file_exists():
            self.__create__()
            module.exit_json(changed=True)
        module.exit_json(changed=False)

    def __check_params__(self, params):
        module = self.module
        missing = []
        for p in params:
            if (p not in module.params) or (not module.params[p]):
                missing.append(p)
        if len(missing) > 0:
            module.fail_json(
                msg='Missing required arguments: %s' %
                (' '.join(missing)))

    def rebalance(self):
        module = self.module
        type = module.params['type']
        chdir = module.params['chdir']
        cmd = 'swift-ring-builder %s.builder rebalance' % (type)
        rc, out, err = module.run_command(cmd, cwd=chdir, check_rc=True)
        module.exit_json(changed=True)

    def add(self):
        self.__check_params__(
            ['dev', 'region', 'zone', 'ip', 'port', 'weight'])
        if not self.builder_file_exists():
            self.__create__()

        module = self.module
        dev = module.params['dev']
        type = module.params['type']
        region = module.params['region']
        zone = module.params['zone']
        chdir = module.params['chdir']
        ip = module.params['ip']
        port = module.params['port']
        weight = module.params['weight']

        # check if the device is already in the ring
        cmd = 'swift-ring-builder %s.builder search R%s:%s/%s' % (
            type, ip, port, dev)
        rc, out, err = module.run_command(cmd, cwd=chdir)
        if 'No matching devices found' in out:
            # add device to ring
            cmd = 'swift-ring-builder %s.builder add r%sz%s-%s:%s/%s %s' % (
                type, region, zone, ip, port, dev, weight)
            rc, out, err = module.run_command(cmd, cwd=chdir, check_rc=True)
            module.exit_json(changed=True)

        module.exit_json(changed=False)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            op=dict(
                required=True,
                aliases=['operation'],
                choices=['add', 'rebalance', 'create']
            ),
            type=dict(
                required=True,
                choices=['container', 'object', 'account']
            ),
            chdir=dict(
                required=False,
                default='/etc/swift',
                aliases=['directory']
            ),
            dev=dict(
                default=None,
                aliases=['device']
            ),
            ip=dict(
                default=None
            ),
            port=dict(
                default=None
            ),
            region=dict(
                default=None
            ),
            zone=dict(
                default=None
            ),
            weight=dict(),
            part_power=dict(
                default='18'
            ),
            replicas=dict(
                default='3'
            ),
            min_part_hours=dict(
                default='1'
            ),
        ),
    )

    builder = RingBuilder(module)

    if module.params['op'] == 'add':
        builder.add()
    elif module.params['op'] == 'create':
        builder.create()
    elif module.params['op'] == 'rebalance':
        builder.rebalance()


# import module snippets
from ansible.module_utils.basic import *
main()

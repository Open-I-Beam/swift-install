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


def fetch_swift_ring(l, ring_name):
    devices_entry = "%s_devices" % (ring_name)
    port_entry = "%s_server_port" % (ring_name)
    r = []
    for host in l:
        device_list = host['swift_devices'][devices_entry]
        ring = host['rings_info']
        ring['port'] = host[port_entry]
        for device in device_list:
            r.append({
                'device': device,
                'ring': ring,
                'type': ring_name
            })
    return r


class FilterModule(object):

    def filters(self):
        return {
            'fetch_swift_ring': fetch_swift_ring,
        }

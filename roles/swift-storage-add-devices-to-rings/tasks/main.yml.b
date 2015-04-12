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
- name: create account ring
  delegate_to: "{{ groups['swift-proxy'][0] }}"
  command: sudo -u swift swift-ring-builder account.builder add r1z1-{{ storage_ip }}:6002R{{ replication_ip }}:6005/{{ item }} 100
           chdir=/etc/swift
  with_items: account_storage_devices
  ignore_errors: yes

- name: create container ring
  delegate_to: "{{ groups['swift-proxy'][0] }}"
  command: sudo -u swift swift-ring-builder container.builder add r1z1-{{ storage_ip }}:6001R{{ replication_ip }}:6004/{{ item }} 100
           chdir=/etc/swift
  with_items: container_storage_devices
  ignore_errors: yes

- name: create object ring
  delegate_to: "{{ groups['swift-proxy'][0] }}"
  command: sudo -u swift swift-ring-builder object.builder add r1z1-{{ storage_ip }}:6000R{{ replication_ip }}:6003/{{ item }} 100
           chdir=/etc/swift
  with_items: object_storage_devices
  ignore_errors: yes



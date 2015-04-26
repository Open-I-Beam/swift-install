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
# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'json'
file = File.read('vagrant_config.json')
$config_hash = JSON.parse(file)
$config_hash = $config_hash["vagrant"]
# a list of machine_type's
# each machine is of the for #{machine_type}#{machine_id}
# where machine_id is in (1..machines[machine_type][num])
machine_list = $config_hash["machines"].keys

ip_suffix = 2
$iptables = Hash.new
machines = $config_hash["machines"]

# be lazy , calculate an ip for each machine 
# beforehand , the final ip will be
# #{ip_prefix}.#{iptables[machine_type][machine_id]}
machine_list.each do |m|
  num = machines[m]["num"]
  if num > 0
    $iptables[m] = Hash.new
    (0..(num - 1)).each do |pid|
       $iptables[m][pid] = ip_suffix
       ip_suffix += 1
    end
  end
end

$machine_num = ip_suffix - 2
$current_machine = 1

# checks if a parameter is set for the machinetype
# if so returns it , otherwise checks if it is set globally
# if so returns it , otherwise , returns default
def get_param(machinetype, param, default)
   machine = $config_hash["machines"][machinetype]
   if machine.has_key?(param)
     machine[param]
   elsif $config_hash.has_key?(param)
     $config_hash[param]
   else
     default 
   end
end

def get_machine_box(machinetype)
  boxes = $config_hash["boxes"]
  boxes[get_param(machinetype,"box","")]
end

def setup_storage_devices(server, machinetype, pid)
  disksize = get_param(machinetype , "disk_size", 4)
  disk_num = get_param(machinetype , "disk", 0)

  box = get_machine_box(machinetype)
  disk_controller = box["disk_controller"] 
  
  server.vm.provider "virtualbox" do | v |
    (1..disk_num).each do |did|
      file_to_disk = "./disk_#{machinetype}_#{pid}_storage_#{did}.vdi"
      unless File.exist?(file_to_disk)
        v.customize ['createhd', '--filename', file_to_disk, '--size', disksize * 1024]
      end
      v.customize ['storageattach', :id, '--storagectl', disk_controller, '--port', did, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
    end
  end
end

def shell_provision(server,machinetype)
  commands = get_param(machinetype, "shell", Array.new)
  commands.each do |c|
    server.vm.provision "shell", inline: c
  end
end

def ansible_cloud_provision(server)
  if $config_hash.has_key?("ansible_cloud")
    ansible_cloud = $config_hash["ansible_cloud"]
    if ansible_cloud.has_key?("playbook") && ansible_cloud.has_key?("inventory_path")
      server.vm.provision :ansible do |ansible|
        ansible.playbook = ansible_cloud["playbook"] 
        ansible.inventory_path = ansible_cloud["inventory_path"]
        ansible.sudo = true
        #ansible.verbose = 'vvvv' 
        ansible.limit = 'all'
      end
    end
  end
end

def get_ip(hostname, pid)
  ip_prefix = $config_hash["ip_prefix"]
  ip_suffix = $iptables[hostname][pid]

  return "#{ip_prefix}.#{ip_suffix}"
end

# setup cpu and memory
def setup_basic_parameters(server , machinetype , pid)
  # setup cpu and memory for the machine
  server.vm.provider "virtualbox" do |v|
    v.cpus = get_param(machinetype , "cpus", 1)
    v.memory = get_param(machinetype , "memory", 1024)
  end
end

def setup_box(server,machinetype,pid)
  box = get_machine_box(machinetype)
  server.vm.box = box["box"]
  if box.has_key?("box_url")
     server.vm.box_url = box["box_url"]
  end
end

def setup_machine(server,machinetype,pid)
  machine = $config_hash["machines"][machinetype]
  # each setup parameter can be local to a machine_type
  # or global
  
  # setup cpu and memory
  setup_basic_parameters(server,machinetype,pid)
  
  # setup vagrant box and its url
  setup_box(server,machinetype,pid)

  unless get_param(machinetype , "disk", 0) == 0
    setup_storage_devices(server, machinetype, pid)
  end
  
  # setup ip address
  ip_address = get_ip(machinetype, pid)
  server.vm.network "private_network",ip: ip_address
  server.vm.hostname = "#{machinetype}#{pid}"
  
  # use default key , one for all , you dont really need
  # security for testing purposes , don't you ?
  server.ssh.insert_key = false
 
  # provision shell
  shell_provision(server, machinetype)
  
  # run ansible provision only after the last machine is
  # set up , to set up to provision the whole cluster at once
  if $current_machine == $machine_num
     ansible_cloud_provision(server)
  end   
  $current_machine += 1
end

Vagrant.configure(2) do |config|
  # setup dns virtual box to intercept dns requests
  # and convey it to host dns
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end
 
  $config_hash["machines"].keys.each do |m|  
    machine = $config_hash["machines"][m]
    (0..(machine["num"] - 1)).each do |pid|
      config.vm.define "#{m}#{pid}" do |server|
        setup_machine(server,m,pid)
      end
    end
  end

end

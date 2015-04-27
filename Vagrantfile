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


class ConfigFile
  private
  
    def init_iplist
      machine_list = @machines.keys
         
      ip_suffix = 2
      @iptables = Hash.new
      machines = @config_hash["machines"]
          
      # be lazy , calculate an ip for each machine 
      # beforehand , the final ip will be
      # #{ip_prefix}.#{iptables[machine_type][machine_id]}
      machine_list.each do |m|
        num = machines[m]["num"]
        if num > 0
          @iptables[m] = Hash.new
          (0..(num - 1)).each do |pid|
             @iptables[m][pid] = ip_suffix
             ip_suffix += 1
          end
        end
      end
      @machine_num = ip_suffix - 2
    end
    
  
  public

    def initialize(filename)
      content = File.read(filename)    
      @config_hash = JSON.parse(content)
      @config_hash = @config_hash["vagrant"]
      @machines = @config_hash["machines"]
      init_iplist    
    end
    
    def [](x)
      @config_hash[x]
    end
    
    def has_key?(key)
      @config_hash.has_key?(key)
    end

    def get_ip(hostname,pid)
      ip_prefix = @config_hash["ip_prefix"]
      ip_suffix = @iptables[hostname][pid]

      "#{ip_prefix}.#{ip_suffix}"
    end

    def machine_num
      @machine_num
    end
end

$conf = ConfigFile.new("vagrant_config.json")
$conf.freeze

class MachineConfig    
  
  def initialize(machinetype)
    @type = machinetype 
    @machine = $conf["machines"][@type]
  end

  def type
    @type
  end

  def get_ip(pid)
    $conf.get_ip(@type,pid)
  end
  
  # checks if a parameter is set for the machinetype
  # if so returns it , otherwise checks if it is set globally
  # if so returns it , otherwise , returns default
  def get(param, default)
     if @machine.has_key?(param)
       @machine[param]
     elsif $conf.has_key?(param)
       $conf[param]
     else
       default 
     end
  end

  def box
    boxes = $conf["boxes"]
    boxes[get("box","")]
  end

end

class Machine
  private
    @@counter = 1
    
    def self.get_machine_number
      c = @@counter
      @@counter += 1
      c
    end
  
    def setup_storage_devices

      disksize = @conf.get("disk_size", 4)
      disk_num = @conf.get("disk", 0)

      disk_controller = @conf.box["disk_controller"] 
      
      @server.vm.provider "virtualbox" do | v |
        (1..disk_num).each do |did|
          file_to_disk = "./disk_#{@conf.type}_#{@pid}_storage_#{did}.vdi"
          unless File.exist?(file_to_disk)
            v.customize ['createhd', 
                         '--filename', file_to_disk, 
                         '--size', disksize * 1024]
          end
          v.customize ['storageattach', :id, 
                       '--storagectl', disk_controller, 
                       '--port', did, 
                       '--device', 0, 
                       '--type', 'hdd', 
                       '--medium', file_to_disk]
        end
      end
    end

    def shell_provision
      commands = @conf.get("shell", Array.new)
      commands.each do |c|
        @server.vm.provision "shell", inline: c
      end
    end

    def ansible_cloud_provision
      if $conf.has_key?("ansible_cloud")
        ansible_cloud = $conf["ansible_cloud"]
        if ansible_cloud.has_key?("playbook") &&
           ansible_cloud.has_key?("inventory_path")
          
          @server.vm.provision :ansible do |ansible|
            ansible.playbook = ansible_cloud["playbook"] 
            ansible.inventory_path = ansible_cloud["inventory_path"]
            ansible.sudo = true
            #ansible.verbose = 'vvvv' 
            ansible.limit = 'all'
          end
        end
      end
    end

    # setup cpu and memory
    def setup_basic_parameters
      # setup cpu and memory for the machine
      @server.vm.provider "virtualbox" do |v|
        v.cpus = @conf.get("cpus", 1)
        v.memory = @conf.get("memory", 1024)
      end
    end

    def setup_box
      box = @conf.box
      @server.vm.box = box["box"]
      if box.has_key?("box_url")
         @server.vm.box_url = box["box_url"]
      end
    end

  public
    def initialize(vagrantserver,machineconf,id)
      @conf = machineconf 
      @pid = id
      @server = vagrantserver
      @number = Machine.get_machine_number
    end
    
    def setup
      # each setup parameter can be local to a machine_type
      # or global
      
      # setup cpu and memory
      setup_basic_parameters
      
      # setup vagrant box and its url
      setup_box

      unless @conf.get("disk", 0) == 0
        setup_storage_devices
      end
      
      # setup ip address
      ip_address = @conf.get_ip(@pid)
      @server.vm.network "private_network",ip: ip_address
      @server.vm.hostname = "#{@conf.type}#{@pid}"
      
      # use default key , one for all , you dont really need
      # security for testing purposes , don't you ?
      @server.ssh.insert_key = false
     
      # provision shell
      shell_provision
      
      # run ansible provision only after the last machine is
      # set up , to set up to provision the whole cluster at once
      if @number == $conf.machine_num
         ansible_cloud_provision
      end   
    end
end

Vagrant.configure(2) do |config|
  # setup dns virtual box to intercept dns requests
  # and convey it to host dns
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end
 
  $conf["machines"].keys.each do |m|  
    machine_conf = MachineConfig.new(m)
    num = machine_conf.get("num", 0)
    (0..(num - 1)).each do |pid|
      config.vm.define "#{m}#{pid}" do |server|
        machine = Machine.new(server,machine_conf, pid)
        machine.setup
      end
    end
  end

end

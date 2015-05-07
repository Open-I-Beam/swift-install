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

# ConfigFile , parses the json config file vagrant_config.json
class ConfigFile
  private

    def init_iplist
      # be lazy , calculate an ip for each machine
      # beforehand , the final ip will be
      # #{ip_prefix}.#{iptables[machine_type][machine_id]}
      @config_hash['machines'].keys.each do |m|
        num = @config_hash['machines'][m]['num']
        num > 0 || next
        @iptables[m] = {}
        (0..(num - 1)).each do |pid|
          @iptables[m][pid] = @machine_num + 2
          @machine_num += 1
        end
      end
    end

  public

    attr_reader :machine_num

    def self.conf
      @conf ||= ConfigFile.new('vagrant_config.json')
    end

    def initialize(filename)
      content = File.read(filename)
      @config_hash = JSON.parse(content)
      @config_hash = @config_hash['vagrant']
      @iptables = {}
      @machine_num = 0
      init_iplist
    end

    def [](x)
      @config_hash[x]
    end

    def key?(key)
      @config_hash.key?(key)
    end

    def ip(hostname, pid)
      "#{@config_hash['ip_prefix']}.#{@iptables[hostname][pid]}"
    end
end

# MachineConfig, a per machine type config global data
class MachineConfig
  private

    def conf
      ConfigFile.conf
    end

  public

    attr_reader :type

    def initialize(machinetype)
      @type = machinetype
      @machine = conf['machines'][@type]
    end

    def ip(pid)
      conf.ip(@type, pid)
    end

    # checks if a parameter is set for the machinetype
    # if so returns it , otherwise checks if it is set globally
    # if so returns it , otherwise , returns default
    def get(param, default)
      return @machine[param] if @machine.key?(param)
      return conf[param] if conf.key?(param)
      default
    end

    def box
      boxes = conf['boxes']
      boxes[get('box', '')]
    end
end

# An instance of a configured single machine
class Machine
  private

    def conf
      ConfigFile.conf
    end

    # works since vagrant is single threaded
    def self.machine_number
      @@counter ||= 1
      c = @@counter
      @@counter += 1
      c
    end

    def setup_storage_device(device_file, size, controller, port)
      @server.vm.provider 'virtualbox' do |v|
        unless File.exist?(device_file)
          v.customize ['createhd', '--filename', device_file,
                       '--size', size * 1024]
        end
        v.customize ['storageattach', :id,
                     '--storagectl', controller,
                     '--port', port, '--device', 0,
                     '--type', 'hdd', '--medium', device_file]
      end
    end

    def setup_storage_devices
      size = @conf.get('disk_size', 4)
      disk_num = @conf.get('disk', 0)

      controller = @conf.box['disk_controller']

      (1..disk_num).each do |did|
        device_file = "./disk_#{@conf.type}_#{@pid}_storage_#{did}.vdi"
        setup_storage_device(device_file, size, controller, did)
      end
    end

    def shell_provision
      commands = @conf.get('shell', [])
      commands.each do |c|
        @server.vm.provision 'shell', inline: c
      end
    end

    def ansible_cloud_provision
      return unless conf.key?('ansible_cloud')
      ac = conf['ansible_cloud']
      return unless ac.key?('playbook') && ac.key?('inventory_path')
      @server.vm.provision :ansible do |ansible|
        ansible.playbook = ac['playbook']
        ansible.inventory_path = ac['inventory_path']
        ansible.sudo = true
        # ansible.verbose = 'vvvv'
        ansible.limit = 'all'
      end
    end

    # setup cpu and memory
    def setup_basic_parameters
      # setup cpu and memory for the machine
      @server.vm.provider 'virtualbox' do |v|
        v.cpus = @conf.get('cpus', 1)
        v.memory = @conf.get('memory', 1024)
      end
    end

    def setup_box
      box = @conf.box
      @server.vm.box = box['box']
      @server.vm.box_url = box['box_url'] if box.key?('box_url')
    end

    def setup_network
      ip_address = @conf.ip(@pid)
      @server.vm.network 'private_network', ip: ip_address
      @server.vm.hostname = "#{@conf.type}#{@pid}"
    end

  public

    def initialize(vagrantserver, machineconf, id)
      @conf = machineconf
      @pid = id
      @server = vagrantserver
      @number = Machine.machine_number
    end

    def setup
      # each setup parameter can be local to a machine_type
      # or global

      # setup cpu and memory
      setup_basic_parameters

      # setup vagrant box and its url
      setup_box

      setup_storage_devices unless @conf.get('disk', 0) == 0

      setup_network

      # use default key , one for all , you dont really need
      # security for testing purposes , don't you ?
      @server.ssh.insert_key = false

      # provision shell
      shell_provision

      # run ansible provision only after the last machine is
      # set up , to set up to provision the whole cluster at once
      ansible_cloud_provision if @number == conf.machine_num
    end
end

Vagrant.configure(2) do |config|
  # setup dns virtual box to intercept dns requests
  # and convey it to host dns
  config.vm.provider :virtualbox do |vb|
    vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
    vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on']
  end

  ConfigFile.conf['machines'].keys.each do |m|
    machine_conf = MachineConfig.new(m)
    num = machine_conf.get('num', 0)
    (0..(num - 1)).each do |pid|
      config.vm.define "#{m}#{pid}" do |server|
        machine = Machine.new(server, machine_conf, pid)
        machine.setup
      end
    end
  end
end

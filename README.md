# swift-install
Ansible scripts to install Swift , on real or virtual vagrant environments. For details on Vagrant virtual cluster , and implementation see [Wiki](https://github.com/Open-I-Beam/swift-install/wiki).

Supported OS'es ,.Ubuntu >= 14.04 , Centos/RHEL >= 7

**the basic usage:**    
cd provisioning    
ansible-playbook -i inventory/swift_install_hosts main-install.yml

# Important!!!!   
1. Please check [Wikis dependencies section](https://github.com/Open-I-Beam/swift-install/wiki/Dependencies) before deploying 
2. The provisioning scripts are located at [provisioning](https://github.com/Open-I-Beam/swift-install/tree/master/provisioning) directory , and all ansible works should be done from there ( everything that is explained below)   


# [Inventory](http://docs.ansible.com/intro_inventory.html)
1. An example of hypothetical inventory with all minimal vars , required for an installation is located:     [provisioning/inventory](https://github.com/Open-I-Beam/swift-install/tree/master/provisioning/inventory)

## General Info
1. Inventory , with the hosts , and hostgroups definitions is defined in one file , and then can be used in ansible ad-hoc commands , and ansible-playbook commands , using **-i** switch, 
    * For example [swift_install_hosts](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/swift_install_hosts)

2. Plus 2 directories (and yml formatted files within them) , that reside in a **same directory** as the inventory file (above) , note the files within should have **no!!!!** extension
    * [host_vars](https://github.com/Open-I-Beam/swift-install/tree/master/provisioning/inventory/host_vars)
    * [group_vars](https://github.com/Open-I-Beam/swift-install/tree/master/provisioning/inventory/group_vars)

3. an example for running ansible [ad-hoc](http://docs.ansible.com/intro_adhoc.html) with the inventory
    * ```ansible -i inventory/swift_install_hosts swift-storage -m shell -a 'swift-init all status'```
       * check status of all swift services , for all hosts in swift-storage host group (if it is a defined host group in an inventory, inventory/swift_install_hosts)
    * ```ansible -i inventory/swift_install_hosts proxy1 -m shell -a 'swift-init all status'```
       * check status of all swift services , for proxy1 host (if it is a defined host in an inventory, inventory/swift_install_hosts)

4. an example of running ansible [playbook](http://docs.ansible.com/playbooks.html)
    * ```ansible-playbook -i inventory/swift_install_hosts main-install.yml```
        * deploy swift using inventory, inventory/swift_install_hosts

## [Hosts](http://docs.ansible.com/intro_inventory.html#hosts-and-groups)
1. For each host define its name and a way to access ,[in an iventory file](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/swift_install_hosts) , for example:
     * ```proxy1 ansible_ssh_host=10.0.0.121 ansible_ssh_user=root ansible_ssh_pass=passw0rd```
         * a host named (in ansible) **proxy1** (nothing to do with its real hostname)
         * ansible_ssh_host - has an ip **10.0.0.121** ( can be any valid url of the target host )
         * ansible_ssh_user - the user under which we will run the provisioning
             * the user must be either **sudo**'er or **root**
         * ansible_ssh_pass - the password for ssh connection , conversely the key can be used (see below)
         * also and ansible_ssh_port can be specified if the target port is not 22
         

  or if it is accessed by ssh_key:
     * ```proxy1 ansible_ssh_host=10.0.0.121 ansible_ssh_user=root ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key```
  
  the parameters should be specified in one line , using spaces between different vars and **'='** without spaces
  
2. You will need hosts , for the following services:
     * swift-proxy service
     * swift-storage services (currently have the same installation policy for all of the three)
         * object  
         * container
         * account
     * keystone(optionally) , note that if you don't want ot install a keystone service , just remove the line ```- include: keystone.yml``` in [main-install.yml](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/main-install.yml)

3. A variables for Host1 are located at (relatively to the inventory file path), host_vars/Host1 

4. A one host may serve for more than one service , moreover all services can be installed on one , **allinone** host (see Host Groups)


## [Host Groups](http://docs.ansible.com/intro_inventory.html#hosts-and-groups)
1. Each Host Group represents a type of a service that will be installed
2. Each Host Group aggregates many hosts
3. Each Host may belong to many Host Groups
4. [Each Host Group may consist of many Host Groups](http://docs.ansible.com/intro_inventory.html#groups-of-groups-and-group-variables)
5. The variables of Host Group HG1 are located at a file (relatively to the inventory file path), group_vars/HG1
6. [**You will have to define host groups**](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/swift_install_hosts)
    * [swift-proxy](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-proxy)
        * Defines the swift hosts that will run the [swift proxy server service](http://docs.openstack.org/juno/config-reference/content/proxy-server-configuration.html) 
    * [swift-storage](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-storage)
        * Defines hosts that will run , swift [object](http://docs.openstack.org/juno/config-reference/content/object-server-configuration.html) ,[account](http://docs.openstack.org/juno/config-reference/content/account-server-configuration.html) and [container](http://docs.openstack.org/juno/config-reference/content/container-server-configuration.html) services 
        * In an [example inventory](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/swift_install_hosts) I have separated this group into 2 groups: ```[swift-storage:children]     
swift-object    
swift-md``` (see bullet 4 above) , such that
             * I can separate variables that common to [object servers](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-object)
             * From variables that are common to [account and container servers](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-md)
    * [swift-ring-builder](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-ring-builder)
        * Contains exactly one host host , ay from swift-storage or swift-proxy groups
    * keystone(optional)
        * Contains exactly one host where keystone service will be installed 
    * You can optionally define a group swift-client


## [Variables](http://docs.ansible.com/playbooks_variables.html)
1. For example if in an [inventory file](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/swift_install_hosts) we have a host [md1](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/host_vars/md1) , which is a part of a group [swift-md](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-md) , which byitself is a subgroup of a group [swift-storage](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-storage) ,then each playbook or an adhoc command that applied on a swift-storage group , while running on host md1 will:
    * see vars from the following locations
        * [group_vars/all](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/all)
        * [group_vars/swift-storage](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-storage)
        * [group_vars/swift-md](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-md)
        * [host_vars/md1](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/host_vars/md1)
    * With the following precidence:
        * all < swift-storage < swift-md < md1 
2. The following variables should be declared: ( remember that in a case of a different configuration of a specific host, the variable can be redefined in its group_vars/host file for some specific host)
    * in [group_vars/all](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/all):    
         * global_log_verbose: False
         * global_log_debug: False
         * keystone_endpoint_host - an ip address , or hostname of a keystone endpoint
         * keystone_internal_url: http://{{ keystone_endpoint_host }}:5000/v2.0
         * keystone_admin_url: http://{{ keystone_endpoint_host }}:35357/v2.0
         * keystone_public_url: http://{{ keystone_endpoint_host }}:5000/v2.0
         * keystone_admin_token - the security admin token of keystone 
         * keystone_admin_password - the password of admin keystone
         * swift_identity_password - the password of swift admin user in keystone
         * swift_hash_path_prefix - a random string fo security
         * swift_hash_path_suffix - a random string for security
         * log_swift_statsd - true if you want swift to report statsd statistics
         * openstack_version - kilo or juno ( affects both packages and config file templates)
         * installation_source - git or packages
         * swift_git - swift git repository in a case , installation_source == 'git'
         * swift_git_dir - a temporary directory to clone a swift code to , in a case installation_source == 'git'
         * swift_git_tag - the tag of a git ( a version of swift ) to clone 
    * in [group_vars/swift-storage](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-storage) , (a union of [group_vars/swift-md](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-md) and [group_vars/swift-object](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-object) in our case):
         * account_server_port - the port on which account service will listen
         * container_server_port - the port on which container service will listen
         * object_server_port - the port on which object service will listen
         * swift_devices - 
            * a dictionary with 3 lists
               * object_devices
               * container_devices
               * account_devices
            * each list is a list of dictionaries in the following format (each entry represents a storage device ):
               * name - the name of the device in a /dev directory 
                   * for example sdr , for /dev/sdr
               * weight - the weight of the device in an appropriate swift ring
                   * for example 100 
               * fs - a filesystem to be formatted on a device
                   * xfs or ext4 
         * In addition for each Host in this group in its [host_vars/host](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/host_vars/object1) file define the following vars:
            * rings_info - a dictionary with the following fields
               * ip - the ip the services will bind to on this host 
               * zone - the zone of this host 
                  * a number >=1
                  * each host is adviced to be in different zone
               * region - the region of this host
                  * a number >=1
    * in [group_vars/swift-proxy](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/group_vars/swift-proxy) file define the following vars:
        * proxy_server_port - the port proxy server will bind to 

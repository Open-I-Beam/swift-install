# swift-install
Ansible scripts to install Swift , on real or virtual vagrant environments. For details on Vagrant virtual cluster , and implementation see [Wiki](https://github.com/Open-I-Beam/swift-install/wiki).

Supported OS'es ,.Ubuntu >= 14.04 , Centos/RHEL >= 7

# [Inventory](http://docs.ansible.com/intro_inventory.html)


## General Info
1. Inventory , with the hosts , and hostgroups definitions is defined in one file , and then can be used in ansible ad-hoc commands , and ansible-playbook commands , using **-i** switch, 
    * For example [inventory/swift_install_hosts](https://github.com/Open-I-Beam/swift-install/blob/master/provisioning/inventory/swift_install_hosts)

2. Plus 2 directories (and yml formatted files within them) , that reside in a **same directory** as the inventory file (above) , note the files within should have **no!!!!** extension
    * host_vars
    * group_vars

3. an example for running ansible [ad-hoc](http://docs.ansible.com/intro_adhoc.html) with the inventory
    * ```ansible -i inventory/swift_install_hosts swift-storage -m shell -a 'swift-init all status'```
       * check status of all swift services , for all hosts in swift-storage host group (if it is a defined host group in an inventory, inventory/swift_install_hosts)
    * ```ansible -i inventory/swift_install_hosts proxy1 -m shell -a 'swift-init all status'```
       * check status of all swift services , for proxy1 host (if it is a defined host in an inventory, inventory/swift_install_hosts)

4. an example of running ansible [playbook](http://docs.ansible.com/playbooks.html)
    * ```ansible-playbook -i inventory/swift_install_hosts main-install.yml```
        * deploy swift using inventory, inventory/swift_install_hosts

## Hosts
1. For each host define its name and a way to access (in an iventory file) , for example:
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
     * keystone(optionally) , note that if you don't want ot install a keystone service , just remove the line ```- include: keystone.yml``` in main-install.yml

3. A one host may serve for more than one service , moreover all services can be installed on one , **allinone** host (see Host Groups)


## Host Groups 


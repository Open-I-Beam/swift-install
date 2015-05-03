# swift-install
Ansible scripts to install Swift , on real or virtual vagrant environments. For further details see Wiki.

Supported OS'es ,.Ubuntu >= 14.04 , Centos/RHEL >= 7

# Inventory

## General Info
1. Inventory , with the hosts , and hostgroups definitions ared defined in one file , and then can be used in ansible ad-hoc commands , and ansible-playbook commands , using **-i** switch, 

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

3. A one host may serve for more than for one service , moreover all services can be installed on one , **allinone** host (see Host Groups)


## Host Groups 


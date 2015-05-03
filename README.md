# swift-install
Ansible scripts to install Swift , on real or virtual vagrant environments. For further details see Wiki.

Supported OS'es ,.Ubuntu >= 14.04 , Centos/RHEL >= 7

# Inventory

## Hosts
1. For each host define its name and a way to access (in an iventory file) , for example:
     * ```proxy1 ansible_ssh_host=10.0.0.121 ansible_ssh_user=root ansible_ssh_pass=passw0rd```

  or if it is accessed by ssh_key:
     * ```proxy1 ansible_ssh_host=10.0.0.121 ansible_ssh_user=root ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key```
     
2. You will need hosts , for the following services:
     * swift-proxy service
     * swift-storage services (currently have the same installation policy for all of the three)
         * object  
         * container
         * account
     * keystone(optionally) , note that if you don't want ot install a keystone service , just remove the line ```- include: keystone.yml``` in main-install.yml

3. A one host may serve for more than for one service , moreover all services can be installed on one , **allinone** host (see Host Groups)

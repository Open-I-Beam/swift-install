# swift-install
Ansible scripts to install Swift , on real or virtual vagrant environments. For further details see Wiki.

Supported OS'es ,.Ubuntu >= 14.04 , Centos/RHEL >= 7

# Inventory

## Hosts
1. For each host define its name and a way to access (in an iventory file) , for example:
     * ```proxy1 ansible_ssh_host=10.0.0.121 ansible_ssh_user=root ansible_ssh_pass=passw0rd```

  or if it is accessed by ssh_key:
     * ```proxy1 ansible_ssh_host=10.0.0.121 ansible_ssh_user=root ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key```

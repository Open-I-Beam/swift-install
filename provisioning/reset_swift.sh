ansible-playbook -i swift_install_inventory.py swift-stop.yml 
ansible-playbook -i swift_install_inventory.py swift-storage-reset.yml 
ansible-playbook -i swift_install_inventory.py swift-start.yml 

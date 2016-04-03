ansible-playbook -i swift_dynamic_inventory.py swift-stop.yml 
ansible-playbook -i swift_dynamic_inventory.py swift-storage-reset.yml 
ansible-playbook -i swift_dynamic_inventory.py swift-start.yml 

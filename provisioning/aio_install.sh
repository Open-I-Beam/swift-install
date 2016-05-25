# The script takes a block device name as an optional parameter
# The device name can be either 'loop0' or any block device under /dev
# that can be formatted and mounted as a Swift device.
# The script assume it 'can sudo'


function usage() {
    echo "Usage: $0 [device-name]";
}

if [ "$#" -eq 0 ]; then
    DEVICE='loop0'
elif [ "$#" -eq 1 ]; then
    DEVICE=$1
    if [ $DEVICE != 'loop0' ] &&  [ ! -b "/dev/$DEVICE" ]; then
        echo "$DEVICE is not a block device"
        exit
    fi
else
    usage
    exit
fi

sudo mkdir -p /srv
sudo truncate -s 1GB /srv/swift-disk
sudo losetup /dev/loop0 /srv/swift-disk

if [ -z cluster_config.json]; then
    cp aio_cluster_config.json-sample cluster_config.json 
    sed -i 's/<set device!>/'$DEVICE'/g' cluster_config.json
fi

ansible-playbook -s -i swift_dynamic_inventory.py main-install.yml

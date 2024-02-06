import fcntl
import struct
import os
from parse_data import parse_pci_data
import json
import argparse
import sys


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-f', '--format', default='no_format')

    return parser




# IOCTL команды
VENDOR_DEVICE_INFO = 0x81
DEVICE_NUM = 0x82

# Определение структуры pci_data
pci_data_format = 'HHHHII'

def main():
    try:
        parser = createParser()
        namespace = parser.parse_args(sys.argv[1:])

        device_file = "/dev/my_pci_device"
        fd = os.open(device_file, os.O_RDWR)

        num_devices = struct.pack('i', 0)
        num_devices = fcntl.ioctl(fd, DEVICE_NUM, num_devices)
        num_devices = struct.unpack('i', num_devices)[0]
        print("Number of devices:", num_devices)



        data=(0,0,0,0,0,0)*num_devices
        # Получаем массив pci_data через IOCTL
        pci_data_array = struct.pack(pci_data_format * num_devices, *data)  # Device 5
        pci_data_array = fcntl.ioctl(fd, VENDOR_DEVICE_INFO, pci_data_array)
        unpacked_data = struct.unpack(pci_data_format * num_devices, pci_data_array)


        if namespace.format not in ('json','string','no_format'):
            print('!!!Entered format not found!!!')
            namespace.format='no_format'

        if namespace.format=='json':
            strjs=parse_pci_data(unpacked_data)
            print(json.dumps(strjs,indent=1))
        elif namespace.format== 'no_format':
            for i in range(num_devices):
                print(f"Device {i + 1} - Vendor ID: {hex(unpacked_data[i * 6])}, Device ID: {hex(unpacked_data[i * 6 + 1])}, , subvend: {hex(unpacked_data[i * 6 + 2])}, subdev: {hex(unpacked_data[i * 6 + 3])},  Class: {hex(unpacked_data[i * 6 + 4])},  rev: {unpacked_data[i * 6 + 5]}")
        elif namespace.format=='string':
            strjs=parse_pci_data(unpacked_data)
            for i,dev in enumerate(strjs):
                if 'Revision' in dev:
                    print(dev['Class'], ": ",dev['Vendor'],dev['Device'],',rev:',str(dev['Revision']))
                else:
                    print(dev['Class'], ": ",dev['Vendor'],dev['Device'] )




        # Закрываем файл устройства
        os.close(fd)

    except IOError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

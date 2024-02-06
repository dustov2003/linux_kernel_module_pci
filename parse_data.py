from LxmlSoup import LxmlSoup
import requests
import json



fl=open('path.json','r')
pci_json=json.load(fl)
fl.close()

def id_key(num):
    temp=hex(num)[2:]
    while len(temp)<4:
        temp='0'+temp
    return temp


def parse_class(pci_class):
    clhex='/0'+hex(pci_class)[2]+'/'+hex(pci_class)[3:5]
    html = requests.get('https://admin.pci-ids.ucw.cz/read/PD'+clhex).text
    soup = LxmlSoup(html)
    return soup.find_all('div',class_='name')[0].find_all('p')[0].text()[6:]

def parse_pci_data(pci_arr):
    num_dev=len(pci_arr)//6
    pci_data=[]
    for i in range(num_dev):
        dt=dict()
        vendor_id=id_key(pci_arr[i*6])
        dev_id=id_key(pci_arr[i*6+1])
        dt['Class']=parse_class(pci_arr[i*6+4])
        dt['Full_class']=hex(pci_arr[i*6+4])
        dt['Vendor']=pci_json[vendor_id]['name']
        dt['Device']=pci_json[vendor_id]['devices'][dev_id]['name']
        # if pci_arr[i*6+2]!=0 and (pci_arr[i*6]!=pci_arr[i*6+2] and pci_arr[i*6+1]!=pci_arr[i*6+3] ):
        #     subvend=id_key(pci_arr[i*6+2])
        #     subdev=id_key(pci_arr[i*6+3])
        #     dt['Subsystem']=pci_json[vendor_id]['devices'][dev_id]['subsystems'][subvend+' '+subdev]['name']
        if pci_arr[i*6+5]!=0:
            dt['Revision']=pci_arr[i*6+5]
        pci_data.append(dt)
    return pci_data



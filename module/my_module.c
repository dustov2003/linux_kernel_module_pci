#include <linux/module.h>
#include <linux/pci.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/ioctl.h>
#include <linux/slab.h>
#include "struct_pci.h"
#define VENDOR_DEVICE_INFO 0x81 // IOCTL команда
#define DEVICE_NUM 0x82

static dev_t dev_num;
static struct cdev my_cdev;
static struct class *my_class;
static int pci_nums=0;


static int my_open(struct inode *inode, struct file *file) {
    printk(KERN_INFO "Device file opened\n");
    return 0;
}

static int count_devs(void){
    struct pci_dev *pdev = NULL;
    int res=0;
    for_each_pci_dev(pdev) res++;
    return res;
}

static long send_data( unsigned long arg){
    printk(KERN_INFO "PCI_NUMS: %d\n",pci_nums);
    struct pci_data pdata[11];
    int i=0;
    struct pci_dev* pdev=NULL;
    for_each_pci_dev(pdev){
        pdata[i].vendor = pdev->vendor;
        pdata[i].device = pdev->device;
        pdata[i].subsystem_vendor = pdev->subsystem_vendor;
        pdata[i].subsystem_device = pdev->subsystem_device;
        pdata[i].class = pdev->class;
        pdata[i].rev = pdev->revision;
        i++;
    }

    if (copy_to_user((int *)arg, &pdata, sizeof(struct pci_data)*pci_nums) != 0) {
        return -EFAULT; // Ошибка копирования данных в пространство пользователя
    }
    return 0;
}











static long my_ioctl(struct file *file, unsigned int cmd, unsigned long arg) {
    switch (cmd) {
        case VENDOR_DEVICE_INFO:
            return send_data(arg);
            break;
        case DEVICE_NUM:
            pci_nums=count_devs();
            if (copy_to_user((int *)arg, &pci_nums, sizeof(int)) != 0) {
                return -EFAULT; // Ошибка копирования данных в пространство пользователя
            }
            break;

        default:
            return -ENOTTY; // Неизвестная команда ioctl
    }

    return 0;
}

static const struct file_operations my_fops = {
        .owner = THIS_MODULE,
        .open = my_open,
        .unlocked_ioctl = my_ioctl,
};

static int __init my_init(void) {
    int ret;

    // Регистрация устройства символьного типа
    ret = alloc_chrdev_region(&dev_num, 0, 1, "my_pci_device");
    if (ret < 0) {
        printk(KERN_ALERT "Failed to allocate character device region\n");
        return ret;
    }

    cdev_init(&my_cdev, &my_fops);
    ret = cdev_add(&my_cdev, dev_num, 1);
    if (ret < 0) {
        unregister_chrdev_region(dev_num, 1);
        printk(KERN_ALERT "Failed to add character device\n");
        return ret;
    }

    my_class = class_create( "my_pci_class");
    device_create(my_class, NULL, dev_num, NULL, "my_pci_device");

    printk(KERN_INFO "PCI Device Info module initialized\n");

    return 0;
}

static void __exit my_exit(void) {
    device_destroy(my_class, dev_num);
    class_destroy(my_class);
    cdev_del(&my_cdev);
    unregister_chrdev_region(dev_num, 1);

    printk(KERN_INFO "PCI Device Info module unloaded\n");
}

module_init(my_init);
module_exit(my_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("PCI Device Info Module");

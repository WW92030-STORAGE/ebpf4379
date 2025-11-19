obj-m += setstarts_mod.o
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

# sudo insmod setvalue_mod.ko
# echo 42 | sudo tee /proc/set_shared_value
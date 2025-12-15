obj-m += setestimate_mod.o
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

# sudo insmod setestimate_mod.ko
# echo 0 | sudo tee /proc/set_estimate 
# echo 1 | sudo tee /proc/set_estimate 
# echo 2 | sudo tee /proc/set_estimate 

# 0 never 1 sometimes 2 always
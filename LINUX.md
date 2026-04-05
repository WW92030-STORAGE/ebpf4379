# ebpf4379

Build the modified CBMM-like Linux kernel. PLEASE DO THIS ON A VIRTUAL MACHINE RUNNING UBUNTU 24.04. I USE A CLOUDLAB MACHINE WHICH MEANS THE BASE KERNEL IS 6.8.

```
sudo apt update && sudo apt install -y build-essential libncurses-dev bison flex libssl-dev libelf-dev fakeroot dwarves bpfcc-tools python3-venv libslang2-dev libperl-dev python3-dev liblzma-dev libnuma-dev pkg-config libtraceevent-dev linux-headers-$(uname -r)

sudo git clone https://github.com/WW92030-STORAGE/ebpf4379.git && sudo git clone https://github.com/WW92030-STORAGE/scea_linux.git

cd scea_linux/kbuild

sudo make -C .. O=$(pwd) oldconfig && sudo make clean && sudo make -j32 && sudo make -j32 bindeb-pkg LOCALVERSION=-my-k && sudo make clean && sudo make clean && cd .. && sudo dpkg -i linux-headers* linux-image-* && sudo rm -r -f linux-* && sudo reboot

```
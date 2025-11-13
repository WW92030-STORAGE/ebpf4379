import bcc
from bcc import BPF
import time

prog = r"""
#include <uapi/linux/ptrace.h>
#include <linux/errno.h>
int inject(struct pt_regs *ctx) {
    bpf_override_return(ctx, 1000000);
    return 0;
}
"""
b = BPF(text=prog)
b.attach_kprobe(event="compute_hpage_benefit", fn_name="inject")
print("Injecting ENOMEM into compute_hpage_benefit (watch dmesg)... Ctrl-C to exit")
try:
    time.sleep(9999)
except KeyboardInterrupt:
    pass

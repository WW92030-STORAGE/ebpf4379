#!/usr/bin/env python3
from bcc import BPF
from time import sleep

bpf_program = r"""
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>

int probe_create_huge_pmd(struct pt_regs *ctx)
{
    struct vm_fault *vmf;
    unsigned long addr = 0;

    /* First argument: struct vm_fault *vmf */
    vmf = (struct vm_fault *)PT_REGS_PARM1(ctx);

    /* Safely read vmf->address */
    bpf_probe_read_kernel(&addr, sizeof(addr), &vmf->address);

    bpf_trace_printk("create_huge_pmd fault addr: 0x%lx\n", addr);
    return 0;
}
"""

b = BPF(text=bpf_program)

# Attach kprobe
b.attach_kprobe(
    event="create_huge_pmd",
    fn_name="probe_create_huge_pmd"
)

print("Probing create_huge_pmd... Ctrl-C to exit.")
print("%-18s %-16s %s" % ("TIME(s)", "PID", "MESSAGE"))

try:
    b.trace_print()
except KeyboardInterrupt:
    pass

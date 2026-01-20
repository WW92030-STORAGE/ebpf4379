from bcc import BPF
from time import sleep

# Print out the addresses of faults
prog = """
#include <uapi/linux/ptrace.h>
int probe_handle_mm_fault(struct pt_regs *ctx)
{
    unsigned long addr = PT_REGS_PARM2(ctx);
    
    bpf_trace_printk("addr: 0x%lx\\n", addr);
    return 0;
}
"""

b = BPF(text=prog)
b.attach_kprobe(event="handle_mm_fault", fn_name="probe_handle_mm_fault")

print("Tracing... Ctrl-C to stop.")

b.trace_print()

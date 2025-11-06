#!/usr/bin/env python3
# trace_handle_mm_fault.py
#
# Minimal BCC tracer to print input + return value of handle_mm_fault.
#
# Usage: sudo python3 trace_handle_mm_fault.py
#

from bcc import BPF
import ctypes, sys, time

bpf_text = r"""
#include <uapi/linux/ptrace.h>

struct data_in_t {
    u64 mm_ptr;
    u64 vma_ptr;
    u64 address;
    u32 flags;
    u32 pad;
};

struct data_out_t {
    int ret;
};

BPF_PERF_OUTPUT(events_in);
BPF_PERF_OUTPUT(events_out);

int probe_handle_mm_fault(struct pt_regs *ctx) {
    struct data_in_t evt = {};
    evt.mm_ptr  = (u64)PT_REGS_PARM1(ctx);
    evt.vma_ptr = (u64)PT_REGS_PARM2(ctx);
    evt.address = (u64)PT_REGS_PARM3(ctx);
    evt.flags   = (u32)PT_REGS_PARM4(ctx);
    events_in.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

int retprobe_handle_mm_fault(struct pt_regs *ctx) {
    struct data_out_t evt = {};
    evt.ret = (int)PT_REGS_RC(ctx);
    events_out.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
"""

# Load and compile
b = BPF(text=bpf_text)

# Try both possible symbol names
attached = False
for sym in ("handle_mm_fault", "__handle_mm_fault"):
    try:
        b.attach_kprobe(event=sym, fn_name="probe_handle_mm_fault")
        b.attach_kretprobe(event=sym, fn_name="retprobe_handle_mm_fault")
        print(f"Attached kprobe + kretprobe to {sym}")
        attached = True
        break
    except:
        pass

if not attached:
    print("ERROR: Could not attach kprobe/kretprobe")
    sys.exit(1)

# Userspace ctypes
class DataIn(ctypes.Structure):
    _fields_ = [
        ("mm_ptr", ctypes.c_uint64),
        ("vma_ptr", ctypes.c_uint64),
        ("address", ctypes.c_uint64),
        ("flags", ctypes.c_uint32),
        ("pad", ctypes.c_uint32),
    ]

class DataOut(ctypes.Structure):
    _fields_ = [
        ("ret", ctypes.c_int),
    ]

def print_in(cpu, data, size):
    ev = ctypes.cast(data, ctypes.POINTER(DataIn)).contents
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] handle_mm_fault(entry):")
    print(f"  mm_ptr  = 0x{ev.mm_ptr:016x}")
    print(f"  vma_ptr = 0x{ev.vma_ptr:016x}")
    print(f"  address = 0x{ev.address:016x} ({ev.address})")
    print(f"  flags   = 0x{ev.flags:x} ({ev.flags})")
    print("")

def print_out(cpu, data, size):
    ev = ctypes.cast(data, ctypes.POINTER(DataOut)).contents
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] handle_mm_fault(return): ret={ev.ret}")
    print("")

b["events_in"].open_perf_buffer(print_in)
b["events_out"].open_perf_buffer(print_out)

print("Tracing handle_mm_fault entry + return — Ctrl-C to quit")
try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    print("Detaching...")

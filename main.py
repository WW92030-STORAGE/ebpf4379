#!/usr/bin/env python3
#
# mm_estimate_changes_trace.py
#
# Minimal BCC + eBPF program to print the contents of:
#   struct mm_action * (arg1)
#   struct mm_cost_delta * (arg2)
#
# Usage: sudo python3 mm_estimate_changes_trace.py
#

from bcc import BPF
import ctypes
import sys

bpf_text = r"""
#include <uapi/linux/ptrace.h>

// Mirror of the user's structs (simple, natural alignment).
struct mm_cost_delta_t {
    long long tlb_misses;
    long long page_fault_freq;
    long long kernel_computation;
    unsigned long long cost;
    unsigned long long benefit;
    unsigned long long extra;
};

struct mm_action_t {
    int action;
    // pad to align the next u64 on 8 bytes on 64-bit arch
    unsigned int _pad;
    unsigned long long address;
    unsigned long long param; // union field (huge_page_order / prezero_n / len / unused)
};

// Combined event sent to userspace
struct event_t {
    struct mm_action_t act;
    struct mm_cost_delta_t delta;
};

BPF_PERF_OUTPUT(events);

int kprobe__mm_estimate_changes(struct pt_regs *ctx) {
    void *act_ptr = (void *)PT_REGS_PARM1(ctx);
    void *delta_ptr = (void *)PT_REGS_PARM2(ctx);

    struct event_t evt = {};
    // Attempt to safely read kernel memory where the pointers point to
    // Use bpf_probe_read (works for kernel memory reads).
    if (act_ptr) {
        bpf_probe_read(&evt.act, sizeof(evt.act), act_ptr);
    }
    if (delta_ptr) {
        bpf_probe_read(&evt.delta, sizeof(evt.delta), delta_ptr);
    }

    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
"""

# Load BPF program
b = BPF(text=bpf_text)

# Define the matching Python ctypes structures
class MmCostDelta(ctypes.Structure):
    _fields_ = [
        ("tlb_misses", ctypes.c_longlong),
        ("page_fault_freq", ctypes.c_longlong),
        ("kernel_computation", ctypes.c_longlong),
        ("cost", ctypes.c_ulonglong),
        ("benefit", ctypes.c_ulonglong),
        ("extra", ctypes.c_ulonglong),
    ]

class MmAction(ctypes.Structure):
    _fields_ = [
        ("action", ctypes.c_int),
        ("_pad", ctypes.c_uint),
        ("address", ctypes.c_ulonglong),
        ("param", ctypes.c_ulonglong),
    ]

class Event(ctypes.Structure):
    _fields_ = [
        ("act", MmAction),
        ("delta", MmCostDelta),
    ]

# callback for perf events
def print_event(cpu, data, size):
    ev = ctypes.cast(data, ctypes.POINTER(Event)).contents
    a = ev.act
    d = ev.delta

    print("=== mm_estimate_changes called ===")
    print(f"action.action = {a.action}")
    print(f"action.address = 0x{a.address:x}")
    print(f"action.param = {a.param}")
    print("mm_cost_delta:")
    print(f"  tlb_misses         = {d.tlb_misses}")
    print(f"  page_fault_freq    = {d.page_fault_freq}")
    print(f"  kernel_computation = {d.kernel_computation}")
    print(f"  cost               = {d.cost}")
    print(f"  benefit            = {d.benefit}")
    print(f"  extra              = {d.extra}")
    print("")

# Open perf buffer and loop
b["events"].open_perf_buffer(print_event)

print("Tracing mm_estimate_changes() — press Ctrl-C to exit")
try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    print("Detaching and exiting...")
    sys.exit(0)

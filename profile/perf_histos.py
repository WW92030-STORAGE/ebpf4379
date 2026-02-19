#!/usr/bin/env python3
from bcc import BPF
import ctypes as ct
import os
import fcntl
import struct

import ctypes.util

libc = ct.CDLL(ctypes.util.find_library("c"), use_errno=True)

# syscall number for perf_event_open on x86_64
SYS_perf_event_open = 298

# ------------------------------------------------------------------
# perf_event_open syscall wrapper
# ------------------------------------------------------------------

PERF_TYPE_RAW = 4
PERF_SAMPLE_IP        = 1 << 0
PERF_SAMPLE_TID       = 1 << 1
PERF_SAMPLE_ADDR      = 1 << 3
PERF_SAMPLE_DATA_SRC  = 1 << 15

PERF_FLAG_FD_CLOEXEC = 8

# Haswell PEBS encoding for:
# MEM_LOAD_UOPS_RETIRED.L3_MISS
EVENT_CONFIG = 0x01d3  # raw event select (Intel SDM)

def perf_event_open(attr, pid, cpu, group_fd, flags):
    ret = libc.syscall(
        SYS_perf_event_open,
        ct.byref(attr),
        ct.c_int(pid),
        ct.c_int(cpu),
        ct.c_int(group_fd),
        ct.c_ulong(flags),
    )

    if ret < 0:
        errno = ct.get_errno()
        raise OSError(errno, "perf_event_open failed")

    return ret

class perf_event_attr(ct.Structure):
    _fields_ = [
        ("type", ct.c_uint),
        ("size", ct.c_uint),
        ("config", ct.c_ulonglong),
        ("sample_period", ct.c_ulonglong),
        ("sample_type", ct.c_ulonglong),
        ("read_format", ct.c_ulonglong),

        ("flags", ct.c_ulonglong),   # includes precise_ip etc.

        ("wakeup_events", ct.c_uint),
        ("bp_type", ct.c_uint),
        ("bp_addr", ct.c_ulonglong),
        ("bp_len", ct.c_ulonglong),

        # kernel expects full size even if unused
        ("branch_sample_type", ct.c_ulonglong),
        ("sample_regs_user", ct.c_ulonglong),
        ("sample_stack_user", ct.c_uint),
        ("clockid", ct.c_int),
        ("sample_regs_intr", ct.c_ulonglong),
        ("aux_watermark", ct.c_uint),
        ("sample_max_stack", ct.c_ushort),
        ("__reserved_2", ct.c_ushort),
        ("aux_sample_size", ct.c_uint),
        ("__reserved_3", ct.c_uint),
    ]


# ------------------------------------------------------------------
# eBPF program
# ------------------------------------------------------------------

bpf_source = r"""
#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf_perf_event.h>
#include <uapi/linux/bpf.h>

struct data_t {
    u64 pid;
    u64 addr;
    u64 ip;
};

BPF_RINGBUF_OUTPUT(events, 1024);

int on_sample(struct bpf_perf_event_data *ctx)
{
    struct data_t *d;

    d = events.ringbuf_reserve(sizeof(*d));
    if (!d)
        return 0;

    d->pid  = bpf_get_current_pid_tgid() >> 32;
    d->addr = ctx->addr;   // <-- actual accessed memory address
    d->ip   = PT_REGS_IP(&ctx->regs);

    events.ringbuf_submit(d, 0);
    return 0;
}
"""

b = BPF(text=bpf_source)

prog_fn = b.load_func("on_sample", BPF.PERF_EVENT)
prog_fd = prog_fn.fd

# ------------------------------------------------------------------
# open perf event per CPU and attach BPF
# ------------------------------------------------------------------

def open_pebs(cpu):
    attr = perf_event_attr()
    attr.type = PERF_TYPE_RAW
    attr.size = ct.sizeof(perf_event_attr)
    attr.config = EVENT_CONFIG
    attr.sample_period = 1000
    attr.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_ADDR | PERF_SAMPLE_DATA_SRC
    attr.flags = (1 << 0)  # disabled=0
    attr.flags |= (2 << 15)  # precise_ip = 2 (PEBS required)
    attr.wakeup_events = 1

    fd = perf_event_open(attr, -1, cpu, -1, PERF_FLAG_FD_CLOEXEC)
    if fd < 0:
        raise OSError("perf_event_open failed")

    # Attach BPF to perf FD (modern replacement)
    fcntl.ioctl(fd, 0x2408, struct.pack("I", prog_fd))  # PERF_EVENT_IOC_SET_BPF
    fcntl.ioctl(fd, 0x2400, 0)        # PERF_EVENT_IOC_ENABLE

    return fd

fds = []
for cpu in range(os.cpu_count()):
    fds.append(open_pebs(cpu))

# ------------------------------------------------------------------
# receive events
# ------------------------------------------------------------------

class Data(ct.Structure):
    _fields_ = [
        ("pid", ct.c_ulonglong),
        ("addr", ct.c_ulonglong),
        ("ip", ct.c_ulonglong),
    ]

def handle(ctx, data, size):
    e = ct.cast(data, ct.POINTER(Data)).contents
    print(f"PID {e.pid:<6} IP 0x{e.ip:x}  ADDR 0x{e.addr:x}")

b["events"].open_ring_buffer(handle)

print("Sampling memory accesses... Ctrl-C to stop.")
while True:
    b.ring_buffer_poll()

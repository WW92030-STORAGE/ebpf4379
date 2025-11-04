#!/usr/bin/env python3
# faultret_hist.py: histogram return values of page-fault handlers
# Requires: bcc (pip install bcc) and root privileges.

from bcc import BPF
import argparse
import signal
import sys
import time

BPF_PROGRAM = r"""
#include <uapi/linux/ptrace.h>

BPF_HISTOGRAM(rv_hist, u64, 256);

int trace_ret(struct pt_regs *ctx)
{
    u64 rv = PT_REGS_RC(ctx);
    // Clamp into 0..255 so we can use a compact linear histogram.
    if (rv > 255) rv = 255;
    rv_hist.increment(rv);
    return 0;
}
"""

def pick_target(bpf, user_func):
    if user_func:
        return user_func

    # Priority list (most stable first for return values)
    candidates = [
        b"handle_mm_fault",      # returns vm_fault_t (bitmask)
        b"do_user_addr_fault",   # returns int on several arches
        b"__do_page_fault",      # sometimes returns int on non-x86
        b"do_page_fault",        # often void (may fail to attach or no RC)
        b"page_fault",           # x86 name in some kernels (often void)
    ]
    avail = set(bpf.get_kprobe_functions(b".*"))
    for c in candidates:
        if c in avail:
            return c.decode()
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Track return values of page fault handling in a histogram."
    )
    parser.add_argument("-f", "--func", help="Function to kretprobe (default: auto-pick)")
    parser.add_argument("-i", "--interval", type=int, default=0,
                        help="Print and clear every N seconds (0 = only on exit)")
    args = parser.parse_args()

    b = BPF(text=BPF_PROGRAM)
    target = pick_target(b, args.func)
    if not target:
        print("Could not find a suitable fault-handling function to kretprobe.", file=sys.stderr)
        sys.exit(1)

    try:
        b.attach_kretprobe(event=target, fn_name="trace_ret")
    except Exception as e:
        print(f"Failed to attach kretprobe to {target}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Tracing return values of {target}... Hit Ctrl-C to end.")
    rv_hist = b.get_table("rv_hist")

    def dump(clear=True):
        # Print as linear histogram (bucket = exact return value)
        rv_hist.print_linear_hist("return value", "count")
        if clear:
            rv_hist.clear()

    def handle_sigint(sig, frame):
        print("\nDetaching and printing final histogram...\n")
        dump(clear=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    if args.interval <= 0:
        while True:
            time.sleep(999999)
    else:
        while True:
            time.sleep(args.interval)
            print()
            dump(clear=True)

if __name__ == "__main__":
    main()

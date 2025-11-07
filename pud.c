#define _GNU_SOURCE
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

int main(void) {
    const unsigned long G = 1UL << 30;   // 1GB
    const unsigned long SIZE = 2 * G;    // map 2GB
    void *p = mmap(NULL, SIZE, PROT_READ|PROT_WRITE,
                   MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    printf("mmap addr=%p\n", p);

    // Touch the mapping at a 1GB-aligned offset from p:
    // compute the next 1GB-aligned address within the mapping
    uintptr_t base = (uintptr_t)p;
    uintptr_t aligned = (base + (G - 1)) & ~(G - 1);
    if (aligned + 4096 > base + SIZE) {
        printf("mapping not large enough or alignment failed\n");
        return 1;
    }

    printf("touching aligned address %p\n", (void*)aligned);
    volatile char *c = (char*)aligned;
    *c = 42;   // fault + populate
    printf("touched\n");
    sleep(2);  // keep mapping alive so you can inspect /proc/meminfo/dmesg
    return 0;
}

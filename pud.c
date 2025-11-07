#define _GNU_SOURCE
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>     // <-- needed for uintptr_t

int main(void)
{
    const unsigned long G = 1UL << 30;   // 1GB
    const unsigned long SIZE = 2UL * G;  // map 2GB

    // Request mapping
    void *p = mmap(NULL, SIZE,
                   PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS,
                   -1, 0);

    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("Mapped %lu bytes at %p\n", SIZE, p);

    // Compute 1GB-aligned address inside the VMA
    uintptr_t base = (uintptr_t)p;
    uintptr_t aligned = (base + (G - 1)) & ~(G - 1);

    if (aligned + 4096 > base + SIZE) {
        printf("Mapping not large enough OR alignment failed\n");
        return 1;
    }

    printf("Touching aligned address %p\n", (void *)aligned);

    volatile char *c = (char *)aligned;
    *c = 42;      // page fault —> triggers transparent hugepage logic

    printf("Touched — write OK\n");
    sleep(2);     // keep mapping alive long enough to inspect meminfo/dmesg
    return 0;
}

// trigger_pmd_thp.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>

int main(void)
{
    size_t size = 2UL << 20;   // 2 MiB
    void *p;

    p = mmap(NULL, size,
             PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS,
             -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("mapped at %p\n", p);

    /* Touch first byte → page fault → handle_mm_fault()
       If THP conditions allow PMD order, create_huge_pmd() is used.
    */
    volatile char *c = p;
    for (size_t i = 0; i < size; i += 4096)
        c[i] = 1;

    printf("write done. Sleeping...\n");
    pause();
    return 0;
}

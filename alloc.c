#define _GNU_SOURCE
#include <sys/mman.h>
#include <stdio.h>
#include <stdlib.h>

#define MAP_HUGE_SHIFT 26
#define MAP_HUGE_1GB   (30 << MAP_HUGE_SHIFT)

int main(void)
{
    size_t size = 2UL << 30;   // 1 GiB

    void *p = mmap(NULL, size,
                   PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS |
                   MAP_HUGETLB |
                   MAP_HUGE_1GB,
                   -1, 0);

    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("Allocated 1GB huge page at %p\n", p);
    return 0;
}

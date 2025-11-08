#include <stdio.h>
#include <stdlib.h>

int main() {
    void *p = malloc(1UL << 30);   // allocate 1GB region
    if (!p) return 1;
    printf("%p\n", p);
    *(volatile char*)p = 1;       // page fault → kernel tries PUD THP
    return 0;
}

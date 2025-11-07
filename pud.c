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

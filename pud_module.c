// minimal_create_huge_pud.c
#include <linux/module.h>
#include <linux/mm.h>
#include <linux/mm_types.h>
#include <linux/mman.h>
#include <linux/sched.h>
#include <linux/highmem.h>
#include <linux/huge_mm.h>
#include <linux/vmalloc.h>

static int __init test_init(void)
{
    struct vm_area_struct *vma;
    struct vm_fault vmf = {0};
    unsigned long addr;
    int ret;

    pr_info("create_huge_pud test loaded\n");

    /* Allocate virtual memory region (1GB-aligned preferred) */
    addr = (unsigned long)vmalloc(1UL << 30);   // 1GB
    if (!addr) {
        pr_err("vmalloc failed\n");
        return -ENOMEM;
    }

    /* Obtain VMA for the current process */
    down_read(&current->mm->mmap_sem);
    vma = find_vma(current->mm, addr);
    up_read(&current->mm->mmap_sem);

    if (!vma) {
        pr_err("No VMA found\n");
        return -EINVAL;
    }

    vmf.vma     = vma;
    vmf.address = addr;
    vmf.pud     = pud_offset(p4d_offset(pgd_offset(current->mm, addr), addr), addr);

    if (!pud_none(*vmf.pud)) {
        pr_info("PUD already present, clearing\n");
        pud_clear(vmf.pud);
    }

    pr_info("Calling create_huge_pud...\n");
    ret = create_huge_pud(&vmf);

    pr_info("create_huge_pud returned %d\n", ret);

    if (!pud_none(*vmf.pud) && pud_present(*vmf.pud))
        pr_info("Success: PUD mapped\n");
    else
        pr_info("Fail: PUD not mapped\n");

    return 0;
}

static void __exit test_exit(void)
{
    pr_info("create_huge_pud test unloaded\n");
}

module_init(test_init);
module_exit(test_exit);
MODULE_LICENSE("GPL");

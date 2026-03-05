// set_starts_mod.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "scale_benefits"
#define BUFSIZE 64

/* Declare the real kernel function you already have.
 * It must be exported or have a visible symbol in kallsyms.
 */
extern void SCALE_BENEFITS(u64 index, u64 num, u64 denom);

static ssize_t proc_write(struct file *file,
                          const char __user *ubuf,
                          size_t count,
                          loff_t *ppos)
{
    char buf[BUFSIZE];
    u64 index, num, denom;

    if (count >= BUFSIZE)
        return -EINVAL;

    if (copy_from_user(buf, ubuf, count))
        return -EFAULT;

    buf[count] = '\0';

    /* Expect: "index value" */
    if (sscanf(buf, "%llu %llu %llu", &index, &num, &denom) != 3) {
        pr_info("increase_benefits: expected \"<index> <value> <positive>\"\n");
        return -EINVAL;
    }

    /* Call into your kernel code */
    INCREASE_BENEFITS(index, val, denom);

    pr_info("scale_benefits: INCREASE_BENEFITS(%llu, %llu, %llu)\n", index, num, denom);

    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init scale_benefits_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops);
    pr_info("scale_benefits_mod loaded\n");
    return 0;
}

static void __exit scale_benefits_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("scale_benefits_mod unloaded\n");
}

module_init(scale_benefits_init);
module_exit(scale_benefits_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose SCALE_BENEFITS(index, num, denom) via /proc/scale_benefits");

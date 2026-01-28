// set_starts_mod.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "increase_benefits"
#define BUFSIZE 64

/* Declare the real kernel function you already have.
 * It must be exported or have a visible symbol in kallsyms.
 */
extern void INCREASE_BENEFITS(u64 index, u64 val, bool POS);

static ssize_t proc_write(struct file *file,
                          const char __user *ubuf,
                          size_t count,
                          loff_t *ppos)
{
    char buf[BUFSIZE];
    u64 index, val, POS;

    if (count >= BUFSIZE)
        return -EINVAL;

    if (copy_from_user(buf, ubuf, count))
        return -EFAULT;

    buf[count] = '\0';

    /* Expect: "index value" */
    if (sscanf(buf, "%llu %llu %llu", &index, &val, &POS) != 3) {
        pr_info("increase_benefits: expected \"<index> <value> <positive>\"\n");
        return -EINVAL;
    }

    /* Call into your kernel code */
    INCREASE_BENEFITS(index, val, POS);

    pr_info("increase_benefits: INCREASE_BENEFITS(%llu, %llu, %llu)\n", index, val, POS);

    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init inc_benefits_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops);
    pr_info("increase_benefits_mod loaded\n");
    return 0;
}

static void __exit inc_benefits_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("increase_benefits_mod unloaded\n");
}

module_init(inc_benefits_init);
module_exit(inc_benefits_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose INCREASE_BENEFITS(index, value) via /proc/increase_benefits");

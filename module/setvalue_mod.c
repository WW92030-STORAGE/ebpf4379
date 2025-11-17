// setvalue_mod.c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "set_shared_value"
#define BUFSIZE 32

/* declare the kernel function that exists in memory.cc */
extern void SET_VALUE(unsigned long long x);  // matches your void SET_VALUE(u64)

/* proc write handler */
static ssize_t proc_write(struct file *file, const char __user *ubuf,
                          size_t count, loff_t *ppos)
{
    char buf[BUFSIZE];
    unsigned long long val = 0;
    int ret;

    if (count >= BUFSIZE)
        return -EINVAL;

    if (copy_from_user(buf, ubuf, count))
        return -EFAULT;
    buf[count] = '\0';

    ret = kstrtoull(buf, 0, &val);
    if (ret)
        return ret;

    /* call the kernel function in your kernel */
    SET_VALUE(val);

    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init setvalue_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops); // write-only
    pr_info("setvalue_mod loaded\n");
    return 0;
}

static void __exit setvalue_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("setvalue_mod unloaded\n");
}

module_init(setvalue_init);
module_exit(setvalue_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose SET_VALUE via /proc/set_shared_value");

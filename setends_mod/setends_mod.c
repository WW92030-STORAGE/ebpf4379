// set_starts_mod.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "set_ends"
#define BUFSIZE 64

/* Declare the real kernel function you already have.
 * It must be exported or have a visible symbol in kallsyms.
 */
extern void SET_ENDS(u64 index, u64 val);

static ssize_t proc_write(struct file *file,
                          const char __user *ubuf,
                          size_t count,
                          loff_t *ppos)
{
    char buf[BUFSIZE];
    u64 index, val;

    if (count >= BUFSIZE)
        return -EINVAL;

    if (copy_from_user(buf, ubuf, count))
        return -EFAULT;

    buf[count] = '\0';

    /* Expect: "index value" */
    if (sscanf(buf, "%llu %llu", &index, &val) != 2) {
        pr_info("set_ends: expected \"<index> <value>\"\n");
        return -EINVAL;
    }

    /* Call into your kernel code */
    SET_ENDS(index, val);

    pr_info("set_ends: SET_ENDS(%llu, %llu)\n", index, val);

    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init set_ends_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops);
    pr_info("set_ends_mod loaded\n");
    return 0;
}

static void __exit set_ends_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("set_ends_mod unloaded\n");
}

module_init(set_ends_init);
module_exit(set_ends_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose SET_ENDS(index, value) via /proc/set_ends");

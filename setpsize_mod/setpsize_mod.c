// set_starts_mod.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "set_prof_size"
#define BUFSIZE 64

/* Declare the real kernel function you already have.
 * It must be exported or have a visible symbol in kallsyms.
 */
extern void SET_PROF_SIZE(u64 index, u64 val);

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
    if (sscanf(buf, "%llu", &val) != 1) {
        pr_info("set_prof_size: expected \"<value>\"\n");
        return -EINVAL;
    }

    /* Call into your kernel code */
    SET_PROF_SIZE(val);

    pr_info("set_prof_size: SET_BENEFITS(%llu, %llu)\n", index, val);

    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init set_prof_size_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops);
    pr_info("set_prof_size_mod loaded\n");
    return 0;
}

static void __exit set_prof_size_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("set_prof_size_mod unloaded\n");
}

module_init(set_prof_size_init);
module_exit(set_prof_size_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose SET_PROF_SIZE(value) via /proc/set_prof_size");

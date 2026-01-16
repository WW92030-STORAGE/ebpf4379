// set_starts_mod.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "force_init"
#define BUFSIZE 64

/* Declare the real kernel function you already have.
 * It must be exported or have a visible symbol in kallsyms.
 */
extern void FORCE_INIT(void);

static ssize_t proc_write(struct file *file,
                          const char __user *ubuf,
                          size_t count,
                          loff_t *ppos)
{
    char buf[BUFSIZE];
    u64 val;

    if (count >= BUFSIZE)
        return -EINVAL;

    if (copy_from_user(buf, ubuf, count))
        return -EFAULT;

    buf[count] = '\0';

    /* Expect: "index value" */
    if (sscanf(buf, "%llu", &val) != 1) {
        pr_info("force_init: expected \"<value>\"\n");
        return -EINVAL;
    }

    /* Call into your kernel code */
    FORCE_INIT();

    pr_info("force_init: FORCE_INIT()\n");

    return count;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
};

static int __init set_prof_size_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops);
    pr_info("force_init_mod loaded\n");
    return 0;
}

static void __exit set_prof_size_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("force_init_mod unloaded\n");
}

module_init(set_prof_size_init);
module_exit(set_prof_size_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose FORCE_INIT() via /proc/force_init");

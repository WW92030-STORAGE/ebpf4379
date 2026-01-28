// set_starts_mod.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

#define PROC_NAME "get_benefits"
#define BUFSIZE 64

/* Declare the real kernel function you already have.
 * It must be exported or have a visible symbol in kallsyms.
 */
extern u64 GET_BENEFITS(u64 val);

static u64 last_value;
static bool value_valid;
static DEFINE_MUTEX(value_lock);

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
        pr_info("get_benefits: expected \"<value>\"\n");
        return -EINVAL;
    }

    /* Call into your kernel code */
    u64 res = GET_BENEFITS(val);

    mutex_lock(&value_lock);
    last_value = res;
    value_valid = true;
    mutex_unlock(&value_lock);

    pr_info("get_benefits: GET_BENEFITS(%llu): %llu\n", val, res);

    return count;
}

static ssize_t proc_read(struct file *file,
                         char __user *ubuf,
                         size_t count,
                         loff_t *ppos)
{
    char buf[BUFSIZE];
    int len;

    /* procfs convention: return EOF after first read */
    if (*ppos > 0)
        return 0;

    mutex_lock(&value_lock);
    if (!value_valid) {
        mutex_unlock(&value_lock);
        return 0;
    }

    len = scnprintf(buf, BUFSIZE, "%llu\n", last_value);
    value_valid = false;  /* consume result */
    mutex_unlock(&value_lock);

    if (copy_to_user(ubuf, buf, len))
        return -EFAULT;

    *ppos = len;
    return len;
}

static const struct proc_ops proc_fops = {
    .proc_write = proc_write,
    .proc_read = proc_read
};

static int __init get_benefits_init(void)
{
    proc_create(PROC_NAME, 0222, NULL, &proc_fops);
    pr_info("get_benefits_mod loaded\n");
    return 0;
}

static void __exit get_benefits_exit(void)
{
    remove_proc_entry(PROC_NAME, NULL);
    pr_info("get_benefits_mod unloaded\n");
}

module_init(get_benefits_init);
module_exit(get_benefits_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Expose GET_BENEFITS(value) via /proc/get_benefits");

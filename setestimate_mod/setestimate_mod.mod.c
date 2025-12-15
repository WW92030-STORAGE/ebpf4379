#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};



static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x5b8239ca, "__x86_return_thunk" },
	{ 0x88db9f48, "__check_object_size" },
	{ 0x13c49cc2, "_copy_from_user" },
	{ 0xbcab6ee6, "sscanf" },
	{ 0xef206eca, "SET_DO_PMD_ESTIMATE" },
	{ 0x87a21cb3, "__ubsan_handle_out_of_bounds" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0x939bb514, "remove_proc_entry" },
	{ 0xbdfb6dbb, "__fentry__" },
	{ 0x8ef841dd, "proc_create" },
	{ 0x122c3a7e, "_printk" },
	{ 0xe4a26819, "module_layout" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "A8FD17DB8E9EC7E24A7095C");

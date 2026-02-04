from execute import exec_
import threading

gb_lock = threading.Lock()


def get_benefits(index):
    with gb_lock:
        cmd = "echo \"%d\" | sudo tee /proc/get_benefits" % (index)
        exec_(cmd)

        value = exec_("sudo cat /proc/get_benefits")
        try:
            return int(value)
        except Exception as e:
            print("get_benefits(" + str(index) + ") returns: [" + str(value) + "]\nRaised exception " + str(e))
            return -1

v = get_benefits(0)
print(v)
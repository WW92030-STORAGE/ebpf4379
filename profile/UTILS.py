from execute import exec_
import threading
import math

# Wrapper function to get benefits
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

def cosine_sim(a, b):
    LL = min(len(a), len(b))
    if LL <= 0:
        return 0

    nsa = sum([a[x] * a[x] for x in range(LL)])
    nsb = sum([b[y] * b[y] for y in range(LL)])
    if nsa == 0 or nsb == 0:
        return 0

    dot = sum([a[x] * b[x] for x in range(LL)])
    return dot / math.sqrt(nsa * nsb)

def emd(a, b):
    LL = min(len(a), len(b))
    if LL <= 0:
        return 0

    a = a[:LL]
    b = b[:LL]
    sa = sum(a)
    sb = sum(b)
    if sa != 0:
        a = [i / sa for i in a]
    if sb != 0:
        b = [i / sb for i in b]
    
    emd = 0
    cdf = 0
    
    for i in range(LL):
        cdf += a[i] - b[i]
        emd += abs(cdf)
    return emd

if __name__ == "__main__":
    v = get_benefits(0)
    print(v)
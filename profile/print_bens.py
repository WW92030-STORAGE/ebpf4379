import subprocess
from CONSTANTS import NUM_BUCKETS
from execute import exec_


res = []
for i in range(NUM_BUCKETS):
    cmd = "echo " + str(i) + " | sudo tee /proc/get_benefits"
    exec_(cmd)
    cmd = "sudo cat /proc/get_benefits"
    res.append(int(exec_(cmd)))

print(res)
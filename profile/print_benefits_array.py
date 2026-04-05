import subprocess
from execute import exec_

N = int(input())

array = []
for i in range(N):
    exec_("echo \"" + str(i) + "\" | sudo tee /proc/get_benefits")
    output = exec_("sudo cat /proc/get_benefits")
    array.append(output)

print(array)
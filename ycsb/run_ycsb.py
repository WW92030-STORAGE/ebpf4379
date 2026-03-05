import subprocess
import time
import sys
import subprocess

def exec_(cmd):
    return subprocess.run(cmd, shell = True,     
    capture_output=True,
    text=True,
    check=True # Optional: raise an exception if the command fails
    ).stdout

def run_test(PRELUDE, CMD):
    exec_(PRELUDE)

    START = time.perf_counter_ns()
    END = None

    cmd = [CMD]

    # Start the subprocess with stdout captured
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,         # decode bytes → str
        bufsize=1,          # line-buffered
        shell = True
    )

    RATE = 0

    try:
        # Read lines as the subprocess prints them
        for line in proc.stdout:
            print("[child]", line.rstrip())
            if "Throughput" in line:
                ls = line.split()
                RATE = float(ls[2])
                proc.terminate()
                break
            if "sleeping..." in line:
                proc.terminate()
                break

    finally:
        END = time.perf_counter_ns()
        # Ensure the process is cleaned up
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    if END is None:
        END = time.perf_counter_ns()

    ELAPSED_NS = END - START

    return ELAPSED_NS, RATE


def run_tests(PRELUDE, CMD):
    WARMUP_CNT = 0
    TEST_CNT = 1

    ELAPSED_NS = 0
    AVG_RATE = 0
    DATA = []
    RATE = []

    for i in range(WARMUP_CNT):

        run_test(PRELUDE, CMD)
        time.sleep(1)

    for i in range(TEST_CNT):
        value, throughput = run_test(PRELUDE, CMD)
        ELAPSED_NS += value
        DATA.append(value)
        AVG_RATE += throughput
        RATE.append(throughput)
        print(str(i + 1) + "/" + str(TEST_CNT) + " DONE...")
        if len(DATA):
            print("RUNNING AVERAGE:", sum(DATA) / len(DATA) * 0.001)
        time.sleep(1)

    ELAPSED_NS /= TEST_CNT
    AVG_RATE /= TEST_CNT


    print("AVG ELAPSED: " + str(ELAPSED_NS) + "ns")
    print("AVG ELAPSED: " + str(ELAPSED_NS * 0.001) + "us")
    print("AVG ELAPSED: " + str(ELAPSED_NS * 0.001 * 0.001) + "ms")
    # print("DATA", str(DATA))
    for data in DATA:
        print(data)
    print("AVG_RATE: " + str(AVG_RATE) + "ops/s")
    # print("RATE" + str(RATE) + "\n")
    for i in RATE:
        print(str(i))

    with open("test_results.dat" ,"w") as FF:
        FF.write("AVG ELAPSED: " + str(ELAPSED_NS) + "ns" + "\n")
        FF.write("AVG ELAPSED: " + str(ELAPSED_NS * 0.001) + "us" + "\n")
        FF.write("AVG ELAPSED: " + str(ELAPSED_NS * 0.001 * 0.001) + "ms" + "\n")
        FF.write("DATA" + str(DATA) + "\n")
        for i in DATA:
            FF.write(str(data) + "\n")
        FF.write("AVG_RATE: " + str(AVG_RATE) + "ops/s")
        FF.write("RATE" + str(RATE) + "\n")
        for i in RATE:
            FF.write(str(i) + "\n")

if __name__ == "__main__":
    run_tests("./install_workload.sh", "./run_tests.sh")


# WARNING - DO NOT RUN THIS AS ROOT
import subprocess
import time

# Tester for framem

def run_test(CMD = "./framem 1"):
    START = time.perf_counter_ns()
    END = None

    cmd = ["sudo stdbuf -oL " + CMD]

    # Start the subprocess with stdout captured
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,         # decode bytes → str
        bufsize=1,          # line-buffered
        shell = True
    )

    try:
        # Read lines as the subprocess prints them
        for line in proc.stdout:
            print("[child]", line.rstrip())
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

    return ELAPSED_NS


def run_tests(CMD = "./framem 1"):
    WARMUP_CNT = 1
    TEST_CNT = 1

    ELAPSED_NS = 0
    DATA = []

    for i in range(WARMUP_CNT):
        run_test(CMD)
        time.sleep(1)

    for i in range(TEST_CNT):
        value = run_test(CMD)
        ELAPSED_NS += value
        DATA.append(value)
        print(str(i + 1) + "/" + str(TEST_CNT) + " DONE...")
        time.sleep(1)

    ELAPSED_NS /= TEST_CNT


    print("AVG ELAPSED: " + str(ELAPSED_NS) + "ns")
    print("AVG ELAPSED: " + str(ELAPSED_NS * 0.001) + "us")
    print("AVG ELAPSED: " + str(ELAPSED_NS * 0.001 * 0.001) + "ms")
    print("DATA", str(DATA))
    for data in DATA:
        print(data)

    with open("test_results.dat" ,"w") as FF:
        FF.write("AVG ELAPSED: " + str(ELAPSED_NS) + "ns" + "\n")
        FF.write("AVG ELAPSED: " + str(ELAPSED_NS * 0.001) + "us" + "\n")
        FF.write("AVG ELAPSED: " + str(ELAPSED_NS * 0.001 * 0.001) + "ms" + "\n")
        FF.write("DATA" + str(DATA) + "\n")
        for data in DATA:
            FF.write(str(data) + "\n")

if __name__ == "__main__":
    run_tests("./mongobench_run.sh")
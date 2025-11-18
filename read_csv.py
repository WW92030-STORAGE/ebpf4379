

CSV = "xz-training-just-huge"

def read_csv(csv = CSV):
    indent = "\t"
    with open(csv + ".csv", 'r') as file:
        with open(csv + ".dat", 'w') as output:
            output.write("void init_values(void) {\n")
            output.write(indent + "if (HAS_INIT) return;\n")
            output.write(indent + "else HAS_INIT = true;\n")
            output.write(indent + "printk(\"INIT VALUES\\n\");\n\n")
            counter = 0
            for line in file:
                arr = line.strip().split()
                output.write(indent + "STARTS[" + str(counter) + "] = " + arr[-4] + ";\n")
                output.write(indent + "ENDS[" + str(counter) + "] = " + arr[-1] + ";\n")
                output.write(indent + "BENEFITS[" + str(counter) + "] = " + arr[2] + ";\n")

                counter += 1

            output.write(indent + "PROFILE_SIZE = " + str(counter) + ";\n")
            output.write("}\n")



if __name__ == "__main__":
    read_csv()


import re
import math


def get_total_memory():
    with open("/proc/meminfo") as f:
        for line in filter(lambda x: "MemTotal" in x, f):
            return int(line.split()[1]) * 1024

    return 0


TOTAL_MEM = get_total_memory()

SINGLE_SUFFIX_REGEX = re.compile(r"^[1-9][0-9]*([EPTGMK])$")
DOUBLE_SUFFIX_REGEX = re.compile(r"^[1-9][0-9]*([EPTGMK])i$")
BYTES_INTEGER_REGEX = re.compile(r"^[1-9][0-9]*$")
EXPONENT_REGEX = re.compile(r"^[1-9][0-9]*e[0-9]+$")

SUFFIX_MULTIPLIERS = {
    "K": 10**3,
    "M": 10**6,
    "G": 10**9,
    "T": 10**12,
    "P": 10**15,
    "E": 10**18,
}

DOUBLE_SUFFIX_MULTIPLIERS = {
    "Ki": 2**10,
    "Mi": 2**20,
    "Gi": 2**30,
    "Ti": 2**40,
    "Pi": 2**50,
    "Ei": 2**60,
}


def transform_memory(memory):
    result = 4096  # Default to 4GB

    if re.match(SINGLE_SUFFIX_REGEX, memory):
        suffix = memory[-1]
        result = int(memory[:-1]) * SUFFIX_MULTIPLIERS[suffix]
    elif re.match(DOUBLE_SUFFIX_REGEX, memory):
        suffix = memory[-2:]
        result = int(memory[:-2]) * DOUBLE_SUFFIX_MULTIPLIERS[suffix]
    elif re.match(BYTES_INTEGER_REGEX, memory):
        result = int(memory)
    elif re.match(EXPONENT_REGEX, memory):
        result = int(float(memory))

    result = math.ceil(result)
    result = min(result, TOTAL_MEM)
    # Convert to Megabytes
    result = result / 1024 / 1024

    if int(result) == 0:
        result = TOTAL_MEM if TOTAL_MEM else 4096

    return int(result)

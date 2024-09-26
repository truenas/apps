import math
import re
import os

CPU_COUNT = os.cpu_count()

NUMBER_REGEX = re.compile(r"^[1-9][0-9]$")
FLOAT_REGEX = re.compile(r"^[0-9]+\.[0-9]+$")
MILI_CPU_REGEX = re.compile(r"^[0-9]+m$")


def transform_cpu(cpu) -> int:
    result = 2
    if NUMBER_REGEX.match(cpu):
        result = int(cpu)
    elif FLOAT_REGEX.match(cpu):
        result = int(math.ceil(float(cpu)))
    elif MILI_CPU_REGEX.match(cpu):
        num = int(cpu[:-1])
        num = num / 1000
        result = int(math.ceil(num))

    if CPU_COUNT is not None:
        # Do not exceed the actual CPU count
        result = min(result, CPU_COUNT)

    if int(result) == 0:
        result = CPU_COUNT if CPU_COUNT else 2

    return int(result)

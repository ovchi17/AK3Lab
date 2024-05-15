#!/usr/bin/python3
import json
from enum import Enum

BITS = 32
MIN_SIGN = -(2 ** (BITS - 1))
MAX_SIGN = 2 ** (BITS - 1) - 1
MAX_UNSIGN = 2**BITS - 1

INPUT_PORT = 0
OUTPUT_PORT = 1


class Opcode(Enum):
    HALT = "hlt"
    JUMP = "jmp"
    JZ = "jmz"

    PUSH = "psh"
    PUSH2 = "psh2"
    POP = "pop"
    LOAD = "get"
    DROP = "drp"
    DUP = "dup"

    INC = "inc"
    ADD = "add"
    DIV = "div"
    MOD = "mod"

    INPUT = "inp"
    OUTPUT = "out"

    NUMBER = "num"
    STRING = "str"
    BUFFER = "buf"


def write_code(filename: str, code: list):
    with open(filename, "w", encoding="utf-8") as file:
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(filename: str):
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        # Конвертация строки в Opcode
        if isinstance(instr, int):
            continue

        instr["opcode"] = Opcode(instr["opcode"])

    return code

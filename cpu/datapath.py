import logging

from cpu.isa import Opcode, MIN_SIGN, BITS, MAX_SIGN, INPUT_PORT, OUTPUT_PORT


class DataPath:
    data: list = None
    data_address: int = None
    stack_size: int = None
    stack: list = None
    stack_pointer: int = None
    input_buffer: list = None
    output_buffer: list = None

    def __init__(self, data: list, stack_size: int, input_buffer: list):
        assert stack_size > 0, "Stack size must be > 0"
        self.data = data
        self.data_address = 0
        self.stack_size = stack_size
        self.stack = [-1] * stack_size
        self.stack_pointer = -1
        self.stack_buffer = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

    def signal_latch_data_address(self, command: dict):
        opcode = command["opcode"]
        if opcode == Opcode.POP:
            self.data_address = self.stack[self.stack_pointer - 1]
        elif opcode == Opcode.LOAD:
            self.data_address = self.stack[self.stack_pointer]
        else:
            raise ValueError(f"Signal wrong opcode: {opcode}")

    def signal_latch_stack_pointer(self, command: dict):
        opcode = command["opcode"]
        if opcode in [Opcode.PUSH, Opcode.PUSH2, Opcode.DUP, Opcode.INPUT]:
            self.stack_pointer += 1
        elif opcode in [Opcode.DROP, Opcode.ADD, Opcode.DIV, Opcode.MOD, Opcode.OUTPUT]:
            self.stack_pointer -= 1
        elif opcode == Opcode.POP:
            self.stack_pointer -= 2
        else:
            raise ValueError(f"Signal wrong opcode: {opcode}")

    def signal_latch_top_of_stack(self, command: dict):
        opcode = command["opcode"]
        if opcode == Opcode.PUSH:
            self.stack[self.stack_pointer] = command["arg"]
        elif opcode == Opcode.PUSH2:
            self.stack[self.stack_pointer] = self.stack[self.stack_pointer - 1]
        elif opcode == Opcode.DUP:
            self.stack[self.stack_pointer] = self.stack[self.stack_pointer - 1]
        elif opcode == Opcode.LOAD:
            if self.data_address == INPUT_PORT:
                self.signal_input()
            else:
                self.stack[self.stack_pointer] = self.data[self.data_address]
        elif opcode == Opcode.INC:
            self.stack[self.stack_pointer] = self.stack[self.stack_pointer] + 1
        else:
            raise ValueError(f"Signal wrong opcode: {opcode}")

    def signal_latch_second_of_stack(self, command: dict):
        opcode = command["opcode"]
        if opcode in [Opcode.ADD, Opcode.DIV, Opcode.MOD]:
            self.stack[self.stack_pointer - 1] = self.get_alu_result(
                opcode,
                self.stack[self.stack_pointer],
                self.stack[self.stack_pointer - 1],
            )
        elif opcode == Opcode.PUSH2:
            self.stack[self.stack_pointer - 1] = command["arg"]
        else:
            raise ValueError(f"Signal wrong opcode: {opcode}")

    def signal_wr(self, command: dict):
        opcode = command["opcode"]
        if opcode == Opcode.POP:
            if self.data_address == OUTPUT_PORT:
                self.signal_output()
            else:
                self.data[self.data_address] = self.stack[self.stack_pointer]
        else:
            raise ValueError(f"Signal wrong opcode: {opcode}")

    def get_alu_result(self, opcode: Opcode, left: int, right: int):
        if opcode == Opcode.ADD:
            res = right + left
        elif opcode == Opcode.DIV:
            if left == 0:
                res = -1
            else:
                res = right // left
        elif opcode == Opcode.MOD:
            if left == 0:
                res = -1
            else:
                res = right % left
        else:
            raise ValueError(f"Wrong alu_operation value: {opcode}")

        if res < MIN_SIGN:
            res += 2**BITS
        if res > MAX_SIGN:
            res -= 2**BITS
        return res

    def signal_input(self):
        if len(self.input_buffer) == 0:
            raise EOFError("End of input file")
        str_symbol = self.input_buffer.pop(0)
        symbol = ord(str_symbol)
        self.stack[self.stack_pointer] = symbol
        if symbol == 0:
            str_symbol = ""
        logging.debug(f"input: {str_symbol}")

    def signal_output(self):
        assert (
            self.stack_pointer >= 0
        ), f"Stack pointer must be >= 0 ({self.stack_pointer})"
        symbol = self.stack[self.stack_pointer]
        self.output_buffer.append(symbol)
        logging.debug(
            f"output: {''.join(map(lambda x: chr(x) if 0 < x < 256 else str(x), self.output_buffer))} << {symbol}"
        )

    def zero(self):
        return self.stack[self.stack_pointer] == 0

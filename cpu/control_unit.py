from cpu.datapath import DataPath
from cpu.isa import Opcode


class ControlUnit:
    code: list = None
    program_counter: int = None
    instruction_register: int = None

    datapath: DataPath = None

    _tick: int = None

    def __init__(
        self,
        code: list,
        datapath: DataPath,
    ):
        self.code = code
        self.program_counter = 0
        self.instruction_register = 0
        self.datapath = datapath
        self._tick = 0

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    # latch signals
    def signal_latch_program_counter(self, command: dict, next: bool = False):
        opcode = Opcode(command["opcode"])
        if next:
            self.program_counter += 1
            return
        elif opcode == Opcode.JUMP:
            self.program_counter = command["arg"]
        elif opcode == Opcode.JZ:
            if self.datapath.zero():
                self.program_counter = command["arg"]
        else:
            raise ValueError(f"Wrong signal: {opcode}")

    def signal_latch_instruction_register(self):
        self.instruction_register = self.code[self.program_counter]

    def decode_and_execute(self):
        """
        Основной цикл процессора
        1. Получение инструкции
        2. Проверка опкода
        3. Вызвать сигналы
        4. Продвинуть тики
        """

        # Получение инструкции
        command = self.code[self.program_counter]
        opcode = Opcode(command["opcode"])
        self.signal_latch_instruction_register()
        self.signal_latch_program_counter(command, next=True)
        self.tick()

        # Вызвать сигналы
        if opcode == Opcode.HALT:
            raise StopIteration("Ы")

        elif opcode in [Opcode.JUMP, Opcode.JZ]:
            self.signal_latch_program_counter(command)

        elif opcode in [Opcode.PUSH, Opcode.DUP]:
            self.datapath.signal_latch_stack_pointer(command)
            self.tick()
            self.datapath.signal_latch_top_of_stack(command)

        elif opcode == Opcode.PUSH2:
            self.datapath.signal_latch_stack_pointer(command)
            self.tick()
            self.datapath.signal_latch_top_of_stack(command)
            self.tick()
            self.datapath.signal_latch_second_of_stack(command)

        elif opcode == Opcode.POP:
            self.datapath.signal_latch_data_address(command)
            self.tick()
            self.datapath.signal_wr(command)
            self.datapath.signal_latch_stack_pointer(command)

        elif opcode == Opcode.LOAD:
            self.datapath.signal_latch_data_address(command)
            self.tick()
            self.datapath.signal_latch_top_of_stack(command)

        elif opcode == Opcode.DROP:
            self.datapath.signal_latch_stack_pointer(command)

        elif opcode == Opcode.INC:
            self.datapath.signal_latch_top_of_stack(command)

        elif opcode in [Opcode.ADD, Opcode.DIV, Opcode.MOD]:
            self.datapath.signal_latch_second_of_stack(command)
            self.datapath.signal_latch_stack_pointer(command)

        # elif opcode == Opcode.INPUT:
        #     self.datapath.signal_latch_stack_pointer(command)
        #     self.tick()
        #     self.datapath.signal_input()
        #
        # elif opcode == Opcode.OUTPUT:
        #     self.datapath.signal_output()
        #     self.datapath.signal_latch_stack_pointer(command)

        else:
            raise ValueError(f"Wrong opcode: {opcode}")

        self.tick()

    def __repr__(self):
        opcode = Opcode(self.instruction_register["opcode"]).name
        tos = self.datapath.stack[self.datapath.stack_pointer]

        state_repr = (
            f"TICK: {self._tick:4} {str(opcode):10} "
            f"PC: {self.program_counter:3} "
            f"DA: {self.datapath.data_address:3} "
            f"SP: {self.datapath.stack_pointer:2} "
            f"TOS: {tos: 3} "
            f"Stack: {self.datapath.stack[:5]}"
        )
        return state_repr

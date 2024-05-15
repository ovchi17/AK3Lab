#!/usr/bin/python3
import argparse

from cpu.isa import Opcode, write_code, INPUT_PORT, OUTPUT_PORT


def get_meaningful_token(line: str):
    return line.split(";", 1)[0].strip()


def translate_data(token: str):
    str_opcode, variable, arg = token.split(" ", 2)
    opcode = Opcode(str_opcode)
    assert opcode in [
        Opcode.NUMBER,
        Opcode.STRING,
        Opcode.BUFFER,
    ], f"Wrong instruction in data part {token}"

    if opcode == Opcode.NUMBER:
        num = int(arg)
        tokens = [num]
    elif opcode == Opcode.STRING:
        arg = arg.strip('"')
        tokens = [ord(c) for c in arg] + [0]
    elif opcode == Opcode.BUFFER:
        num = int(arg)
        tokens = [0] * num
    else:
        raise ValueError(f"Wrong opcode: {opcode}")

    return variable, tokens


def translate_code(token: str):
    if " " in token:  # instruction with argument
        sub_tokens = token.split(" ")
        assert (
            len(sub_tokens) == 2
        ), f"Invalid instruction, check arguments amount: {token}"
        opcode = Opcode(sub_tokens[0])
        assert opcode in [
            Opcode.PUSH,
            Opcode.JUMP,
            Opcode.JZ,
        ], f"Instruction shouldn't have an argument: {token}"
        arg = sub_tokens[1]
        if arg.isdigit():
            arg = int(arg)

        return opcode, arg

    else:  # instruction without argument
        opcode = Opcode(token)
        return opcode, None


def translate_stage_1(text: str):
    variables = {}
    labels = {}
    tokens = [2, 0, 0]  # first token is data part length + input and output cells

    data_stage = True

    data_counter = 2
    program_counter = 0
    for line in text.splitlines():
        token = get_meaningful_token(line)
        if not data_stage and token == "section .data":
            raise ValueError(".data shouldn't't be there")
        if token == "" or token == "section .data:":
            continue

        if token == "section .code:":
            tokens[0] = data_counter  # set first word as data part length
            data_stage = False
            continue

        if data_stage:
            variable, data_part = translate_data(token)
            assert variable not in variables, f"Redefinition of variable: {variable}"
            variables[variable] = data_counter
            data_counter += len(data_part)
            tokens += data_part

        else:
            if token.endswith(":"):  # label
                label = token.strip(":")
                assert label not in labels, f"Redefinition of label: {label}"
                labels[label] = program_counter
            else:
                if token == "inp":
                    tokens.append({"index": program_counter, "opcode": Opcode.PUSH.value, "arg": INPUT_PORT})
                    tokens.append({"index": program_counter + 1, "opcode": Opcode.LOAD.value, "arg": None})
                    program_counter += 2
                    continue
                elif token == "out":
                    tokens.append({"index": program_counter, "opcode": Opcode.PUSH2.value, "arg": OUTPUT_PORT})
                    tokens.append({"index": program_counter + 1, "opcode": Opcode.POP.value, "arg": None})
                    program_counter += 2
                    continue

                opcode, arg = translate_code(token)
                tokens.append(
                    {"index": program_counter, "opcode": opcode.value, "arg": arg}
                )
                program_counter += 1

    return labels, variables, tokens


def translate_stage_2(labels: dict, variables: dict, tokens: list):
    code = []
    for ind, token in enumerate(tokens):
        if isinstance(token, int):
            code.append(token)
        elif isinstance(token, dict):
            arg = token["arg"]
            if isinstance(arg, str):
                assert (
                    arg in labels or arg in variables
                ), f"Label or variable is not defined: {token}"
                if arg in variables:
                    token["arg"] = variables[arg]
                elif arg in labels:
                    token["arg"] = labels[arg]
                else:
                    raise ValueError("Bruh")
            code.append(token)

    return code


def translate(text: str):
    labels, variables, tokens = translate_stage_1(text)
    code = translate_stage_2(labels, variables, tokens)

    return code


def main(source: str, target: str):
    with open(source, "r") as f:
        text = f.read()

    code = translate(text)

    write_code(target, code)
    print("LoC:", len(text.split("\n")), "Code instr:", len(code))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Трансляция кода")
    parser.add_argument("source_file", help="Имя файла с кодом")
    parser.add_argument("target_file", help="Имя выходного файла")

    args = parser.parse_args()

    main(args.source_file, args.target_file)

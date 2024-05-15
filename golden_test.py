import contextlib
import io
import logging
import os
import tempfile

import pytest

import start
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)

    STACK_SIZE = 10
    DEBUG_LIMIT = 200
    LIMIT = 100000

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.o")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target)
            print("============================================================")
            start.main(target, input_stream, STACK_SIZE, DEBUG_LIMIT, LIMIT)

        with open(target, encoding="utf-8") as file:
            code = file.read()

        assert stdout.getvalue() == golden.out["out_stdout"]
        assert code == golden.out["out_code"]
        assert caplog.text == golden.out["out_log"]

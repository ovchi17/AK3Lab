section .data:
    str hello "Hello, world!"

section .code:

start:
    psh hello

print:
    dup
    get
    jmz stop
    out
    inc
    jmp print

stop:
    drp
    drp
    hlt
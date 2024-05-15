section .data:
    str hello "Hello, "
    buf name 50

section .code:

start:
    psh hello

print_hello:
    dup
    get
    jmz before_read
    out
    inc
    jmp print_hello

before_read:
    drp
    drp
    psh name

read_name:
    dup
    inp
    jmz after_read
    pop
    inc
    jmp read_name

after_read:
    drp
    drp
    psh name

print_name:
    dup
    get
    jmz stop
    out
    inc
    jmp print_name

stop:
    drp
    drp
    hlt

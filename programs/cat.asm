section .code:

read:
    inp
    jmz stop
    out
    jmp read

stop:
    drp
    hlt

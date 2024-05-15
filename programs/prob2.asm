section .data:
    num first 1
    num second 2
    num third 0
    num total_sum 0

section .code:

sum:
    psh third
    psh first
    get
    psh second
    get
    add
    pop

continue:
    psh third
    get
    psh 4000000
    div
    jmz add
    jmp stop

add:
    drp
    psh third
    get
    psh 2
    mod
    jmz true

update:
    drp
    psh first
    psh second
    get
    pop
    psh second
    psh third
    get
    pop
    jmp sum

true:
    psh total_sum
    dup
    get
    psh third
    get
    add
    pop
    jmp update

stop:
    psh total_sum
    get
    out
    hlt

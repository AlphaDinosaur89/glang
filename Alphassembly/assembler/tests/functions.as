#15 iterations of the fibonacci sequence

mov [i], 0
main:
    mov dx, [i]
    call fib
    push ax
    call println

    add [i], 1

    cmp [i] == 15
    jf main

    # local variables test

    mov [var], "Variable in global scope"
    call vartest
    push [var]
    call println
	
	# TODO: Add local stack test

push 0
done

vartest:
    mov [var], "Variable in local scope"
    call vartest_1
    push [var]
    call println
    ret
vartest_1:
    mov [var], "Variable with deeper local scope"
    push [var]
    call println
    ret

print:
    print
    pop
    ret

println:
    call print
    call nwl
    ret

nwl:
    ld "\n"
    call print
    ret

fib:
    mov [n], dx
    push [n]
    cmp [n] > 1
    jt .L2
    mov ax, [n]
    jmp .L3
.L2:
    mov ax, [n]
    sub ax, 1
    mov dx, ax
    call fib

    mov bx, ax

    mov ax, [n]
    sub ax, 2
    mov dx, ax
    call fib

    add ax, bx
.L3:
    ret
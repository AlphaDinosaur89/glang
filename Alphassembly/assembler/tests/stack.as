# Stack tests

mov [var], "Hello, world"

ld "Hello, world 3 times"
call println
pop

push [var]
call println
call println
call println
pop

call line

ld "Dummy string"
push sp # duplicate top of Stack
# must be able to pop twice with no errors
pop
pop

# moving to top sp
mov sp, "Mov to stack\n"
print
pop

call line

# arithmetics on top of stack
ld "arithmetics on top of stack\n69+117*30/10"
call println
push 69

# switch this to swap keyword to make the calculations instead
mov ax, 117
mul ax, 30
div ax, 10
add sp, ax
print
pop

push 0
done

line:
    ld "-----------------------"
    call println
    pop
    ret

print:
    print
    ret

nwl:
    ld "\n"
    call print
    pop
    ret

println:
    call print
    call nwl
    ret
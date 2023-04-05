ld "See arithmetics.s to see if calculations are correct\nAddition\n"
call print

mov ax, 35
add ax, 34
push ax
call print

ld "\nSubtraction\n"
call print

mov ax, 500
sub ax, 80
push ax
call print
call nwl

mov ax, 6.9
sub ax, 4.2
push ax
call print

ld "\nDivision\n"
call print

mov ax, 69000
div ax, 1000
push ax
call print
call nwl

mov ax, 6.9
div ax, 4.2
push ax
call print

ld "\nMultiplication\n"
call print

mov ax, 42
mul ax, 10
push ax
call print
call nwl

mov ax, 4.2
mul ax, 0.5
push ax
call print

ld "\nModulo\n"
call print

mov ax, 5
mod ax, 100
push ax
call print
call nwl
mov ax, 104
mod ax, 100
push ax
call print

push 0
done

print:
    print
    pop
    ret

nwl:
    ld "\n"
    print
    pop
    ret
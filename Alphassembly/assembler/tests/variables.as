mov [var69], 69
mov [var420], 420

cmp [var69] < [var420]
jt true
jmp false

true:
    ld "var69 is less than var420\n"
    print
    pop

false:

ld "var420 + var69 = "
print
pop
add [var420], [var69]
push [var420]
print
pop

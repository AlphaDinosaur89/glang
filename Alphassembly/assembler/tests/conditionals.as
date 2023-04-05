main:
	cmp 1 == 1 || 2 == 3 || 5 == 1 && 20 == 21 || 76 != 2
	jt true
	
	ld "false\n"
	print
	pop
	push 1
	done

true:
	ld "true\n"
	print
	pop
	push 0
	done
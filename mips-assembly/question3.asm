		.data
input: .space 150
output: .space 150
filesize: .word 0
header: .space 44
audio: .space 1024

		.text
		.globl main

main:
	li $v0, 8
	la $a0, input
	li $a1, 150
	syscall

	li $v0, 8
	la $a0, output
	li $a1, 150
	syscall

	li $v0, 5
	syscall
	sw $v0, filesize

	li $t0, 0

replace_in:
	lb $t1, input($t0)
	beqz $t1, check_outfile
	li $t2, 10
	beq $t1, $t2, setnull_in
	addi $t0, $t0, 1
	b replace_in

setnull_in:
	sb $zero, input($t0)

check_outfile:
	li $t0, 0

replace_out:
	lb $t1, output($t0)
	beqz $t1, openfile
	li $t2, 10
	beq $t1, $t2, setnull_out
	addi $t0, $t0, 1
	b replace_out

setnull_out:
	sb $zero, output($t0)

openfile:		
	li $v0, 13
	la $a0, input
	li $a1, 0
	li $a2, 0
	syscall
	move $t0, $v0
	bltz $t0, exit

	li $v0, 14
	move $a0, $t0
	la $a1, header
	li $a2, 44
	syscall

	lw $t1, filesize
	li $t2, 44
	sub $t3, $t1, $t2

	li $v0, 14
	move $a0, $t0
	la $a1, audio
	move $a2, $t3
	syscall

	li $v0, 16
	move $a0, $t0
	syscall

	la $t2, audio
	sub $t3, $t1, 44
	add $t3, $t2, $t3

reverse:
	blt $t3, $t2, done

	lh $t4, 0($t2)
	lh $t5, -2($t3)

	sh $t5, 0($t2)
	sh $t4, -2($t3)

	addi $t2, $t2, 2
	addi $t3, $t3, -2
	j reverse

done:
	li $v0, 13
	la $a0, output
	li $a1, 577
	li $a2, 438
	syscall
	move $t0, $v0

	li $v0, 15
	move $a0, $t0
	la $a1, header
	li $a2, 44
	syscall

	li $t2, 44
	sub $t3, $t1, $t2

	li $v0, 15 
	move $a0, $t0
	la $a1, audio
	move $a2, $t3
	syscall

	li $v0, 16
	move $a0, $t0
	syscall

exit:
	li $v0, 10
	syscall
		.data
outputfile: .space 150
tonef: .word 0
samplef: .word 0
tonel: .word 0
header: .space 44
high: .half 32767
low: .half -32768

		.text
		.globl main

main:
	li $v0, 8
	la $a0, outputfile
	li $a1, 150
	syscall

	li $v0, 5
	syscall
	sw $v0, tonef

	li $v0, 5
	syscall
	sw $v0, samplef

	li $v0, 5
	syscall
	sw $v0, tonel

	li $t0, 0

replace:
	lb $t1, outputfile($t0)
	beqz $t1, createfile
	li $t2, 10
	beq $t1, $t2, setnull
	addi $t0, $t0, 1
	b replace

setnull:
	sb $zero, outputfile($t0)

createfile:
	li $v0, 13
	la $a0, outputfile
	li $a1, 577
	li $a2, 438
	syscall
	move $t0, $v0

	li $v0, 15
	move $a0, $t0
	la $a1, header
	la $a2, 44
	syscall

	lw $t1, samplef
	lw $t2, tonel
	mul $t3, $t1, $t2

	lw $t4, tonef
	div $t1, $t1, $t4

	li $t5, 0

loop:
	bge $t5, $t3, close

	div $t2, $t1, 2
	move $t6, $t2

whigh:
	beqz $t6, wlow

	li $v0, 15
	move $a0, $t0
	la $a1, high
	li $a2, 2
	syscall
	addi $t5, $t5, 1
	addi $t6, $t6, -1
	j whigh

wlow:
	move $t6, $t2

lowloop:
	beqz $t6, loop

	li $v0, 15
	move $a0, $t0
	la $a1, low
	li $a2, 2
	syscall

	addi $t5, $t5, 1
	addi $t6, $t6, -1

	j lowloop

close:
	li $v0, 16
	move $a0, $t0
	syscall

exit:
	li $v0, 10
	syscall
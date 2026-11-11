		.data
prompt1: .asciiz "Enter a wave file name:\n"
prompt2: .asciiz "Enter the file size (in bytes):\n"
outheading: .asciiz "Information about the wave file:\n================================\n"
outmax: .asciiz "Maximum amplitude: "
outmin: .asciiz "\nMinimum amplitude: "

filename: .space 150
filesize: .word 0
buffer: .space 2048
max: .word -32768
min: .word 32767

		.text
		.globl main

main:
	li $v0, 4
	la $a0, prompt1
	syscall

	li $v0, 8
	la $a0, filename
	li $a1, 150
	syscall

	li $t0, 0

replace_n:
	lb $t1, filename($t0)
	beqz $t1, openfile
	li $t2, 10
	beq $t1, $t2, setnull
	addi $t0, $t0, 1
	b replace_n

setnull:
	sb $zero, filename($t0)

openfile:		
	li $v0, 13
	la $a0, filename
	li $a1, 0
	li $a2, 0
	syscall
	move $t0, $v0
	bltz $t0, exit

	li $v0, 14
	move $a0, $t0
	la $a1, buffer
	li $a2, 44
	syscall

	li $v0, 4
	la $a0, prompt2
	syscall

	li $v0, 5
	syscall
	sw $v0, filesize

	lw $t1, filesize
	li $t2, 44
	sub $t3, $t1, $t2
	divu $t4, $t3, 2 

	li $v0, 14
	move $a0, $t0
	la $a1, buffer
	move $a2, $t3
	syscall

	li $v0, 16
	move $a0, $t0
	syscall

	la $t3, buffer
	
	li $t5, 0

process:
	beq $t5, $t4, printout

	lh $t6, 0($t3)
	addi $t3, $t3, 2
	addi $t5, $t5, 1

	lw $t7, max
	bge $t7, $t6, maxskip
	move $t7, $t6
	sw $t7, max

maxskip:
	lw $t7, min
	ble $t7, $t6, minskip
	move $t7, $t6
	sw $t7, min

minskip:
	b process

printout:
	li $v0, 4
	la $a0, outheading
	syscall

	li $v0, 4
	la $a0, outmax
	syscall

	lw $a0, max
	li $v0, 1
	syscall

	li $v0, 4
	la $a0, outmin
	syscall

	lw $a0, min
	li $v0, 1
	syscall

exit:
	li $v0, 10
	syscall


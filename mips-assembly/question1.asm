		.data
prompt1: .asciiz "Enter a wave file name:\n"
prompt2: .asciiz "Enter the file size (in bytes):\n"
outheading: .asciiz "Information about the wave file:\n================================\n"
outchannels: .asciiz "Number of channels: "
outsamplerate: .asciiz "\nSample rate: "
outbyterate: .asciiz "\nByte rate: "
outbits: .asciiz "\nBits per sample: "

filename: .space 150
filesize: .word 0
buffer: .space 44

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
	beqz $t1, open
	li $t2, 10
	beq $t1, $t2, nullify
	addi $t0, $t0, 1
	b replace_n

nullify:		
	sb $zero, filename($t0)

open:		
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

	li $v0, 16
	move $a0, $t0
	syscall

	li $v0, 4
	la $a0, prompt2
	syscall

	li $v0, 5
	syscall 
	sw $v0, filesize

	li $v0, 4
	la $a0, outheading
	syscall

	li $v0, 4 
	la $a0, outchannels
	syscall
	la $t3, buffer
	lhu $t1, 22($t3)
	li $v0, 1
	move $a0, $t1
	syscall

	li $v0, 4
	la $a0, outsamplerate
	syscall
	lw $t1, 24($t3)
	li $v0, 1
	move $a0, $t1
	syscall

	li $v0, 4
	la $a0, outbyterate
	syscall
	lw $t1, 28($t3)
	li $v0, 1
	move $a0, $t1
	syscall

	li $v0, 4
	la $a0, outbits
	syscall
	lhu $t1, 34($t3)
	li $v0, 1
	move $a0, $t1
	syscall

exit:
	li $v0, 10
	syscall



addi x1, x0, 5
addi x2, x0, 3
loop1: add x3, x1, x2
addi x1, x1, -1
bne x1, x0, loop1
add x4, x3, x2

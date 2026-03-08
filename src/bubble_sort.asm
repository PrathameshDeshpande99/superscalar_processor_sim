.data
    # An array of 20 32-bit integers to sort
    numbers: .word 45, 12, 89, 3, 22, 78, 91, 15, 6, 33, 50, 67, 8, 99, 21, 10, 4, 60, 88, 1
    length:  .word 20

.text
.globl _start

_start:
    la a0, numbers       # a0 = base address of the array
    la t6, length        # Load address of the length variable
    lw a1, 0(t6)         # a1 = number of elements (20)

    # Initialize N-1 for loop bounds
    addi t5, a1, -1      # t5 = 19 (Loop limit)
    li t0, 0             # t0 = i (Outer loop counter)

outer_loop:
    bge t0, t5, end_sort # If i >= 19, sorting is complete

    li t1, 0             # t1 = j (Inner loop counter)

inner_loop:
    bge t1, t5, end_inner # If j >= 19, inner loop is complete

    # Calculate memory address for array[j]
    slli t2, t1, 2       # Multiply j by 4 (since each word is 4 bytes)
    add t2, a0, t2       # t2 = base address + (j * 4)

    # Load array[j] and array[j+1]
    lw t3, 0(t2)         # t3 = array[j]
    lw t4, 4(t2)         # t4 = array[j+1]

    # Compare elements
    ble t3, t4, no_swap  # If array[j] <= array[j+1], branch to no_swap

    # Swap the elements if they are out of order
    sw t4, 0(t2)         # array[j] = t4
    sw t3, 4(t2)         # array[j+1] = t3

no_swap:
    addi t1, t1, 1       # j = j + 1
    j inner_loop         # Jump back to start of inner loop

end_inner:
    addi t0, t0, 1       # i = i + 1
    j outer_loop         # Jump back to start of outer loop

end_sort:
    # Program exit (using standard ecall for exit)
    li a7, 10            # syscall number for exit (in environments like RARS/Venus)
    ecall
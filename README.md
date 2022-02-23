```
# RISC-V executor

## The objective of the project:
This is a Python script that emulates the most common 32-bit RISC-V 
instructions and displays in console "pass" or "fail" depending on the result
of the tests. 

### Team name: Unbreakables 2.0

### Project completed by:
    Panait Ana-Maria (group 132)
    Teodorescu George-Tiberiu (group 132)
    Neaga-Budoiu Maria (group 132)
    Trufas Dafina (group 132)
### Syntax for running the script:
    python riscv_executor.py input_file.mc 

Note: input_file.mc contains machine code, we recommend to use the existing tests
in the project folder

### Implementation:

We have stored all the machine-code instructions in a bytes-array and the 32 registers in a register-file. 
We have to search the “memory” for the instruction to be treated, then split its associated code so that we find its 
type, implement the operations it involves with the proper use of memory, and obtain its final result.

The interpretation of each instruction is done respecting the following decoding cycle: 
IF (Instruction Fetch), ID (Instruction Decode), EX (Execute), MEM (Memory Access), WB (Write Back). 
The main types of instructions are R, I, S, U, J and can be recognized by the opcode:
![image](https://github.com/anamariapanait10/Proiect_ASC_2/blob/main/instructions_types.png?raw=true)

The five steps in decoding an instruction are described below:
1. `Instruction Fetch` – in this stage, we use the pc (program counter register), in order to get the next instruction 
from the memory and, after that, the value of pc is incremented by 4, pointing to the next instruction 
2. `Instruction Decode` – the decode step is divided in two sub-stages:
   
    a. A function which matches each instruction with its type: r/i/b/j/u/s

    b. 6 functions, one for each type of instruction, which split the bytes of the instruction, according to its format,
   and provide the exact type of the current instruction (the operation and the registers which store the values of the operands)
3. `Execute` – we have used specific functions, in order to implement the effective operations
4. `Memory Access` – this step is necessary, when we need to access data which is not stored in registers
5. `Write back` – the final step, in the decoding-process, is to load the result of the operation in the appropriate 
   location (a register, or a memory location)
```

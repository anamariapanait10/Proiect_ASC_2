# RISC-V executor

## The objective of the project:

Creating a Python script that executes files that test the most common 32-bit RISC-V 
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

The interpretation of each instruction is done respecting the following decoding cycle: 
IF (Instruction Fetch), ID (Instruction Decode), EX (Execute), MEM (Memory Access), WB (Write Back). 
The main types of instructions are R, I, S, U, J and can be recognized by the opcode:
![image](https://github.com/anamariapanait10/Proiect_ASC_2/blob/main/instructions_types.png?raw=true)

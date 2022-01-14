# TODO Vedeti ca noi trebuia sa folosim registrul pc in loc de x2 ca pointer la
#  instructiunea curenta (https://en.wikichip.org/wiki/risc-v/registers)

# linkuri utile: https://github.com/riscv-non-isa/riscv-asm-manual/blob/master/riscv-asm.md

import sys


instructions = []
x = [0 for x in range(32)]


def complDoi(bits, nrBits):
    sum = -1 * (1 << (nrBits - 1)) * (int(bits[0]))
    pow = 1 << (nrBits - 2)
    for poz in range(1, nrBits):
        sum += (int(bits[poz])) * pow
        pow >>= 1
    return sum


def fetch(x2):
    new_instr = instructions[x2] + instructions[x2+1] + instructions[x2+2] + instructions[x2+3]
    instr_bin = '{:032b}'.format(int(new_instr, 16))
    decode(instr_bin)

# ecall = 000000000000 00000 000 00000 1110011
# a0-a6 arguments; system call number in a7
# 31...20  19...15  14...12 11...7 6 ...0
# funct12   rs1     funct3   rd    opcode
#   12      5         3       5       7
# ecall     0        priv     0    system
# https://stackoverflow.com/questions/59800430/risc-v-ecall-syscall-calling-convention-on-pk-linux

def execute_ecall(instr):
    sys_call = x[17]  # a7 = x[17]
    argvs = x[10:17]  # a0-a6 = x[10]-x[16]
    if sys_call == "1":  # exit
        sys.exit(argvs[0])
    else:
        print("Unknown syscall")

# unimp = 000000000000 00000 000 00000 0000000
# https://reviews.llvm.org/D54316

def execute_unimp(instr):
    sys.exit(0)

# nop instruction = addi x0, x0, 0



# I-type instructions: with immediates, loads (addi, lw, jalr, slli) - 2 registers + immediate
# 31 ... 20 19 ... 15 14 ... 12 11 ... 7 6 ...0
# imm[11:0]    rs1     funct3      rd    opcode
#   12          5          3        5       7
# opcode -> 0010011

# imm[11:0]        funct3      instruction
# imm[11:0]         000         addi
# imm[11:0]         010         slti
# imm[11:0]         011         sltiu
# imm[11:0]         100         xori
# imm[11:0]         110         ori
# imm[11:0]         111         andi
# 0000000 + shamt   001         slli
# 0000000 + shamt   101         srli
# 0100000 + shamt   101         srai

def i_type(instr):
    imm = instr[:12]
    funct3 = instr[-15:-12]
    # print(funct3)
    # print(imm)
    if funct3 == "000":
        execute_addi(instr)
    elif funct3 == "001":
        execute_slli(instr)
    elif funct3 == "101":
        if instr[:7] == "0000000":
            execute_srli(instr)
        else:
            execute_srai(instr)


def execute_srai(instr):
    rd = int(instr[-12:-7], 2)
    shamt = int(instr[-25:-20], 2)
    rs1 = int(instr[-20:-15], 2)
    x[rd] = x[rs1] >> shamt

def execute_srli(instr):
    rd = int(instr[-12:-7],2)
    shamt = int(instr[-25:-20],2)
    rs1 = int(instr[-20:-15],2)
    bits = '{:032b}'.format(x[rs1])
    bits = "0"*shamt + bits
    bits = bits[0:32]
    x[rd] = int(bits,2)




def execute_slli(instr):
    rd = int(instr[-12:-7], 2)
    shamt = int(instr[-25:-20], 2)
    rs1 = int(instr[-20:-15], 2)
    x[rd] = x[rs1] << shamt

def execute_addi(instr):  # rd = rs1 + imm
    rs1 = instr[-20: -15]
    imm = instr[:12]
    rd = instr[-12:-7]
    # print(rs1)
    # print(imm)
    # print(rd)
    rs1 = int(rs1, 2)
    imm = complDoi(imm, 12)
    rd = int(rd, 2)
    # print(rs1)
    # print(imm)
    x[rd] = rs1 + imm


# R-type instructions: using 3 register inputs (add, xor, mul) - arithmetic/logical operations
# 31 ... 25 24 ... 20 19 ... 15 14 ... 12 11 ... 7 6 ...0
#   funct7      rs2     rs1     funct3      rd      opcode
#     7         5         5        3        5         7
# opcode -> 0110011
# funct7+funct3 describes what operation to perform
def r_type(instr):
    # funct7        funct3    instruction
    # 0000000       000         add
    # 0100000       000         sub
    # 0000000       001         sll
    # 0000000       010         slt
    # 0000000       011         sltu
    # 0000000       100         xor
    # 0000000       101         slr
    # 0100000       101         sra
    # 0000000       110         or
    # 0000000       111         and
    # funct7 = instr[:8]
    funct3 = instr[17:21]
    if funct3 == "110":
        execute_ori(instr)

def execute_ori(instr):
    rs1 = int(instr[-20:-15], 2)
    rs2 = int(instr[-25:-20], 2)
    rd = instr[-12:-7]
    rd = int(rd, 2)
    x[rd] = rs1 | rs2

def b_type(instr):
    funct3 = instr[-15:-12]
    if funct3 == "001":
        execute_bne(instr)
    if funct3 == "000":
        execute_beq(instr)


def execute_beq(instr):
    imm = complDoi(instr[0] + instr[-8] + instr[-31:-25] + instr[-12:-8], 12)
    rs1 = int(instr[-20:-15], 2)
    rs2 = int(instr[-25:-20], 2)
    if rs1 == rs2:
        x[2] += imm * 2

def execute_bne(instr):
    imm = complDoi(instr[0] + instr[-8] + instr[-31:-25] + instr[-12:-8], 12)
    rs1 = int(instr[-20:-15], 2)
    rs2 = int(instr[-25:-20], 2)
    if rs1 != rs2:
        x[2] += imm*2

def execute_u_type(instr):
    rd = int(instr[-12:-7],2)
    imm = int(instr[-32:-12],2)
    x[rd] = imm
    x[rd] <<= 12

def execute_j_type(instr):
    offset=complDoi(instr[0]+instr[-20:-12]+instr[-20]+instr[-31:-21],20)
    rd=int(instr[-12:-7],2)
    if rd!=0:
        x[rd]=x[2]+4
    x[2]+=offset*2



def decode(instr):
    # print(instr)
    opcode = instr[-7:]
    # print(opcode)
    if opcode == "0110011":
        r_type(instr)
    elif opcode == "0010011":
        i_type(instr)
    elif opcode == "1100011":
        b_type(instr)
    elif opcode == "1101111":
        j_type(instr)
    elif opcode == "0110111":
        execute_u_type(instr)
    elif opcode == "1110011":
        execute_ecall(instr)
    elif opcode == "0000000":
        execute_unimp(instr)


def main():
    with open("input.txt") as f:
        lines = f.readlines()
        # print(lines)
        last = 0
        for l in lines:
            l = l.split()
            # print(l)
            if len(l) == 2 and len(l[0]) == 9 and len(l[1]) == 8 and l[1].isalnum() and l[0][:8].isalnum():
                addr = int(l[0][:8], 16)
                addr = addr - 2 ** 31
                while last != addr:
                    instructions.append("00")
                    last += 1
                instructions.append(l[1][:2])
                instructions.append(l[1][2:4])
                instructions.append(l[1][4:6])
                instructions.append(l[1][6:8])
                last += 4


    # print(instructions)
    # print("\n".join([f" {x} : {instructions[x]}" for x in range(len(instructions))]))
    x[3] = 5  # stack pointer
    while x[2] + 4 <= len(instructions):
        fetch(x[2])
        x[2] += 4
    print(x[10])


if __name__ == '__main__':
    main()


# S-type instructions: store instructions (sw, sb)
# 31 ... 25 24 ... 20 19 ... 15 14 ... 12 11 ... 7 6 ...0
#   imm[11:5]      rs2     rs1   funct3   imm[4:0] opcode
#       7

def s_type():
    pass
# SB-type instructions: branch instructions (beq, bge)
# 31 ... 25 24 ... 20 19 ... 15 14 ... 12 11 ... 7 6 ...0
#   imm[12|10:5]      rs2     rs1   funct3   imm[4:0] opcode
#       7
# opcode 1100011
def sb_type():
    pass
# U-type instructions: with upper immediates (luim auipc)
# 31 ... 12 11 ... 7 6 ...0
# imm[31:12]    rd   opcode
#    20
def u_type():
    pass
# UJ-type instructions: jump instructions (jal)
# 31 ... 12             S11 ... 7 6 ...0
# imm[20|10:1|11|19:12]    rd   opcode
#    20
def uj_type():
    pass
def j_type():
    pass
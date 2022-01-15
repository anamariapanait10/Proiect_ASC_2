import sys

instructions = []  # bytes array
x = [0 for x in range(32)]  # registers x0-x31
pc = 0  # program counter register


def from_two_s_compl_bin_to_int(bits, nrBits):
    sum = -1 * (1 << (nrBits - 1)) * (int(bits[0]))
    pow = 1 << (nrBits - 2)
    for pos in range(1, nrBits):
        sum += (int(bits[pos])) * pow
        pow >>= 1
    return sum


def write_back(rd, res):
    x[rd] = res

def memory_access(res):
    global pc
    pc = res

def execute_ori(rs1, rs2, rd):
    res = x[rs1] | x[rs2]
    write_back(rd, res)


def execute_srl(rs1, rs2, rd):
    res = x[rs1] << x[rs2]
    write_back(rd, res)


def execute_xor(rs1, rs2, rd):
    res = x[rs1] ^ x[rs2]
    write_back(rd, res)


def execute_rem(rs1, rs2, rd):
    if x[rs1] < 0:
        res = -x[rs1]
        res = (res % x[rs2]) * -1
    else:
        res = x[rs1] % x[rs2]
    write_back(rd, res)


def execute_addi(imm, rs1, rd):
    res = x[rs1] + imm
    write_back(rd, res)


def execute_slli(shamt, rs1, rd):
    res = x[rs1] << shamt
    write_back(rd, res)

def execute_srli(shamt, rs1, rd):
    bits = '{:032b}'.format(x[rs1])
    bits = "0" * shamt + bits
    bits = bits[0:32]
    res = int(bits, 2)
    write_back(rd, res)

def execute_srai(shamt, rs1, rd):
    res = x[rs1] >> shamt
    write_back(rd, res)


def execute_lw(imm, rs1, rd):
    if x[rs1] < imm: # ???
        x[rd] = 1
    else:
        x[rd] = 0


def execute_beq(imm, rs1, rs2):
    if x[rs1] == x[rs2]:
        global pc
        res = pc + imm * 2 - 4
        memory_access(res)


def execute_bne(imm, rs1, rs2):
    if x[rs1] != x[rs2]:
        global pc
        res = pc + imm * 2 - 4
        memory_access(res)


def execute_jal(offset, rd):
    global pc
    new_pc = pc + offset * 2
    memory_access(new_pc)
    if rd != 0:
        res = pc + 4
        write_back(rd, res)

def execute_lui(imm, rd):
    res = from_two_s_compl_bin_to_int(imm + "0" * 12, 32)
    write_back(rd, res)


def execute_auipc(imm, rd):
    imm = from_two_s_compl_bin_to_int(imm + "0" * 12)
    global pc
    res = imm + pc
    write_back(rd, res)


def execute_sw(imm, rs1, rs2):
    res = x[rs1] + imm
    write_back(rs2, res)

def execute_fsw(imm, rs1, rs2):
    res = float(int(x[rs1], 2)) + imm
    write_back(rs2, res)


# R-type instructions: using 3 register inputs (add, xor, mul) - arithmetic/logical operations
# 31 ... 25 24 ... 20 19 ... 15 14 ... 12 11 ... 7 6 ...0
#   funct7      rs2     rs1     funct3      rd      opcode
#     7         5         5        3        5         7
# funct7+funct3 describes what operation to perform

# funct7        funct3    instruction
# 0000000       000         add
# 0100000       000         sub
# 0000000       001         sll
# 0000000       010         slt
# 0000000       011         sltu
# 0000000       100         xor
# 0000000       101         srl
# 0100000       101         sra
# 0000000       110         or
# 0000000       111         and


def decode_r_type(instr):

    funct7 = instr[-32:-25]
    rs2 = int(instr[-25:-20], 2)
    rs1 = int(instr[-20:-15], 2)
    funct3 = instr[17:21]
    rd = int(instr[-12:-7], 2)

    if funct3 == "110" and funct7 == "0000000":  # ori instruction
        execute_ori(rs1, rs2, rd)
    elif funct3 == "101":  # srl instruction
        execute_srl(rs1, rs2, rd)
    elif funct3 == "100":  # xor instruction
        execute_xor(rs1, rs2, rd)
    elif funct3 == "110" and funct7 == "0000001":  # rem instruction
        execute_rem(rs1, rs2, rd)


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

def decode_i_type(instr):
    imm = from_two_s_compl_bin_to_int(instr[:12])
    if imm[0] == "0":
        imm = "0" * 20 + imm
    else:
        imm = "1" * 20 + imm
    imm = from_two_s_compl_bin_to_int(imm)
    shamt = int(instr[-25:-20], 2)
    rs1 = int(instr[-20: -15], 2)
    funct3 = instr[-15:-12]
    rd = int(instr[-12:-7], 2)
    opcode = instr[-7:]

    if opcode == "0000011":
        execute_lw(imm, rs1, rd)
    if funct3 == "000":
        execute_addi(imm, rs1, rd)
    elif funct3 == "001":
        execute_slli(shamt, rs1, rd)
    elif funct3 == "101":
        if instr[:7] == "0000000":
            execute_srli(shamt, rs1, rd)
        else:
            execute_srai(shamt, rs1, rd)


def decode_b_type(instr):
    imm = from_two_s_compl_bin_to_int(instr[0] + instr[-8] + instr[-31:-25] + instr[-12:-8], 12)
    funct3 = instr[-15:-12]
    rs1 = int(instr[-20:-15], 2)
    rs2 = int(instr[-25:-20], 2)

    if funct3 == "001":
        execute_bne(imm, rs1, rs2)
    if funct3 == "000":
        execute_beq(imm, rs1, rs2)


# U-type instructions: with upper immediates (lui, auipc)
# 31 ... 12 11 ... 7 6 ...0
# imm[31:12]    rd   opcode
#    20         5      7

def decode_u_type(instr):
    imm = instr[-32:-12]
    rd = int(instr[-12:-7], 2)
    opcode = instr[-7:]
    if opcode == "0110111":
        execute_lui(imm, rd)
    elif opcode == "0010111":
        execute_auipc(imm, rd)


# UJ-type instructions: jump instructions (jal)
# 31 ... 12             11 ... 7 6 ...0
# imm[20|10:1|11|19:12]    rd   opcode
#    20

def decode_j_type(instr):
    offset = from_two_s_compl_bin_to_int(instr[0] + instr[-20:-12] + instr[-21] + instr[-31:-21], 20)
    rd = int(instr[-12:-7], 2)
    execute_jal(offset, rd)



# S-type instructions: store instructions (sw, sb)
# 31 ... 25    24 ... 20 19 ... 15 14 ... 12 11 ... 7 6 ...0
#   imm[11:5]      rs2     rs1      funct3   imm[4:0] opcode
#       7          5        5          3        5       7

def decode_s_type(instr):
    funct3 = instr[-15:-12]
    imm = instr[-32:-25] + instr[-12:-7]
    if imm[0] == "0":
        imm = "0" * 20 + imm
    else:
        imm = "1" * 20 + imm
    imm = from_two_s_compl_bin_to_int(imm, 32)
    rs1 = int(instr[-20:-15], 2)
    rs2 = int(instr[-25:-20], 2)
    opcode = instr[-7:]

    if funct3 == "010":
        execute_sw(imm, rs1, rs2)
    elif opcode == "0100111":
        execute_fsw(imm, rs1, rs2)






def decode(instr):  # figure out what the instruction says to do and get values from the registers that will be used
    opcode = instr[-7:]
    if opcode == "0110011":
        decode_r_type(instr)
    elif opcode == "0010011":
        decode_i_type(instr)
    elif opcode == "1100011":
        decode_b_type(instr)
    elif opcode == "1101111":
        decode_j_type(instr)
    elif opcode == "0110111":
        decode_u_type(instr)
    elif opcode == "0100011":
        decode_s_type(instr)


def fetch(pc):  # get next instruction and increment pc with 4
    next_instr = instructions[pc] + instructions[pc + 1] + instructions[pc + 2] + instructions[pc + 3]
    instr_bin = '{:032b}'.format(int(next_instr, 16))
    decode(instr_bin)
    pc += 4


def main():
    global pc
    input_file_name = sys.argv[1]
    try:
        with open(input_file_name) as f:
            lines = f.readlines()
            last = 0
            for l in lines:
                l = l.split()

                # check if the current line is an instruction (ex: "8000000c: 00000093" is a valid instruction)
                if len(l) == 2 and len(l[0]) == 9 and len(l[1]) == 8 and l[0][:8].isalnum() and l[1].isalnum():
                    addr = int(l[0][:8], 16)
                    addr = addr - 2 ** 31  # subtract 2 ^ 31 from addresses to have lower indexes
                    while last != addr:  # if the addresses of the instructions are not consecutive we put bytes of 0 between
                        instructions.append("00")  # so that the program does not execute anything
                        last += 1
                    instructions.append(l[1][:2])
                    instructions.append(l[1][2:4])
                    instructions.append(l[1][4:6])
                    instructions.append(l[1][6:8])
                    last += 4
    except FileNotFoundError:
        print("Input file not found!")
    else:
        while pc + 4 <= len(instructions):
            fetch(pc)


if __name__ == '__main__':
    main()

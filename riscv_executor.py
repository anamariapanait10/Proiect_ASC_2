import sys

memory = []  # bytes array
x = [0] * 32  # registers x0-x31
pc = 0  # program counter register


def from_two_s_compl_bin_to_int(bits, nrBits):
    sum = -1 * (1 << (nrBits - 1)) * (int(bits[0]))
    pow = 1 << (nrBits - 2)
    for pos in range(1, nrBits):
        sum += (int(bits[pos])) * pow
        pow >>= 1
    return sum


def unsigned32(signed):
    return signed % 0x100000000


def write_back(rd, res):
    if rd != 0:
        x[rd] = res


def write_back_mem(val, addr):
    val = hex(val)[2:10]
    while len(val) < 8:
        val = "0" + val
    memory[addr] = val[0:2]
    memory[addr + 1] = val[2:4]
    memory[addr + 2] = val[4:6]
    memory[addr + 3] = val[6:8]


def memory_access_pc(res):
    global pc
    pc = res - 4


def memory_access_load(addr):
    return "".join(memory[addr:addr + 4])


def execute_ori(rs1, rs2, rd):
    res = x[rs1] | x[rs2]
    write_back(rd, res)


def execute_srl(rs1, rs2, rd):
    val = x[rs1]
    val1 = unsigned32(x[rs2])
    low5 = int('{:032b}'.format(val1)[-5:], 2)
    if low5 > 0:
        shift = unsigned32(x[rs1]) >> low5
    else:
        shift = val
    write_back(rd, shift)


def execute_xor(rs1, rs2, rd):
    res = x[rs1] ^ x[rs2]
    write_back(rd, res)


def execute_rem(rs1, rs2, rd):
    divident = x[rs1]
    divisor = x[rs2]
    if divisor != 0:
        sgn = 1 if divident * divisor > 0 else -1
        quotient = abs(divident) // abs(divisor) * sgn
        remainder = divident - divisor * quotient
        write_back(rd, remainder)
    else:
        write_back(rd, divident)


def execute_addi(imm, rs1, rd):
    res = x[rs1] + imm
    if res > ((1 << 31) - 1):
        res -= (1 << 31) - 1
        res = -(1 << 31) + res - 1
    if res < (-(1 << 31)):
        res = -(res + (1 << 31))
        res = (1 << 31) - 1 - res + 1
    write_back(rd, res)


def execute_slli(shamt, rs1, rd):
    res = x[rs1] << shamt
    write_back(rd, res)


def execute_srai(shamt, rs1, rd):
    res = x[rs1] >> shamt
    write_back(rd, res)


def execute_lw(imm, rs1, rd):
    addr = imm + x[rs1]
    res = from_two_s_compl_bin_to_int('{:032b}'.format((int(memory_access_load(addr), 16))), 32)
    write_back(rd, res)


def execute_beq(imm, rs1, rs2):
    if x[rs1] == x[rs2]:
        global pc
        res = pc + imm * 2
        memory_access_pc(res)


def execute_bne(imm, rs1, rs2):
    if x[rs1] != x[rs2]:
        global pc
        res = pc + imm * 2
        memory_access_pc(res)


def execute_jal(offset, rd):
    global pc
    new_pc = pc + offset * 2
    memory_access_pc(new_pc)
    if rd != 0:
        res = pc + 4
        write_back(rd, res)


def execute_lui(imm, rd):
    res = from_two_s_compl_bin_to_int(imm + "0" * 12, 32)
    write_back(rd, res)


def execute_auipc(imm, rd):
    imm = from_two_s_compl_bin_to_int(imm + "0" * 12, 32)
    global pc
    res = imm + pc
    write_back(rd, res)


def execute_sw(imm, rs1, rs2):
    write_back_mem(unsigned32(x[rs2]), x[rs1] + imm)


def execute_fsw(imm, rs1, rs2):
    res = float(int(x[rs1], 2)) + imm
    write_back(rs2, res)


def execute_ecall():
    argvs = x[10:17]  # a0-a6 = x[10]-x[16]
    if argvs[0] == 1:
        print("pass")
    else:
        print("fail")
    sys.exit(0)


def execute_unimp():
    sys.exit(0)


# R-type memory: using 3 register inputs (add, xor, mul) - arithmetic/logical operations
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
    funct3 = instr[-15:-12]
    rd = int(instr[-12:-7], 2)

    if funct3 == "110" and funct7 == "0000000":  # ori instruction
        execute_ori(rs1, rs2, rd)
    elif funct3 == "101":  # srl instruction
        execute_srl(rs1, rs2, rd)
    elif funct3 == "100":  # xor instruction
        execute_xor(rs1, rs2, rd)
    elif funct3 == "110" and funct7 == "0000001":  # rem instruction
        execute_rem(rs1, rs2, rd)


# I-type memory: with immediates, loads (addi, lw, jalr, slli) - 2 registers + immediate
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
    imm = instr[:12]
    if imm[0] == "0":
        imm = "0" * 20 + imm
    else:
        imm = "1" * 20 + imm
    imm = from_two_s_compl_bin_to_int(imm, 32)
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
    # elif funct3 == "101":
    # if instr[:7] == "0000000":
    #    execute_srli(shamt, rs1, rd)
    #
    #   execute_srai(shamt, rs1, rd)


def decode_b_type(instr):
    imm = from_two_s_compl_bin_to_int(instr[0] + instr[-8] + instr[-31:-25] + instr[-12:-8], 12)
    funct3 = instr[-15:-12]
    rs1 = int(instr[-20:-15], 2)
    rs2 = int(instr[-25:-20], 2)

    if funct3 == "001":
        execute_bne(imm, rs1, rs2)
    if funct3 == "000":
        execute_beq(imm, rs1, rs2)


# U-type memory: with upper immediates (lui, auipc)
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


# UJ-type memory: jump memory (jal)
# 31 ... 12             11 ... 7 6 ...0
# imm[20|10:1|11|19:12]    rd   opcode
#    20

def decode_j_type(instr):
    offset = from_two_s_compl_bin_to_int(instr[0] + instr[-20:-12] + instr[-21] + instr[-31:-21], 20)
    rd = int(instr[-12:-7], 2)
    execute_jal(offset, rd)


# S-type memory: store memory (sw, sb)
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
    elif opcode == "0010011" or opcode == "0000011":
        decode_i_type(instr)
    elif opcode == "1100011":
        decode_b_type(instr)
    elif opcode == "1101111":
        decode_j_type(instr)
    elif opcode == "0110111" or opcode == "0010111":
        decode_u_type(instr)
    elif opcode == "0100011":
        decode_s_type(instr)
    elif opcode == "1110011":
        execute_ecall()


def fetch():  # get next instruction and increment pc with 4
    global pc
    next_instr = memory[pc] + memory[pc + 1] + memory[pc + 2] + memory[pc + 3]
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
            for line in lines:
                line = line.split()

                # check if the current line is an instruction (ex: "8000000c: 00000093" is a valid instruction)
                if len(line) == 2 and len(line[0]) == 9 and len(line[1]) <= 8 and line[0][:8].isalnum() and line[1].isalnum():
                    addr = int(line[0][:8], 16)
                    addr = addr - 2 ** 31  # subtract 2 ^ 31 from addresses to have lower indexes
                    while last != addr:  # if the addresses of the memory are not consecutive we put bytes of 0 between
                        memory.append("00")  # so that the program does not execute anything
                        last += 1
                    if len(line[1]) >= 2:
                        memory.append(line[1][:2])
                    if len(line[1]) >= 4:
                        memory.append(line[1][2:4])
                    if len(line[1]) >= 6:
                        memory.append(line[1][4:6])
                    if len(line[1]) >= 8:
                        memory.append(line[1][6:8])
                    if len(line[1]) == 8:
                        last += 4
                    else:
                        last += 2

    except FileNotFoundError:
        print("Input file not found!")
    else:
        memory.extend(["00"] * 1000000)
        while pc + 4 <= len(memory):
            fetch()


if __name__ == '__main__':
    main()
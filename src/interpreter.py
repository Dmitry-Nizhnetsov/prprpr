"""Interpreter for the educational virtual machine."""

import sys
import xml.etree.ElementTree as ET


def mask(n):
    """Return bitmask with n ones."""
    return 2 ** n - 1


def parse_arguments(argv):
    """Parse command line arguments and return a tuple."""
    if len(argv) < 5:
        return None, None, 0, 0
    bin_path = argv[1]
    dump_path = argv[2]
    start_addr = int(argv[3])
    end_addr = int(argv[4])
    return bin_path, dump_path, start_addr, end_addr


def load_binary(path):
    """Load binary file and return bytes."""
    with open(path, "rb") as file:
        return file.read()


def save_dump(memory, start, end, path):
    """Save memory range to XML."""
    root = ET.Element("memory")
    for i in range(start, end + 1):
        cell = ET.SubElement(root, "cell", address=str(i))
        cell.text = str(memory[i])
    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def run_program(bytecode, dump_path, start, end):
    """Main interpreter loop."""
    memory = [0] * 65536
    pc = 0
    acc = 0
    while pc < len(bytecode):
        b1 = bytecode[pc]
        opcode = b1 & 0b11111
        if opcode == 22:
            b2 = bytecode[pc + 1]
            b3 = bytecode[pc + 2]
            val = b1 | (b2 << 8) | (b3 << 16)
            acc = (val >> 5) & mask(18)
            pc += 3
        elif opcode == 4:
            b2 = bytecode[pc + 1]
            val = b1 | (b2 << 8)
            offset = (val >> 5) & mask(9)
            acc = memory[acc + offset]
            pc += 2
        elif opcode == 17:
            b2 = bytecode[pc + 1]
            b3 = bytecode[pc + 2]
            b4 = bytecode[pc + 3]
            val = b1 | (b2 << 8) | (b3 << 16) | (b4 << 24)
            addr = (val >> 5) & mask(24)
            memory[addr] = acc
            pc += 4
        else:
            break

    save_dump(memory, start, end, dump_path)


def main(argv):
    """Entry point of the interpreter."""
    bin_path, dump_path, start, end = parse_arguments(argv)
    if bin_path is None:
        print("Usage: python src/interpreter.py <bin> <xml> <start> <end>")
        return
    bytecode = load_binary(bin_path)
    run_program(bytecode, dump_path, start, end)


if __name__ == "__main__":
    main(sys.argv)
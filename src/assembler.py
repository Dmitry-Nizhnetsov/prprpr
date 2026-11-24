"""Assembler for the educational virtual machine."""

import sys
import yaml


def mask(n):
    """Return bitmask with n ones."""
    return 2 ** n - 1


def parse_arguments(argv):
    """Parse command line arguments and return a tuple."""
    if len(argv) < 3:
        return None, None, False
    source_path = argv[1]
    binary_path = argv[2]
    test_mode = len(argv) > 3 and argv[3] == "--test"
    return source_path, binary_path, test_mode


def load_yaml(path):
    """Read yaml file and return list of operations."""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def to_intermediate(program):
    """Convert yaml dicts to list of intermediate tuples."""
    result = []
    for item in program:
        op = item["op"]
        if op == "load_const":
            result.append(("load_const", item["arg"]))
        if op == "read_mem":
            result.append(("read_mem", item["arg"]))
        if op == "write_mem":
            result.append(("write_mem", item["arg"]))
        if op == "unary_minus":
            result.append(("unary_minus", 0))
    return result


def pack_load_const(value):
    """Pack load_const command into 3 bytes."""
    bits = 22
    bits |= (value & mask(18)) << 5
    return bits.to_bytes(3, byteorder="little")


def pack_read_mem(offset):
    """Pack read_mem command into 2 bytes."""
    bits = 4
    bits |= (offset & mask(9)) << 5
    return bits.to_bytes(2, byteorder="little")


def pack_write_mem(address):
    """Pack write_mem command into 4 bytes."""
    bits = 17
    bits |= (address & mask(24)) << 5
    return bits.to_bytes(4, byteorder="little")


def pack_unary_minus():
    """Pack unary_minus command into 1 byte."""
    return bytes([31])


def assemble_to_bytes(intermediate):
    """Convert intermediate tuples to a single byte string."""
    binary_data = b""
    for inst in intermediate:
        if inst[0] == "load_const":
            binary_data += pack_load_const(inst[1])
        if inst[0] == "read_mem":
            binary_data += pack_read_mem(inst[1])
        if inst[0] == "write_mem":
            binary_data += pack_write_mem(inst[1])
        if inst[0] == "unary_minus":
            binary_data += pack_unary_minus()
    return binary_data


def main(argv):
    """Entry point of the assembler."""
    source, binary, test_mode = parse_arguments(argv)
    if source is None:
        print("Usage: python src/assembler.py <src> <bin> [--test]")
        return

    data = load_yaml(source)

    if isinstance(data, dict) and "program" in data:
        program = data["program"]
    else:
        program = data

    intermediate = to_intermediate(program)

    if test_mode:
        print("Intermediate representation:")
        for item in intermediate:
            print(item)

    bytecode = assemble_to_bytes(intermediate)
    with open(binary, "wb") as file:
        file.write(bytecode)

    print(f"Assembled {len(intermediate)} commands")
    print(f"File size: {len(bytecode)} bytes")


if __name__ == "__main__":
    main(sys.argv)
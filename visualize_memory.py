#!/usr/bin/python3
# Copyright 2023, Luca Weiss
# SPDX-License-Identifier: MIT

#
# Script to show a visual representation of reserved-memory nodes in devicetree.
#

from collections.abc import Iterator
import sys
import matplotlib.pyplot as plt

import libfdt
from libfdt import FDT_ERR_NOTFOUND


def fdt_subnodes(self: libfdt.FdtRo, parent: int) -> Iterator[int]:
    offset = self.first_subnode(parent, [FDT_ERR_NOTFOUND])
    while offset != -FDT_ERR_NOTFOUND:
        yield offset
        offset = self.next_subnode(offset, [FDT_ERR_NOTFOUND])


libfdt.FdtRo.subnodes = fdt_subnodes


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <dtb_file>")
        sys.exit(1)

    with open(sys.argv[1], mode='rb') as f:
        fdt = libfdt.FdtRo(f.read())

    memory: int = fdt.path_offset('/reserved-memory')

    address_cells = fdt.getprop(memory, "#address-cells").as_uint32()
    size_cells = fdt.getprop(memory, "#size-cells").as_uint32()
    if address_cells == 1 and size_cells == 1:
        reg_prop_cells = 1
    elif address_cells == 2 and size_cells == 2:
        reg_prop_cells = 2
    else:
        print(f"ERROR: Unexpected combination of #address-cells ({address_cells}) and #size-cells ({size_cells})")
        sys.exit(1)

    print(f"INFO: Detected #address-cells = <{address_cells}> and #size-cells = <{size_cells}>")

    i = 1
    for memory_subnode in fdt.subnodes(memory):
        name = fdt.get_name(memory_subnode)
        name_clean = name.split("@")[0]
        phandle = fdt.get_phandle(memory_subnode)
        path = fdt.get_path(memory_subnode)

        reg_prop = fdt.getprop(memory_subnode, "reg").as_uint32_list()
        match reg_prop_cells:
            case 1:
                reg_addr = reg_prop[0]
                reg_size = reg_prop[1]
            case 2:
                reg_addr = reg_prop[0] << 8 | reg_prop[1]
                reg_size = reg_prop[2] << 8 | reg_prop[3]
            case _:
                raise RuntimeError(f"Invalid reg_prop_cells value {reg_prop_cells}")

        reg_end = reg_addr + reg_size

        print(f"name={name}, phandle={phandle}, path={path}, reg={hex(reg_addr)}+{hex(reg_size)}={hex(reg_end)}")
        plt.plot([reg_addr, reg_end], [i, i], linewidth = '10')
        plt.annotate(hex(reg_addr), (reg_addr, i), textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate(hex(reg_end), (reg_end, i), textcoords="offset points", xytext=(0,-10), ha='center')

        plt.annotate(name_clean, (reg_addr + (reg_size/2), i), textcoords="offset points", xytext=(0,0), ha='center')
        i += 1

    plt.grid(axis = 'x')
    plt.show()


if __name__ == '__main__':
    main()

#!/usr/bin/python3
# Copyright 2023, Luca Weiss
# SPDX-License-Identifier: MIT

#
# Script to show a visual representation of reserved-memory nodes in devicetree.
#

import sys
import matplotlib.pyplot as plt

import libfdt
from libfdt import FDT_ERR_NOTFOUND


def fdt_subnodes(self, parent):
    offset = self.first_subnode(parent, [FDT_ERR_NOTFOUND])
    while offset != -FDT_ERR_NOTFOUND:
        yield offset
        offset = self.next_subnode(offset, [FDT_ERR_NOTFOUND])


libfdt.FdtRo.subnodes = fdt_subnodes


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <dtb_file>")
        sys.exit(1)

    with open(sys.argv[1], mode='rb') as f:
        fdt = libfdt.FdtRo(f.read())

    memory: int = fdt.path_offset('/reserved-memory')

    i = 1
    for memory_subnode in fdt.subnodes(memory):
        name = fdt.get_name(memory_subnode)
        name_clean = name.split("@")[0]
        phandle = fdt.get_phandle(memory_subnode)
        path = fdt.get_path(memory_subnode)
        reg = fdt.getprop(memory_subnode, "reg").as_uint32_list()
        reg_end = reg[0] + reg[1]

        print(f"name={name}, phandle={phandle}, path={path}, reg={hex(reg[0])}+{hex(reg[1])}={hex(reg_end)}")
        plt.plot([reg[0], reg_end], [i, i], linewidth = '10')
        plt.annotate(hex(reg[0]), (reg[0], i), textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate(hex(reg_end), (reg_end, i), textcoords="offset points", xytext=(0,-10), ha='center')

        plt.annotate(name_clean, (reg[0] + (reg[1]/2), i), textcoords="offset points", xytext=(0,0), ha='center')
        i += 1

    plt.grid(axis = 'x')
    plt.show()


if __name__ == '__main__':
    main()

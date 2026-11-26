#!/usr/bin/env python3
"""Turn on MSVC multi-processor compilation for one generated vcxproj.

CMake never emits /MP for tdesktop, so MSBuild compiles the ~1500 translation
units of the Telegram project strictly one at a time. That single-threaded
project is what pushed a run to 5h50m and into the runner's 6h job limit.

Two processes is deliberate: every cl.exe keeps its own mapping of the very
large precompiled header, and the runner's commit limit is what kills four
nodes with C3859/C1060/LNK1102.

Usage: python3 ci_enable_mp.py <path to Telegram.vcxproj>
"""

import sys

BLOCK = (
    "  <ItemDefinitionGroup>\n"
    "    <ClCompile>\n"
    "      <MultiProcessorCompilation>true</MultiProcessorCompilation>\n"
    "      <ProcessorNumber>2</ProcessorNumber>\n"
    "    </ClCompile>\n"
    "  </ItemDefinitionGroup>\n"
)

MARKER = "<MultiProcessorCompilation>true</MultiProcessorCompilation>"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8-sig") as handle:
        text = handle.read()

    if MARKER in text:
        print("MultiProcessorCompilation is already enabled in", path)
        return

    index = text.rindex("</Project>")
    text = text[:index] + BLOCK + text[index:]

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)

    with open(path, "r", encoding="utf-8-sig") as handle:
        written = handle.read()

    if MARKER not in written:
        sys.exit("the property did not land in " + path)

    print("enabled /MP2 in", path)


if __name__ == "__main__":
    main()

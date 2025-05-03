from typing import List, TextIO
from sys import stdout

def gen(nodes: List[List[int]], output: TextIO = stdout) -> None:
    print(len(nodes), file=output)
    for node in nodes:
        print(node[0], end=' ', file=output)
        print(len(node) - 1, end=' ', file=output)
        print(' '.join(map(str, node[1:])), file=output)
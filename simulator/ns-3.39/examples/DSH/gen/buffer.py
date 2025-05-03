from typing import List, TextIO
from sys import stdout

def gen(nodes: List[int], output: TextIO = stdout) -> None:
    print(len(nodes), file=output)
    print(' '.join(map(str, nodes)), file=output)

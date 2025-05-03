#!/usr/bin/env python3
from typing import Tuple, List, TextIO, Iterable
from sys import stdout
import random
from bisect import bisect

FlowList = List[Tuple[int, int, int, int, int, float]]


def gen_flows(dport: int, size: int, src_dst_stime: List[Tuple[int, int, int, float]]) -> FlowList:
    return [(src, dst, pg, dport, size, stime) for src, dst, pg, stime in src_dst_stime]


def gen(flows: FlowList, output: TextIO = stdout) -> None:
    for src, dst, pg, _, size, stime in flows:
        assert(src != dst)
        assert(size > 0)
        assert(stime > 0)
        assert(1 <= pg < 8)
    print(len(flows), file=output)
    for src, dst, pg, dport, sz, stime in flows:
        print(src, dst, pg, dport, sz, stime, file=output)
        

class FlowSizeRng:
    def __init__(self, cdf: Iterable[Tuple[float, int]]) -> None:
        self.cdf = list(cdf)
        self.cdf.sort()
        assert self.cdf[0][0] == 0
        assert self.cdf[-1][0] == 1
        for i in range(1, len(self.cdf)):
            assert self.cdf[i][0] > self.cdf[i-1][0]
            assert self.cdf[i][1] >= self.cdf[i-1][1]

    @staticmethod
    def from_tcl(fname: str) -> 'FlowSizeRng':
        cdf = []
        with open(fname, 'r') as fp:
            for line in fp.readlines():
                rec = line.strip().split(' ')
                if len(rec) != 3:
                    continue
                size = round(float(rec[0]) * 1460)
                cdf.append((float(rec[2]), size))
        ret = FlowSizeRng(cdf)
        return ret

    def rand(self) -> int:
        r = random.random()
        i = bisect(self.cdf, (r, 0))
        assert 0 < i < len(self.cdf)
        mx = self.cdf[i][1]
        mn = min(max(self.cdf[i-1][1]+1, 1), mx)
        return random.randint(mn, mx)

    def avg(self) -> float:
        ret = 0.0
        for i in range(1, len(self.cdf)):
            sz = (self.cdf[i-1][1] + self.cdf[i][1]) / 2
            p = self.cdf[i][0] - self.cdf[i-1][0]
            ret += sz * p
        return ret

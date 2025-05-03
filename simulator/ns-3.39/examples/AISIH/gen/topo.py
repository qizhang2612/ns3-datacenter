#!/usr/bin/env python3
from typing import Tuple, List, Set, TextIO
from sys import stdout

LinkList = List[Tuple[int, int, str, str]]


def gen_links(rate, delay, src_dst: List[Tuple[int, int]]) -> LinkList:
    return [(src, dst, rate, delay) for src, dst in src_dst]


def gen(hosts: Set[int], switchs: Set[int], links: LinkList, output: TextIO = stdout) -> None:
    total_n = len(hosts) + len(switchs)
    for src, dst, _, _ in links:
        assert(src < total_n)
        assert(dst < total_n)
        assert(src != dst)
    print(total_n, len(switchs), len(switchs), len(links), file=output)
    print(*sorted(switchs), file=output)
    for src, dst, rate, delay in links:
        print(src, dst, rate, delay, '0', file=output)


def build_fattree(k: int, LR_Gbps: int, pod_delay: str, core_delay: str) -> Tuple[List[int], List[int], LinkList]:
    nhost = (k**3)//4
    nedge = (k**2)//2
    nagg = (k**2)//2
    ncore = (k**2)//4
    all_nodes = list(range(nhost + nedge + nagg + ncore))
    hosts, all_nodes = all_nodes[:nhost], all_nodes[nhost:]
    edges, all_nodes = all_nodes[:nedge], all_nodes[nedge:]
    aggs, all_nodes = all_nodes[:nagg], all_nodes[nagg:]
    cores, all_nodes = all_nodes[:ncore], all_nodes[ncore:]
    assert len(all_nodes) == 0

    pod_links: List[Tuple[int, int]] = []
    core_links: List[Tuple[int, int]] = []
    for i in range(k):
        for j in range(i*k//2, (i+1)*k//2):
            for h in hosts[j*k//2:(j+1)*k//2]:
                pod_links.append((h, edges[j]))
            for agg in aggs[i*k//2:(i+1)*k//2]:
                pod_links.append((edges[j], agg))
            t = j - i*k//2
            for core in cores[t*k//2:(t+1)*k//2]:
                core_links.append((aggs[j], core))

    links = gen_links(f'{LR_Gbps}Gbps', pod_delay, pod_links)
    links += gen_links(f'{LR_Gbps}Gbps', core_delay, core_links)
    return hosts, edges + aggs + cores, links


def build_roce_at_scale(LR_Gbps: int) -> Tuple[List[int], List[int], LinkList]:
    npod = 2
    nhost = 576 * npod
    ntor = 24 * npod
    nleaf = 4 * npod
    nspine = 64
    all_nodes = list(range(nhost + ntor + nleaf + nspine))
    hosts, all_nodes = all_nodes[:nhost], all_nodes[nhost:]
    tors, all_nodes = all_nodes[:ntor], all_nodes[ntor:]
    leafs, all_nodes = all_nodes[:nleaf], all_nodes[nleaf:]
    spines, all_nodes = all_nodes[:nspine], all_nodes[nspine:]
    assert len(all_nodes) == 0

    tor_links: List[Tuple[int, int]] = []
    leaf_links: List[Tuple[int, int]] = []
    spine_links: List[Tuple[int, int]] = []
    for i in range(npod):
        for j in range(4):
            leaf = leafs[i*4 + j]
            for spine in spines[j*16:(j+1)*16]:
                spine_links.append((leaf, spine))
            for tor in tors[i*24:(i+1)*24]:
                leaf_links.append((tor, leaf))
    for i in range(ntor):
        tor = tors[i]
        for host in hosts[i*24:(i+1)*24]:
            tor_links.append((host, tor))

    bw = f'{LR_Gbps}Gbps'
    links = gen_links(bw, '0.02us', tor_links)
    links += gen_links(bw, '0.2us', leaf_links)
    links += gen_links(bw, '3us', spine_links)

    return hosts, tors + leafs + spines, links


def build_spine_leaf(nspine: int, nleaf: int, nhost: int, SL_Gbps: int, LH_Gbps: int, delay: str) \
                    -> Tuple[List[int], List[int], LinkList]:
    all_nodes = list(range(nspine + nleaf + nleaf * nhost))
    hosts, all_nodes = all_nodes[:nleaf * nhost], all_nodes[nleaf * nhost:]
    leafs, all_nodes = all_nodes[:nleaf], all_nodes[nleaf:]
    spines, all_nodes = all_nodes[:nspine], all_nodes[nspine:]
    assert len(all_nodes) == 0

    leaf_links: List[Tuple[int, int]] = []
    spine_links: List[Tuple[int, int]] = []
    for spine in spines:
        for leaf in leafs:
            spine_links.append((spine, leaf))

    for i in range(nleaf):
        for j in range(nhost):
            leaf_links.append((leafs[i], hosts[i * nhost + j]))
    
    sl_bw = f'{SL_Gbps}Gbps'
    lh_bw = f'{LH_Gbps}Gbps'
    links = gen_links(lh_bw, delay, leaf_links)
    links += gen_links(sl_bw, delay, spine_links)

    return hosts, leafs + spines, links



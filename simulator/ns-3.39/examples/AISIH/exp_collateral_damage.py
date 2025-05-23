#!/usr/bin/env python3
from typing import List, Set, Dict, Any, Tuple
from gen.flow import FlowList

import random
from multiprocessing import Pool, cpu_count

import gen.topo as topo
import gen.flow as flow
import gen.config as config
import gen.waf as waf
import analyze as ana
import utils

from random import randint
from subprocess import CalledProcessError
import pandas as pd
import time
from pathlib import Path

import gen.buffer as buflog
import gen.flow_status as flowlog
import gen.hdrm_local_max as hdrmlog

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

ID_MAP = {i: i for i in range(1, 8)}


def exp_send_time(lam: float, n: int, seed: int = 0) -> List[float]:
    if seed != 0:
        random.seed(seed)
    stime = [0.0] * n
    for i in range(1, n):
        stime[i] = stime[i-1] + random.expovariate(lam)
    if seed != 0:
        random.seed(time.time())
    return stime


def get_test_dir(test_name: str) -> Path:
    return Path('./data') / test_name


def exp_pfc_avoidance(  # pylint: disable=W0102
        SH_Gbps=100,
        delay='2000ns',
        buffer_size=16,
        port_hdrm_k=4.0,
        mx_pg=7,
        mmu_kind="NORMAL",
        start_time=2000000,

        burst_start=2800,
        burst_hosts=24, 
        burst_size=64,

        sche='DWRR',
        cc='None',
        hdrm_reserve=1,
        quantums: List[int] = [1600]*8,
        pg_map: Dict[int, int] = ID_MAP,
) -> str:
    test_name = f'exp_collateral_damage_{mmu_kind}-{sche}-{cc}-{burst_hosts}h-{mx_pg+1}pg'
    test_dir = utils.get_test_dir(test_name)
    test_dir.mkdir(exist_ok=True)

    # topo
    all_nodes = list(range(2 + 2 + burst_hosts + 2))
    hosts, sws = all_nodes[:2 + burst_hosts + 2], all_nodes[2 + burst_hosts + 2:]

    link: List[Tuple[int, int]] = []

    for host in hosts[:2]:
        link.append((host, sws[0]))

    for host in hosts[2:]:
        link.append((host, sws[1]))

    link.append((sws[0], sws[1]))

    bw = f'{SH_Gbps}Gbps'
    links = topo.gen_links(bw, delay, link)


    with open(test_dir / 'topo.txt', 'w') as topof:
        topo.gen(set(hosts), set(sws), links, output=topof)

    flows: FlowList = []

    # F0, F1, F2
    flows += flow.gen_flows(100, 2500000000, [(hosts[0], hosts[-1], 2, start_time)])
    flows += flow.gen_flows(100, 2500000000, [(hosts[1], hosts[-2], 2, start_time)])
    # flows += flow.gen_flows(100, 2500000000, [(hosts[2], hosts[-2], 2, start_time)])

    #Burst
    dst = hosts[-2]
    for src in hosts[2:2 + burst_hosts]:
        flows += flow.gen_flows(100, burst_size*KB, [(src, dst, 2, start_time + burst_start)])
    
    with open(test_dir / 'flow.txt', 'w') as flowf:
        flow.gen(flows, output=flowf)

    with open(test_dir / 'config.txt', 'w') as configf:
        config.gen(test_name,
                   cc=cc,
                   buffer_size=buffer_size,
                   # stop_time=(start_time + 
                   #    last_send_time + 100) / 1e6,
                   stop_time=(start_time + 3600
                   ) / 1e6,
                   dt_alpha=4,
                   pg_count=mx_pg+1,
                   sche_alg=sche,
                   quantums=quantums,
                   mmu_kind=mmu_kind,
                   hdrm_reserve=hdrm_reserve,
                   port_hdrm_k=port_hdrm_k,
                   output=configf)
        with open(test_dir / 'buffer_in.txt', 'w') as buflogf:
            buflog.gen([], output=buflogf)

        with open(test_dir / 'flow_status_in.txt', 'w') as flowlogf:
            flowlog.gen([], output=flowlogf)
        
        with open(test_dir / 'hdrm_local_max_value_in.txt', 'w') as hdrmlogf:
            hdrmlog.gen([], output=hdrmlogf, all=False)

    return test_name


def build_pg_map(*pg_grps: List[int]) -> Dict[int, int]:
    ret = {}
    for to in range(len(pg_grps)):
        assert 1 <= to+1 <= 7
        for frm in pg_grps[to]:
            assert frm not in ret
            assert 1 <= frm <= 7
            ret[frm] = to+1
    return ret


PGMAPS = {
    3: (
        build_pg_map([1, 2], [3, 4], [5, 6, 7]),
        [1600, 1600, 1600, 3200],
    ),
    5: (
        build_pg_map([1], [2], [3, 4], [5, 6], [7]),
        [1600, 1600, 1600, 3200, 3200, 3200],
    ),
    6: (
        build_pg_map([1], [2], [3], [4], [5, 6], [7]),
        [1600, 1600, 1600, 1600, 1600, 3200, 3200],
    ),
    7: (
        ID_MAP,
        [1600] * 7 + [3200],
    ),
    8: (
        ID_MAP,
        [1600] * 8,
    ),
}


def main() -> None:
    tests: Set[str] = set()
    for CC in ['None', 'HPCC', 'PowerTCP', 'DCQCN']:
        for pg in [8]:
            pgmap, quantums = PGMAPS[pg]
            #for mmu in ['Normal']:
            for mmu in ['Normal','AISIH']:
                ks : List[Any]
                if mmu == 'Normal' or mmu == "AISIH" :
                    ks = [pg+1]
                else:
                    ks = [pg+1]
                for k in ks:
                    ## hdrm_utilization_incast
                    test_name = exp_pfc_avoidance(
                        mx_pg=7,
                        cc=CC,
                        mmu_kind=mmu,
                        port_hdrm_k=k,
                        pg_map=pgmap,
                        quantums=quantums)                    
                    if test_name in tests:
                        print('tests:')
                        print(tests)
                        print(f'test_name: {test_name}')
                        raise BaseException
                    tests.add(test_name)

    utils.run_in_pool(24, tests)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from typing import List, Set, Dict, Any
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
        nspine=0,
        nleaf=1,
        nhost=32,
        SL_Gbps=100,
        LH_Gbps=100,
        delay='2000ns',
        buffer_size=3,
        port_hdrm_k=4.0,
        mx_pg=7,
        mmu_kind="DSH",
        start_time=2000000,

        burst_size_perc=0.9,
        burst_start=10000,
        burst_hosts=16, 

        sche='DWRR',
        cc='None',
        hdrm_reserve=1,
        quantums: List[int] = [1600]*8,
        pg_map: Dict[int, int] = ID_MAP,
) -> str:
    test_name = f'exp_pfc_avoidance_{mmu_kind}-{sche}-{cc}-{burst_hosts}h-{burst_size_perc}bp-{mx_pg+1}pg'
    test_dir = utils.get_test_dir(test_name)
    test_dir.mkdir(exist_ok=True)

    host, sw, links = topo.build_spine_leaf(nspine, nleaf, nhost, SL_Gbps, LH_Gbps, delay)

    with open(test_dir / 'topo.txt', 'w') as topof:
        topo.gen(set(host), set(sw), links, output=topof)

    flows: FlowList = []

    # two background flow
    flows += flow.gen_flows(100, 2500000000, [(host[0], host[-1], 2, start_time)])
    flows += flow.gen_flows(100, 2500000000, [(host[1], host[-1], 2, start_time)])
    # for src in range(0, 2):
    #     for j in range(1, 3):
    #         flows += flow.gen_flows(100, 2500000000, [(src, host[-1], j, start_time)])

    # 16 fan-in bursty flows
    burst_size = (int)(MB * burst_size_perc * buffer_size / burst_hosts)
    dst = host[-2]
    if burst_size > 0:
        for src in host[2:2 + burst_hosts]:
        #for src in host[2:2 + burst_hosts]:
            for j in range(1, 8):
                flows += flow.gen_flows(100, int(burst_size/7), [(src, dst, j, start_time + burst_start)])
                #flows += flow.gen_flows(100, burst_size, [(src, dst, j, start_time + burst_start)])

    with open(test_dir / 'flow.txt', 'w') as flowf:
        flow.gen(flows, output=flowf)

    with open(test_dir / 'config.txt', 'w') as configf:
        config.gen(test_name,
                   cc=cc,
                   buffer_size=buffer_size,
                   # stop_time=(start_time + 
                   #    last_send_time + 100) / 1e6,
                   stop_time=(start_time + 100000 + 100) / 1e6,
                   dt_alpha=4,
                   pg_count=mx_pg+1,
                   sche_alg=sche,
                   quantums=quantums,
                   mmu_kind=mmu_kind,
                   port_hdrm_k=port_hdrm_k,
                   hdrm_reserve=hdrm_reserve,
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
    for burst in range(0, 11):
        burst_perc = burst / 10
        for pg in [8]:
            pgmap, quantums = PGMAPS[pg]
            #for mmu in ['DSH', 'Normal']:
            # for mmu in ['DSH','DSHPLUS']:
            for mmu in ['Normal']:
                # for mmu in ['DH', 'DH3']:
                ks : List[Any]
                # if mmu == 'Normal' or mmu == 'DSH' or mmu == 'QASH' or mmu == 'DSHPLUS':
                if mmu == 'Normal' or mmu == 'AISIH':
                    ks = [pg+1]
                else:
                    ks = [1, 1.5, 2, 2.5, 3]
                for k in ks:
                    ## hdrm_utilization_incast
                    test_name = exp_pfc_avoidance(
                        mx_pg=7,
                        mmu_kind=mmu,
                        port_hdrm_k=k,
                        burst_size_perc=burst_perc,
                        pg_map=pgmap,
                        quantums=quantums)                    
                    if test_name in tests:
                        print('tests:')
                        print(tests)
                        print(f'test_name: {test_name}')
                        raise BaseException
                    tests.add(test_name)

    utils.run_in_pool(40, tests)


if __name__ == '__main__':
    main()
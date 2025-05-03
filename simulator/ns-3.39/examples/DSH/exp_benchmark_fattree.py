#!/usr/bin/env python3
from typing import List, Set, Dict, Any, Tuple
from gen.flow import FlowList
from datetime import datetime

import os
import random
import time
import numpy as np


import gen.topo as topo
import gen.flow as flow
import gen.config as config
import gen.buffer as buflog
import gen.flow_status as flowlog
import gen.hdrm_local_max as hdrmlog
import utils


KB = 1024
MB = 1024 * KB
GB = 1024 * MB


def exp_send_time(lam: float, n: int, seed: int = 0) -> List[float]:
    if seed != 0:
        random.seed(seed)
    stime = [0.0] * n
    for i in range(1, n):
        stime[i] = stime[i-1] + random.expovariate(lam)
    if seed != 0:
        random.seed(time.time())
    return stime


ID_MAP = {i: i for i in range(1, 8)}


def exp_benchmark_fattree(  # pylint: disable=W0102
        LR_Gbps=100,
        fattree_k=16,
        pod_delay='2000ns',
        core_delay='2000ns',
        buffer_size=15,
        port_hdrm_k=4.0,
        mx_pg=7,
        mmu_kind="Normal",
        back_load=0.5,
        burst_load=0.4,
        
        burst_size=64,
        burst_hosts=128,
        flow_stop_time=2010000,

        flow_num=200000,
        start_time=2000000,
        send_time_seed=223333, 
        seed=575771,
        sche='PQ',
        cc='HPCC',
        quantums: List[int] = [1600]*8,
        pg_map: Dict[int, int] = ID_MAP,
) -> str:
    if mmu_kind == "Normal":
        buffer_size = 10
    test_name = f'exp_benchmark_fattree_k{fattree_k}-{mmu_kind}-{sche}-{cc}-{back_load}back-{burst_load}burst-{burst_hosts}x{burst_size}KB-{mx_pg+1}pg-0.01'
    test_dir = utils.get_test_dir(test_name)
    test_dir.mkdir(exist_ok=True)

    hosts, sw, links = topo.build_fattree(fattree_k, LR_Gbps, pod_delay, core_delay)
    nhost = len(hosts) // fattree_k

    with open(test_dir / 'topo.txt', 'w') as topof:
        topo.gen(set(hosts), set(sw), links, output=topof)

    # control the same flow between SIH and DSH
    copy_src = f'./data/exp_benchmark_fattree_k{fattree_k}-Normal-{sche}-{cc}-{back_load}back-{burst_load}burst-{burst_hosts}x{burst_size}KB-{mx_pg+1}pg-0.01/flow.txt'
    copy_dst = f'./data/exp_benchmark_fattree_k{fattree_k}-DSH-{sche}-{cc}-{back_load}back-{burst_load}burst-{burst_hosts}x{burst_size}KB-{mx_pg+1}pg-0.01/flow.txt'
    if mmu_kind == 'DSH' and os.path.exists(copy_src):
        os.system('cp -rf %s %s'%(copy_src, copy_dst))
    else:
        flows: FlowList = []

        # background flow
        flowsz = flow.FlowSizeRng.from_tcl('./flow-cdf/search_cdf.tcl')

        random.seed(seed)
        last_send_time = 0.0
        send_times: List[float] = []
        lam = back_load * (LR_Gbps * 1000 / 8) / flowsz.avg()

        if lam > 0:
            for src in hosts:
                send_times = exp_send_time(lam, flow_num // len(hosts), seed=send_time_seed)
                last_send_time = max(last_send_time, send_times[-1])
                for i in range(len(send_times)):
                    stime: float = start_time + send_times[i]
                    if stime > flow_stop_time:
                        break
                    fsz = flowsz.rand()
                    dst = random.sample(hosts, 1)[0]
                    # src and dst should not under the same pod
                    while (dst // nhost) == (src // nhost):
                        dst = random.sample(hosts, 1)[0]
                    pg = pg_map[random.randint(1, mx_pg)]
                    assert 1 <= pg <= mx_pg
                    # pg = 1
                    flows += flow.gen_flows(100, fsz, [(src, dst, pg, stime)])

        # incast flow
        burst_size = burst_size * KB
        lam = burst_load * (LR_Gbps * 1000 / 8) / (burst_hosts * burst_size)

        if lam > 0:
            for dst in hosts:
                send_times = exp_send_time(lam, flow_num // len(hosts), seed=send_time_seed)
                last_send_time = max(last_send_time, send_times[-1])
                for i in range(1, len(send_times)):
                    stime: float = start_time + send_times[i]
                    if stime > flow_stop_time:
                        break
                    pg = pg_map[random.randint(1, mx_pg)]
                    assert 1 <= pg <= mx_pg
                    # pg = 1
                    for j in range(burst_hosts):
                        src = random.randint(hosts[0], hosts[-1])
                        while (dst // nhost) == (src // nhost):
                            src = random.randint(hosts[0], hosts[-1])
                        flows += flow.gen_flows(200, burst_size, [(src, dst, pg, stime)])

    # # all dst in pod 0
    # # background flow
    # flowsz = flow.FlowSizeRng.from_tcl('./flow-cdf/search_cdf.tcl')

    # random.seed(seed)
    # last_send_time = 0.0
    # send_times: List[float] = []
    # lam = back_load * (LH_Gbps * 1000 / 8) / flowsz.avg()

    # if lam > 0:
    #     for dst in hosts[:nhost]:
    #         send_times = exp_send_time(lam, flow_num // (nhost * nleaf), seed=send_time_seed)
    #         last_send_time = max(last_send_time, send_times[-1])
    #         for i in range(len(send_times)):
    #             stime: float = start_time + send_times[i]
    #             fsz = flowsz.rand()
    #             src = random.randint(hosts[nhost], hosts[-1])
    #             pg = pg_map[random.randint(2, mx_pg)]
    #             assert 2 <= pg <= mx_pg
    #             flows += flow.gen_flows(100, fsz, [(src, dst, pg, stime)])
    
    # # incast flow 
    # burst_size = burst_size * KB
    # lam = burst_load * (LH_Gbps * 1000 / 8) / (burst_hosts * burst_size)

    # if lam > 0:
    #     send_times = exp_send_time(lam, flow_num // (nleaf * nhost), seed=send_time_seed)
    #     last_send_time = max(last_send_time, send_times[-1])
    #     for i in range(len(send_times)):
    #         stime: float = start_time + send_times[i]
    #         for dst in hosts[:nhost]:
    #             for i in range(burst_hosts):
    #                 src = random.randint(hosts[nhost], hosts[-1])
    #                 pg = 1 
    #                 flows += flow.gen_flows(100, burst_size, [(src, dst, pg, stime)])

        with open(test_dir / 'flow.txt', 'w') as flowf:
            flow.gen(flows, output=flowf)

    with open(test_dir / 'config.txt', 'w') as configf:
        config.gen(test_name,
                   cc=cc,
                   buffer_size=buffer_size,
                   # stop_time=(start_time + 
                   #    last_send_time + 100) / 1e6,
                   stop_time=(start_time + 2000000) / 1e6,
                   pg_count=mx_pg+1,
                   sche_alg=sche,
                   quantums=quantums,
                   mmu_kind=mmu_kind,
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
    for load10 in range(2, 9):
        load = load10 / 10
        for cc in ['DCQCN', 'PowerTCP']:
            for pg in [8]:
                pgmap, quantums = PGMAPS[pg]
                for mmu in ['Normal', 'DSH']:
                    # for mmu in ['DH', 'DH3']:
                    ks : List[Any]
                    if mmu == 'Normal' or mmu == 'DSH':
                        ks = [pg+1]
                    else:
                        ks = [1, 1.5, 2, 2.5, 3]
                    for k in ks:
                        test_name = exp_benchmark_fattree(
                            cc=cc,
                            mx_pg=7,
                            mmu_kind=mmu,
                            port_hdrm_k=k,
                            back_load=load,
                            burst_load=int(9-load10)/10,
                            pg_map=pgmap,
                            quantums=quantums)                    
                        if test_name in tests:
                            print('tests:')
                            print(tests)
                            print(f'test_name: {test_name}')
                            raise BaseException
                        tests.add(test_name)

    utils.run_in_pool(30, tests)


if __name__ == '__main__':
    main()

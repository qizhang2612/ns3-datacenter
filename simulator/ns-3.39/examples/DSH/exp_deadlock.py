#!/usr/bin/env python3
from typing import List, Set, Dict, Any, Tuple
from gen.flow import FlowList

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


def exp_deadlock(  # pylint: disable=W0102
        nspine=2,
        nleaf=4,
        #nhost=20,
        nhost=16,
        SL_Gbps=400,
        LH_Gbps=100,
        delay='2000ns',
        buffer_size=16,
        port_hdrm_k=4.0,
        mx_pg=7,
        mmu_kind="Normal",
        load=0.5,
        
        burst_size=300,
        burst_start=0,
        burst_hosts=15,

        test=1,

        flow_num=20000,
        start_time=2000000,
        send_time_seed=223333,
        seed=575771,
        sche='DWRR',
        cc='HPCC',
        cdf='search',
        hdrm_reserve=1,
        quantums: List[int] = [1600]*8,
        pg_map: Dict[int, int] = ID_MAP,
) -> str:
    test_name = f'exp_deadlock-xpod_{mmu_kind}-{sche}-{cc}-{cdf}_flow-{mx_pg+1}pg-{test}test'
    test_dir = utils.get_test_dir(test_name)
    test_dir.mkdir(exist_ok=True)

    host, sw, links = topo.build_spine_leaf(nspine, nleaf, nhost, SL_Gbps, LH_Gbps, delay)
    sl_bw = f'{SL_Gbps}Gbps'
    # # Add extra hosts to keep the headroom allocation
    # extra = [i for i in range(len(host) + len(sw), len(host) + len(sw) + 12 + 4)]
    # for h in extra[:5]:
    #     links.append((sw[-2], h, sl_bw, delay))
    
    # for h in extra[5:10]:
    #     links.append((sw[-1], h, sl_bw, delay))

    # links.append((sw[0], extra[10], sl_bw, delay))
    # links.append((sw[-3], extra[11], sl_bw, delay))

    # for i in range(4):
    #     links.append((sw[i], extra[12+i], sl_bw, delay))
    
    # host += extra

    # Link down: L0-T3, L1-T0
    #links.remove((84, 83, sl_bw, delay))
    #links.remove((85, 80, sl_bw, delay))
    links.remove((68, 67, sl_bw, delay))
    links.remove((69, 64, sl_bw, delay))

    with open(test_dir / 'topo.txt', 'w') as topof:
        topo.gen(set(host), set(sw), links, output=topof)

    flows: FlowList = []

    burst_size = burst_size * KB
    # ## incast
    # # T0 -> T3
    # dst = 60
    # for src in host[1:1+burst_hosts]:
    #     flows += flow.gen_flows(100, burst_size, [(src, dst, 2, start_time + burst_start)])

    # # T3 -> T0
    # dst = 0
    # for src in host[61:61+burst_hosts]:
    #     flows += flow.gen_flows(100, burst_size, [(src, dst, 2, start_time + burst_start)])

    # # T1 -> T2
    # dst = 40
    # for src in host[21:21+burst_hosts]:
    #     flows += flow.gen_flows(100, burst_size, [(src, dst, 2, start_time + burst_start)])   

    # # T2 -> T1
    # dst = 20
    # for src in host[41:41+burst_hosts]:
    #     flows += flow.gen_flows(100, burst_size, [(src, dst, 2, start_time + burst_start)]) 

    # gen incast from web search
    flow_cdf = f'./flow-cdf/{cdf}_cdf.tcl'
    flowsz = flow.FlowSizeRng.from_tcl(flow_cdf)

    copy_src = f'./data/exp_deadlock-xpod_Normal-DWRR-HPCC-{cdf}_flow-8pg-{test}test/flow.txt'
    copy_dst = f'./data/exp_deadlock-xpod_{mmu_kind}-DWRR-{cc}-{cdf}_flow-8pg-{test}test/flow.txt'
    if (mmu_kind != 'Normal' or cc != 'HPCC') and os.path.exists(copy_src):
        os.system('cp -rf %s %s'%(copy_src, copy_dst))
    else:
        random.seed(seed)
        last_send_time = 0.0
        flows: FlowList = []
        send_times: List[float] = []

        #dsts = [60, 0, 40, 20]
        #srcs = [1, 61, 21, 41]
        dsts = [48, 0, 32, 16]
        srcs = [1, 49, 17, 33]

        # incast-like
        lam = 2.0 * load * (LH_Gbps * 1000 / 8) / burst_hosts / flowsz.avg()
        send_times = exp_send_time(lam, flow_num // (4 * burst_hosts), seed=send_time_seed)
        last_send_time = max(last_send_time, send_times[-1])
        for i in range(len(send_times)):
            stime: float = start_time + send_times[i]
            for j in range(len(dsts)):
                burst_num = random.randint(1, burst_hosts)
                for src in host[srcs[j]:srcs[j]+burst_num]:
                    fsz = flowsz.rand()
                    dst = dsts[j]
                    pg = 2
                    assert 1 <= pg <= mx_pg
                    flows += flow.gen_flows(100, fsz, [(src, dst, pg, stime)])

        # # background-like
        # lam = load * (LH_Gbps * 1000 / 8) / burst_hosts / flowsz.avg()

        # for j in range(len(dsts)):
        #     for src in host[srcs[j]:srcs[j]+burst_hosts]:
        #         send_times = exp_send_time(lam, flow_num // (len(dsts) * burst_hosts), seed=send_time_seed)
        #         for i in range(len(send_times)):
        #             stime: float = start_time + send_times[i]
        #             fsz = flowsz.rand()
        #             dst = dsts[j]
        #             pg = 2
        #             assert 1 <= pg <= mx_pg
        #             flows += flow.gen_flows(100, fsz, [(src, dst, pg, stime)])


        with open(test_dir / 'flow.txt', 'w') as flowf:
            flow.gen(flows, output=flowf)

    with open(test_dir / 'config.txt', 'w') as configf:
        config.gen(test_name,
                   cc=cc,
                   buffer_size=buffer_size,
                   # stop_time=(start_time + 
                   #    last_send_time + 100) / 1e6,
                   stop_time=(start_time + 100000) / 1e6,
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
    # print(hdrm_utilization())
    # return
    tests: Set[str] = set()
    for test in range(100):
        for cdf in ['search', 'hadoop']:
            for cc in ['HPCC', 'PowerTCP', 'DCQCN']:
                for pg in [8]:
                    pgmap, quantums = PGMAPS[pg]
                    #for mmu in ['Normal', 'DSH']:
                    for mmu in ['Normal', 'DSHPLUS', 'Adaptive']:
                        # for mmu in ['DH', 'DH3']:
                        ks : List[Any]
                        if mmu == 'Normal' or mmu == 'DSH' or mmu == 'DSHnoSH' or mmu == 'DSHnoIH' or mmu == 'Adaptive' or mmu == 'DSHPLUS' or mmu == 'Normal50' or mmu == 'Normal80':
                            ks = [pg+1]
                        else:
                            ks = [1, 1.5, 2, 2.5, 3]
                        for k in ks:
                            test_name = exp_deadlock(
                                test=test,
                                cc=cc,
                                cdf=cdf,
                                mx_pg=7,
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

    utils.run_in_pool(60, tests)


if __name__ == '__main__':
    main()

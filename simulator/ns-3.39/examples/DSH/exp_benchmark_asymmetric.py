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


def exp_benchmark_asymmetric(  # pylint: disable=W0102
        nspine=16,
        nleaf=16,
        nhost=16,
        SL_Gbps=100,
        LH_Gbps=100,
        delay='2000ns',
        buffer_size=16,
        port_hdrm_k=4.0,
        mx_pg=7,
        mmu_kind="Normal",
        back_load=0.5,
        burst_load=0.4,
        
        burst_size=64,
        burst_hosts=16,
        flow_stop_time=2020000,

        flow_num=200000,
        start_time=2000000,
        send_time_seed=223333, 
        seed=575771,
        sche='DWRR',
        cc='HPCC',
        quantums: List[int] = [1600]*8,
        pg_map: Dict[int, int] = ID_MAP,
) -> str:
    test_name = f'exp_benchmark_asymmetric-search-xpod_{mmu_kind}-{sche}-{cc}-{back_load}back-{burst_load}burst-{burst_size}KB-{mx_pg+1}pg'
    test_dir = utils.get_test_dir(test_name)
    test_dir.mkdir(exist_ok=True)

    hosts, sw, links = topo.build_spine_leaf(nspine, nleaf, nhost, SL_Gbps, LH_Gbps, delay)

    with open(test_dir / 'topo.txt', 'w') as topof:
        topo.gen(set(hosts), set(sw), links, output=topof)

    # control the same flow between SIH and DSH
    copy_src = f'./data/exp_benchmark_asymmetric-search-xpod_Normal-{sche}-{cc}-{back_load}back-{burst_load}burst-{burst_size}KB-{mx_pg+1}pg/flow.txt'
    copy_dst = f'./data/exp_benchmark_asymmetric-search-xpod_{mmu_kind}-{sche}-{cc}-{back_load}back-{burst_load}burst-{burst_size}KB-{mx_pg+1}pg/flow.txt'
    if mmu_kind != 'Normal' and os.path.exists(copy_src):
        os.system('cp -rf %s %s'%(copy_src, copy_dst))
    else:
        flows: FlowList = []

        leaf_groups = [
            ("dynamic", back_load),    # 第一组动态调整
            ("fixed_high", 0.9),       # 第二组固定高负载
            ("fixed_medium", 0.6),     # 第三组固定中负载
            ("fixed_low", 0.3)         # 第四组固定低负载
        ]


        # background flow
        flowsz = flow.FlowSizeRng.from_tcl('./flow-cdf/search_cdf.tcl')

        random.seed(seed)
        last_send_time = 0.0
        send_times: List[float] = []
        host_loads = {}

        valid_src_map = {
            dst: [h for h in hosts if h//nhost != dst//nhost]
            for dst in hosts
        }

        for dst in hosts:
            leaf_idx = dst // nhost  # 计算目标主机所属的leaf交换机索引
            group_idx = leaf_idx // 4  # 每4个leaf划分为一组（0-3,4-7,8-11,12-15）
            group_type, load = leaf_groups[group_idx]
            host_loads[dst] = load  # 应用分组负载系数

        if any(v > 0 for v in host_loads.values()):
            for dst in hosts:
                current_load = host_loads[dst]
                if current_load <= 0:
                    continue
                valid_srcs = valid_src_map[dst]
                if not valid_srcs:
                    continue
                lam = current_load * (LH_Gbps * 1000 / 8) / flowsz.avg()
                send_times = exp_send_time(lam, flow_num // (nhost * nleaf), seed=datetime.now().timestamp())
                last_send_time = max(last_send_time, send_times[-1])
                for i in range(len(send_times)):
                    stime: float = start_time + send_times[i]
                    if stime > flow_stop_time:
                        break
                    fsz = flowsz.rand()
                    src = random.choice(valid_srcs)
                    # src and dst should not under the same leaf sw
                    while (src // nhost) == (dst // nhost):
                        src = random.choice(valid_srcs)
                    pg = pg_map[random.randint(1, mx_pg)]
                    assert 1 <= pg <= mx_pg
                    flows += flow.gen_flows(100, fsz, [(src, dst, pg, stime)])

        # incast flow
        burst_size = burst_size * KB
        for dst in hosts:
            leaf_idx = dst // nhost
            group_idx = leaf_idx // 4
            if group_idx != 0:  # 跳过非第一组的主机
                continue
            lam = burst_load * (LH_Gbps * 1000 / 8) / (burst_hosts * burst_size)
            if lam <= 0:
                continue
            send_times = exp_send_time(lam, flow_num // (nleaf * nhost), seed=datetime.now().timestamp())
            last_send_time = max(last_send_time, send_times[-1])
            for i in range(1, len(send_times)):
                stime: float = start_time + send_times[i]
                if stime > flow_stop_time:
                    break
                for j in range(burst_hosts):
                    src = random.randint(hosts[0], hosts[-1])
                    while (dst // nhost) == (src // nhost):
                    #while (dst == src):
                        src = random.randint(hosts[0], hosts[-1])
                    pg = pg_map[random.randint(1, mx_pg)]
                    assert 1 <= pg <= mx_pg
                    flows += flow.gen_flows(100, burst_size, [(src, dst, pg, stime)])

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
    #for load10 in range(1, 9):
    for load10 in range(1, 9):
        load = load10 / 10
        #for cc in ['DCQCN', 'HPCC', 'PowerTCP', 'None']:
        for cc in ['DCQCN', 'PowerTCP', 'HPCC', 'None']:
            for pg in [8]:
                pgmap, quantums = PGMAPS[pg]
                #for mmu in ['Normal', 'DSH']:
                #for mmu in ['Normal','DSH', 'Adaptive', 'DSHPLUS', 'Normal50', 'Normal80']:
                for mmu in ['DSHPLUS']:
                    # for mmu in ['DH', 'DH3']:
                    ks : List[Any]
                    if mmu == 'Normal' or mmu == 'DSH' or mmu == 'DSHnoSH' or mmu == 'DSHnoIH' or mmu == 'Adaptive' or mmu == 'DSHPLUS' or mmu == 'Normal50' or mmu == 'Normal80':
                        ks = [pg+1]
                    else:
                        ks = [pg+1]
                    for k in ks:
                        test_name = exp_benchmark_asymmetric(
                            cc=cc,
                            mx_pg=7,
                            mmu_kind=mmu,
                            port_hdrm_k=k,
                            back_load=load,
                            burst_load=(9-load10)/10,
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

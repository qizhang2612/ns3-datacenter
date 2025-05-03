#!/usr/bin/env python3
from typing import List, Set, Dict, Any, Tuple
from gen.flow import FlowList

import random
import os
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

# this script is for complex topo test, and its hostNum = 4

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

ID_MAP = {i: i for i in range(1, 8)} # locked by PFC


def exp_send_time(lam: float, n: int, seed: int = 0) -> List[float]:
    # E(x), flow_num, seed
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
        SH_Gbps=100,    # rateList = [10, 25, 40, 100]
        delay='2000ns',
        buffer_size=16,     # 16MB
        port_hdrm_k=4.0,
        mx_pg=7,            # locked by Switch Structure
        mmu_kind="DSH",
        start_time=2000000, # 2000000us = 2000ms = 2s

        burst_start=100,    # 100us -> 0.1 ms
        burst_hosts=4,      # hostNum
        burst_size=64,      # 64KB or 128KB
        seed = 575771,      # the original time seed
        flow_stop_time = 3000000, # 3s => flow_gen duration = 1s = 1000ms 
        burst_load_1 = 0.2,   # the occupation ratio of this link (nend 'for' in real controlling Part) => flow1
        burst_load_2 = 0.1,   # flow2
        burst_load_3 = 0.1,   # flow3
        burst_load_4 = 0.1,   # flow4
        burst_load_5 = 0.1,   # flow5
        burst_load_6 = 0.1,   # flow6
        burst_load_7 = 0.1,   # flow7

        sche='DWRR',
        cc='None',
        hdrm_reserve=1,
        quantums: List[int] = [1600] * 8, # DWRR => the priority of RR
        pg_map: Dict[int, int] = ID_MAP,
) -> str:
    # set output texts into corresponding folder
    total_inf_burst_load = round(burst_load_2+burst_load_3+burst_load_4+burst_load_5+burst_load_6+burst_load_7, 1)
    test_name = f'exp_isolation_InsRoom_{mmu_kind}-{sche}-{cc}-{burst_hosts}h-{mx_pg+1}pg-{total_inf_burst_load}bstload'
    test_dir = utils.get_test_dir(test_name)
    test_dir.mkdir(exist_ok=True)

    receiver_hosts_1 = burst_hosts # 4
    receiver_hosts_2to7 = burst_hosts // 2 # 2

    # topo
    all_nodes = list(range(burst_hosts + receiver_hosts_1 + receiver_hosts_2to7 + 1))
    hosts, sws = all_nodes[ : burst_hosts + receiver_hosts_1 + receiver_hosts_2to7], all_nodes[burst_hosts + receiver_hosts_1 + receiver_hosts_2to7 : ]
    
    '''
    NodeID in this experiment
    - Sw: 10
    - Host: 
        - src hosts: 0 - 3
        - dst hosts: 4  -  5  -  6      7  -  8  -  9
                    2-7    1     1     2-7    1     1
    '''


    # set links
    link: List[Tuple[int, int]] = []

    for host in all_nodes[ : burst_hosts + receiver_hosts_1 + receiver_hosts_2to7]:
        # connect between Host and Sw-0
        link.append((host, sws[0]))
    
    
    # config links
    links: List[Tuple[int, int, str, str]] = []
    
    bw = f'{SH_Gbps}Gbps'
    
    # host - Sw0 (rate all same)
    for i in range(burst_hosts + receiver_hosts_1 + receiver_hosts_2to7):
        tmpl = []
        tmpl.append(link[i])
        links = links + topo.gen_links(bw, delay, tmpl)
            
    
    # write the topology into topo.txt
    with open(test_dir / 'topo.txt', 'w') as topof:
        topo.gen(set(hosts), set(sws), links, output=topof)
    '''
    - open a file called topo.txt, and write the following content into it:
    - the file is in the test_dir
    main function: gen => generate a detailed topology and write it into the specified file
    '''

    copy_src = f'./data/exp_isolation_InsRoom_Normal-{sche}-{cc}-{burst_hosts}h-{mx_pg+1}pg-{total_inf_burst_load}bstload/flow.txt'
    copy_dst_dsh = f'./data/exp_isolation_InsRoom_DSHPLUS-{sche}-{cc}-{burst_hosts}h-{mx_pg+1}pg-{total_inf_burst_load}bstload/flow.txt'
    copy_dst_dshnosh = f'./data/exp_isolation_InsRoom_DSHnoSH-{sche}-{cc}-{burst_hosts}h-{mx_pg+1}pg-{total_inf_burst_load}bstload/flow.txt'

    if mmu_kind == 'DSHPLUS' and os.path.exists(copy_src):
        os.system('cp -rf %s %s'%(copy_src, copy_dst_dsh))
    elif mmu_kind == 'DSHnoSH' and os.path.exists(copy_src):
        os.system('cp -rf %s %s'%(copy_src, copy_dst_dshnosh))
    else:
        # flow generation:
        flows: FlowList = []
        bakFlow1: FlowList = []
        bakFlow2: FlowList = []
        bakFlow3: FlowList = []
        bakFlow4: FlowList = []
        bakFlow5: FlowList = []
        bakFlow6: FlowList = []
        bakFlow7: FlowList = []
        
        # config every 7 flows in each port(host)
        index = 0
        groupDelta = burst_hosts # Must guarantee this condition. It has been rigorously mathematically derived
        burst_size = burst_size * KB
        
        for host in hosts[ : burst_hosts]:
            flowsz = flow.FlowSizeRng.from_tcl('./flow-cdf/search_cdf.tcl')
            '''
            if (index % 2 == 0):
                cp the flow (for next one usage)   0, 2, 4, 6
            else:
                paste the flow [size / send-time]  1, 3, 5, 7
            '''
            if (index % 2 == 0):
                # flow1: web-search
                QoS_1 = 1
                random.seed(seed)
                n = 1000000
                
                last_send_time_1 = 0.0
                send_times_1: List[float] = []
                lam_1 = burst_load_1 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                # lam_1 = burst_load_1 * (SH_Gbps * 1000 / 8) / (burst_size)
                
                if lam_1 > 0:
                    send_times_1 = exp_send_time(lam_1, n, seed)
                    last_send_time_1 = max(send_times_1[-1], last_send_time_1)
                    
                    for i in range(len(send_times_1)):
                        stime: float = start_time + send_times_1[i]
                        if stime > flow_stop_time:
                            break
                        fsz = flowsz.rand()
                        # fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta], QoS_1, stime)]) # Default  burstTotalSize  srcHost  dstHost  QoS  beginTime
                        # for flow bak. of the next one
                        bakFlow1 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 1], QoS_1, stime)]) # a copy of flow (CoS1)
                        
                # flow2: burst
                QoS_2 = 2
                random.seed(seed)
                n = 1000000
                
                last_send_time_2 = 0.0
                send_times_2: List[float] = []
                # lam_2 = burst_load_2 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                lam_2 = burst_load_2 * (SH_Gbps * 1000 / 8) / (burst_size)
                
                if lam_2 > 0:
                    send_times_2 = exp_send_time(lam_2, n, seed)
                    last_send_time_2 = max(send_times_2[-1], last_send_time_2)
                    
                    for i in range(len(send_times_2)):
                        stime: float = start_time + send_times_2[i]
                        if stime > flow_stop_time:
                            break
                        # fsz = flowsz.rand()
                        fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta + 2], QoS_2, stime)])
                        # for flow bak. of the next one
                        bakFlow2 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 2], QoS_2, stime)]) # a copy of flow (CoS2)
                        
                # flow3: burst
                QoS_3 = 3
                random.seed(seed)
                n = 1000000
                
                last_send_time_3 = 0.0
                send_times_3: List[float] = []
                # lam_3 = burst_load_3 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                lam_3 = burst_load_3 * (SH_Gbps * 1000 / 8) / (burst_size)
                
                if lam_3 > 0:
                    send_times_3 = exp_send_time(lam_3, n, seed)
                    last_send_time_3 = max(send_times_3[-1], last_send_time_3)
                    
                    for i in range(len(send_times_3)):
                        stime: float = start_time + send_times_3[i]
                        if stime > flow_stop_time:
                            break
                        # fsz = flowsz.rand()
                        fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta + 2], QoS_3, stime)])
                        # for flow bak. of the next one
                        bakFlow3 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 2], QoS_3, stime)]) # a copy of flow (CoS3)
                        
                # flow4: burst
                QoS_4 = 4
                random.seed(seed)
                n = 1000000
                
                last_send_time_4 = 0.0
                send_times_4: List[float] = []
                # lam_4 = burst_load_4 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                lam_4 = burst_load_4 * (SH_Gbps * 1000 / 8) / (burst_size)
                
                if lam_4 > 0:
                    send_times_4 = exp_send_time(lam_4, n, seed)
                    last_send_time_4 = max(send_times_4[-1], last_send_time_4)
                    
                    for i in range(len(send_times_4)):
                        stime: float = start_time + send_times_4[i]
                        if stime > flow_stop_time:
                            break
                        # fsz = flowsz.rand()
                        fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta + 2], QoS_4, stime)])
                        # for flow bak. of the next one
                        bakFlow4 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 2], QoS_4, stime)]) # a copy of flow (CoS4)
                        
                # flow5: burst
                QoS_5 = 5
                random.seed(seed)
                n = 1000000
                
                last_send_time_5 = 0.0
                send_times_5: List[float] = []
                # lam_5 = burst_load_5 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                lam_5 = burst_load_5 * (SH_Gbps * 1000 / 8) / (burst_size)
                
                if lam_5 > 0:
                    send_times_5 = exp_send_time(lam_5, n, seed)
                    last_send_time_5 = max(send_times_5[-1], last_send_time_5)
                    
                    for i in range(len(send_times_5)):
                        stime: float = start_time + send_times_5[i]
                        if stime > flow_stop_time:
                            break
                        # fsz = flowsz.rand()
                        fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta + 2], QoS_5, stime)])
                        # for flow bak. of the next one
                        bakFlow5 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 2], QoS_5, stime)]) # a copy of flow (CoS5)
                        
                # flow6: burst
                QoS_6 = 6
                random.seed(seed)
                n = 1000000
                
                last_send_time_6 = 0.0
                send_times_6: List[float] = []
                # lam_6 = burst_load_6 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                lam_6 = burst_load_6 * (SH_Gbps * 1000 / 8) / (burst_size)

                if lam_6 > 0:
                    send_times_6 = exp_send_time(lam_6, n, seed)
                    last_send_time_6 = max(send_times_6[-1], last_send_time_6)
                    
                    for i in range(len(send_times_6)):
                        stime: float = start_time + send_times_6[i]
                        if stime > flow_stop_time:
                            break
                        # fsz = flowsz.rand()
                        fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta + 2], QoS_6, stime)])
                        # for flow bak. of the next one
                        bakFlow6 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 2], QoS_6, stime)]) # a copy of flow (CoS6)
                        
                # flow7: burst
                QoS_7 = 7
                random.seed(seed)
                n = 1000000
                
                last_send_time_7 = 0.0
                send_times_7: List[float] = []
                # lam_7 = burst_load_7 * (SH_Gbps * 1000 / 8) / flowsz.avg()
                lam_7 = burst_load_7 * (SH_Gbps * 1000 / 8) / (burst_size)
                
                if lam_7 > 0:
                    send_times_7 = exp_send_time(lam_7, n, seed)
                    last_send_time_7 = max(send_times_7[-1], last_send_time_7)
                    
                    for i in range(len(send_times_7)):
                        stime: float = start_time + send_times_7[i]
                        if stime > flow_stop_time:
                            break
                        # fsz = flowsz.rand()
                        fsz = burst_size
                        flows += flow.gen_flows(100, fsz, [(host, hosts[index + groupDelta + 2], QoS_7, stime)])
                        # for flow bak. of the next one
                        bakFlow7 += flow.gen_flows(100, fsz, [(host + 1, hosts[index + groupDelta + 2], QoS_7, stime)]) # a copy of flow (CoS7)
                        
            else:
                flows += bakFlow1
                flows += bakFlow2
                flows += bakFlow3
                flows += bakFlow4
                flows += bakFlow5
                flows += bakFlow6
                flows += bakFlow7
                # clear the bakFlow for the next pair / iteration
                bakFlow1: FlowList = []
                bakFlow2: FlowList = []
                bakFlow3: FlowList = []
                bakFlow4: FlowList = []
                bakFlow5: FlowList = []
                bakFlow6: FlowList = []
                bakFlow7: FlowList = []
                
                groupDelta += 1
                
            index += 1     

                
        # write the flow into flow.txt
        with open(test_dir / 'flow.txt', 'w') as flowf:
            flow.gen(flows, output=flowf)
    
    # write the configuration arguments into config.txt
    with open(test_dir / 'config.txt', 'w') as configf:
        config.gen(test_name,
                   cc=cc,
                   buffer_size=buffer_size,
                   stop_time=(start_time + 2000000
                   ) / 1e6, # 2000000us = 2000ms = 2s
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
    
    for bst_load in range(2, 8 + 1):
        burst_load = bst_load / 10 # 0.2 ~ 0.8
        for CC in ['None', 'PowerTCP', 'DCQCN']:
            for pg in [8]:
                pgmap, quantums = PGMAPS[pg]
                for mmu in ['DSHPLUS', 'Normal', 'DSHnoSH']:
                    # for mmu in ['DH', 'DH3']:
                    ks : List[Any]
                    if mmu == 'Normal' or mmu == 'DSH' or mmu == 'DSHnoSH' or mmu == 'DSHnoIH' or mmu == 'Adaptive' or mmu == 'DSHPLUS' or mmu == 'Normal50' or mmu == 'Normal80':
                        ks = [pg+1]
                    else:
                        ks = [1, 1.5, 2, 2.5, 3]
                    for k in ks:
                        ## hdrm_utilization_incast
                        test_name = exp_pfc_avoidance(
                            mx_pg=7,
                            burst_load_1 = 0.2,
                            burst_load_2 = burst_load / 6,
                            burst_load_3 = burst_load / 6,
                            burst_load_4 = burst_load / 6,
                            burst_load_5 = burst_load / 6,
                            burst_load_6 = burst_load / 6,
                            burst_load_7 = burst_load / 6,
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
    

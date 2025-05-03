#!/usr/bin/env python3
from typing import Dict, List, Tuple

from collections import defaultdict
import numpy as np
import pandas as pd
from pandas import DataFrame
import sys

def filepath(test_name:str, fname: str) -> str:
    return f'./data/{test_name}/{fname}'


def fct(test_name: str) -> DataFrame:
    fct_all: List[int] = []
    fcts: Dict[str, Dict[str, List[int]]] = defaultdict(
        lambda: defaultdict(list))
    with open(filepath(test_name, 'fct.txt'), 'r') as fctf:
        for line in fctf.readlines():
            rec = line.strip().split(' ')
            src = rec[0]
            dst = rec[1]
            fctv = int(rec[6])
            fcts[src][dst].append(fctv)
            fct_all.append(fctv)

    print("avg:", round(np.mean(fct_all), 2), "p50:", round(np.percentile(fct_all, 50), 2),
             "p95:", round(np.percentile(fct_all, 95), 2), "p99:", round(np.percentile(fct_all, 99), 2))
    # df = DataFrame(columns=['src', 'dst', 'min',
    #                         'avg', 'p50', 'p95', 'p99', 'max'])
    # for src, srcv in fcts.items():
    #     for dst, values in srcv.items():
    #         df.loc[len(df)] = [src, dst,
    #                            np.min(values),
    #                            round(np.mean(values), 2),
    #                            np.percentile(values, 50),
    #                            np.percentile(values, 95),
    #                            np.percentile(values, 99),
    #                            np.max(values), ]
    # return df

def qct_fct(test_name: str):
    fct_back: List[List[int]] = [[] for i in range(3)]
    fct_all: List[int] = []
    qct_all: List[int] = []
    incast_flow = {}
    with open(filepath(test_name, 'fct.txt'), 'r') as fctf:
        for line in fctf.readlines():
            rec = line.strip().split(' ')
            dst = rec[1]
            pg = rec[4]
            size = rec[5]
            start = rec[6]
            fct_all.append(int(rec[7]))
            if int(pg) > 1:
                if float(size) < 100 * 1024:
                    fctv = int(rec[7])
                    fct_back[0].append(fctv)
                elif float(size) > 10 * 1024 * 1024:
                    fctv = int(rec[7])
                    fct_back[2].append(fctv)  
                else:
                    fctv = int(rec[7])
                    fct_back[1].append(fctv)                                       
            else:
                if (dst, int(start)) not in incast_flow.keys():
                    incast_flow[(dst, int(start))] = 1
                else:
                    incast_flow[(dst, int(start))] += 1
                    if incast_flow[(dst, int(start))] == 8:
                        qct_all.append(int(rec[7]))
                        del incast_flow[(dst, int(start))]

    return fct_back, qct_all, fct_all


def list_fqct():
    mmus = ['Normal', 'DSH']
    ccs = ['HPCC', 'PowerTCP', 'DCQCN']
    col = [ 'SIH(avg)', 'DSH(avg)', 
            'SIH(p99)', 'DSH(p99)', 
            'SIH(L-avg)', 'DSH(L-avg)', 
            'SIH(M-avg)', 'DSH(M-avg)', 
            'SIH(S-avg)', 'DSH(S-avg)', 
            'SIH(S-p99)', 'DSH(S-p99)']
    hpcc = DataFrame(columns=mmus)
    power = DataFrame(columns=mmus)
    dcqcn = DataFrame(columns=mmus)
    arr1 = np.zeros((9, 12))
    arr2 = np.zeros((9, 12))
    arr3 = np.zeros((9, 12))
    hpcc = DataFrame(arr1, columns=col)
    power = DataFrame(arr2, columns=col)
    dcqcn = DataFrame(arr3, columns=col)
    for load10 in range(1, 9):
        back_load = load10 / 10
        burst_load = (9 - load10) / 10
        for mmu in mmus:
            for cc in ccs:
                dir = f'exp_benchmark_fct-xpod_{mmu}-DWRR-{cc}-{back_load}back-{burst_load}burst-64KB-8pg'
                fct_back, qct_all, fct_all = qct_fct(dir)
                if cc == 'HPCC':
                    if len(fct_back):
                        if mmu == 'Normal':
                            hpcc.loc[load10, col[0]] = round(np.mean(fct_all), 2)
                            hpcc.loc[load10, col[2]] = np.percentile(fct_all, 99)
                            if len(fct_back[2]):
                                hpcc.loc[load10, col[4]] = round(np.mean(fct_back[2]), 2)
                            hpcc.loc[load10, col[6]] = round(np.mean(fct_back[1]), 2)
                            hpcc.loc[load10, col[8]] = round(np.mean(fct_back[0]), 2)
                            hpcc.loc[load10, col[10]] = np.percentile(fct_back[0], 99)
                        else:
                            hpcc.loc[load10, col[1]] = round(np.mean(fct_all), 2)
                            hpcc.loc[load10, col[3]] = np.percentile(fct_all, 99)
                            if len(fct_back[2]):
                                hpcc.loc[load10, col[5]] = round(np.mean(fct_back[2]), 2)
                            hpcc.loc[load10, col[7]] = round(np.mean(fct_back[1]), 2)
                            hpcc.loc[load10, col[9]] = round(np.mean(fct_back[0]), 2)
                            hpcc.loc[load10, col[11]] = np.percentile(fct_back[0], 99)                            
                elif cc == 'PowerTCP':
                    if len(fct_back):
                        if mmu == 'Normal':
                            power.loc[load10, col[0]] = round(np.mean(fct_all), 2)
                            power.loc[load10, col[2]] = np.percentile(fct_all, 99)
                            power.loc[load10, col[4]] = round(np.mean(fct_back[2]))
                            power.loc[load10, col[6]] = round(np.mean(fct_back[1]))
                            power.loc[load10, col[8]] = round(np.mean(fct_back[0]))
                            power.loc[load10, col[10]] = np.percentile(fct_back[0], 99)
                        else:
                            power.loc[load10, col[1]] = round(np.mean(fct_all), 2)
                            power.loc[load10, col[3]] = np.percentile(fct_all, 99)
                            power.loc[load10, col[5]] = round(np.mean(fct_back[2]))
                            power.loc[load10, col[7]] = round(np.mean(fct_back[1]))
                            power.loc[load10, col[9]] = round(np.mean(fct_back[0]))
                            power.loc[load10, col[11]] = np.percentile(fct_back[0], 99)    
                elif cc == 'DCQCN':
                    if len(fct_back):
                        if mmu == 'Normal':
                            dcqcn.loc[load10, col[0]] = round(np.mean(fct_all), 2)
                            dcqcn.loc[load10, col[2]] = np.percentile(fct_all, 99)
                            dcqcn.loc[load10, col[4]] = round(np.mean(fct_back[2]))
                            dcqcn.loc[load10, col[6]] = round(np.mean(fct_back[1]))
                            dcqcn.loc[load10, col[8]] = round(np.mean(fct_back[0]))
                            dcqcn.loc[load10, col[10]] = np.percentile(fct_back[0], 99)
                        else:
                            dcqcn.loc[load10, col[1]] = round(np.mean(fct_all), 2)
                            dcqcn.loc[load10, col[3]] = np.percentile(fct_all, 99)
                            dcqcn.loc[load10, col[5]] = round(np.mean(fct_back[2]))
                            dcqcn.loc[load10, col[7]] = round(np.mean(fct_back[1]))
                            dcqcn.loc[load10, col[9]] = round(np.mean(fct_back[0]))
                            dcqcn.loc[load10, col[11]] = np.percentile(fct_back[0], 99) 
                    

    print('HPCC:')
    print(hpcc)
    print('PowerTCP:')
    print(power)
    print('DCQCN')
    print(dcqcn)




def pfc(test_name: str) -> DataFrame:
    pfc_status: Dict[int, Dict[int, Dict[int, List[Tuple[int, int]]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with open(filepath(test_name, 'pfc.txt'), 'r') as pfcf:
        for line in pfcf.readlines():
            rec = line.strip().split(' ')
            ts = int(rec[0])
            node = int(rec[1])
            interface = int(rec[3])
            pg = int(rec[4])
            pause = int(rec[5])
            if len(pfc_status[node][interface]) == 0:
                pfc_status[node][interface][pg] = []
            status = pfc_status[node][interface][pg]
            assert pause in [0, 1]
            if pause == 1:
                assert len(status) == 0 or status[-1][1] >= 0
                status.append((ts, -1))
            else:
                assert len(status) > 0 and status[-1][1] < 0
                ts0, _ = status[-1]
                status[-1] = (ts0, ts)

    df = DataFrame(columns=[
        'node', 'interface', 'pg', 'cnt',
        'pmin', 'pmax', 'pavg', 'pmedian', 'ptot',
        'rmin', 'rmax', 'ravg', 'rmedian',
    ])
    for node, nodev in pfc_status.items():
        for interface, pgs in nodev.items():
            ifcnt = 0
            ifpdur = []
            ifrdur = []
            for pg, pauses in pgs.items():
                cnt = len(pauses)

                pdur = [ts1 - ts0 for ts0, ts1 in pauses]
                pdur = list(filter(lambda x: x > 0, pdur))
                if len(pdur) == 0:
                    pdur = [0]

                rdur = []
                for i in range(1, len(pauses)):
                    rdur.append(pauses[i][0] - pauses[i-1][1])
                if len(rdur) == 0:
                    rdur = [0]

                df.loc[len(df)] = [
                    node, interface, pg, cnt,
                    np.min(pdur), np.max(pdur), round(np.mean(pdur), 2),
                    np.median(pdur), np.sum(pdur),
                    np.min(rdur), np.max(rdur), round(np.mean(rdur), 2),
                    np.median(rdur),
                ]

                ifcnt += cnt
                ifpdur += pdur
                ifrdur += rdur

            df.loc[len(df)] = [
                node, interface, -1, ifcnt,
                np.min(ifpdur), np.max(ifpdur), round(np.mean(ifpdur), 2),
                np.median(ifpdur), np.sum(ifpdur),
                np.min(ifrdur), np.max(ifrdur), round(np.mean(ifrdur), 2),
                np.median(ifrdur),
            ]


    return df.sort_values(['node', 'interface', 'pg'])

# statistic pfc times
def pfc_times(test_name: str):
    pfc_time = 0
    with open(filepath(test_name, 'pfc.txt'), 'r') as pfcf:
        for line in pfcf.readlines(): 
            rec = line.strip().split(' ')
            pause = int(rec[5])
            assert pause in [0, 1]
            if pause == 1:
                pfc_time = pfc_time + 1

    return pfc_time

def pfc_deadlock(test_name: str):
    if test_name.find('exp_deadlock') == -1:
        return
    deadlock = 0
    #loop = [(84, 3), (81, 21), (85, 1), (82, 22), (82, 21), (84, 2), (81, 22), (85, 2)]
    loop = [(68, 3), (65, 17), (69, 1), (66, 18), (66, 17), (68, 2), (65, 18), (69, 2)]
    pause_state = [0, 0, 0, 0, 0, 0, 0, 0]
    deadlock_time = 0
    with open(filepath(test_name, 'pfc.txt'), 'r') as pfcf:
        for line in pfcf.readlines():
            rec = line.strip().split(' ')
            pause = (int(rec[1]), int(rec[3]))
            if pause in loop and int(rec[5]) == 1:
                pause_state[loop.index(pause)] = 1
                deadlock_time = int(rec[0])
            if pause in loop and int(rec[5]) == 0:
                pause_state[loop.index(pause)] = 0

        deadlock = 1
        for i in range(4):
            if pause_state[i] == 0:
                deadlock = 0
        
        if deadlock == 0:
            deadlock = 1
            for i in range(4, 8):
                if pause_state[i] == 0:
                    deadlock = 0

    mmu = 'Normal'
    if test_name.find('DSHPLUS') != -1:
        mmu = 'DSHPLUS'
    elif test_name.find('DSH') != -1:
        mmu = 'DSH'
    elif test_name.find('Adaptive') != -1:
        mmu = 'Adaptive'
    elif test_name.find('QASH') != -1:
        mmu = 'QASH'
    
    cc = 'None'
    if test_name.find('HPCC') != -1:
        cc = 'HPCC'
    elif test_name.find('PowerTCP') != -1:
        cc = 'PowerTCP'
    elif test_name.find('DCQCN') != -1:
        cc = 'DCQCN'

    flow = 'search'
    if test_name.find('hadoop') != -1:
        flow = 'hadoop'
        
    resultf = f'./data/pfc_deadlock/{cc}-{mmu}-{flow}.txt'
    with open(resultf, 'a') as rf:
        count = len(open(resultf, 'r').readlines())
        rf.write(str(count + 1) + ' ' + str(deadlock) + ' ')
        if deadlock == 0:
            #deadlock_time = 2050000000
            deadlock_time = 2100000000
        rf.write(str(deadlock_time) + '\n')




def main() -> None:
    # test_name = sys.argv[1].split('/')[-1]
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', None)
    # print('==== fct ====')
    # fct(test_name)
    # for load10 in range(1, 10):
    #     load = load10 / 10
    #     test_name1 = test_name + '-' + str(load) + 'ld-8pg'
    #     print("load:", load, end=' ')
    #     fct(test_name1)
    # print('==== pfc ====')
    # print(pfc(test_name))
    # print(pfc_times(test_name))
    list_fqct()


if __name__ == '__main__':
    main()

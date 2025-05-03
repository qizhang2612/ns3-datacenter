from typing import TextIO, List
from sys import stdout

TEMPLATE = '''
TOPOLOGY_FILE examples/AISIH/data/{test_name}/topo.txt
FLOW_FILE examples/AISIH/data/{test_name}/flow.txt
TRACE_FILE examples/AISIH/trace.txt
TRACE_OUTPUT_FILE examples/AISIH/data/{test_name}/trace.tr
FCT_OUTPUT_FILE examples/AISIH/data/{test_name}/fct.txt
PFC_OUTPUT_FILE examples/AISIH/data/{test_name}/pfc.txt
PACKET_OUTPUT_FILE examples/AISIH/data/{test_name}/packet.txt
BUFFER_FILE mexamples/AISIH/data/{test_name}/buffer_in.txt
BUFFER_OUTPUT_FILE examples/AISIH/data/{test_name}/buffer.txt
DROP_OR_PAUSE_FILE examples/AISIH/data/{test_name}/drop_or_pause.txt
QLEN_MON_FILE examples/AISIH/data/{test_name}/qlen.txt
THPUT_MON_FILE examples/AISIH/data/{test_name}/throughput.txt
ILEN_MON_FILE examples/AISIH/data/{test_name}/ilen.txt
HEADROOM_MON_FILE examples/AISIH/data/{test_name}/headroom.txt
FLOW_STATUS_FILE examples/AISIH/data/{test_name}/flow_status_in.txt
FLOW_STATUS_OUTPUT_FILE examples/AISIH/data/{test_name}/flow_status.txt
HDRM_LOCAL_MAX_FILE examples/AISIH/data/{test_name}/hdrm_local_max_value_in.txt
HDRM_LOCAL_MAX_OUTPUT_FILE examples/AISIH/data/{test_name}/hdrm_local_max_value.txt

SIMULATOR_STOP_TIME {stop_time}
BUFFER_SIZE {buffer_size}
DT_ALPHA {dt_alpha}
PG_COUNT {pg_count}
BEQ_SCHE_ALG {sche_alg}
BEQ_DWRR_QUANTUMS {quantums}
MMU_KIND {mmu_kind}

PORT_HDRM_K {port_hdrm_k}
ACTIVE_OFFSET {active_offset}

HDRM_RESERVE {hdrm_reserve}
'''
COMMON = '''
PACKET_LEVEL_ECMP 0
FLOW_LEVEL_ECMP 1

ENABLE_QCN 1
USE_DYNAMIC_PFC_THRESHOLD 1
PACKET_PAYLOAD_SIZE 1500

ERROR_RATE_PER_LINK 0.0000
L2_CHUNK_SIZE 4000
L2_ACK_INTERVAL 1
L2_BACK_TO_ZERO 0

ACK_HIGH_PRIO 1

LINK_DOWN 0 0 0

ENABLE_TRACE 0

KMAX_MAP 5 10000000000 160 25000000000 400 40000000000 640 100000000000 1600 400000000000 6400
KMIN_MAP 5 10000000000 40 25000000000 100 40000000000 160 100000000000 400 400000000000 1600
PMAX_MAP 5 10000000000 0.2 25000000000 0.2 40000000000 0.2 100000000000 0.2 400000000000 0.2

QLEN_MON_START 2000000000
QLEN_MON_END 3000000000
'''

CC_SETTING = {'None': '''
CC_MODE 0
ALPHA_RESUME_INTERVAL 1
RATE_DECREASE_INTERVAL 4
CLAMP_TARGET_RATE 0
RP_TIMER 300
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 1
RATE_AI 20Mb/s
RATE_HAI 200Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 0
GLOBAL_T 1
VAR_WIN 0
FAST_REACT 0
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0
              
WIEN 0
DELAY_WIEN 0

RATE_BOUND 1
''',

                    'HPCC': '''
CC_MODE 3
ALPHA_RESUME_INTERVAL 1
RATE_DECREASE_INTERVAL 4
CLAMP_TARGET_RATE 0
RP_TIMER 300
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 1
RATE_AI 16Mb/s
RATE_HAI 16Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 1
GLOBAL_T 1
VAR_WIN 1
FAST_REACT 1
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0

WIEN 0
DELAY_WIEN 0

RATE_BOUND 1
''',

                'PowerTCP': '''
CC_MODE 1
ALPHA_RESUME_INTERVAL 1
RATE_DECREASE_INTERVAL 4
CLAMP_TARGET_RATE 0
RP_TIMER 300
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 1
RATE_AI 16Mb/s
RATE_HAI 16Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 1
GLOBAL_T 1
VAR_WIN 1
FAST_REACT 1
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0

WIEN 1
DELAY_WIEN 0

RATE_BOUND 1
''',

                'Theta-PowerTCP': '''
CC_MODE 3
ALPHA_RESUME_INTERVAL 1
RATE_DECREASE_INTERVAL 4
CLAMP_TARGET_RATE 0
RP_TIMER 300
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 1
RATE_AI 16Mb/s
RATE_HAI 16Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 1
GLOBAL_T 1
VAR_WIN 1
FAST_REACT 1
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0

WIEN 0
DELAY_WIEN 1

RATE_BOUND 1
''',

              'DCQCN': '''
CC_MODE 1
ALPHA_RESUME_INTERVAL 1
RATE_DECREASE_INTERVAL 4
CLAMP_TARGET_RATE 0
RP_TIMER 300
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 1
RATE_AI 20Mb/s
RATE_HAI 200Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 0
GLOBAL_T 1
VAR_WIN 0
FAST_REACT 0
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0

RATE_BOUND 1
''',
              'DCQCN-PAPER': '''
CC_MODE 1
ALPHA_RESUME_INTERVAL 55
RATE_DECREASE_INTERVAL 55
CLAMP_TARGET_RATE 0
RP_TIMER 55
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 5
RATE_AI 40Mb/s
RATE_HAI 200Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 0
GLOBAL_T 1
VAR_WIN 0
FAST_REACT 0
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0

RATE_BOUND 1
''',
              'DCQCN-MY': '''
CC_MODE 1
ALPHA_RESUME_INTERVAL 1
RATE_DECREASE_INTERVAL 10
CLAMP_TARGET_RATE 0
RP_TIMER 55
EWMA_GAIN 0.00390625
FAST_RECOVERY_TIMES 5
RATE_AI 40Mb/s
RATE_HAI 200Mb/s
MIN_RATE 100Mb/s
DCTCP_RATE_AI 1000Mb/s

HAS_WIN 0
GLOBAL_T 1
VAR_WIN 0
FAST_REACT 0
U_TARGET 0.95
MI_THRESH 0
INT_MULTI 1
MULTI_RATE 0
SAMPLE_FEEDBACK 0

RATE_BOUND 1
'''}


def gen(test_name: str,  # pylint: disable=W0102
        stop_time: float,
        buffer_size: int,
        pg_count: int,
        cc: str = 'DCQCN',
        sche_alg: str = "DRR",
        quantums: List[int] = [],
        mmu_kind: str = "PFB",
        dt_alpha: int = 4,
        port_hdrm_k: float = 2.0,
        active_offset: int = 3 * 1024,
        hdrm_reserve: int = 0,
        output: TextIO = stdout):
    quantums_str = '1|1500'
    if len(quantums) > 0:
        quantums_str = f'{len(quantums)}|{quantums[0]}'
        for q in quantums[1:]:
            quantums_str += f',{q}'
    print(COMMON, file=output)
    print(CC_SETTING[cc], file=output)
    print(TEMPLATE.format(test_name=test_name,
                          buffer_size=buffer_size,
                          pg_count=pg_count,
                          sche_alg=sche_alg,
                          quantums=quantums_str,
                          mmu_kind=mmu_kind,
                          dt_alpha=dt_alpha,
                          port_hdrm_k=port_hdrm_k,
                          active_offset=active_offset,
                          hdrm_reserve=hdrm_reserve,
                          stop_time=stop_time),
          file=output)

import subprocess as subproc
from subprocess import CompletedProcess
import os

def get_work_directory():
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    father_directory = os.path.dirname(current_directory)
    grandpa_directory = os.path.dirname(father_directory)
    return os.path.dirname(grandpa_directory)

def run(test_name: str, capture: bool = False) -> CompletedProcess:
    out = None
    if capture:
        out = subproc.PIPE
    
    # mmu
    mmu_kind = 1
    if test_name.find('DSHnoSH') != -1:
        mmu_kind = 3
    elif test_name.find('DSHnoIH') != -1:
        mmu_kind = 4
    elif test_name.find('DSHPLUS') != -1:
        mmu_kind = 6
    elif test_name.find('DSH') != -1:
        mmu_kind = 2
    elif test_name.find('QASH') != -1:
        mmu_kind = 5
    elif test_name.find('Adaptive') != -1:
        mmu_kind = 7
    elif test_name.find('Normal50') != -1:
        mmu_kind = 8
    elif test_name.find('Normal80') != -1:
        mmu_kind = 9
    
    # cc
    cc_mode = 'None'
    if test_name.find('HPCC') != -1:
        cc_mode = 'hpcc'
    elif test_name.find('PowerTCP') != -1:
        cc_mode = 'powerINT'
    elif test_name.find('DCQCN') != -1:
        cc_mode = 'dcqcn'
    
    # flow
    flow = 'search'
    if test_name.find('hadoop') != -1:
        flow = 'hadoop'
    
    # wien
    wien = False
    if cc_mode == 'powerINT':
        wien = True
        
    # delayWien
    deley = False
    if cc_mode == 'powerDeley':
        wien = True
        
    # window
    window = 1
    if cc_mode == 'dcqcn' or cc_mode =='timely':
        window = 0
    
    return subproc.run(['./waf', '--run', f'dsh-test --conf=examples/DSH/data/{test_name}/config.txt --mmuKind={mmu_kind}'],
                       cwd=get_work_directory(),
                       check=False, stdout=out, stderr=subproc.STDOUT)

# print(get_work_directory())
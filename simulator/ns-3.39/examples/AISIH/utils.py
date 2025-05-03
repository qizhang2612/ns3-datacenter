from typing import Set
from pathlib import Path
from subprocess import CalledProcessError
from multiprocessing import Pool

import pandas as pd

import gen.waf as waf
import analyze as ana

import time


def get_test_dir(test_name: str) -> Path:
    return Path('./data') / test_name


def run(test_name: str, disp: bool = True) -> None:
    test_dir = get_test_dir(test_name)
    result = waf.run(test_name, capture=True)
    output = result.stdout.decode('utf-8')
    with (test_dir / 'output.txt').open('w') as outf:
        outf.write(output)
    result.check_returncode()

    # fct = ana.fct(test_name)
    # fct.to_csv(test_dir / 'fct.csv')

    # pfc = ana.pfc(test_name)
    # pfc.to_csv(test_dir / 'pfc.csv')

    ana.pfc_deadlock(test_name)

    if disp:
        print(output, flush=True)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_rows', None)
        # print(fct)
        # print(pfc)


def run_wrapped(test_name: str) -> None:
    cnt = 5
    while cnt > 0:
        try:
            print(f'*{test_name}* starting', flush=True)
            run(test_name, disp=False)
            time.sleep(1)
        except CalledProcessError as err:
            print(f'*{test_name}* met exception: {err}', flush=True)
            cnt -= 1
        else:
            print(f'*{test_name}* finished', flush=True)
            break

def run_in_pool(size: int, tests: Set[str]):
    print(f'{len(tests)} tests:')
    for test in sorted(tests):
        print(test)
    print('-------------')

    process_cnt = min(size, len(tests))
    with Pool(processes=process_cnt) as pool:
        pool.map(run_wrapped, tests)

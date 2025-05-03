import matplotlib.pyplot as plt  


x1_values = []
x2_values = []
y1_values = []  
y2_values = []
import numpy as np

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
dsh_back_avgs = []
dsh_burst_avgs = []
normal_back_avgs = []
normal_burst_avgs = []

for back_load in back_loads:
    burst_load = round(0.9 - back_load, 1)
    #filename1 = f'data/exp_benchmark_fct-xpod_QASH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
    filename1 = f'data/exp_microbenchmark_fct-xpod_DSH-DWRR-None-{back_load}back-{burst_load}burst-64KB-8pg/flow.txt'
    #filename2 = f'data/exp_benchmark_fct-xpod_Normal-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
    filename2 = f'data/exp_microbenchmark_fct-xpod_Normal-DWRR-None-{back_load}back-{burst_load}burst-64KB-8pg/flow.txt'
    print(filename1)

    dsh_flow = np.zeros(32)
    dsh_time = np.zeros((32,8))
    dsh_pause = np.zeros((32,8))

    normal_flow = np.zeros(32)
    normal_time = np.zeros((32,8))
    normal_pause = np.zeros((32,8))

    with open(filename1, 'r') as file1:
        for line in file1:
            values = line.strip().split()
            port = int(values[0])
            if(port >=0 and port <= 15):
                size = int(values[4])
                if(size != 65536):
                    dsh_flow[port] += size
                   

    with open(filename2, 'r') as file2:
        for line in file2:
            values = line.strip().split()
            port = int(values[0])
            if(port >=0 and port <= 15):
                size = int(values[4])
                if(size != 65536):
                    normal_flow[port] += size
    
    dsh_total = 0
    normal_total = 0
    for i in range(16):
        dsh_total += dsh_flow[i]
        normal_total += normal_flow[i]
        load = dsh_flow[i] / float(back_load * (100 * 1000 / 8) * 10000)
        print(f"DSH{i}:{dsh_flow[i]} load: {load}")
        #print(f"Normal{i}:{normal_flow[i]}")
    
    total_load = dsh_total / float(back_load * (100 * 1000 / 8) * 10000 * 16)
    print(f'{dsh_total} load: {total_load}')
    #rint(normal_total)


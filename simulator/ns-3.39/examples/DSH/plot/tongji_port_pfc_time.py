import matplotlib.pyplot as plt  


x1_values = []
x2_values = []
y1_values = []  
y2_values = []
import numpy as np

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
dsh_back_avgs = []
normal_back_avgs = []

for back_load in back_loads:
    burst_load = round(0.9 - back_load, 1)
    #filename1 = f'data/exp_benchmark_fct-xpod_QASH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
    filename1 = f'data/exp_benchmark_fct-search-xpod_DSH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
    #filename2 = f'data/exp_benchmark_fct-xpod_Normal-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
    filename2 = f'data/exp_benchmark_fct-search-xpod_DSHnoSH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
    print(filename1)

    dsh_pfc = np.zeros(289)
    dsh_time = np.zeros((289,33))
    dsh_pause = np.zeros((289,33))

    normal_pfc = np.zeros(289)
    normal_time = np.zeros((289,33))
    normal_pause = np.zeros((289,33))

    with open(filename1, 'r') as file1:
        for line in file1:
            values = line.strip().split()
            pause = int(values[0])
            time = int(values[1])
            node = int(values[2])
            port = int(values[3])
            if(pause == 1):
                if(dsh_pause[node][port] == 0):
                    dsh_time[node][port] = time
                dsh_pause[node][port] = 1
            if(pause == 2):
                if(dsh_pause[node][port] == 1):
                    dsh_pfc[node] += (time - dsh_time[node][port])
                dsh_pause[node][port] = 0
                   

    with open(filename2, 'r') as file2:
        for line in file2:
            values = line.strip().split()
            pause = int(values[0])
            time = int(values[1])
            node = int(values[2])
            port = int(values[3])
            if(pause == 1):
                if(normal_pause[node][port] == 0):
                    normal_time[node][port] = time
                normal_pause[node][port] = 1
            if(pause == 2):
                if(normal_pause[node][port] == 1):
                    normal_pfc[node] += (time - normal_time[node][port])
                normal_pause[node][port] = 0
    
    dsh_total = 0
    normal_total = 0
    for i in range(289):
        dsh_total += dsh_pfc[i]
        normal_total += normal_pfc[i]
        # print(f"DSH node: {i}    back_pause_time: {dsh_pfc[i]} burst_pause_time: {dsh_burst_pfc[i]}")
        # print(f"Normal node: {i} back_pause_time: {normal_pfc[i]} burst_pause_time: {normal_burst_pfc[i]}")
    # print(f"dsh_back_total:    {dsh_total} burst_total: {dsh_burst_total}")
    # print(f"noraml_back_total: {normal_total} burst_total: {normal_burst_total}")
    print(f"dsh_total:     {dsh_total}")
    print(f"dshnosh_total: {normal_total}")
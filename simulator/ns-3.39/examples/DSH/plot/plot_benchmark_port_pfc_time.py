import matplotlib.pyplot as plt  



import numpy as np

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

for cc_kind in ['DCQCN', 'PowerTCP']:
    x1_values = []
    x2_values = []
    y1_values = []  
    y2_values = []
    for back_load in back_loads:
        burst_load = round(0.9 - back_load, 1)
        filename1 = f'data/exp_benchmark_fct-search-xpod_DSH-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/pfc.txt'
        filename3 = f'data/exp_benchmark_fct-search-xpod_DSH-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
        filename2 = f'data/exp_benchmark_fct-search-xpod_DSHnoSH-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/pfc.txt'
        print(filename1)
        filename4 = f'data/exp_benchmark_fct-search-xpod_DSHnoSH-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'

        dsh_pfc = np.zeros(289)
        dsh_port_pfc = np.zeros(289)
        dsh_time = np.zeros((289,33,8))
        dsh_port_time = np.zeros((289, 33))
        dsh_pause = np.zeros((289,33,8))
        dsh_port_pause = np.zeros((289, 33))

        normal_pfc = np.zeros(289)
        normal_port_pfc = np.zeros(289)
        normal_time = np.zeros((289,33,8))
        normal_port_time = np.zeros((289,33))
        normal_pause = np.zeros((289,33,8))
        normal_port_pause = np.zeros((289,33))

        with open(filename1, 'r') as file1:
            for line in file1:
                values = line.strip().split()
                time = int(values[0])
                node = int(values[1])
                port = int(values[3])
                queue = int(values[4])
                pause = int(values[5])
                if(pause == 1):
                    if(dsh_pause[node][port][queue] == 0):
                        dsh_time[node][port][queue] = time
                    dsh_pause[node][port][queue] = 1
                if(pause == 0):
                    if(dsh_pause[node][port][queue] == 1):
                        dsh_pfc[node] += (time - dsh_time[node][port][queue])
                    dsh_pause[node][port][queue] = 0

        with open(filename3, 'r') as file3:
            for line in file3:
                values = line.strip().split()
                pause = int(values[0])
                time = int(values[1])
                node = int(values[2])
                port = int(values[3]) 
                if(pause == 1):
                    if(dsh_port_pause[node][port] == 0):
                        dsh_port_time[node][port] = time
                    dsh_port_pause[node][port] = 1
                if(pause == 2):
                    if(dsh_port_pause[node][port] == 1):
                        dsh_port_pfc[node] += (time - dsh_port_time[node][port])
                    dsh_port_pause[node][port] = 0          

        with open(filename2, 'r') as file2:
            for line in file2:
                values = line.strip().split()
                time = int(values[0])
                node = int(values[1])
                port = int(values[3])
                queue = int(values[4])
                pause = int(values[5])
                if(pause == 1):
                    if(normal_pause[node][port][queue] == 0):
                        normal_time[node][port][queue] = time
                    normal_pause[node][port][queue] = 1
                if(pause == 0):
                    if(normal_pause[node][port][queue] == 1):
                        normal_pfc[node] += (time - normal_time[node][port][queue])
                    normal_pause[node][port][queue] = 0

        with open(filename4, 'r') as file4:
            for line in file4:
                values = line.strip().split()
                pause = int(values[0])
                time = int(values[1])
                node = int(values[2])
                port = int(values[3])
                if(pause == 1):
                    if(normal_port_pause[node][port] == 0):
                        normal_port_time[node][port] = time
                    normal_port_pause[node][port] = 1
                if(pause == 2):
                    if(normal_port_pause[node][port] == 1):
                        normal_port_pfc[node] += (time - normal_port_time[node][port])
                    normal_port_pause[node][port] = 0
        
        dsh_total = 0
        dsh_port_total = 0
        normal_total = 0
        normal_port_total = 0
        for i in range(289):
            dsh_total += dsh_pfc[i]
            dsh_port_total += dsh_port_pfc[i]
            normal_total += normal_pfc[i]
            normal_port_total += normal_port_pfc[i]
            # print(f"DSH node: {i}    back_pause_time: {dsh_pfc[i]} burst_pause_time: {dsh_burst_pfc[i]}")
            # print(f"Normal node: {i} back_pause_time: {normal_pfc[i]} burst_pause_time: {normal_burst_pfc[i]}")
        # print(f"dsh_back_total:    {dsh_total} burst_total: {dsh_burst_total}")
        # print(f"noraml_back_total: {normal_total} burst_total: {normal_burst_total}")
        x1_values.append(back_load)
        y1_values.append((dsh_port_total * 7)/(dsh_total))
        x2_values.append(back_load)
        y2_values.append((normal_port_total * 7)/(normal_total))
        print(f"dsh_total:          {dsh_total}")
        print(f"dshnosh_total:      {normal_total}")
        print(f"dsh_port_total:     {dsh_port_total}")
        print(f"dshnosh_port_total: {normal_port_total}")
        print(f"//: {(dsh_port_total * 7)/(dsh_total)}, {(normal_port_total * 7)/(normal_total)} ")

    plt.figure(figsize=(10, 8))

    plt.plot(x1_values, y1_values, marker='o',markersize=15,linestyle='-', color='r', linewidth=3, label='DSH')  
  
    plt.plot(x2_values, y2_values, marker='x',markersize=15,linestyle = '--', color='g',linewidth=3,label='DSHnoSH')  

    # plt.xlim(0.0, 1.0)  
    #plt.ylim(0.1, 1.2) 
  
    plt.legend(loc='upper right', prop={'size': 20})  
  

    #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
    #plt.title('[DCQCN] Background traffic', fontsize=22)
    plt.title(f'[{cc_kind}] pfc time', fontsize=22)
    plt.xlabel('Load of Background Traffic', fontsize=20)  
    plt.ylabel('time', fontsize=20)  
  
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
    # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 

    plt.tick_params(axis='both', which='major', labelsize=20)  

    plt.savefig(f'image/benchmark_fct_pfctime_{cc_kind}.png', format='png')  
  
    plt.close()
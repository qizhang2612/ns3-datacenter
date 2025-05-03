import matplotlib.pyplot as plt  




back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
# back_loads = [0.9]


for mmu_kind in ['DCQCN', 'PowerTCP']: 
    x1_values = []
    x2_values = []
    y1_values = []  
    y2_values = []
    for back_load in back_loads:
        burst_load = round(0.9 - back_load, 1)
        #filename1 = f'data/exp_benchmark_fct-xpod_QASH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        filename1 = f'data/exp_benchmark_fct-search-xpod_DSH-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
        #filename2 = f'data/exp_benchmark_fct-xpod_Normal-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        filename2 = f'data/exp_benchmark_fct-search-xpod_DSHnoSH-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
        print(filename1)
        pause = 0.0
        pause2 = 0.0
        time = 0.0
        time2 = 0.0
        with open(filename1, 'r') as file1:
            for line in file1:
                values = line.strip().split()
                ty = float(values[0])
                if(ty == 1.0):
                    time = float(values[1])
                    pause += 1.0
        time = (time - 2000000000.0) / 1000000
        x1_values.append(back_load)
        y1_values.append(pause / time)

        with open(filename2, 'r') as file2:
            for line in file2:
                values = line.strip().split()
                ty = float(values[0])
                if(ty == 1.0):
                    time2 = float(values[1])
                    pause2 += 1.0
        time2 = (time2 - 2000000000.0) / 1000000
        x2_values.append(back_load)
        y2_values.append(pause2 / time2)
        # print(sum(back_values))
        # print(sum(back2_values))
        # print(sum(burst_values))
        # print(sum(burst2_values))
        # print(back_avg )
        # print(back2_avg)
        # print(burst_avg)
        # print(burst2_avg)
        # print(len(back_values))
        # print(len(back2_values))
        # print(len(burst_values))
        # print(len(burst2_values))
                

    plt.figure(figsize=(12, 8))  # 宽度为10英寸，高度为6英寸  
    
    # 绘制第一条线，使用虚线、红色，并设置线宽和标记  
    plt.plot(x1_values, y1_values, marker='o',markersize=15,linestyle='-', color='r', linewidth=3, label='DSH')  
    
    # 绘制第二条线，使用实线、蓝色，并设置标记  
    plt.plot(x2_values, y2_values, marker='<',markersize=15,linestyle = '-', color='b',linewidth=3,label='DSHnoSH')  
    
    # 设置坐标轴范围（如果需要）  
    # plt.xlim(0.0, 1.0)  
    #plt.ylim(0.1, 1.2)  # 增加10%的裕量  
    
    # 添加图例，并设置其位置和字体大小  
    plt.legend(loc='upper right', prop={'size': 20})  
    
    # 设置图表标题和坐标轴标签，并调整字体大小  

    #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
    #plt.title('[DCQCN] Background traffic', fontsize=22)
    plt.title(f'[{mmu_kind}] Port Pause', fontsize=22)
    plt.xlabel('Load of Background Traffic', fontsize=20)  
    plt.ylabel('Port-level Pause Frequency(per ms)', fontsize=20)  
    
    # 显示网格，并设置其线型和颜色  
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
    # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
    
    # 设置坐标轴刻度标签的字体大小  
    plt.tick_params(axis='both', which='major', labelsize=20)  
    
    # 将图形保存为PDF文件  f
    plt.savefig(f'image/benchmark_port_pause_search_{mmu_kind}.png', format='png')  
    
    # 关闭图形，释放内存  
    plt.close()
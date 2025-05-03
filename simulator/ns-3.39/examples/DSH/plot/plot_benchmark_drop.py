import matplotlib.pyplot as plt  




back_loads = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
#back_loads = [0.1]


for mmu_kind in ['DCQCN', 'PowerTCP']: 
    x1_values = []
    x2_values = []
    y1_values = []  
    y2_values = []
    for back_load in back_loads:
        burst_load = round(0.9 - back_load, 1)
        #filename1 = f'data/exp_benchmark_fct-xpod_QASH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        filename1 = f'data-DSH60000/benchmark_noIH/exp_benchmark_fct-search-xpod_DSHPLUS-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
        filename3 = f'data-DSH60000/benchmark_noIH/exp_benchmark_fct-search-xpod_DSHPLUS-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/packet.txt'
        #filename2 = f'data/exp_benchmark_fct-xpod_Normal-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        filename2 = f'data-final/benchmark_noIH/exp_benchmark_fct-search-xpod_DSHnoIH-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/drop_or_pause.txt'
        filename4 = f'data-final/benchmark_noIH/exp_benchmark_fct-search-xpod_DSHnoIH-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/packet.txt'
        print(filename1)
        drop = 0.0
        drop2 = 0.0
        packet = 0.0
        packet2 = 0.0
        # time = 0.0
        # time2 = 0.0
        with open(filename1, 'r') as file1:
            for line in file1:
                values = line.strip().split()
                ty = float(values[0])
                if(ty == 0.0):
                    # time = float(values[1])
                    drop += 1.0
        # time = (time - 2000000000.0) / 1000000
        print(drop)
        with open(filename3, 'r') as file3:
            for line in file3:
                values = line.strip().split()
                ty = float(values[0])
                if(ty == 1.0):
                    packet += 1.0
        print(packet)
        x1_values.append(burst_load)
        y1_values.append(drop / packet)

        with open(filename2, 'r') as file2:
            for line in file2:
                values = line.strip().split()
                ty = float(values[0])
                if(ty == 0.0):
                    # time2 = float(values[1])
                    drop2 += 1.0
        print(drop2)
        with open(filename4, 'r') as file4:
            for line in file4:
                values = line.strip().split()
                ty = float(values[0])
                if(ty == 1.0):
                    # time2 = float(values[1])
                    packet2 += 1.0
        print(packet2)
        #time2 = (time2 - 2000000000.0) / 1000000
        x2_values.append(burst_load)
        y2_values.append(drop2 / packet2)
        print(drop2 / packet2)
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
    plt.plot(x1_values, y1_values, marker='o',markersize=15,linestyle='-', color='r', linewidth=3, label='DSHPLUS')  
    
    # 绘制第二条线，使用实线、蓝色，并设置标记  
    plt.plot(x2_values, y2_values, marker='s',markersize=15,linestyle = '-', color='y',linewidth=3,label='DSHnoIH') 
    
    # 设置坐标轴范围（如果需要）  
    # plt.xlim(0.0, 1.0)  
    #plt.ylim(0.1, 1.2)  # 增加10%的裕量  
    
    # 添加图例，并设置其位置和字体大小  
    plt.legend(loc='upper right', prop={'size': 20})  
    
    # 设置图表标题和坐标轴标签，并调整字体大小  

    #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
    #plt.title('[DCQCN] Background traffic', fontsize=22)
    plt.title(f'[{mmu_kind}] Drop', fontsize=22)
    plt.xlabel('Load of Fan-in Traffic', fontsize=20)  
    plt.ylabel('proportion(drop / packet)', fontsize=20)  
    
    # 显示网格，并设置其线型和颜色  
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
    # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
    
    # 设置坐标轴刻度标签的字体大小  
    plt.tick_params(axis='both', which='major', labelsize=20)  
    
    # 将图形保存为PDF文件  f
    plt.savefig(f'image/benchmark_drop_search_{mmu_kind}.png', format='png')  
    
    # 关闭图形，释放内存  
    plt.close()
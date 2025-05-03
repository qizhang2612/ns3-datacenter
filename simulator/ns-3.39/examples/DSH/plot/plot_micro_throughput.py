import matplotlib.pyplot as plt  




back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

for back_load in back_loads:
    burst_load = round(0.9 - back_load, 1)
    #filename1 = f'data/exp_benchmark_fct-xpod_QASH-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
    filename1 = f'data/exp_microbenchmark_fct-xpod_DSH-DWRR-None-{back_load}back-{burst_load}burst-64KB-8pg/throughput.txt'
    #filename2 = f'data/exp_benchmark_fct-xpod_Normal-DWRR-DCQCN-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
    filename2 = f'data/exp_microbenchmark_fct-xpod_Normal-DWRR-None-{back_load}back-{burst_load}burst-64KB-8pg/throughput.txt'
    print(filename1)
    time = []
    dsh_throught = []
    normal_throught = []
    with open(filename1, 'r') as file1:
        for line in file1:
            values = line.strip().split()
            x = float(values[0])
            throughput = float(values[35])
            if(x >= 2000100000.0 and x<= 2010000000.0):
                x = (x - 2000000000.0) / 1000000
                time.append(x)
                dsh_throught.append(throughput)
    
    with open(filename2, 'r') as file2:
        for line in file2:
            values = line.strip().split()
            x = float(values[0])
            throughput = float(values[35])
            if(x >= 2000100000.0 and x<= 2010000000.0):
                x = (x - 2000000000.0) / 1000000
                # time.append(x)
                normal_throught.append(throughput)

            

    plt.figure(figsize=(20, 8))  # 宽度为10英寸，高度为6英寸  
    
    # 绘制第一条线，使用虚线、红色，并设置线宽和标记  
    plt.plot(time, dsh_throught,linestyle='-', color='r', linewidth=3, label='DSH')  
    
    # 绘制第二条线，使用实线、蓝色，并设置标记  
    plt.plot(time, normal_throught,linestyle = '--', color='g',linewidth=3,label='SIH')  
    
    # 设置坐标轴范围（如果需要）  
    # plt.xlim(0.0, 1.0)  
    #plt.ylim(0.3, 1.2)  # 增加10%的裕量  
    
    # 添加图例，并设置其位置和字体大小  
    plt.legend(loc='upper right', prop={'size': 20})  
    
    # 设置图表标题和坐标轴标签，并调整字体大小  

    #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
    plt.title('[DCQCN] Background traffic', fontsize=22)  
    #plt.title('[PowerTCP] Background traffic', fontsize=22) 
    #plt.title('[PowerTCP] Fan-in traffic', fontsize=22)
    plt.xlabel('Load of Background Traffic', fontsize=20)  
    plt.ylabel('Normalized FCT', fontsize=20)  
    
    # 显示网格，并设置其线型和颜色  
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
    # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
    
    # 设置坐标轴刻度标签的字体大小  
    plt.tick_params(axis='both', which='major', labelsize=20)  
    
    # 将图形保存为PDF文件  
    plt.savefig(f'benchmark_fct_{back_load}.png', format='png')  
    
    # 关闭图形，释放内存  
    plt.close()
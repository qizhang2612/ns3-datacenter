import matplotlib.pyplot as plt  
import numpy as np 
import os

current_directory = os.getcwd()

image_directory = os.path.join(current_directory, 'image')

os.makedirs(image_directory, exist_ok=True)

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
#back_loads = [0.3]
# back_loads = [0.9]

for kind in ['back']:
    for mmu_kind in ['DCQCN','PowerTCP']: 
        for back_load in back_loads:
            x1_values = []
            y1_values = []
            x2_values = []
            y2_values = []
            cdf1 = []
            cdf2 = []
            burst_load = round(0.9 - back_load, 1)
            #filename1 = f'data/exp_motivation-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg-1cos/headroom.txt'
            filename1 = f'data/exp_motivation-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/headroom.txt'
            print(filename1)
            with open(filename1, 'r') as file1:
                for line in file1:
                    values = line.strip().split()
                    ty = int(values[0])
                    if(ty == 4):
                        rate = float(values[6])
                        y1_values.append(rate)
                    if(ty == 5):
                        rate = float(values[6])
                        y2_values.append(rate)

            sorted_data1 = np.sort(y1_values)
            sorted_data2 = np.sort(y2_values)
            for i in range(1, len(sorted_data1) + 1):
                cdf1.append(float(i / len(sorted_data1)))
            for i in range(1, len(sorted_data2) + 1):
                cdf2.append(float(i / len(sorted_data2)))
            plt.figure(figsize=(10, 8))  # 宽度为10英寸，高度为6英寸  
            
            # 绘制第一条线，使用虚线、红色，并设置线宽和标记  
            plt.plot(sorted_data1, cdf1, linestyle='-', color='r', linewidth=3, label='SIH upstream')
            plt.plot(sorted_data2, cdf2, linestyle='-', color='g', linewidth=3, label='SIH transmit')  
            
            # 设置坐标轴范围（如果需要）  
            plt.xlim(0, 110)  
            plt.ylim(0.0, 1.2)  # 增加10%的裕量  
            
            # 添加图例，并设置其位置和字体大小  
            plt.legend(loc='upper right', prop={'size': 20})  
            
            # 设置图表标题和坐标轴标签，并调整字体大小  

            #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
            #plt.title('[DCQCN] Background traffic', fontsize=22)
            plt.title(f'[{mmu_kind}] Rate CDF', fontsize=22)
            plt.xlabel('Rate (Gbps)', fontsize=20)  
            plt.ylabel('CDF', fontsize=20)  
            
            # 显示网格，并设置其线型和颜色  
            plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
            # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
            # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
            
            # 设置坐标轴刻度标签的字体大小  
            plt.tick_params(axis='both', which='major', labelsize=20)  
            
            # 将图形保存为PDF文件  f
            plt.savefig(f'image/motivation_search_rate_{mmu_kind}_{back_load}back_{burst_load}burst_20ms.png', format='png')  
            #plt.savefig(f'image/motivation_search_1cos_rate_{mmu_kind}_{back_load}back_{burst_load}burst_20ms.png', format='png')
            
            # 关闭图形，释放内存  
            plt.close()
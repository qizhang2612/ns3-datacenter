import matplotlib.pyplot as plt  
import numpy as np  

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
#back_loads = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
# back_loads = [0.9]

for kind in ['back']:
    for mmu_kind in ['DCQCN', 'PowerTCP']:
        for sw in ['spine', 'leaf', 'all']:
            #plt.figure(figsize=(10, 8))  # 宽度为10英寸，高度为6英寸
            for back_load in back_loads:
                x1_values = []
                y1_values = []
                cdf1 = []
                burst_load = round(0.9 - back_load, 1)
                #back_load = 0.0
                #burst_load = 0.0
                filename1 = f'data/exp_motivation-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg-1cos/headroom.txt'
                print(filename1)
                with open(filename1, 'r') as file1:
                    for line in file1:
                        values = line.strip().split()
                        ty = int(values[0])
                        node_id = int(values[1])
                        if(sw == 'leaf'):
                            if(ty == 2 and node_id >= 256 and node_id <= 271):
                                usage = float(values[4])
                                y1_values.append(usage)
                        elif(sw == 'spine'):
                            if(ty == 2 and node_id >= 256 and node_id <= 271):
                                usage = float(values[4])
                                y1_values.append(usage)
                        else:
                            if(ty == 2):
                                usage = float(values[4])
                                y1_values.append(usage)
                            

                sorted_data1 = np.sort(y1_values)
                for i in range(1, len(sorted_data1) + 1):
                    cdf1.append(float(i / len(sorted_data1)))
                  
                plt.figure(figsize=(10, 8))  # 宽度为10英寸，高度为6英寸
                # 绘制第一条线，使用虚线、红色，并设置线宽和标记  
                plt.plot(sorted_data1, cdf1, linestyle='-', linewidth=3, label=f'SIH{back_load}back_{burst_load}burst')  
                
                # 设置坐标轴范围（如果需要）  
                # plt.xlim(0.0, 1.0)  
                #plt.ylim(0.1, 1.2)  # 增加10%的裕量  
                
                # 添加图例，并设置其位置和字体大小  
                plt.legend(loc='upper right', prop={'size': 20})  
                
                # 设置图表标题和坐标轴标签，并调整字体大小  

                #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
                #plt.title('[DCQCN] Background traffic', fontsize=22)
                plt.title(f'[{mmu_kind}] usage CDF', fontsize=22)
                plt.xlabel('usage', fontsize=20)  
                plt.ylabel('CDF', fontsize=20)  
                
                # 显示网格，并设置其线型和颜色  
                plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
                # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
                # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
                
                # 设置坐标轴刻度标签的字体大小  
                plt.tick_params(axis='both', which='major', labelsize=20)  
                
                # 将图形保存为PDF文件  f
                #plt.savefig(f'image/motivation_search_1cos_{sw}_single_usage_{mmu_kind}_20ms.png', format='png')
                plt.savefig(f'image/motivation_search_single_usage_{mmu_kind}_{back_load}_20ms.png', format='png')
                #plt.savefig(f'image/motivation_search_1cos_onlyback_leaf_single_usage_{mmu_kind}_{back_load}_20ms.png', format='png')
                #plt.savefig(f'motivation_search_1cos_onlyburst_spine_single_usage_{mmu_kind}_{burst_load}_20ms.png', format='png')
                
                # 关闭图形，释放内存  
                plt.close()
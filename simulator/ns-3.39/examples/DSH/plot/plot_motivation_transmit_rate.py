import matplotlib.pyplot as plt  
import numpy as np 
import os

current_directory = os.getcwd()

image_directory = os.path.join(current_directory, 'image')

os.makedirs(image_directory, exist_ok=True)

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
#back_loads = [0.8,0.7,0.6,0.5,0.4,0.3,0.2]
#back_loads = [0.3]
# back_loads = [0.9]

for kind in ['all', 'onlyback', 'onlyburst', '7cos']:
    for mmu_kind in ['DCQCN','PowerTCP']: 
        plt.figure(figsize=(10, 8)) 
        for back_load in back_loads:
            x1_values = []
            y1_values = []
            x2_values = []
            y2_values = []
            cdf1 = []
            cdf2 = []
            if(kind == 'onlyback'):
                burst_load = 0.0
            elif(kind == 'onlyburst'):
                burst_load = round(0.9 - back_load, 1)
                back_load = 0.0
            else:
                burst_load = round(0.9 - back_load, 1)
            if(kind == '7cos'):
                filename1 = f'data/exp_motivation-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/headroom.txt'
            else:
                filename1 = f'data/exp_motivation-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg-1cos/headroom.txt'
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
            
            
             
            #plt.plot(sorted_data1, cdf1, linestyle='-', linewidth=3, label=f'SIH upstream{back_load}back_{burst_load}burst')
            if(kind == 'all'):
                plt.plot(sorted_data2, cdf2, linestyle='-', linewidth=3, label=f'SIH transmit{back_load}back_{burst_load}burst')
            elif(kind == 'onlyback'):
                plt.plot(sorted_data2, cdf2, linestyle='-', linewidth=3, label=f'SIH transmit{back_load}back')
            elif(kind == 'onlyburst'):
                plt.plot(sorted_data2, cdf2, linestyle='-', linewidth=3, label=f'SIH transmit{burst_load}burst') 
            else:
                plt.plot(sorted_data2, cdf2, linestyle='-', linewidth=3, label=f'SIH transmit{back_load}back_{burst_load}burst')
             
        plt.xlim(0, 110)  
        plt.ylim(0.0, 1.6)  
        
        plt.legend(loc='upper left', prop={'size': 20},) 

        #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
        #plt.title('[DCQCN] Background traffic', fontsize=22)
        plt.title(f'[{mmu_kind}] Rate CDF', fontsize=22)
        plt.xlabel('Rate (Gbps)', fontsize=20)  
        plt.ylabel('CDF', fontsize=20)  
        
        plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5) 
        
        plt.tick_params(axis='both', which='major', labelsize=20)  
        
        #plt.savefig(f'motivation_search_1cos_rate_{mmu_kind}_{back_load}.png', format='png')  
        if(kind == 'all'):
            plt.savefig(f'image/motivation_search_1cos_transmit_rate_{mmu_kind}.png', format='png')
        elif(kind == 'onlyback'):
            plt.savefig(f'image/motivation_search_1cos_onlyback_transmit_rate_{mmu_kind}.png', format='png')
        elif(kind == "onlyburst"):
            plt.savefig(f'image/motivation_search_1cos_onlyburst_transmit_rate_{mmu_kind}.png', format='png')
        else:
            plt.savefig(f'image/motivation_search_transmit_rate_{mmu_kind}.png', format='png')

        plt.close()
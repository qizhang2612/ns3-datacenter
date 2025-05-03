import matplotlib.pyplot as plt  
import numpy as np  

back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
#back_loads = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
# back_loads = [0.9]

for kind in ['7cos', 'all', 'onlyback', 'onlyburst']:
    for mmu_kind in ['DCQCN', 'PowerTCP']:
        #for sw in ['spine', 'leaf', 'all']:
        for sw in ['all']:
            plt.figure(figsize=(10, 8))
            for back_load in back_loads:
                x1_values = []
                y1_values = []
                cdf1 = []
                burst_load = round(0.9 - back_load, 1)
                if(kind == 'onlyburst'):
                    back_load = 0.0
                elif(kind == 'onlyback'):
                    burst_load = 0.0
                if(kind == '7cos'):
                    filename1 = f'data/exp_motivation-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/headroom.txt'
                else:
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

                if(kind == 'onlyback'):
                    plt.plot(sorted_data1, cdf1, linestyle='-', linewidth=3, label=f'SIH{back_load}back')
                elif(kind == 'onlyburst'):
                    plt.plot(sorted_data1, cdf1, linestyle='-', linewidth=3, label=f'SIH{burst_load}burst')
                else:
                    plt.plot(sorted_data1, cdf1, linestyle='-', linewidth=3, label=f'SIH{back_load}back_{burst_load}burst')  
                
            # plt.xlim(0.0, 1.0)  
            #plt.ylim(0.1, 1.2)  

            plt.legend(loc='upper right', prop={'size': 20})  


            #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
            #plt.title('[DCQCN] Background traffic', fontsize=22)
            plt.title(f'[{mmu_kind}] usage CDF', fontsize=22)
            plt.xlabel('usage', fontsize=20)  
            plt.ylabel('CDF', fontsize=20)  
            
            plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
                
            plt.tick_params(axis='both', which='major', labelsize=20)  
            
            #plt.savefig(f'image/motivation_search_1cos_{sw}_single_usage_{mmu_kind}_20ms.png', format='png')
            if(kind == '7cos'):
                plt.savefig(f'image/motivation_search_single_usage_{mmu_kind}.png', format='png')
            elif(kind == 'all'):
                plt.savefig(f'image/motivation_search_1cos_single_usage_{mmu_kind}.png', format='png')
            elif(kind == 'onlyback'):
                plt.savefig(f'image/motivation_search_1cos_onlyback_single_usage_{mmu_kind}.png', format='png')
            else:
                plt.savefig(f'image/motivation_search_1cos_onlyburst_single_usage_{mmu_kind}.png', format='png')
            #plt.savefig(f'image/motivation_search_1cos_onlyback_leaf_single_usage_{mmu_kind}_{back_load}_20ms.png', format='png')
            #plt.savefig(f'motivation_search_1cos_onlyburst_spine_single_usage_{mmu_kind}_{burst_load}_20ms.png', format='png')

            plt.close()
import matplotlib.pyplot as plt  




back_loads = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
# back_loads = [0.9]
#for load_kind in['hadoop','cache','mining']:
for load_kind in['search']:
    for kind in ['back','burst']:
        for cc_kind in ['DCQCN', 'PowerTCP']: 
            x1_values = []
            x2_values = []
            x3_values = []
            y1_values = []  
            y2_values = []
            y3_values = []
            dsh_back_avgs = []
            dsh_burst_avgs = []
            normal_back_avgs = []
            normal_burst_avgs = []
            dshnosh_back_avgs = []
            dshnosh_burst_avgs = []
            data_dict = {}
            for back_load in back_loads:
                burst_load = round(0.9 - back_load, 1)
                #filename1 = f'data/exp_benchmark_fct-{load_kind}-1.0ratio-DSH-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64x64KB-8pg/fct.txt'
                #filename2 = f'data/exp_benchmark_fct-{load_kind}-1.0ratio-Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64x64KB-8pg/fct.txt'
                filename1 = f'data-DSH60000/benchmark_noIH/exp_benchmark_fct-{load_kind}-xpod_DSHPLUS-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                #filename2 = f'data/exp_benchmark_fct-{load_kind}-xpod_Normal-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                filename3 = f'data-final/benchmark_noIH/exp_benchmark_fct-{load_kind}-xpod_DSHnoIH-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                print(filename1)
                back_values = []
                burst_values = []
                back2_values = []
                burst2_values = []
                back3_values = []
                burst3_values = []
                back_avg = 0.0
                burst_avg = 0.0
                back2_avg = 0.0
                burst2_avg = 0.0
                back3_avg = 0.0
                burst3_avg = 0.0

                with open(filename3, 'r') as file3:
                    for line in file3:
                        values = line.strip().split()
                        size = float(values[5])
                        time = float(values[7])
                        key = tuple(values[:7]) 
                        if key not in data_dict:  
                            data_dict[key] = []
                        if(size == 65536.0):
                            burst3_values.append(time)
                        else:
                            back3_values.append(time)
                back3_avg = sum(back3_values) / len(back3_values)
                if(len(burst3_values) > 0):
                    burst3_avg = sum(burst3_values) / len(burst3_values)
                dshnosh_back_avgs.append(back3_avg)
                dshnosh_burst_avgs.append(burst3_avg)
                
                # with open(filename2, 'r') as file2:
                #     for line in file2:
                #         values = line.strip().split()
                #         size = float(values[5])
                #         time = float(values[7])
                #         key = tuple(values[:7])  # 前五个字段作为键（转换为元组以便作为字典键）  
                #         if key in data_dict:
                #             if(size == 65536.0):
                #                 burst2_values.append(time)
                #             else:
                #                 back2_values.append(time)
                #         # if(size == 65536.0):
                #         #     burst2_values.append(time)
                #         # else:
                #         #     back2_values.append(time)
                # back2_avg = sum(back2_values) / len(back2_values)
                # if(len(burst2_values) > 0):
                #     burst2_avg = sum(burst2_values) / len(burst2_values)
                # normal_back_avgs.append(back2_avg)
                # normal_burst_avgs.append(burst2_avg)
                
                with open(filename1, 'r') as file1:
                    for line in file1:
                        values = line.strip().split()
                        size = float(values[5])
                        time = float(values[7])
                        key = tuple(values[:7])
                        if key in data_dict:
                            if(size == 65536.0):
                                burst_values.append(time)
                            else:
                                back_values.append(time)
                        # if(size == 65536.0):
                        #     burst_values.append(time)
                        # else:
                        #     back_values.append(time)
                back_avg = sum(back_values) / len(back_values)
                if(len(burst_values) > 0):
                    burst_avg = sum(burst_values) / len(burst_values)
                dsh_back_avgs.append(back_avg)
                dsh_burst_avgs.append(burst_avg)
                # print(len(back_values))
                # print(len(back2_values))
                # print(len(back3_values))
                # print(len(burst_values))
                # print(len(burst2_values))
                # print(len(burst3_values))
            if(kind == 'burst'):
                for i in range(1,8):
                    x1_values.append(0.1 * (i + 1))
                    #x2_values.append(0.1 * (i + 1))
                    x3_values.append(0.1 * (i + 1))
                    # y1_values.append(dsh_burst_avgs[i-1] / normal_burst_avgs[i-1])
                    y1_values.append(dsh_burst_avgs[i-1] / 1e6)
                    y3_values.append(dshnosh_burst_avgs[i-1] / 1e6)
                    #y2_values.append(normal_burst_avgs[i-1])
            
            if(kind == 'back'):
                for i in range(1,8):
                    x1_values.append(0.1 * (i + 1))
                    #x2_values.append(0.1 * (i + 1))
                    x3_values.append(0.1 * (i + 1))
                    y1_values.append(dsh_back_avgs[i-1] / 1e6)
                    y3_values.append(dshnosh_back_avgs[i-1] / 1e6)
                    #y2_values.append(normal_back_avgs[i-1])
                        

            plt.figure(figsize=(10, 8))  # 宽度为10英寸，高度为6英寸  
            
            # 绘制第一条线，使用虚线、红色，并设置线宽和标记  
            plt.plot(x1_values, y1_values, marker='o',markersize=15,linestyle='-', color='r', linewidth=3, label='DSH')  
            
            # 绘制第二条线，使用实线、蓝色，并设置标记  
            #plt.plot(x2_values, y2_values, marker='x',markersize=15,linestyle = '--', color='g',linewidth=3,label='SIH')  

            plt.plot(x3_values, y3_values, marker='s',markersize=15,linestyle = '-', color='y',linewidth=3,label='DSHnoIH')  
            
            # 设置坐标轴范围（如果需要）  
            # plt.xlim(0.0, 1.0)  
            #plt.ylim(0.4, 1.4)  # 增加10%的裕量  
            
            # 添加图例，并设置其位置和字体大小  
            plt.legend(loc='upper right', prop={'size': 20})  
             

            #plt.title('[DCQCN] Fan-in traffic', fontsize=22) 
            #plt.title('[DCQCN] Background traffic', fontsize=22)
            if(kind == 'back'):
                plt.title(f'[{cc_kind}] Background traffic', fontsize=22)
            if(kind == 'burst'):
                plt.title(f'[{cc_kind}] Fan-in traffic', fontsize=22)
            plt.xlabel('Load of Fan-in Traffic', fontsize=20)  
            plt.ylabel('FCT(ms)', fontsize=20)  
            
            plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
            # plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
            # plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
             
            plt.tick_params(axis='both', which='major', labelsize=20)  
            
            plt.savefig(f'image/benchmark_fct_DSHnoIH_{load_kind}_{kind}_{cc_kind}.png', format='png')  
            
            plt.close()
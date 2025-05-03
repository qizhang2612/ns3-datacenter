import matplotlib.pyplot as plt

back_loads = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

for mmu_kind in ['DCQCN']:
    x1_values = []
    x2_values = []
    y1_values = []
    y2_values = []
    
    for back_load in back_loads:
        burst_load = round(0.9 - back_load, 1)
        filename3 = f'data/exp_benchmark_fct-search-xpod_Normal-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/packet.txt'
        filename4 = f'data/exp_benchmark_fct-search-xpod_Normal80-DWRR-{mmu_kind}-{back_load}back-{burst_load}burst-64KB-8pg/packet.txt'
        
        packet = 0.0
        
        with open(filename3, 'r') as file3:
            packet = sum(1 for _ in file3)  # 统计总行数
        

        packet2 = 0.0
        
        with open(filename4, 'r') as file4:
            packet2 = sum(1 for _ in file4)
        
        ratio = packet2 / packet
    
        print(f"MMU Kind: {mmu_kind}, Back Load: {back_load}, Burst Load: {burst_load}, Packet Ratio: {ratio:.6f}")
        
    # # 绘制图表
    # plt.figure(figsize=(12, 8))
    # plt.plot(x1_values, y1_values, marker='o', markersize=15, linestyle='-', color='r', linewidth=3, label='DSHPLUS')
    # plt.plot(x2_values, y2_values, marker='s', markersize=15, linestyle='-', color='y', linewidth=3, label='DSHnoIH')
    
    # plt.legend(loc='upper right', prop={'size': 20})
    # plt.title(f'[{mmu_kind}] Drop Ratio (drop/packet)', fontsize=22)
    # plt.xlabel('Load of Fan-in Traffic', fontsize=20)
    # plt.ylabel('Drop Ratio', fontsize=20)
    # plt.grid(True, which='both', linestyle='--', color='gray', alpha=0.5)
    # plt.tick_params(axis='both', which='major', labelsize=20)
    
    # plt.savefig(f'image/benchmark_drop_search_{mmu_kind}.png', format='png')
    # plt.close()
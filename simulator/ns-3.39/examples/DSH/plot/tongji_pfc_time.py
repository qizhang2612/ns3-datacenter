import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# 配置参数
back_loads = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
load_kinds = ['search']
cc_kinds = ['DCQCN']
configurations = ['DSHPLUS', 'Adaptive', 'Normal50', 'Normal80']  # 新增配置

# 数据结构初始化
results = defaultdict(lambda: {
    'back_loads': [],
    'dsh_normal_ratio': []
})

def process_pfc_file(filename):
    """处理单个PFC文件并返回统计结果"""
    pfc = np.zeros(289)
    time_matrix = np.zeros((289, 33, 8))
    pause_matrix = np.zeros((289, 33, 8))
    event_counts = {'pause': 0, 'resume': 0}

    try:
        with open(filename, 'r') as f:
            for line in f:
                values = line.strip().split()
                time = int(values[0])
                node = int(values[1])
                port = int(values[3])
                queue = int(values[4])
                pause = int(values[5])

                if pause == 1:
                    if pause_matrix[node, port, queue] == 0:
                        time_matrix[node, port, queue] = time
                    pause_matrix[node, port, queue] = 1
                    event_counts['pause'] += 1
                else:
                    if pause_matrix[node, port, queue] == 1:
                        pfc[node] += (time - time_matrix[node, port, queue])
                    pause_matrix[node, port, queue] = 0
                    event_counts['resume'] += 1
    except FileNotFoundError:
        print(f"Warning: File {filename} not found")
        return None, None

    return np.sum(pfc), event_counts

# 主处理循环
for load_kind in load_kinds:
    for cc_kind in cc_kinds:
        # 预处理Normal基准数据
        normal_data = {}
        for back_load in back_loads:
            burst_load = round(0.9 - back_load, 1)
            normal_file = f'data-bak/exp_benchmark_fct-{load_kind}-xpod_Normal-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/pfc.txt'
            normal_total, _ = process_pfc_file(normal_file)
            normal_data[back_load] = normal_total

        for config in configurations:
            current_back_loads = []
            current_ratios = []
            
            for back_load in back_loads:
                burst_load = round(0.9 - back_load, 1)
                # 生成配置文件路径
                config_file = f'data-bak/exp_benchmark_fct-{load_kind}-xpod_{config}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/pfc.txt'
                # 处理配置文件
                config_total, _ = process_pfc_file(config_file)
                if config_total is None:
                    continue
                
                # 获取对应的Normal基准值
                normal_total = normal_data.get(back_load, 0)
                ratio = config_total / normal_total if normal_total != 0 else 1.0

                current_back_loads.append(back_load)
                current_ratios.append(ratio)

            # 存储结果
            key = (load_kind, cc_kind, config)
            results[key]['back_loads'] = current_back_loads
            results[key]['dsh_normal_ratio'] = current_ratios

# 绘图配置
plt.style.use('seaborn-v0_8')

# 遍历所有组合
for load_kind in load_kinds:
    for cc_kind in cc_kinds:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 为每个配置绘制曲线
        markers = ['o', 's', '^', 'D']  # 不同标记区分配置
        for i, config in enumerate(configurations):
            key = (load_kind, cc_kind, config)
            back_loads = results[key]['back_loads']
            ratios = results[key]['dsh_normal_ratio']
            
            if not back_loads:  # 跳过无数据的配置
                continue
            
            ax.plot(back_loads, ratios, 
                    marker=markers[i], markersize=8, linestyle='-', 
                    linewidth=2, label=config)

        ax.invert_xaxis()
        ax.axhline(1.0, color='darkorange', linestyle='--', linewidth=2, label='Baseline')
        
        ax.set_xlabel('Background Traffic Load', fontsize=12)
        ax.set_ylabel('PFC Time Ratio', fontsize=12)
        ax.set_title(f'{load_kind.capitalize()} ({cc_kind})', fontsize=14, pad=12)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.2)
        ax.legend(fontsize=10, loc='upper right', bbox_to_anchor=(1.35, 1.0))
        
        filename = f'pfc_time_{load_kind}_{cc_kind}_all_configs.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

print(f"Processing completed. Generated {len(load_kinds)*len(cc_kinds)} composite plots.")
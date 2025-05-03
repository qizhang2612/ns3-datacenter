import matplotlib.pyplot as plt
from collections import defaultdict

# 常量定义
#WORK_LOADS = ['cache', 'mining', 'alistorage', 'hadoop']
WORK_LOADS = ['search']
BACK_LOADS = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
#CC_KINDS = ['PowerTCP', 'DCQCN', 'HPCC', 'None']
CC_KINDS = ['PowerTCP']
POLICIES = ['DSHPLUS', 'Normal', 'Normal80', 'Adaptive']
COLORS = {
    'DSHPLUS': 'r', 
    'Normal': 'g',  # SIH
    'Normal50': 'b', 
    'Normal80': 'm', 
    'Adaptive': 'c'
}
MARKERS = {
    'DSHPLUS': 'o', 
    'Normal': 'x',  # SIH
    'Normal50': 's', 
    'Normal80': '^', 
    'Adaptive': '*'
}
LINE_STYLES = {
    'DSHPLUS': '-', 
    'Normal': '--',  # SIH
    'Normal50': '-.', 
    'Normal80': ':', 
    'Adaptive': '-'
}

# 缓存文件数据和键的交集
file_cache = {}  # 文件路径 -> (keys_set, data_list)
intersection_cache = {}  # (cc_kind, back_load, burst_load, work_load) -> 交集集合

def read_file_keys_and_data(filepath):
    """读取文件并缓存键集合和数据列表"""
    if filepath in file_cache:
        return file_cache[filepath]
    
    keys_set = set()
    data_list = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 8:
                    continue  # 跳过不完整的行
                key = tuple(parts[:7])
                size = float(parts[5])
                time = float(parts[7])
                keys_set.add(key)
                data_list.append((key, size, time))
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
    
    file_cache[filepath] = (keys_set, data_list)
    return file_cache[filepath]

def precompute_intersections():
    """预先计算所有Normal50和Normal80文件的键交集"""
    for work_load in WORK_LOADS:
        for cc_kind in CC_KINDS:
            for back_load in BACK_LOADS:
                burst_load = round(0.9 - back_load, 1)
                # 生成文件路径
                # file_50 = f'data-final/benchmark_diff_workload/exp_benchmark_fct-{work_load}-xpod_Normal50-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                # file_80 = f'data-final/benchmark_diff_workload/exp_benchmark_fct-{work_load}-xpod_Normal80-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                file_50 = f'data-final/benchmark_search/exp_benchmark_fct-{work_load}-xpod_Normal80-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                file_80 = f'data-final/benchmark_search/exp_benchmark_fct-{work_load}-xpod_Normal-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
                # 读取文件数据
                keys50, _ = read_file_keys_and_data(file_50)
                keys80, _ = read_file_keys_and_data(file_80)
                # 计算交集并缓存
                intersection = keys50 & keys80
                intersection_cache[(cc_kind, back_load, burst_load, work_load)] = intersection

def read_fct_data(policy_file, base_file, cc_kind, back_load, burst_load, work_load):
    """使用缓存数据快速计算比率"""
    # 获取预先计算的交集
    intersection = intersection_cache.get((cc_kind, back_load, burst_load, work_load), set())
    
    # 处理策略文件
    _, policy_data = read_file_keys_and_data(policy_file)
    back_times = []
    burst_times = []
    for key, size, time in policy_data:
        if key in intersection:
            if size == 65536.0:
                burst_times.append(time)
            else:
                back_times.append(time)
    
    # 处理基准文件
    _, base_data = read_file_keys_and_data(base_file)
    base_back_times = []
    base_burst_times = []
    for key, size, time in base_data:
        if key in intersection:
            if size == 65536.0:
                base_burst_times.append(time)
            else:
                base_back_times.append(time)
    
    # 计算平均时间比率
    back_avg = sum(back_times)/len(back_times) if back_times else 0
    burst_avg = sum(burst_times)/len(burst_times) if burst_times else 0
    base_back_avg = sum(base_back_times)/len(base_back_times) if base_back_times else 0
    base_burst_avg = sum(base_burst_times)/len(base_burst_times) if base_burst_times else 0
    
    back_ratio = back_avg / base_back_avg if base_back_avg else 0
    burst_ratio = burst_avg / base_burst_avg if base_burst_avg else 0
    return back_ratio, burst_ratio

def process_workload(cc_kind, policy, work_load):
    """处理单个工作负载类型，并返回 back 和 burst 比率"""
    back_ratios = []
    burst_ratios = []
    
    for back_load in BACK_LOADS:
        burst_load = round(0.9 - back_load, 1)
        # 生成文件路径
        if policy == "DSHPLUS":
            policy_file = f'data-DSH60000/benchmark_search/exp_benchmark_fct-{work_load}-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        else:
            policy_file = f'data-final/benchmark_search/exp_benchmark_fct-{work_load}-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        base_file = f'data-final/benchmark_search/exp_benchmark_fct-{work_load}-xpod_Normal-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        
        # 读取数据并计算比率
        print(policy_file)
        back_ratio, burst_ratio = read_fct_data(policy_file, base_file, cc_kind, back_load, burst_load, work_load)
        back_ratios.append(back_ratio)
        burst_ratios.append(burst_ratio)
    
    return back_ratios, burst_ratios

def prepare_plot_data(cc_kind, traffic_kind, work_load):
    """准备绘图数据，并将所有 policy 的数据保存到一个 .rsv 文件"""
    data = defaultdict(dict)
    
    # 打开一个 rsv 文件用于写入
    rsv_filename = f'result/fct_ratios_{work_load}_{cc_kind}.rsv'
    with open(rsv_filename, 'w') as rsv_file:
        # 写入表头
        header = ["Back_Load", "Burst_Load"]
        for policy in POLICIES:
            header.append(f"{policy}_Back_Ratio")
            header.append(f"{policy}_Burst_Ratio")
        rsv_file.write("\t".join(header) + "\n")
        
        # 并行处理不同策略
        all_ratios = defaultdict(lambda: defaultdict(list))
        for policy in POLICIES:
            back_ratios, burst_ratios = process_workload(cc_kind, policy, work_load)
            data[policy]['back'] = back_ratios
            data[policy]['burst'] = burst_ratios
            
            # 存储比率数据，用于写入 rsv 文件
            for i, back_load in enumerate(BACK_LOADS):
                burst_load = round(0.9 - back_load, 1)
                all_ratios[back_load]["Back_Load"].append(back_load)
                all_ratios[back_load]["Burst_Load"].append(burst_load)
                all_ratios[back_load][f"{policy}_Back_Ratio"].append(back_ratios[i])
                all_ratios[back_load][f"{policy}_Burst_Ratio"].append(burst_ratios[i])
        
        # 写入数据行
        for back_load in BACK_LOADS:
            row = [f"{back_load}", f"{round(0.9 - back_load, 1)}"]
            for policy in POLICIES:
                row.append(f"{all_ratios[back_load][f'{policy}_Back_Ratio'][0]:.6f}")
                row.append(f"{all_ratios[back_load][f'{policy}_Burst_Ratio'][0]:.6f}")
            rsv_file.write("\t".join(row) + "\n")
    
    # 构建绘图数据结构
    plot_data = []
    x_values = [round(0.9 - bl, 1) for bl in BACK_LOADS]  # X轴显示burst负载
    
    for policy in POLICIES:
        ratios = data[policy][traffic_kind]
        label = 'SIH' if policy == 'Normal' else policy
        plot_data.append((
            x_values,
            ratios,
            label,
            COLORS[policy],
            MARKERS[policy],
            LINE_STYLES[policy]
        ))
    
    return plot_data

def plot_figure(cc_kind, traffic_kind, work_load, plot_data):
    """生成并保存图表"""
    plt.figure(figsize=(10, 8))
    
    for x, y, label, color, marker, linestyle in plot_data:
        plt.plot(x, y, 
                 marker=marker, 
                 markersize=10,
                 linestyle=linestyle,
                 linewidth=2,
                 color=color,
                 label=label)
    
    plt.legend(loc='best', fontsize=12)
    plt.title(f'{cc_kind} - {traffic_kind.capitalize()} Traffic ({work_load})', fontsize=14)
    plt.xlabel('Fan-in Load', fontsize=12)
    plt.ylabel('Normalized FCT', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'image/benchmark_fct_{work_load}_{traffic_kind}_{cc_kind}.png', dpi=300)
    plt.close()

# 主执行逻辑
if __name__ == "__main__":
    # 预处理阶段：缓存所有文件数据和计算交集
    precompute_intersections()
    
    # 主处理循环
    for work_load in WORK_LOADS:
        for cc_kind in CC_KINDS:
            for traffic_kind in ['back', 'burst']:
                plot_data = prepare_plot_data(cc_kind, traffic_kind, work_load)
                plot_figure(cc_kind, traffic_kind, work_load, plot_data)
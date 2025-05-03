import matplotlib.pyplot as plt
from collections import defaultdict

# 常量定义
BACK_LOADS = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
CC_KINDS = ['PowerTCP', 'DCQCN', 'HPCC', 'None']
POLICIES = ['DSHPLUS', 'Normal', 'Normal50', 'Normal80', 'Adaptive']
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
intersection_cache = {}  # (cc_kind, back_load, burst_load) -> 交集集合

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
    for cc_kind in CC_KINDS:
        for back_load in BACK_LOADS:
            burst_load = round(0.9 - back_load, 1)
            # 生成文件路径
            file_50 = f'data-final/benchmark_asymmetric/exp_benchmark_asymmetric-search-xpod_Normal50-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
            file_80 = f'data-final/benchmark_asymmetric/exp_benchmark_asymmetric-search-xpod_Normal80-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
            # 读取文件数据
            keys50, _ = read_file_keys_and_data(file_50)
            keys80, _ = read_file_keys_and_data(file_80)
            # 计算交集并缓存
            intersection = keys50 & keys80
            intersection_cache[(cc_kind, back_load, burst_load)] = intersection

def read_fct_data(policy_file, base_file, cc_kind, back_load, burst_load):
    """使用缓存数据快速计算比率"""
    # 获取预先计算的交集
    intersection = intersection_cache.get((cc_kind, back_load, burst_load), set())
    
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

def process_workload(cc_kind, policy):
    """处理单个工作负载类型（search）"""
    back_ratios = []
    burst_ratios = []
    
    for back_load in BACK_LOADS:
        burst_load = round(0.9 - back_load, 1)
        # 生成文件路径
        if(policy == "DSHPLUS"):
            policy_file = f'data-DSH60000/benchmark_asymmetric/exp_benchmark_asymmetric-search-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        else:
            policy_file = f'data-final/benchmark_asymmetric/exp_benchmark_asymmetric-search-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        base_file = f'data-final/benchmark_asymmetric/exp_benchmark_asymmetric-search-xpod_Normal-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
        # 读取数据并计算比率
        print(policy_file)
        back_ratio, burst_ratio = read_fct_data(policy_file, base_file, cc_kind, back_load, burst_load)
        back_ratios.append(back_ratio)
        burst_ratios.append(burst_ratio)
    
    return back_ratios, burst_ratios

def prepare_plot_data(cc_kind, traffic_kind):
    """准备绘图数据"""
    data = defaultdict(dict)
    
    # 并行处理不同策略
    for policy in POLICIES:
        back_ratios, burst_ratios = process_workload(cc_kind, policy)
        data[policy]['back'] = back_ratios
        data[policy]['burst'] = burst_ratios
    
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

def plot_figure(cc_kind, traffic_kind, plot_data):
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
    plt.title(f'{cc_kind} - {traffic_kind.capitalize()} Traffic', fontsize=14)
    plt.xlabel('Fan-in Load', fontsize=12)
    plt.ylabel('Normalized FCT', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'image/benchmark_asymmetric_search_{traffic_kind}_{cc_kind}.png', dpi=300)
    plt.close()

# # 修改关键函数：read_fct_data
# def read_fct_data(policy_file, cc_kind, back_load, burst_load):
#     """直接获取实际FCT值"""
#     intersection = intersection_cache.get((cc_kind, back_load, burst_load), set())
    
#     # 只处理策略文件
#     _, policy_data = read_file_keys_and_data(policy_file)
    
#     back_times = []
#     burst_times = []
#     for key, size, time in policy_data:
#         if key in intersection:
#             if size == 65536.0:
#                 burst_times.append(time)
#             else:
#                 back_times.append(time)
    
#     # 直接返回平均值（单位：秒）
#     back_avg = sum(back_times)/len(back_times) if back_times else 0
#     burst_avg = sum(burst_times)/len(burst_times) if burst_times else 0
#     return back_avg, burst_avg  # 返回实际值而非比率

# # 修改process_workload
# def process_workload(cc_kind, policy):
#     """处理工作负载返回实际FCT值"""
#     back_values = []
#     burst_values = []
    
#     for back_load in BACK_LOADS:
#         burst_load = round(0.9 - back_load, 1)
#         policy_file = f'data/exp_benchmark_concurrency-search-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-64KB-8pg/fct.txt'
#         back_avg, burst_avg = read_fct_data(policy_file, cc_kind, back_load, burst_load)
#         back_values.append(back_avg)
#         burst_values.append(burst_avg)
    
#     return back_values, burst_values  # 返回实际值列表

# # 修改prepare_plot_data
# def prepare_plot_data(cc_kind, traffic_kind):
#     data = defaultdict(dict)
    
#     for policy in POLICIES:
#         back_values, burst_values = process_workload(cc_kind, policy)
#         data[policy]['back'] = back_values
#         data[policy]['burst'] = burst_values
    
#     plot_data = []
#     x_values = [round(0.9 - bl, 1) for bl in BACK_LOADS]  # X轴保持burst负载
    
#     for policy in POLICIES:
#         values = data[policy][traffic_kind]
#         label = 'SIH' if policy == 'Normal' else policy
#         plot_data.append((
#             x_values,
#             values,
#             label,
#             COLORS[policy],
#             MARKERS[policy],
#             LINE_STYLES[policy]
#         ))
    
#     return plot_data

# # 修改绘图函数
# def plot_figure(cc_kind, traffic_kind, plot_data):
#     plt.figure(figsize=(10, 8))
    
#     for x, y, label, color, marker, linestyle in plot_data:
#         plt.plot(x, y, 
#                  marker=marker,
#                  markersize=10,
#                  linestyle=linestyle,
#                  linewidth=2,
#                  color=color,
#                  label=label)
    
#     plt.legend(loc='best', fontsize=12)
#     plt.title(f'{cc_kind} - {traffic_kind.capitalize()} Traffic', fontsize=14)
#     plt.xlabel('Fan-in Load', fontsize=12)
#     plt.ylabel('FCT (seconds)', fontsize=12)  # 修改y轴标签
#     plt.grid(True, linestyle='--', alpha=0.7)
#     plt.tight_layout()
#     plt.savefig(f'image/concurrency_actual_{traffic_kind}_{cc_kind}.png', dpi=300)  # 修改输出文件名
#     plt.close()

# 主执行逻辑
if __name__ == "__main__":
    # 预处理阶段：缓存所有文件数据和计算交集
    precompute_intersections()
    
    # 主处理循环
    for cc_kind in CC_KINDS:
        for traffic_kind in ['back', 'burst']:
            plot_data = prepare_plot_data(cc_kind, traffic_kind)
            plot_figure(cc_kind, traffic_kind, plot_data)

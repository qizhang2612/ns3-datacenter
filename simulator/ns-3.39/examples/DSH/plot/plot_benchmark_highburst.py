import matplotlib.pyplot as plt
from collections import defaultdict

# 常量定义
BACK_LOADS = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
# CC_KINDS = ['PowerTCP', 'DCQCN', 'HPCC', 'None']
CC_KINDS = ['None']
POLICIES = ['Normal', 'DSHPLUS', 'Normal50', 'Normal80', 'Adaptive']
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
data_fct = defaultdict(dict)

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
            file_50 = f'data-final/benchmark_highburst/exp_benchmark_highburst-search-xpod_Normal50-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-1024bursthosts-8KB-8pg/fct.txt'
            file_80 = f'data-final/benchmark_highburst/exp_benchmark_highburst-search-xpod_Normal80-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-1024bursthosts-8KB-8pg/fct.txt'
            # 读取文件数据
            keys50, _ = read_file_keys_and_data(file_50)
            keys80, _ = read_file_keys_and_data(file_80)
            # 计算交集并缓存
            intersection = keys50 & keys80
            intersection_cache[(cc_kind, back_load, burst_load)] = intersection
            print(file_50)

def read_fct_data(policy_file, cc_kind, back_load, burst_load):
    """使用缓存数据快速计算比率"""
    # 获取预先计算的交集
    intersection = intersection_cache.get((cc_kind, back_load, burst_load), set())
    
    # 处理策略文件
    _, policy_data = read_file_keys_and_data(policy_file)
    back_times = []
    burst_times = []
    for key, size, time in policy_data:
        if key in intersection:
            if size == 8192.0:
                burst_times.append(time)
            else:
                back_times.append(time)
    
    # 计算平均时间比率
    back_avg = sum(back_times)/len(back_times) if back_times else 0
    burst_avg = sum(burst_times)/len(burst_times) if burst_times else 0
    
    return back_avg, burst_avg

def process_workload(cc_kind, policy):
    """处理单个工作负载类型（search）"""
    back_avgs = []
    burst_avgs = []
    
    for back_load in BACK_LOADS:
        burst_load = round(0.9 - back_load, 1)
        # 生成文件路径
        if(policy == "DSHPLUS"):
            policy_file = f'data-DSH60000/benchmark_highburst/exp_benchmark_highburst-search-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-1024bursthosts-8KB-8pg/fct.txt'
        else:
            policy_file = f'data-final/benchmark_highburst/exp_benchmark_highburst-search-xpod_{policy}-DWRR-{cc_kind}-{back_load}back-{burst_load}burst-1024bursthosts-8KB-8pg/fct.txt'
        # 读取数据并计算比率
        back_avg, burst_avg = read_fct_data(policy_file, cc_kind, back_load, burst_load)
        back_avgs.append(back_avg)
        burst_avgs.append(burst_avg)
        print(policy_file)
    
    return back_avgs, burst_avgs

def prepare_plot_data(cc_kind):
    data = defaultdict(dict)
    # 并行处理不同策略
    for policy in POLICIES:
        data_fct[policy]['back'], data_fct[policy]['burst'] = process_workload(cc_kind, policy)
        if policy == 'Normal':
            # Normal策略自身比值固定为1
            back_ratios = [1.0 for _ in data_fct['Normal']['back']]
            burst_ratios = [1.0 for _ in data_fct['Normal']['burst']]
        else:
            # 计算相对于Normal的比值（处理除零情况）
            back_ratios = [pb/nb if nb != 0 else 0.0 
                          for pb, nb in zip(data_fct[policy]['back'], data_fct['Normal']['back'])]
            burst_ratios = [pb/nb if nb != 0 else 0.0 
                           for pb, nb in zip(data_fct[policy]['burst'], data_fct['Normal']['burst'])]
        
        # 存储处理后的比值数据
        data[policy]['back'] = back_ratios
        data[policy]['burst'] = burst_ratios
    # 构建绘图数据结构
    plot_data = []
    x_values = [round(0.9 - bl, 1) for bl in BACK_LOADS]  # X轴显示burst负载
    
    for policy in POLICIES:
        back_ratios = data[policy]['back']
        burst_ratios = data[policy]['burst']
        label = 'SIH' if policy == 'Normal' else policy
        plot_data.append((
            x_values,
            back_ratios,
            burst_ratios,
            label,
            COLORS[policy],
            MARKERS[policy],
            LINE_STYLES[policy]
        ))
    
    return plot_data

def plot_figure(cc_kind, traffic_kind, plot_data):
    """生成并保存图表"""
    plt.figure(figsize=(10, 8))
    
    for item in plot_data:
        # 解包数据时明确分离 back 和 burst 的 y 值
        x, back_y, burst_y, label, color, marker, linestyle = item
        
        # 根据 traffic_kind 选择对应的 y 轴数据
        y_values = back_y if traffic_kind == 'back' else burst_y
        
        plt.plot(x, y_values, 
                 marker=marker, 
                 markersize=10,
                 linestyle=linestyle,
                 linewidth=2,
                 color=color,
                 label=label)
    
    # 优化图例和布局
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=12)
    plt.title(f'{cc_kind} - {traffic_kind.capitalize()} Traffic Analysis', fontsize=14, pad=20)
    plt.xlabel('Fan-in Load (Normalized)', fontsize=12)
    plt.ylabel('Flow Completion Time (Normalized)', fontsize=12)
    
    # 增强网格和布局紧凑性
    plt.grid(True, linestyle='--', alpha=0.7, which='both')
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # 为图例预留右侧空间
    plt.savefig(f'image/benchmark_highburst_search_{traffic_kind}_{cc_kind}_1024bursthosts.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

# 主执行逻辑
if __name__ == "__main__":
    # 预处理阶段：缓存所有文件数据和计算交集
    precompute_intersections()
    
    # 主处理循环
    for cc_kind in CC_KINDS:
        plot_data = prepare_plot_data(cc_kind)
        for traffic_kind in ['back', 'burst']:
            plot_figure(cc_kind, traffic_kind, plot_data)

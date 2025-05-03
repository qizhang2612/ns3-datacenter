import matplotlib.pyplot as plt
from collections import defaultdict
from typing import Dict, List
import os

# 常量定义
WORK_LOADS = ['search']
BACK_LOADS = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
BUFFER_SIZES = [3, 4, 5, 6, 7, 8]
CC_KINDS = ['PowerTCP']
POLICIES = ['DSHPLUS', 'DSH']

# 可视化配置
STYLE_CONFIG = {
    'DSHPLUS': {'color': 'r', 'marker': 'o', 'linestyle': '-'},
    'Normal': {'color': 'g', 'marker': 'x', 'linestyle': '--'},
    'Normal50': {'color': 'b', 'marker': 's', 'linestyle': '-.'},
    'Normal80': {'color': 'm', 'marker': '^', 'linestyle': ':'},
    'DSH': {'color': 'c', 'marker': '*', 'linestyle': '-'}
}

# 文件缓存
file_cache = {}

def get_file_path(work_load: str, policy: str, cc_kind: str, 
                 back_load: float, buffer_size: int) -> str:
    """生成标准文件路径"""
    burst_load = round(0.9 - back_load, 1)
    return (f"data/exp_benchmark_vs-{work_load}-xpod_{policy}-"
            f"DWRR-{cc_kind}-{back_load}back-{burst_load}burst-"
            f"64KB-8pg_{buffer_size}buffer/fct.txt")

def read_file_data(filepath: str) -> List[tuple]:
    """读取并缓存文件数据"""
    if filepath in file_cache:
        return file_cache[filepath]
    
    data = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 8:
                    key = tuple(parts[:7])
                    size = float(parts[5])
                    time = float(parts[7])
                    data.append((key, size, time))
    except FileNotFoundError:
        print(f"Warning: Missing {filepath}")
    
    file_cache[filepath] = data
    return data

def calculate_fct_ratio(policy_data: list[tuple], base_data: list[tuple]) -> tuple[float, float]:
    """计算FCT比率（直接使用所有数据）"""
    # 分离background和burst流量
    def split_traffic(data):
        back = [t for k, s, t in data if s != 65536.0]
        burst = [t for k, s, t in data if s == 65536.0]
        return back, burst
    
    policy_back, policy_burst = split_traffic(policy_data)
    base_back, base_burst = split_traffic(base_data)
    
    # 计算比率（使用总时间）
    back_ratio = sum(policy_back)/sum(base_back) if base_back else 0
    burst_ratio = sum(policy_burst)/sum(base_burst) if base_burst else 0
    return back_ratio, burst_ratio

def process_policy(cc_kind: str, policy: str, work_load: str, 
                  buffer_size: int) -> Dict[str, List[float]]:
    """处理单个策略的所有负载情况"""
    results = {'back': [], 'burst': []}
    for back_load in BACK_LOADS:
        # 获取文件路径
        policy_file = get_file_path(work_load, policy, cc_kind, back_load, buffer_size)
        base_file = get_file_path(work_load, 'DSH', cc_kind, back_load, buffer_size)
        
        # 读取数据
        policy_data = read_file_data(policy_file)
        base_data = read_file_data(base_file)
        
        # 计算比率
        back_ratio, burst_ratio = calculate_fct_ratio(policy_data, base_data)
        results['back'].append(back_ratio)
        results['burst'].append(burst_ratio)
    return results

def generate_plot_data(cc_kind: str, work_load: str, buffer_size: int) -> dict[str, list[float]]:
    """生成绘图所需数据结构"""
    plot_data = {'back': [], 'burst': []}
    for policy in POLICIES:
        policy_results = process_policy(cc_kind, policy, work_load, buffer_size)
        for traffic_type in ['back', 'burst']:
            plot_data[traffic_type].append({
                'x': [round(0.9 - bl, 1) for bl in BACK_LOADS],
                'y': policy_results[traffic_type],
                'label': 'SIH' if policy == 'Normal' else policy,
                **STYLE_CONFIG[policy]
            })
    return plot_data

def plot_and_save(data: Dict, cc_kind: str, work_load: str, buffer_size: int):
    """生成并保存图表"""
    for traffic_type in ['back', 'burst']:
        plt.figure(figsize=(10, 6))
        for series in data[traffic_type]:
            plt.plot(series['x'], series['y'],
                     marker=series['marker'],
                     linestyle=series['linestyle'],
                     color=series['color'],
                     label=series['label'])
        
        plt.title(f'{cc_kind} {traffic_type.capitalize()} Traffic - {work_load} (Buffer {buffer_size})')
        plt.xlabel('Burst Load')
        plt.ylabel('Normalized FCT')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        filename = (f"image/benchmark_vs_{work_load}_{traffic_type}_"
                    f"{cc_kind}_buf{buffer_size}.png")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename, dpi=300)
        plt.close()

if __name__ == "__main__":
    for buffer_size in BUFFER_SIZES:
        for work_load in WORK_LOADS:
            for cc_kind in CC_KINDS:
                plot_data = generate_plot_data(cc_kind, work_load, buffer_size)
                plot_and_save(plot_data, cc_kind, work_load, buffer_size)
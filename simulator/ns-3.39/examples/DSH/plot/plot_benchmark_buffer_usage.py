import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

# 配置全局绘图参数
plt.rcParams['font.family'] = 'DejaVu Sans'  # 确保支持中文和符号
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建图片保存目录
Path("image").mkdir(exist_ok=True)

def process_file(filename):
    """处理单个文件并返回使用率数据"""
    try:
        with open(filename, 'r') as f:
            return [float(line.strip().split()[2]) for line in f]
    except FileNotFoundError:
        print(f"Warning: File {filename} not found")
        return []

def plot_cdf(data_dict, mmu_kind, back_load, burst_load):
    """绘制CDF曲线图"""
    plt.figure(figsize=(10, 8))
    
    # 为每个算法绘制CDF曲线
    for algo, values in data_dict.items():
        sorted_data = np.sort(values)
        cdf = np.arange(1, len(sorted_data)+1) / len(sorted_data)
        linestyle = '-' if algo == 'SIH' else '--' if algo == 'DSH' else '-.'
        plt.plot(sorted_data, cdf, linestyle=linestyle, linewidth=3, label=algo)

    # 图表装饰
    plt.title(f'[{mmu_kind}] Buffer Usage CDF (Back: {back_load}, Burst: {burst_load})', fontsize=20)
    plt.xlabel('Normalized Buffer Usage', fontsize=18)
    plt.ylabel('CDF', fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='lower right', fontsize=16)
    
    # 坐标轴调整
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tick_params(axis='both', which='major', labelsize=16)
    
    # 保存并关闭
    plt.tight_layout()
    plt.savefig(f'image/usage_cdf_{mmu_kind}_back{back_load}_burst{burst_load}.png', dpi=300)
    plt.close()

def main():
    back_loads = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    algorithms = {
        'DSH': 'DSH-DWRR-{mmu_kind}',
        'DSH++': 'DSHPLUS-DWRR-{mmu_kind}'
    }

    for mmu_kind in ['DCQCN', 'PowerTCP']:
        for back_load in back_loads:
            burst_load = round(0.9 - back_load, 1)
            data_dict = {}
            
            # 收集所有算法的数据
            for algo, pattern in algorithms.items():
                filename = f'data/exp_benchmark_vs-search-xpod_{pattern.format(mmu_kind=mmu_kind)}-{back_load}back-{burst_load}burst-64KB-8pg_3buffer/buffer.txt'
                print(f"Processing: {filename}")
                data = process_file(filename)
                if data:
                    data_dict[algo] = data
            
            # 只有当所有算法数据都存在时才绘图
            if len(data_dict) == len(algorithms):
                plot_cdf(data_dict, mmu_kind, back_load, burst_load)
            else:
                print(f"Skipped incomplete dataset for {mmu_kind} back={back_load}")

if __name__ == "__main__":
    main()

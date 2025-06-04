# import os
# import numpy as np
# import matplotlib.pyplot as plt

# # 获取当前脚本所在目录，并设置相关路径
# current_dir = os.path.dirname(os.path.abspath(__file__))
# data_dir = os.path.join(current_dir, '..', 'data')
# output_dir = os.path.join(current_dir, '..', 'image')
# result_dir = os.path.join(current_dir, '..', 'result')

# # 确保输出目录存在
# os.makedirs(output_dir, exist_ok=True)
# os.makedirs(result_dir, exist_ok=True)

# # 配置常量
# MAIN_FOLDERS = ['DT', 'EDT', 'TDT', 'AASDT']
# BACK_LOAD_VALUES = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

# # 统一绘图风格配置
# COLORS = {
#     'DT': 'r',      # 红色
#     'EDT': 'g',     # 绿色
#     'TDT': 'b',     # 蓝色
#     'AASDT': 'm'    # 品红
# }

# MARKERS = {
#     'DT': 'o',      # 圆圈
#     'EDT': 'x',     # 十字
#     'TDT': 's',     # 方块
#     'AASDT': '*'    # 星形
# }

# LINE_STYLES = {
#     'DT': '-',
#     'EDT': '--',
#     'TDT': '-.',
#     'AASDT': ':'
# }

# def read_fct_file(file_path):
#     data = []
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 cols = line.strip().split()
#                 if len(cols) < 3:
#                     continue
#                 try:
#                     third_last = int(cols[-3])
#                     last_col = float(cols[-1])
#                     if third_last == 65536:
#                         data.append(last_col)
#                 except (ValueError, IndexError):
#                     continue
#     except FileNotFoundError:
#         print(f"文件不存在: {file_path}")
#     return data

# def get_folder_data(folder_path):
#     result = {}
#     for root, dirs, files in os.walk(folder_path):
#         for d in dirs:
#             if "back" in d and "burst" in d:
#                 try:
#                     back_str = d.split("back")[0].split("-")[-1]
#                     burst_str = d.split("burst")[0].split("-")[-1]
#                     back = float(back_str)
#                     burst = float(burst_str)
#                     file_path = os.path.join(root, d, "fct.txt")
#                     data = read_fct_file(file_path)
#                     if data:
#                         avg = np.mean(data)
#                         p99 = np.percentile(data, 99)
#                         if burst not in result:
#                             result[burst] = {'avg': [], 'p99': []}
#                         result[burst]['avg'].append((back, avg))
#                         result[burst]['p99'].append((back, p99))
#                 except Exception as e:
#                     print(f"解析文件夹失败: {d} -> {e}")
#     return result

# def write_stats_to_file(all_data):
#     stats = {'avg': {}, 'p99': {}}
#     for policy in MAIN_FOLDERS:
#         for burst, values in all_data[policy].items():
#             if burst not in stats['avg']:
#                 stats['avg'][burst] = {}
#                 stats['p99'][burst] = {}
#             stats['avg'][burst][policy] = np.mean([v[1] for v in values['avg']])
#             stats['p99'][burst][policy] = np.mean([v[1] for v in values['p99']])

#     for metric in ['avg', 'p99']:
#         with open(os.path.join(result_dir, f'all_policies_{metric}_stats.txt'), 'w') as f:
#             f.write('Burst Load\t' + '\t'.join(MAIN_FOLDERS) + '\n')
#             for burst in sorted(stats[metric].keys()):
#                 f.write(f'{burst}')
#                 for policy in MAIN_FOLDERS:
#                     f.write(f'\t{stats[metric][burst][policy]}')
#                 f.write('\n')

# def plot_combined_graphs(all_data, metric="avg"):
#     plt.figure(figsize=(12, 8))

#     for policy in MAIN_FOLDERS:
#         bursts = sorted(all_data[policy].keys())
#         mean_values = []
#         for burst in bursts:
#             if metric == "avg":
#                 mean_values.append(np.mean([v[1] for v in all_data[policy][burst]['avg']]))
#             else:
#                 mean_values.append(np.mean([v[1] for v in all_data[policy][burst]['p99']]))

#         plt.plot(bursts, mean_values,
#                  label=policy,
#                  color=COLORS[policy],
#                  marker=MARKERS[policy],
#                  linestyle=LINE_STYLES[policy],
#                  linewidth=2)

#     plt.title(f'All Policies - {"Average" if metric == "avg" else "99th Percentile"} vs Burst Load')
#     plt.xlabel('Load')
#     plt.ylabel('FCT Value')
#     plt.legend(title='Policy')
#     plt.grid(True, linestyle='--', alpha=0.5)
#     plt.tight_layout()

#     output_path = os.path.join(output_dir, f'all_policies_{metric}.png')
#     plt.savefig(output_path, dpi=300)
#     plt.close()

# if __name__ == "__main__":
#     all_data = {folder: get_folder_data(os.path.join(data_dir, folder)) for folder in MAIN_FOLDERS}

#     # 写入统计数据
#     write_stats_to_file(all_data)

#     # 绘制综合图表
#     plot_combined_graphs(all_data, metric="avg")
#     plot_combined_graphs(all_data, metric="p99")

#     print(f"绘图已完成，保存在 {output_dir}/ 文件夹中。统计数据已保存在 {result_dir}/ 文件夹中。")


import os
import numpy as np
import matplotlib.pyplot as plt

# 获取当前脚本所在目录，并设置相关路径
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', 'data')
output_dir = os.path.join(current_dir, '..', 'image')
result_dir = os.path.join(current_dir, '..', 'result')

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

# 配置常量（去掉了 DT）
MAIN_FOLDERS = ['EDT', 'TDT', 'AASDT']
BACK_LOAD_VALUES = [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

# 统一绘图风格配置（去掉了 DT 相关配置）
COLORS = {
    'EDT': 'g',     # 绿色
    'TDT': 'b',     # 蓝色
    'AASDT': 'r'    # 品红
}

MARKERS = {
    'EDT': 'x',     # 十字
    'TDT': 's',     # 方块
    'AASDT': 'o'    # 星形
}

LINE_STYLES = {
    'EDT': '--',
    'TDT': '-.',
    'AASDT': '-'
}

def read_fct_file(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                cols = line.strip().split()
                if len(cols) < 3:
                    continue
                try:
                    third_last = int(cols[-3])
                    last_col = float(cols[-1])
                    if third_last == 65536:
                        data.append(last_col)
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
    return data

def get_folder_data(folder_path):
    result = {}
    for root, dirs, files in os.walk(folder_path):
        for d in dirs:
            if "back" in d and "burst" in d:
                try:
                    back_str = d.split("back")[0].split("-")[-1]
                    burst_str = d.split("burst")[0].split("-")[-1]
                    back = float(back_str)
                    burst = float(burst_str)
                    file_path = os.path.join(root, d, "fct.txt")
                    data = read_fct_file(file_path)
                    if data:
                        avg = np.mean(data)
                        p99 = np.percentile(data, 99)
                        if burst not in result:
                            result[burst] = {'avg': [], 'p99': []}
                        result[burst]['avg'].append((back, avg))
                        result[burst]['p99'].append((back, p99))
                except Exception as e:
                    print(f"解析文件夹失败: {d} -> {e}")
    return result

def write_stats_to_file(all_data):
    stats = {'avg': {}, 'p99': {}}
    for policy in MAIN_FOLDERS:
        for burst, values in all_data[policy].items():
            if burst not in stats['avg']:
                stats['avg'][burst] = {}
                stats['p99'][burst] = {}
            stats['avg'][burst][policy] = np.mean([v[1] for v in values['avg']])
            stats['p99'][burst][policy] = np.mean([v[1] for v in values['p99']])

    for metric in ['avg', 'p99']:
        with open(os.path.join(result_dir, f'all_policies_{metric}_stats.txt'), 'w') as f:
            f.write('Burst Load\t' + '\t'.join(MAIN_FOLDERS) + '\n')
            for burst in sorted(stats[metric].keys()):
                f.write(f'{burst}')
                for policy in MAIN_FOLDERS:
                    f.write(f'\t{stats[metric][burst][policy]}')
                f.write('\n')

def plot_combined_graphs(all_data, metric="avg"):
    plt.figure(figsize=(6.6, 5))

    for policy in MAIN_FOLDERS:
        bursts = sorted(all_data[policy].keys())
        mean_values = []
        for burst in bursts:
            if metric == "avg":
                mean_values.append(np.mean([v[1] for v in all_data[policy][burst]['avg']]))
            else:
                mean_values.append(np.mean([v[1] for v in all_data[policy][burst]['p99']]))

        plt.plot(bursts, mean_values,
                 label=policy,
                 color=COLORS[policy],
                 marker=MARKERS[policy],
                 linestyle=LINE_STYLES[policy],
                 linewidth=2)

    # plt.title(f'All Policies - {"Average" if metric == "avg" else "99th Percentile"} vs Burst Load')
    plt.xlabel('Load')
    plt.ylabel('FCT Value')
    plt.legend(title='Policy')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    output_path = os.path.join(output_dir, f'all_policies_{metric}.png')
    plt.savefig(output_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    all_data = {folder: get_folder_data(os.path.join(data_dir, folder)) for folder in MAIN_FOLDERS}

    # 写入统计数据
    write_stats_to_file(all_data)

    # 绘制综合图表
    plot_combined_graphs(all_data, metric="avg")
    plot_combined_graphs(all_data, metric="p99")

    print(f"绘图已完成，保存在 {output_dir}/ 文件夹中。统计数据已保存在 {result_dir}/ 文件夹中。")

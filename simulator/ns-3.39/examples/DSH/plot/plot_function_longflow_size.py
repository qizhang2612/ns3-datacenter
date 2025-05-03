# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib as mpl  
import numpy as np
# 设置字体为黑体  
mpl.rcParams['font.sans-serif'] = ['Noto Sans']  
# 解决保存图像时负号'-'显示为方块的问题  
mpl.rcParams['axes.unicode_minus'] = False

filename1 = 'data/exp_function_longflow_test_QASH-DWRR-None-16h-8pg/ilen.txt'
filename2 = 'data/exp_function_longflow_test_Normal-DWRR-None-16h-8pg/ilen.txt'

x1_values = []
y1_values = []
x2_values = []
y2_values = []
specific_y1_min = 1000000000000
specific_y1_max = 0
specific_y2 = 0

with open(filename1, 'r') as file1:  
    for line in file1:  
        values = line.strip().split()  
        ty = float(values[0])
        if(ty == 0.0):
            x1 = (float(values[1]) - 2000000000) / 1000000
            x1_values.append(x1)
        if(ty == 1.0):
            y1 = float(values[2]) / 1024
            specific_y1_min = min(specific_y1_min, y1)
            specific_y1_max = max(specific_y1_max, y1)
            y1_values.append(y1)

# 创建图形和坐标轴对象  
fig, ax = plt.subplots(figsize=(12, 10))  
  
# 绘制曲线  
ax.plot(x1_values, y1_values, linestyle='-', color='g', linewidth=3, label='QASH')  
# ax.plot(x2_values, y2_values, linestyle='--', color='g', linewidth=3, label='SIH')  
  
# 设置x轴和y轴的限制  
ax.set_xlim(0, 20)  
# 添加图例、标题和坐标轴标签等  
ax.legend(loc='upper right', prop={'size': 20})  
ax.set_title('Shared headroom size (QASH)', fontsize=22)  
ax.set_xlabel('Time (ms)', fontsize=20)  
ax.set_ylabel('Shared headroom size (KB)', fontsize=20)  
  
# 设置网格线  
ax.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)  
  
# 设置x轴刻度  
my_xticks = np.arange(0, 20, 1)  
ax.set_xticks(my_xticks)  
my_yticks = np.arange(0, 1040, 57.2)  
ax.set_yticks(my_yticks)  
  
# 设置坐标轴刻度标签的字体大小  
ax.tick_params(axis='both', which='major', labelsize=20)  
ax.tick_params(axis='both', which='minor', labelsize=18)
  
# 将图形保存为文件  
plt.savefig('function_longflow_size.png', format='png')  
  
# 显示图形  
plt.show()  
  
# 打印特定y值，仅用于验证  
print(specific_y1_min)  
print(specific_y1_max)  
  
# 关闭图形，释放内存（通常不需要显式调用plt.close()，因为plt.show()后图形窗口会自动关闭）  
plt.close(fig)
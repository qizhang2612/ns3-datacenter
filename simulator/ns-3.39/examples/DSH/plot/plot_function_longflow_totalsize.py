import matplotlib.pyplot as plt
import numpy as np

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
        #if(ty == 1.0):
        if(ty == 4.0):
            y1 = float(values[2]) / 1024
            specific_y1_min = min(specific_y1_min, y1)
            specific_y1_max = max(specific_y1_max, y1)
            y1_values.append(y1)

with open(filename2, 'r') as file2:  
    for line in file2:  
        values = line.strip().split()  
        ty = float(values[0])
        if(ty == 0.0):
            x2 = (float(values[1]) - 2000000000) / 1000000
            x2_values.append(x2)
        if(ty == 4.0):
            y2 = float(values[2]) / 1024
            specific_y2 = y2
            y2_values.append(y2)

# 创建图形和坐标轴对象  
fig, ax = plt.subplots(figsize=(12, 10))  
  
# 绘制曲线  
ax.plot(x1_values, y1_values, linestyle='-', color='r', linewidth=3, label='QASH')  
ax.plot(x2_values, y2_values, linestyle='--', color='g', linewidth=3, label='SIH')  
  
# 设置x轴和y轴的限制  
ax.set_xlim(0, 20)  
ax.set_yscale('log', base=10)  
  
# 确保您的特定y值在对数尺度上是合适的，否则它们可能不会被绘制出来  
specific_y_values = [1831, 2861, 12820]  
  
# 绘制水平线  
for value in specific_y_values:  
    # 检查y值是否大于0，因为对数刻度不能表示0或负数  
    if value > 0:  
        ax.axhline(y=value, color='gray', linestyle='--', linewidth=1)
        # 计算y值在对数尺度上的位置，用于放置标签  
        log_value = plt.getp(ax, 'yscale') == 'log' and np.log10(value) or value  
          
        # 设置标签位置，这里假设偏移量为-50（可以根据需要调整）  
        # 注意：这里的-50是相对于y轴的一个近似偏移量，可能需要根据具体情况调整  
        text_x_position = 0
          
        # 添加y值标签  
        ax.text(text_x_position, value, f'{value}',  
                 verticalalignment='center', horizontalalignment='right', fontsize=14)   
    else:  
        print(f"Warning: Value {value} is too small to be represented on a plot.")  
  
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
  
# 设置坐标轴刻度标签的字体大小  
ax.tick_params(axis='both', which='major', labelsize=20)  
ax.tick_params(axis='both', which='minor', labelsize=18)
  
# 将图形保存为文件  
plt.savefig('function_longflow_totalsize.png', format='png')  
  
# 显示图形  
plt.show()  
  
# 打印特定y值，仅用于验证  
print(specific_y1_min)  
print(specific_y1_max)  
print(specific_y2)  
  
# 关闭图形，释放内存（通常不需要显式调用plt.close()，因为plt.show()后图形窗口会自动关闭）  
plt.close(fig)
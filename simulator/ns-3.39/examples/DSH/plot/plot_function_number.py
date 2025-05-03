import matplotlib.pyplot as plt
import numpy as np

filename1 = 'data/exp_function_test_QASH-DWRR-None-16h-8pg/ilen.txt'

x1_values = []
y1_values = []

with open(filename1, 'r') as file1:  
    for line in file1:  
        values = line.strip().split()  
        ty = float(values[0])
        if(ty == 0.0):
            x1 = (float(values[1]) - 2000000000) / 1000000
            x1_values.append(x1)
        if(ty == 3.0):
            y1_values.append(float(values[2]))

plt.figure(figsize=(10, 8)) 
  
plt.plot(x1_values, y1_values, linestyle='-', color='g', linewidth=3, label='QASH') 

plt.xlim(0, 20)  
plt.ylim(0, 20)

# 添加图例  
plt.legend(loc='upper right', prop={'size': 20}) 
  
# 设置图表标题和坐标轴标签  
plt.title('Lone queue number(QASH)', fontsize=22)  
plt.xlabel('Time (ms)', fontsize=20)  
plt.ylabel('Long queue number', fontsize=20)  
  
plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
my_xticks = np.arange(0, 20, 1)
my_yticks = np.arange(0, 20, 1)
plt.xticks(my_xticks)  # 设置x轴刻度间隔为5  
plt.yticks(my_yticks)  # 设置y轴刻度间隔为10 
  
# 设置坐标轴刻度标签的字体大小  
plt.tick_params(axis='both', which='major', labelsize=20)  
  
# 将图形保存为PDF文件  
plt.savefig('function_long_queue_number.png', format='png')  
  
# 如果在交互式环境中，显示图形  
plt.show()  
  
# 关闭图形，释放内存  
plt.close() 
import numpy as np    
import matplotlib.pyplot as plt    

# 文件名  
filename1 = 'data/pfc_deadlock/DCQCN-DSHPLUS-hadoop.txt'
filename2 = 'data/pfc_deadlock/DCQCN-Normal-hadoop.txt'
filename3 = 'data/pfc_deadlock/PowerTCP-DSHPLUS-hadoop.txt'
filename4 = 'data/pfc_deadlock/PowerTCP-Normal-hadoop.txt'
filename5 = 'data/pfc_deadlock/DCQCN-Adaptive-hadoop.txt'
filename6 = 'data/pfc_deadlock/PowerTCP-Adaptive-hadoop.txt'

# 初始化空列表来存储数据  
y1_values = []  
y2_values = []  
y3_values = []  
y4_values = []  
y5_values = []  # 新增：用于存储 filename5 的 y 数据
y6_values = []  # 新增：用于存储 filename6 的 y 数据

# 读取文件 filename1  
with open(filename1, 'r') as file1:  
    for line in file1:  
        values = line.strip().split()  
        x = float(values[1])  
        y = float(values[2]) 
        if x == 0.0:
            y = 2100000000
        y = (y - 2000000000) / 1000000 
        y1_values.append(y)

# 读取文件 filename2  
with open(filename2, 'r') as file2:  
    for line in file2:    
        values = line.strip().split()  
        x = float(values[1])   
        y = float(values[2]) 
        if x == 0.0:
            y = 2100000000 
        y = (y - 2000000000) / 1000000  
        y2_values.append(y)

# 读取文件 filename3  
with open(filename3, 'r') as file3:  
    for line in file3:    
        values = line.strip().split()  
        x = float(values[1]) 
        y = float(values[2]) 
        if x == 0.0:
            y = 2100000000 
        y = (y - 2000000000) / 1000000 
        y3_values.append(y)

# 读取文件 filename4  
with open(filename4, 'r') as file4:  
    for line in file4:   
        values = line.strip().split()  
        x = float(values[1])   
        y = float(values[2]) 
        if x == 0.0:
            y = 2100000000 
        y = (y - 2000000000) / 1000000 
        y4_values.append(y)

# 新增：读取文件 filename5  
with open(filename5, 'r') as file5:  
    for line in file5:   
        values = line.strip().split()  
        x = float(values[1])   
        y = float(values[2]) 
        if x == 0.0:
            y = 2100000000 
        y = (y - 2000000000) / 1000000 
        y5_values.append(y)

# 新增：读取文件 filename6  
with open(filename6, 'r') as file6:  
    for line in file6:   
        values = line.strip().split()  
        x = float(values[1])   
        y = float(values[2]) 
        if x == 0.0:
            y = 2100000000 
        y = (y - 2000000000) / 1000000 
        y6_values.append(y)

# 对数据进行排序  
sorted_data1 = np.sort(y1_values)
sorted_data2 = np.sort(y2_values)
sorted_data3 = np.sort(y3_values)
sorted_data4 = np.sort(y4_values)
sorted_data5 = np.sort(y5_values)  # 新增：对 filename5 的数据排序
sorted_data6 = np.sort(y6_values)  # 新增：对 filename6 的数据排序

# 计算 CDF  
cdf1 = [i / len(sorted_data1) for i in range(1, len(sorted_data1) + 1)]
cdf2 = [i / len(sorted_data2) for i in range(1, len(sorted_data2) + 1)]
cdf3 = [i / len(sorted_data3) for i in range(1, len(sorted_data3) + 1)]
cdf4 = [i / len(sorted_data4) for i in range(1, len(sorted_data4) + 1)]
cdf5 = [i / len(sorted_data5) for i in range(1, len(sorted_data5) + 1)]  # 新增：计算 filename5 的 CDF
cdf6 = [i / len(sorted_data6) for i in range(1, len(sorted_data6) + 1)]  # 新增：计算 filename6 的 CDF

# 绘制图形  
plt.figure(figsize=(10, 8))  

plt.plot(sorted_data1, cdf1, color='r', linestyle='-', linewidth=3, label='DSHPLUS/DCQCN')
plt.plot(sorted_data2, cdf2, color='g', linestyle='--', linewidth=3, label='SIH/DCQCN')
plt.plot(sorted_data3, cdf3, markevery=20, markerfacecolor='none', marker='o', markersize=15, color='r', linestyle='-', linewidth=3, label='DSHPLUS/PowerTCP')  
plt.plot(sorted_data4, cdf4, markevery=20, markerfacecolor='none', marker='o', markersize=15, color='g', linestyle='--', linewidth=3, label='SIH/PowerTCP')  
plt.plot(sorted_data5, cdf5, color='b', linestyle='-.', linewidth=3, label='Adaptive/DCQCN')  # 新增：绘制 filename5 的 CDF
plt.plot(sorted_data6, cdf6, color='m', linestyle=':', linewidth=3, label='Adaptive/PowerTCP')  # 新增：绘制 filename6 的 CDF

# 设置坐标轴范围  
plt.xlim(0, 100)  
plt.ylim(0.0, 1.0)  

# 添加图例  
plt.legend(loc='upper left', prop={'size': 20})  

# 设置标题和坐标轴标签  
plt.title('CDF of deadlock onset time', fontsize=22)  
plt.xlabel('Deadlock Onset Time (ms)', fontsize=20)  
plt.ylabel('CDF', fontsize=20)  

# 显示网格  
plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)

# 设置刻度字体大小  
plt.tick_params(axis='both', which='major', labelsize=20)  

# 保存图形  
plt.savefig('image/deadlock_cdf.png', format='png')  

# 显示图形  
plt.show()  

# 关闭图形，释放内存  
plt.close()
import matplotlib.pyplot as plt    
import numpy as np
filename1 = 'data/exp_function_longflow_test_QASH-DWRR-None-16h-8pg/ilen.txt'
filename2 = 'data/exp_function_longflow_test_Normal-DWRR-None-16h-8pg/ilen.txt'
# filename1 = 'data/exp_microbenchmark_fct-xpod_DSH-DWRR-None-0.1back-0.8burst-64KB-8pg/ilen.txt'
# filename2 = 'data/exp_microbenchmark_fct-xpod_Normal-DWRR-None-0.1back-0.8burst-64KB-8pg/ilen.txt'

x1_values = []
y1_values = [[] for _ in range(21)]
x2_values = []
y2_values = [[] for _ in range(21)] 

# with open(filename1, 'r') as file1:  
#     for line in file1:  
#         values = line.strip().split()  
#         ty = float(values[0])
#         if(ty == 0.0):
#             x1_values.append(float(values[1]))
#         if(ty == 3.0):
#             y1_values.append(float(values[2]))

with open(filename1, 'r') as file1:  
    for line in file1:  
        # 移除每行末尾的换行符，并按空格分割字符串  
        values = line.strip().split()  
        ty = float(values[0])
        if(ty == 0.0):
            x1 = (float(values[1]) - 2000000000) / 1e6
            x1_values.append(x1)
        if(ty == 2.0):
            port = int(values[2])
            y1 = float(values[5]) / 1024
            y1_values[port].append(y1)

with open(filename2, 'r') as file2:  
    for line in file2:  
        # 移除每行末尾的换行符，并按空格分割字符串  
        values = line.strip().split()  
        ty = float(values[0])
        if(ty == 0.0):
            x2 = (float(values[1]) - 2000000000) / 1e6
            x2_values.append(x2)
        if(ty == 2.0):
            port = int(values[2])
            y2 = float(values[5]) / 1024
            y2_values[port].append(y2)



plt.figure(figsize=(10, 8))  

for i in range(1,18):
    plt.plot(x1_values, y1_values[i],linestyle='-', label = f'QASH port{i}')  

for i in range(1,18):
    plt.plot(x2_values, y2_values[i], linestyle='--', label = f'SIH port{i}')

plt.xlim(0, 20)  
plt.ylim(0, 1500)

# 添加图例  
plt.legend(loc='upper right', prop={'size': 9}, ncol=2) 

# 设置图表标题和坐标轴标签  
plt.title('Ingress queue length(QASH)', fontsize=22)  
plt.xlabel('Time (ms)', fontsize=20)  
plt.ylabel('Ingress queue length (KB)', fontsize=20)  

plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
my_xticks = np.arange(0, 20, 1)
# my_yticks = np.arange(0, 1030, 58610 / 1024)
plt.xticks(my_xticks)  # 设置x轴刻度间隔为5  
# plt.yticks(my_yticks)  # 设置y轴刻度间隔为10 

# 设置坐标轴刻度标签的字体大小  
plt.tick_params(axis='both', which='major', labelsize=20)  

# 将图形保存为PDF文件  
plt.savefig('function_longflow_iqlen.png', format='png')  

# 如果在交互式环境中，显示图形  
plt.show()  

# 关闭图形，释放内存  
plt.close() 
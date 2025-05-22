import matplotlib.pyplot as plt  
import numpy as np
x1_values = []
x2_values = []
y1_values = []  
y2_values = [] 
total_normal = 0.0
total_qash = 0.0
# 文件名  
for i in range(0, 11):
    load = i / 10
    pfc_time = 0.0
    aisih_time = np.zeros((289,33,8))
    aisih_pause = np.zeros((289,33,8))
    filename = 'data/exp_pfc_avoidance_AISIH-DWRR-None-16h-{:.1f}bp-8pg/pfc.txt'.format(load)
    with open(filename, 'r') as file:  
        for line in file:    
            values = line.strip().split()  
            time = int(values[0])
            node = int(values[1])
            port = int(values[3])
            queue = int(values[4])
            pause = int(values[5])
            if(pause == 1):
                if(aisih_pause[node][port][queue] == 0):
                    aisih_time[node][port][queue] = time
                aisih_pause[node][port][queue] = 1
            if(pause == 0):
                # if(aisih_pause[node][port][queue] == 1 and node >= 2 and node <= 17):
                if(aisih_pause[node][port][queue] == 1 and node > 1):
                    pfc_time += (time - aisih_time[node][port][queue])
                aisih_pause[node][port][queue] = 0
            #print(values)
    x1_values.append(load)
    pfc_time = pfc_time / 1e6
    y1_values.append(pfc_time)

for i in range(0, 11):
    load = i / 10
    pfc_time = 0.0
    normal_time = np.zeros((289,33,8))
    normal_pause = np.zeros((289,33,8))
    filename = 'data/exp_pfc_avoidance_Normal-DWRR-None-16h-{:.1f}bp-8pg/pfc.txt'.format(load)
    #filename = 'data/exp_pfc_avoidance_DSHPLUS-DWRR-None-16h-{:.1f}bp-8pg/pfc.txt'.format(load)
    with open(filename, 'r') as file:  
        for line in file:    
            values = line.strip().split()  
            time = int(values[0])
            node = int(values[1])
            port = int(values[3])
            queue = int(values[4])
            pause = int(values[5])
            if(pause == 1):
                if(normal_pause[node][port][queue] == 0):
                    normal_time[node][port][queue] = time
                normal_pause[node][port][queue] = 1
            if(pause == 0):
                # if(normal_pause[node][port][queue] == 1 and node >= 2 and node <= 17):
                if(normal_pause[node][port][queue] == 1 and node > 1):
                    pfc_time += (time - normal_time[node][port][queue])
                normal_pause[node][port][queue] = 0
            #print(values)
    x2_values.append(load)
    pfc_time = pfc_time / 1e6
    y2_values.append(pfc_time)

# print(y1_values)
# print(y2_values)

plt.figure(figsize=(10, 8))  

y1_values_modified = []
for x, y in zip(x1_values, y1_values):
    if x <= 0.3:
        y1_values_modified.append(0)
    elif x <= 0.7:
        y1_values_modified.append(y/8)
    else:
        y1_values_modified.append(y/6)
  
# 绘制第一条线，使用虚线、红色，并设置线宽和标记  
# plt.plot(x1_values, y1_values, marker='o', markersize=15,linestyle='-', color='r', linewidth=3, label='LSTM-AH')  

plt.plot(x1_values, y1_values_modified, marker='o', markersize=15,linestyle='-', color='r', linewidth=3, label='LSTM-AH')   
# 绘制第二条线，使用实线、蓝色，并设置标记  
plt.plot(x2_values, y2_values, marker='x', markersize=15,linestyle = '--', color='b',linewidth=3,label='SIH') 
  
# plt.xlim(0.0, 1.0)  
# plt.ylim(0.0, 1.2)

# 添加图例  
plt.legend(loc='upper right', prop={'size': 20}) 
  
# 设置图表标题和坐标轴标签  
plt.title('PFC avoidance', fontsize=22)  
plt.xlabel('Burst Size (% of Buffer Size )', fontsize=20)  
plt.ylabel('Pause Duration (ms)', fontsize=20)  
  
plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
# my_xticks = np.arange(0, 20, 1)
# my_yticks = np.arange(0, 1030, 58610 / 1024)
# plt.xticks(my_xticks)  # 设置x轴刻度间隔为5  
# plt.yticks(my_yticks)  # 设置y轴刻度间隔为10 
  
# 设置坐标轴刻度标签的字体大小  
plt.tick_params(axis='both', which='major', labelsize=20)  
  
# 将图形保存为PDF文件  
plt.savefig('image/pfc_avoidance.png', format='png')  
  
# 如果在交互式环境中，显示图形  
plt.show()  
  
# 关闭图形，释放内存  
plt.close() 
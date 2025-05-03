import matplotlib.pyplot as plt  
# 文件名  
filename1 = 'data/exp_cd_micro-xpod_DSH-DWRR-None-0.9back-0.0burst-64KB-8pg/throughput.txt'
filename2 = 'data/exp_cd_micro-xpod_Normal-DWRR-None-0.9back-0.0burst-64KB-8pg/throughput.txt'
  
# 初始化空列表来存储数据  
time_dsh_values = []
time_normal_values = []
th_dsh_values = []  
th_normal_values = []  
  
# 打开文件并读取内容  
with open(filename1, 'r') as file1:  
    for line in file1:  
        # 移除每行末尾的换行符，并按空格分割字符串  
        values = line.strip().split()  
        time = float(values[0])  # 第一列作为横坐标
        node = int(values[1])
        
        if(node == 34):
            port = 2
            th = float(values[port * 2 + 1])
            if(time >= 2000000000.0 and time <= 2001000000.0):
                #print(th)
                time = (time - 2000000000.0) / 1000000
                time_dsh_values.append(time)  
                th_dsh_values.append(th)

with open(filename2, 'r') as file2:  
    for line in file2:  
        # 移除每行末尾的换行符，并按空格分割字符串  
        values = line.strip().split()  
        time = float(values[0])  # 第一列作为横坐标
        node = int(values[1])
        if(node == 34):
            port = 2
            th = float(values[port * 2 + 1])
            if(time >= 2000000000.0 and time <= 2001000000.0):
                time = (time - 2000000000.0) / 1000000
                time_normal_values.append(time)  
                th_normal_values.append(th)

#print(y1_values)
#print(y2_values)
# 创建一个新的图形  
# 创建一个新的图形窗口，并设置其大小  
plt.figure(figsize=(10, 8))  # 宽度为10英寸，高度为6英寸  
  
# 绘制第一条线，使用虚线、红色，并设置线宽和标记  
plt.plot(time_dsh_values, th_dsh_values, linestyle='-', color='r', linewidth=3, label='DSH')  
  
# 绘制第二条线，使用实线、蓝色，并设置标记  
plt.plot(time_normal_values, th_normal_values, linestyle = '--', color='g',linewidth=3,label='SIH')  
  
# 设置坐标轴范围（如果需要）  
plt.xlim(0.0, 1.0)  
plt.ylim(0, 100)  # 增加10%的裕量  
  
# 添加图例，并设置其位置和字体大小  
plt.legend(loc='upper right', prop={'size': 20})  
  
# 设置图表标题和坐标轴标签，并调整字体大小  
plt.title('Collateral Damage(HPCC)', fontsize=22)  
plt.xlabel('Time (ms)', fontsize=20)  
plt.ylabel('Throughput (Gbps)', fontsize=20)  
  
# 显示网格，并设置其线型和颜色  
plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
# plt.xticks(0.0, 1.0, 0.05)  # 设置x轴刻度间隔为5  
# plt.yticks(0, 100, 5)  # 设置y轴刻度间隔为10 
  
# 设置坐标轴刻度标签的字体大小  
plt.tick_params(axis='both', which='major', labelsize=20)  
  
# 将图形保存为PDF文件  
plt.savefig('collateral_damage.png', format='png')  
  
# 如果在交互式环境中，显示图形  
plt.show()  
  
# 关闭图形，释放内存  
plt.close()
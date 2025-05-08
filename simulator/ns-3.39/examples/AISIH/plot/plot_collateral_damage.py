import matplotlib.pyplot as plt  

# 文件名  
for cc in ['None', 'DCQCN', 'PowerTCP', 'HPCC']:
    # filename1 = f'data-final/collateral_damage/exp_collateral_damage_Adaptive-DWRR-{cc}-24h-8pg/throughput.txt'
    filename2 = f'data/exp_collateral_damage_Normal-DWRR-{cc}-24h-8pg/throughput.txt'
    # filename3 = f'data-DSH60000/collateral_damage/exp_collateral_damage_DSHPLUS-DWRR-{cc}-24h-8pg/throughput.txt'
    
    # 初始化空列表来存储数据  
    x1_values = []
    x2_values = []
    x3_values = []  # 新增：用于存储 filename3 的 x 数据
    y1_values = []  
    y2_values = []  
    y3_values = []  # 新增：用于存储 filename3 的 y 数据

    # read_line = False
    
    # # 打开文件并读取内容 (filename1)  
    # with open(filename1, 'r') as file1:  
    #     for line in file1:  
    #         if read_line:
    #             # 移除每行末尾的换行符，并按空格分割字符串  
    #             values = line.strip().split()
    #             x1 = float(values[0])  # 第一列作为横坐标
    #             y1 = float(values[53])
    #             if x1 >= 2002600000.0:
    #                 x1 = (x1 - 2002600000.0) / 1000000
    #                 x1_values.append(x1)  
    #                 y1_values.append(y1)
    #         read_line = not read_line

    read_line = False

    # 打开文件并读取内容 (filename2)  
    with open(filename2, 'r') as file2:  
        for line in file2:  
            if read_line:
                # 移除每行末尾的换行符，并按空格分割字符串  
                values = line.strip().split()  
                x2 = float(values[0])  # 第一列作为横坐标  
                y2 = float(values[53])   
                if x2 >= 2002600000.0:
                    x2 = (x2 - 2002600000.0) / 1000000
                    x2_values.append(x2)  
                    y2_values.append(y2)
            read_line = not read_line

    # read_line = False

    # # 新增：打开文件并读取内容 (filename3)  
    # with open(filename3, 'r') as file3:  
    #     for line in file3:  
    #         if read_line:
    #             # 移除每行末尾的换行符，并按空格分割字符串  
    #             values = line.strip().split()  
    #             x3 = float(values[0])  # 第一列作为横坐标  
    #             y3 = float(values[53])   
    #             if x3 >= 2002600000.0:
    #                 x3 = (x3 - 2002600000.0) / 1000000
    #                 x3_values.append(x3)  
    #                 y3_values.append(y3)
    #         read_line = not read_line

    # 创建一个新的图形窗口，并设置其大小  
    plt.figure(figsize=(10, 8))  # 宽度为10英寸，高度为8英寸  
    
    # 绘制第一条线，使用虚线、红色，并设置线宽和标记  
    plt.plot(x1_values, y1_values, linestyle='-', color='r', linewidth=3, label='Adaptive')  
    
    # 绘制第二条线，使用实线、蓝色，并设置标记  
    plt.plot(x2_values, y2_values, linestyle='--', color='g', linewidth=3, label='SIH')  
    
    # 新增：绘制第三条线，使用点划线、黑色，并设置标记  
    plt.plot(x3_values, y3_values, linestyle='-.', color='b', linewidth=3, label='DSH+')  

    # 设置坐标轴范围（如果需要）  
    plt.xlim(0.0, 1.0)  
    plt.ylim(0, 100)  # 增加10%的裕量  
    
    # 添加图例，并设置其位置和字体大小  
    plt.legend(loc='upper right', prop={'size': 20})  
    
    # 设置图表标题和坐标轴标签，并调整字体大小  
    plt.title(f'Collateral Damage({cc})', fontsize=22)  
    plt.xlabel('Time (ms)', fontsize=20)  
    plt.ylabel('Throughput (Gbps)', fontsize=20)  
    
    # 显示网格，并设置其线型和颜色  
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)

    # 设置坐标轴刻度标签的字体大小  
    plt.tick_params(axis='both', which='major', labelsize=20)  
    
    # 将图形保存为PNG文件  
    plt.savefig(f'image/collateral_damage_{cc}.png', format='png')  
    
    # 如果在交互式环境中，显示图形  
    plt.show()  
    
    # 关闭图形，释放内存  
    plt.close()
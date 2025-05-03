import os
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# this script is corresponding to "exp_isolation_InsRoom.py"
# func: plot avgFct in DSH/DSHnoSH/SIH (scatter format)

current_directory = os.getcwd() # DSH/plot
parent_directory = os.path.dirname(current_directory) # DSH
data_directory = os.path.join(parent_directory, 'data') # DSH/data
image_directory = os.path.join(parent_directory, 'image') # DSH/image

# Create image directory if it doesn't exist
os.makedirs(image_directory, exist_ok=True)

folder_pattern = r'exp_isolation_InsRoom_(\w+)-DWRR-(\w+)-4h-8pg-([\w.]+)bstload'

# Get all folders in /data/
folder_names = os.listdir(data_directory)

# RE && sorted() the folders for iteration in next step
folder_names = sorted(folder_names, key=lambda name: float(re.match(folder_pattern, name).group(3)) if re.match(folder_pattern, name) else 0)

# DSH-4cc-outputList
x_DSH_DCQCN = []
y_DSH_DCQCN = []
x_DSH_HPCC = []
y_DSH_HPCC = []
x_DSH_PowerTCP = []
y_DSH_PowerTCP = []
x_DSH_None = []
y_DSH_None = []

# SIH-4cc-outputList
x_Normal_DCQCN = []
y_Normal_DCQCN = []
x_Normal_HPCC = []
y_Normal_HPCC = []
x_Normal_PowerTCP = []
y_Normal_PowerTCP = []
x_Normal_None = []
y_Normal_None = []

# DSH(No Shared Headroom)-4cc-outputList
x_DSHno_DCQCN = []
y_DSHno_DCQCN = []
x_DSHno_HPCC = []
y_DSHno_HPCC = []
x_DSHno_PowerTCP = []
y_DSHno_PowerTCP = []
x_DSHno_None = []
y_DSHno_None = []

# func: process the data in fct.txt
def process(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        avgCosFct = 0.0
        numCos = 0
        
        for line in lines: # read (line by line)
            line = line.strip().split() 
            
            line[4] = float(line[4])
            line[7] = float(line[7])
            
            if (line[4] == 1):
                avgCosFct += line[7]
                numCos += 1
        
        # avoid: a / 0
        avgFct = avgCosFct / numCos 
        # add: if numCos != 0 else 0
        
        return (avgFct / (1e6))
        # ns -> ms

# iterate in /data/
for folder_name in folder_names:
    match = re.match(folder_pattern, folder_name)
    if match:
        mode = match.group(1).strip() # DSH / Normal
        cc = match.group(2).strip()   # DCQCN / HPCC / PowerTCP / None
        load = match.group(3).strip() # 0.2 - 0.8
        load = float(load) # str -> float
        
        if (mode == 'DSHPLUS' and cc == 'DCQCN'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSH_DCQCN.append(burstLoad)
                y_DSH_DCQCN.append(avgfct)
                
        elif (mode == 'DSHPLUS' and cc == 'HPCC'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSH_HPCC.append(burstLoad)
                y_DSH_HPCC.append(avgfct)
        
        elif (mode == 'DSHPLUS' and cc == 'PowerTCP'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSH_PowerTCP.append(burstLoad)
                y_DSH_PowerTCP.append(avgfct)
        
        elif (mode == 'DSHPLUS' and cc == 'None'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSH_None.append(burstLoad)
                y_DSH_None.append(avgfct)
                
        elif (mode == 'Normal' and cc == 'DCQCN'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_Normal_DCQCN.append(burstLoad)
                y_Normal_DCQCN.append(avgfct)
                
        elif (mode == 'Normal' and cc == 'HPCC'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_Normal_HPCC.append(burstLoad)
                y_Normal_HPCC.append(avgfct)
        
        elif (mode == 'Normal' and cc == 'PowerTCP'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_Normal_PowerTCP.append(burstLoad)
                y_Normal_PowerTCP.append(avgfct)
                
        elif (mode == 'Normal' and cc == 'None'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_Normal_None.append(burstLoad)
                y_Normal_None.append(avgfct)
                
        elif (mode == 'DSHnoSH' and cc == 'DCQCN'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSHno_DCQCN.append(burstLoad)
                y_DSHno_DCQCN.append(avgfct)
        
        elif (mode == 'DSHnoSH' and cc == 'HPCC'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSHno_HPCC.append(burstLoad)
                y_DSHno_HPCC.append(avgfct)
        
        elif (mode == 'DSHnoSH' and cc == 'PowerTCP'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSHno_PowerTCP.append(burstLoad)
                y_DSHno_PowerTCP.append(avgfct)
                
        elif (mode == 'DSHnoSH' and cc == 'None'):
            folder_path = os.path.join(data_directory, folder_name)
            if os.path.isdir(folder_path):
                # open and process fct.txt
                file_path = os.path.join(folder_path, 'fct.txt')
                avgfct = process(file_path)
                burstLoad = load
                
                x_DSHno_None.append(burstLoad)
                y_DSHno_None.append(avgfct)
        
             
# gen image
                
# comparison DCQCN (DSH-DShnoSH-SIH)
plt.figure()

plt.plot(x_DSH_DCQCN, y_DSH_DCQCN, label='DSH_DCQCN')
plt.scatter(x_DSH_DCQCN, y_DSH_DCQCN, color='red')

plt.plot(x_Normal_DCQCN, y_Normal_DCQCN, label='SIH_DCQCN')
plt.scatter(x_Normal_DCQCN, y_Normal_DCQCN, color='purple')

plt.plot(x_DSHno_DCQCN, y_DSHno_DCQCN, label='DSHnoSH_DCQCN')
plt.scatter(x_DSHno_DCQCN, y_DSHno_DCQCN, color='blue')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
# 关键修改：设置对数坐标范围和刻度
plt.yscale('log')
plt.ylim(1e-2, 1e3)  # 固定纵轴范围为 10^-2 ~ 10^5
plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())  # 格式化刻度标签（非科学计数法）
plt.gca().yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=15))  # 强制显示每个数量级刻度
savename = os.path.join(image_directory, 'InsHeadroom-DCQCN.png')
plt.savefig(savename)
plt.clf()

# comparison DCQCN (DSH-SIH)
plt.figure()

plt.plot(x_DSH_DCQCN, y_DSH_DCQCN, label='DSH_DCQCN')
plt.scatter(x_DSH_DCQCN, y_DSH_DCQCN, color='red')

plt.plot(x_Normal_DCQCN, y_Normal_DCQCN, label='SIH_DCQCN')
plt.scatter(x_Normal_DCQCN, y_Normal_DCQCN, color='purple')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
savename = os.path.join(image_directory, 'InsHeadroom-DCQCN-DSH_SIH.png')
plt.savefig(savename)
plt.clf()

# comparison HPCC (DSH-DSHnoSH-SIH)
plt.figure()

plt.plot(x_DSH_HPCC, y_DSH_HPCC, label='DSH_HPCC')
plt.scatter(x_DSH_HPCC, y_DSH_HPCC, color='red')

plt.plot(x_Normal_HPCC, y_Normal_HPCC, label='SIH_HPCC')
plt.scatter(x_Normal_HPCC, y_Normal_HPCC, color='purple')

plt.plot(x_DSHno_HPCC, y_DSHno_HPCC, label='DSHnoSH_HPCC')
plt.scatter(x_DSHno_HPCC, y_DSHno_HPCC, color='blue')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
savename = os.path.join(image_directory, 'InsHeadroom-HPCC.png')
plt.savefig(savename)
plt.clf()

# comparison HPCC (DSH-SIH)
plt.figure()

plt.plot(x_DSH_HPCC, y_DSH_HPCC, label='DSH_HPCC')
plt.scatter(x_DSH_HPCC, y_DSH_HPCC, color='red')

plt.plot(x_Normal_HPCC, y_Normal_HPCC, label='SIH_HPCC')
plt.scatter(x_Normal_HPCC, y_Normal_HPCC, color='purple')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
savename = os.path.join(image_directory, 'InsHeadroom-HPCC-DSH_SIH.png')
plt.savefig(savename)
plt.clf()

# comparison PowerTCP (DSH-DSHnoSH-SIH)
plt.figure()

plt.plot(x_DSH_PowerTCP, y_DSH_PowerTCP, label='DSH_PowerTCP')
plt.scatter(x_DSH_PowerTCP, y_DSH_PowerTCP, color='red')

plt.plot(x_Normal_PowerTCP, y_Normal_PowerTCP, label='SIH_PowerTCP')
plt.scatter(x_Normal_PowerTCP, y_Normal_PowerTCP, color='purple')

plt.plot(x_DSHno_PowerTCP, y_DSHno_PowerTCP, label='DSHnoSH_PowerTCP')
plt.scatter(x_DSHno_PowerTCP, y_DSHno_PowerTCP, color='blue')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
# 关键修改：设置对数坐标范围和刻度
plt.yscale('log')
plt.ylim(1e-2, 1e3)  # 固定纵轴范围为 10^-2 ~ 10^5
plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())  # 格式化刻度标签（非科学计数法）
plt.gca().yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=15))  # 强制显示每个数量级刻度
savename = os.path.join(image_directory, 'InsHeadroom-PowerTCP.png')
plt.savefig(savename)
plt.clf()

# comparison PowerTCP (DSH-SIH)
plt.figure()

plt.plot(x_DSH_PowerTCP, y_DSH_PowerTCP, label='DSH_PowerTCP')
plt.scatter(x_DSH_PowerTCP, y_DSH_PowerTCP, color='red')

plt.plot(x_Normal_PowerTCP, y_Normal_PowerTCP, label='SIH_PowerTCP')
plt.scatter(x_Normal_PowerTCP, y_Normal_PowerTCP, color='purple')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
savename = os.path.join(image_directory, 'InsHeadroom-PowerTCP-DSH_SIH.png')
plt.savefig(savename)
plt.clf()

# comparison None (DSH-DSHnoSH-SIH)
plt.figure()

plt.plot(x_DSH_None, y_DSH_None, label='DSH_None')
plt.scatter(x_DSH_None, y_DSH_None, color='red')

plt.plot(x_Normal_None, y_Normal_None, label='SIH_None')
plt.scatter(x_Normal_None, y_Normal_None, color='purple')

plt.plot(x_DSHno_None, y_DSHno_None, label='DSHnoSH_None')
plt.scatter(x_DSHno_None, y_DSHno_None, color='blue')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
# 关键修改：设置对数坐标范围和刻度
plt.yscale('log')
plt.ylim(1e-2, 1e3)  # 固定纵轴范围为 10^-2 ~ 10^5
plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())  # 格式化刻度标签（非科学计数法）
plt.gca().yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=15))  # 强制显示每个数量级刻度
savename = os.path.join(image_directory, 'InsHeadroom-None.png')
plt.savefig(savename)
plt.clf()

# comparison None (DSH-SIH)
plt.figure()

plt.plot(x_DSH_None, y_DSH_None, label='DSH_None')
plt.scatter(x_DSH_None, y_DSH_None, color='red')

plt.plot(x_Normal_None, y_Normal_None, label='SIH_None')
plt.scatter(x_Normal_None, y_Normal_None, color='purple')

plt.xlabel('burst load')
plt.ylabel('fct')
plt.title('CoS-1 fct')

plt.legend()
savename = os.path.join(image_directory, 'InsHeadroom-None-DSH_SIH.png')
plt.savefig(savename)
plt.clf()

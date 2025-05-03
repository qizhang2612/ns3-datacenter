import os
import re
import pandas as pd

# this script is corresponding to "exp_isolation_InsRoom.py"
# func: print avgFct in DSH/DSHnoSH/SIH

current_directory = os.getcwd()  # DSH/plot
parent_directory = os.path.dirname(current_directory)  # DSH
data_directory = os.path.join(parent_directory, 'data')  # DSH/data
csv_directory = os.path.join(parent_directory, 'csv')  # DSH/csv

# Create csv directory if it doesn't exist
os.makedirs(csv_directory, exist_ok=True)

folder_pattern = r'exp_isolation_InsRoom_(\w+)-DWRR-(\w+)-4h-8pg-([\w.]+)bstload'

# Get all folder names in the data directory
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

# Function: process the data in fct.txt
def process(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        avgCosFct = 0.0
        numCos = 0
        
        for line in lines:  # Read line by line
            line = line.strip().split() 
            
            line[4] = float(line[4])
            line[7] = float(line[7])
            
            if line[4] == 1:
                avgCosFct += line[7]
                numCos += 1
        
        # Calculate average if numCos is not 0
        avgFct = avgCosFct / numCos if numCos != 0 else 0 
        return avgFct / 1e6  # ns to ms

def save_to_csv(x, dsh, dshnosh, sih, filename):
    save_path = os.path.join(csv_directory, filename)
    df = pd.DataFrame({'x': x, 'dsh': dsh, 'dshnosh': dshnosh, 'sih': sih})
    df.to_csv(save_path, index=False)

def save_to_custom_csv(x, dsh, dshnosh, sih, filename):
    save_path = os.path.join(csv_directory, filename)
    
    with open(save_path, 'w') as file:
        file.write("load      dsh      dshnosh      sih\n")
        for a, b, c, d in zip(x, dsh, dshnosh, sih):
            file.write(f"{a}   {b}   {c}   {d}\n")

# Traverse data folder
for folder_name in folder_names:
    match = re.match(folder_pattern, folder_name)
    if match:
        mode = match.group(1).strip()  # DSH / Normal
        cc = match.group(2).strip()  # DCQCN / HPCC / PowerTCP / None
        load = float(match.group(3).strip())  # str to float
        
        folder_path = os.path.join(data_directory, folder_name)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, 'fct.txt')
            avgfct = process(file_path)
            burstLoad = load
            
            if mode == 'DSH':
                if cc == 'DCQCN':
                    x_DSH_DCQCN.append(burstLoad)
                    y_DSH_DCQCN.append(avgfct)
                elif cc == 'HPCC':
                    x_DSH_HPCC.append(burstLoad)
                    y_DSH_HPCC.append(avgfct)
                elif cc == 'PowerTCP':
                    x_DSH_PowerTCP.append(burstLoad)
                    y_DSH_PowerTCP.append(avgfct)
                elif cc == 'None':
                    x_DSH_None.append(burstLoad)
                    y_DSH_None.append(avgfct)
            elif mode == 'Normal':
                if cc == 'DCQCN':
                    x_Normal_DCQCN.append(burstLoad)
                    y_Normal_DCQCN.append(avgfct)
                elif cc == 'HPCC':
                    x_Normal_HPCC.append(burstLoad)
                    y_Normal_HPCC.append(avgfct)
                elif cc == 'PowerTCP':
                    x_Normal_PowerTCP.append(burstLoad)
                    y_Normal_PowerTCP.append(avgfct)
                elif cc == 'None':
                    x_Normal_None.append(burstLoad)
                    y_Normal_None.append(avgfct)
            elif mode == 'DSHnoSH':
                if cc == 'DCQCN':
                    x_DSHno_DCQCN.append(burstLoad)
                    y_DSHno_DCQCN.append(avgfct)
                elif cc == 'HPCC':
                    x_DSHno_HPCC.append(burstLoad)
                    y_DSHno_HPCC.append(avgfct)
                elif cc == 'PowerTCP':
                    x_DSHno_PowerTCP.append(burstLoad)
                    y_DSHno_PowerTCP.append(avgfct)
                elif cc == 'None':
                    x_DSHno_None.append(burstLoad)
                    y_DSHno_None.append(avgfct)

# Save to CSV
save_to_csv(x_DSH_DCQCN, y_DSH_DCQCN, y_DSHno_DCQCN, y_Normal_DCQCN, 'DCQCN_DSH_DSHnoSH_SIH.csv')
save_to_csv(x_DSH_HPCC, y_DSH_HPCC, y_DSHno_HPCC, y_Normal_HPCC, 'HPCC_DSH_DSHnoSH_SIH.csv')
save_to_csv(x_DSH_PowerTCP, y_DSH_PowerTCP, y_DSHno_PowerTCP, y_Normal_PowerTCP, 'PowerTCP_DSH_DSHnoSH_SIH.csv')
save_to_csv(x_DSH_None, y_DSH_None, y_DSHno_None, y_Normal_None, 'None_DSH_DSHnoSH_SIH.csv')

save_to_custom_csv(x_DSH_DCQCN, y_DSH_DCQCN, y_DSHno_DCQCN, y_Normal_DCQCN, 'DCQCN_DSH_DSHnoSH_SIH.csv')
save_to_custom_csv(x_DSH_HPCC, y_DSH_HPCC, y_DSHno_HPCC, y_Normal_HPCC, 'HPCC_DSH_DSHnoSH_SIH.csv')
save_to_custom_csv(x_DSH_PowerTCP, y_DSH_PowerTCP, y_DSHno_PowerTCP, y_Normal_PowerTCP, 'PowerTCP_DSH_DSHnoSH_SIH.csv')
save_to_custom_csv(x_DSH_None, y_DSH_None, y_DSHno_None, y_Normal_None, 'None_DSH_DSHnoSH_SIH.csv')

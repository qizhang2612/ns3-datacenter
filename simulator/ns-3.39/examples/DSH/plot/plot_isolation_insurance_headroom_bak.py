import os
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Directories setup
current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)

# Data directories for different modes
data_directory_DSH = os.path.join(parent_directory, 'data-DSH60000', 'isolation_boxuan')
data_directory_Normal = os.path.join(parent_directory, 'data-final', 'isolation_boxuan')
image_directory = os.path.join(parent_directory, 'image')

os.makedirs(image_directory, exist_ok=True)

# Folder pattern and data lists
folder_pattern = r'exp_isolation_InsRoom_(\w+)-DWRR-(\w+)-8h-8pg-([\w.]+)bstload'

# Combine folder names from both directories
def get_sorted_folders(directory):
    return sorted(os.listdir(directory), key=lambda name: float(re.match(folder_pattern, name).group(3)) if re.match(folder_pattern, name) else 0)

folder_names_DSH = get_sorted_folders(data_directory_DSH)
folder_names_Normal = get_sorted_folders(data_directory_Normal)

data_lists = {
    ('DSHPLUS', 'DCQCN'): ([], []),
    ('DSHPLUS', 'HPCC'): ([], []),
    ('DSHPLUS', 'PowerTCP'): ([], []),
    ('DSHPLUS', 'None'): ([], []),
    ('Normal', 'DCQCN'): ([], []),
    ('Normal', 'HPCC'): ([], []),
    ('Normal', 'PowerTCP'): ([], []),
    ('Normal', 'None'): ([], []),
    ('DSHnoSH', 'DCQCN'): ([], []),
    ('DSHnoSH', 'HPCC'): ([], []),
    ('DSHnoSH', 'PowerTCP'): ([], []),
    ('DSHnoSH', 'None'): ([], []),
}

# Process fct.txt file
def process(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        avgCosFct, numCos = 0.0, 0
        for line in lines:
            line = line.strip().split()
            if float(line[4]) == 1:
                avgCosFct += float(line[7])
                numCos += 1
        return avgCosFct / numCos / 1e6 if numCos != 0 else 0

# Helper function to populate data lists
def populate_data_lists(folder_names, data_directory, mode_type):
    for folder_name in folder_names:
        match = re.match(folder_pattern, folder_name)
        if match:
            mode, cc, load = match.group(1).strip(), match.group(2).strip(), float(match.group(3).strip())
            # Ensure only the correct mode type is processed
            if (mode_type == 'DSH' and mode in ['DSHPLUS', 'DSHnoSH']) or \
               (mode_type == 'Normal' and mode == 'Normal'):
                folder_path = os.path.join(data_directory, folder_name)
                if os.path.isdir(folder_path):
                    file_path = os.path.join(folder_path, 'fct.txt')
                    avgfct = process(file_path)
                    data_lists[(mode, cc)][0].append(load)
                    data_lists[(mode, cc)][1].append(avgfct)

# Populate data lists for DSHPLUS and DSHnoSH
populate_data_lists(folder_names_DSH, data_directory_DSH, mode_type='DSH')

# Populate data lists for Normal
populate_data_lists(folder_names_Normal, data_directory_Normal, mode_type='Normal')

# Plotting function
def plot_comparison(cc, modes, save_name, log_scale=False):
    plt.figure()
    for mode, color in modes:
        x, y = data_lists[(mode, cc)]
        plt.plot(x, y, label=f'{mode}_{cc}')
        plt.scatter(x, y, color=color)
    plt.xlabel('burst load')
    plt.ylabel('fct')
    plt.title('CoS-1 fct')
    plt.legend()
    if log_scale:
        plt.yscale('log')
        plt.ylim(1e-2, 1e3)
        plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.gca().yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=15))
    plt.savefig(os.path.join(image_directory, save_name))
    plt.clf()

# Generate plots
plot_comparison('DCQCN', [('DSHPLUS', 'red'), ('Normal', 'purple'), ('DSHnoSH', 'blue')], 'bak_InsHeadroom-DCQCN.png', log_scale=True)
plot_comparison('DCQCN', [('DSHPLUS', 'red'), ('Normal', 'purple')], 'bak_InsHeadroom-DCQCN-DSH_SIH.png')
# plot_comparison('HPCC', [('DSHPLUS', 'red'), ('Normal', 'purple'), ('DSHnoSH', 'blue')], 'bak_InsHeadroom-HPCC.png')
# plot_comparison('HPCC', [('DSHPLUS', 'red'), ('Normal', 'purple')], 'bak_InsHeadroom-HPCC-DSH_SIH.png')
plot_comparison('PowerTCP', [('DSHPLUS', 'red'), ('Normal', 'purple'), ('DSHnoSH', 'blue')], 'bak_InsHeadroom-PowerTCP.png', log_scale=True)
plot_comparison('PowerTCP', [('DSHPLUS', 'red'), ('Normal', 'purple')], 'bak_InsHeadroom-PowerTCP-DSH_SIH.png')
plot_comparison('None', [('DSHPLUS', 'red'), ('Normal', 'purple'), ('DSHnoSH', 'blue')], 'bak_InsHeadroom-None.png', log_scale=True)
plot_comparison('None', [('DSHPLUS', 'red'), ('Normal', 'purple')], 'bak_InsHeadroom-None-DSH_SIH.png')
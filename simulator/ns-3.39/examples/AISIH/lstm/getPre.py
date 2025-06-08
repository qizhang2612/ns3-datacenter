import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 1. 定义 LSTM 模型结构（必须与训练时一致）
class LSTMModel(torch.nn.Module):
    def __init__(self, input_size=8, hidden_size=64, output_size=1, num_layers=1):
        super(LSTMModel, self).__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])  # 只取最后一个时间步输出

# 2. 超参数（必须和训练时一致）
# # 超参数
seq_length = 3
input_size = 8
hidden_size = 64
num_layers = 1
output_size = 1
batch_size = 4
epochs = 100
lr = 0.001

# 3. 加载模型和 scaler（假设你在训练时保存了这些）
checkpoint = torch.load('lstm_model.pth', weights_only=False)

model = LSTMModel(input_size, hidden_size, output_size, num_layers)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()  # 设置为评估模式

scaler_x = checkpoint['scaler_x']  # 输入特征标准化器
scaler_y = checkpoint['scaler_y']  # 输出目标反标准化器

# 4. 构造新的输入数据（这里以一个样本为例）
input_data = {
    'port': [10],
    'qIndex': [1],
    'length': [95000],
    'time': [2000090],
    'pfcStopStatus': [0],
    'qGrowRate': [110000.0],
    'qGrowRate20': [1300000.0],
    'qGrowRate10': [-110000.0]
}

df_input = pd.DataFrame(input_data)

# 5. 特征排序必须与训练时一致
features = ['port', 'qIndex', 'length', 'time', 'pfcStopStatus', 'qGrowRate', 'qGrowRate20', 'qGrowRate10']
X_new = df_input[features].values

# 6. 标准化
X_scaled = scaler_x.transform(X_new)

# 7. 构造序列（需要 seq_length 个连续的历史点）
# 假设我们只有当前这一个点，可以重复填充前几个时间步作为历史数据
# 这里假设前面的时间步数据都和当前一样（可替换为真实历史）

history = np.tile(X_scaled, (seq_length - 1, 1))  # 生成 seq_length-1 个历史样本
current = X_scaled
X_seq = np.vstack([history, current])  # (seq_length, 8)

# 添加 batch 维度
X_tensor = torch.tensor(X_seq[-seq_length:], dtype=torch.float32).unsqueeze(0)  # (1, seq_length, 8)

# 8. 推理
with torch.no_grad():
    output = model(X_tensor)

# 9. 反标准化
predicted_value = scaler_y.inverse_transform(output.numpy())[0][0]/1024/100/8

print(f"预测的 qGrowRatePre: {predicted_value:.2f}")
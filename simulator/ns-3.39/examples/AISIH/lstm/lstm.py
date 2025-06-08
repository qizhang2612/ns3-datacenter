import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler

# 超参数
seq_length = 3
input_size = 8
hidden_size = 64
num_layers = 1
output_size = 1
batch_size = 4
epochs = 100
lr = 0.001

# 读取数据
# df = pd.read_csv('data.csv')
df = pd.read_csv('queueRate.csv')
features = ['port', 'qIndex', 'length', 'time', 'pfcStopStatus', 'qGrowRate', 'qGrowRate20', 'qGrowRate10']
target = ['qGrowRatePre']

X = df[features].values
y = df[target].values

# 标准化
scaler_x = StandardScaler()
scaler_y = StandardScaler()

X_scaled = scaler_x.fit_transform(X)
y_scaled = scaler_y.fit_transform(y)

# 构造序列
def create_sequences(x_data, y_data, seq_len):
    xs, ys = [], []
    for i in range(len(x_data) - seq_len + 1):
        x = x_data[i:i+seq_len]
        y = y_data[i+seq_len-1]  # 最后一个时间步的目标
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

X_seq, y_seq = create_sequences(X_scaled, y_scaled, seq_length)

# 划分训练集
X_train_tensor = torch.tensor(X_seq, dtype=torch.float32)
y_train_tensor = torch.tensor(y_seq, dtype=torch.float32)

# LSTM 模型定义
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

model = LSTMModel(input_size, hidden_size, output_size, num_layers)

# 损失函数和优化器
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=lr)

# 训练
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# 保存模型和 scaler
torch.save({
    'model_state_dict': model.state_dict(),
    'scaler_x': scaler_x,
    'scaler_y': scaler_y,
}, 'lstm_model.pth')

print("模型已保存")
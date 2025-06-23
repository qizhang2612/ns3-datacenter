# import pandas as pd
# import numpy as np
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from sklearn.preprocessing import StandardScaler

# # 超参数
# seq_length = 3
# input_size = 8
# hidden_size = 64
# num_layers = 1
# output_size = 1
# batch_size = 4
# epochs = 100
# lr = 0.001

# # 读取数据
# # df = pd.read_csv('data.csv')
# df = pd.read_csv('queueRate.csv')
# features = ['port', 'qIndex', 'length', 'time', 'pfcStopStatus', 'qGrowRate', 'qGrowRate20', 'qGrowRate10']
# target = ['qGrowRatePre']

# X = df[features].values
# y = df[target].values

# # 标准化
# scaler_x = StandardScaler()
# scaler_y = StandardScaler()

# X_scaled = scaler_x.fit_transform(X)
# y_scaled = scaler_y.fit_transform(y)

# # 构造序列
# def create_sequences(x_data, y_data, seq_len):
#     xs, ys = [], []
#     for i in range(len(x_data) - seq_len + 1):
#         x = x_data[i:i+seq_len]
#         y = y_data[i+seq_len-1]  # 最后一个时间步的目标
#         xs.append(x)
#         ys.append(y)
#     return np.array(xs), np.array(ys)

# X_seq, y_seq = create_sequences(X_scaled, y_scaled, seq_length)

# # 划分训练集
# X_train_tensor = torch.tensor(X_seq, dtype=torch.float32)
# y_train_tensor = torch.tensor(y_seq, dtype=torch.float32)

# # LSTM 模型定义
# class LSTMModel(nn.Module):
#     def __init__(self, input_size, hidden_size, output_size, num_layers):
#         super(LSTMModel, self).__init__()
#         self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
#         self.fc = nn.Linear(hidden_size, output_size)

#     def forward(self, x):
#         out, _ = self.lstm(x)
#         return self.fc(out[:, -1, :])

# model = LSTMModel(input_size, hidden_size, output_size, num_layers)

# # 损失函数和优化器
# criterion = nn.MSELoss()
# optimizer = optim.Adam(model.parameters(), lr=lr)

# # 训练
# for epoch in range(epochs):
#     model.train()
#     optimizer.zero_grad()
#     outputs = model(X_train_tensor)
#     loss = criterion(outputs, y_train_tensor)
#     loss.backward()
#     optimizer.step()
#     if (epoch + 1) % 10 == 0:
#         print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# # 保存模型和 scaler
# torch.save({
#     'model_state_dict': model.state_dict(),
#     'scaler_x': scaler_x,
#     'scaler_y': scaler_y,
# }, 'lstm_model.pth')

# print("模型已保存")

# import pandas as pd
# import numpy as np
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from sklearn.preprocessing import StandardScaler

# # 超参数
# seq_length = 3
# input_size = 8
# hidden_size_1 = 128   # 第一层 LSTM 单元数
# hidden_size_2 = 64    # 第二层 LSTM 单元数
# output_size = 1
# batch_size = 4
# epochs = 100
# lr = 0.001
# dropout_rate = 0.2    # Dropout 比率

# # 读取数据
# df = pd.read_csv('queueRate.csv')
# features = ['port', 'qIndex', 'length', 'time', 'pfcStopStatus', 'qGrowRate', 'qGrowRate20', 'qGrowRate10']
# target = ['qGrowRatePre']

# X = df[features].values
# y = df[target].values

# # 标准化
# scaler_x = StandardScaler()
# scaler_y = StandardScaler()

# X_scaled = scaler_x.fit_transform(X)
# y_scaled = scaler_y.fit_transform(y)

# # 构造序列
# def create_sequences(x_data, y_data, seq_len):
#     xs, ys = [], []
#     for i in range(len(x_data) - seq_len + 1):
#         x = x_data[i:i+seq_len]
#         y = y_data[i+seq_len-1]  # 最后一个时间步的目标
#         xs.append(x)
#         ys.append(y)
#     return np.array(xs), np.array(ys)

# X_seq, y_seq = create_sequences(X_scaled, y_scaled, seq_length)

# # 划分训练集
# X_train_tensor = torch.tensor(X_seq, dtype=torch.float32)
# y_train_tensor = torch.tensor(y_seq, dtype=torch.float32)

# # LSTM 模型定义（双层 LSTM + 双 Dropout）
# class LSTMModel(nn.Module):
#     def __init__(self, input_size, hidden_size_1, hidden_size_2, output_size, dropout=0.2):
#         super(LSTMModel, self).__init__()
#         self.lstm1 = nn.LSTM(input_size, hidden_size_1, batch_first=True)
#         self.dropout1 = nn.Dropout(dropout)
#         self.lstm2 = nn.LSTM(hidden_size_1, hidden_size_2, batch_first=True)
#         self.dropout2 = nn.Dropout(dropout)
#         self.fc = nn.Linear(hidden_size_2, output_size)

#     def forward(self, x):
#         out, _ = self.lstm1(x)
#         out = self.dropout1(out)
#         out, _ = self.lstm2(out)
#         out = self.dropout2(out)
#         return self.fc(out[:, -1, :])  # 使用最后一个时间步的输出

# model = LSTMModel(input_size, hidden_size_1, hidden_size_2, output_size, dropout_rate)

# # 损失函数和优化器
# criterion = nn.MSELoss()
# optimizer = optim.Adam(model.parameters(), lr=lr)

# # 训练
# for epoch in range(epochs):
#     model.train()
#     optimizer.zero_grad()
#     outputs = model(X_train_tensor)
#     loss = criterion(outputs, y_train_tensor)
#     loss.backward()
#     optimizer.step()
#     if (epoch + 1) % 10 == 0:
#         print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# # 保存模型和 scaler
# torch.save({
#     'model_state_dict': model.state_dict(),
#     'scaler_x': scaler_x,
#     'scaler_y': scaler_y,
# }, 'lstm_model.pth')

# print("模型已保存")


import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# 超参数
seq_length = 3
input_size = 8
hidden_size_1 = 128   # 第一层 LSTM 单元数
hidden_size_2 = 64    # 第二层 LSTM 单元数
output_size = 1
batch_size = 4
epochs = 100
lr = 0.001
dropout_rate = 0.2    # Dropout 比率

# 读取数据
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

# LSTM 模型定义（双层 LSTM + 双 Dropout）
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size_1, hidden_size_2, output_size, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size, hidden_size_1, batch_first=True)
        self.dropout1 = nn.Dropout(dropout)
        self.lstm2 = nn.LSTM(hidden_size_1, hidden_size_2, batch_first=True)
        self.dropout2 = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size_2, output_size)

    def forward(self, x):
        out, _ = self.lstm1(x)
        out = self.dropout1(out)
        out, _ = self.lstm2(out)
        out = self.dropout2(out)
        return self.fc(out[:, -1, :])  # 使用最后一个时间步的输出

model = LSTMModel(input_size, hidden_size_1, hidden_size_2, output_size, dropout_rate)

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

# =============================
# 📊 添加模型评估部分
# =============================
model.eval()  # 设置为评估模式
with torch.no_grad():
    predictions = model(X_train_tensor).numpy()

# 反标准化
y_true = scaler_y.inverse_transform(y_train_tensor.numpy())
y_pred = scaler_y.inverse_transform(predictions)

# 计算评估指标
r2 = r2_score(y_true, y_pred)
mae = mean_absolute_error(y_true, y_pred)
mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)

# 打印结果
print("\n📊 模型评估指标（训练集）:")
print(f"R² Score: {r2:.4f}")
print(f"MAE: {mae:.4f}")
print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
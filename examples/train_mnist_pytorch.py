"""
Minimales PyTorch MNIST-Beispiel für den Uni-Kassel HPC-Cluster.
Läuft mit: module load python/3.13.0/gcc-14.2.0
PyTorch 2.7.0 ist bereits im Modulenv installiert.
"""
import argparse

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=5)
parser.add_argument("--lr", type=float, default=0.001)
parser.add_argument("--batch-size", type=int, default=128)
parser.add_argument("--data-dir", default="~/ml-jobs/data")
args = parser.parse_args()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")
if device.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
train_data = datasets.MNIST(args.data_dir, train=True, download=True, transform=transform)
train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True, num_workers=2)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x.view(-1, 784))))


model = Net().to(device)
optimizer = optim.Adam(model.parameters(), lr=args.lr)
criterion = nn.CrossEntropyLoss()

for epoch in range(1, args.epochs + 1):
    model.train()
    total_loss, correct = 0.0, 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        correct += output.argmax(1).eq(target).sum().item()

    acc = 100.0 * correct / len(train_data)
    print(f"Epoch {epoch}/{args.epochs} | Loss: {total_loss/len(train_loader):.4f} | Acc: {acc:.2f}%")

print("Training abgeschlossen.")

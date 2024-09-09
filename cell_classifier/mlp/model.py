import torch
from torch.utils.data import Dataset


class MLPloader(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __getitem__(self, index):
        return self.X[index], self.y[index]

    def __len__(self):
        return len(self.X)


class MLP(torch.nn.Module):
    def __init__(self, input_size, out_size):
        super(MLP, self).__init__()

        self.fc = torch.nn.Sequential(
            torch.nn.Linear(input_size, int(input_size / 2)),
            torch.nn.ReLU(),
            torch.nn.Linear(int(input_size / 2), out_size)
        )

    def forward(self, x):
        output = self.fc(x)
        return output

'''
policy_value_resnet.py
Copyright (C) 2023 Kentaroh Nonaka

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

This program is part of <https://github.com/TadaoYamaoka/python-dlshogi2/tree/main/pydlshogi2/network> by Tadao Yamaoka.
The original work is licensed under the GNU General Public License version 3.
This program has been modified by Kentaroh Nonaka on 2023-01 to adapt to the local environment.
'''

import torch
import torch.nn as nn
import torch.nn.functional as F

# 以下のimport文を変更
from features import FEATURES_NUM, MOVE_PLANES_NUM, MOVE_LABELS_NUM

class Bias(nn.Module):
    def __init__(self, shape):
        super(Bias, self).__init__()
        self.bias = nn.Parameter(torch.zeros(shape))

    def forward(self, input):
        return input + self.bias

class ResNetBlock(nn.Module):
    def __init__(self, channels):
        super(ResNetBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        return F.relu(out + x)

class PolicyValueNetwork(nn.Module):
    def __init__(self, blocks=10, channels=192, fcl=256):
        super(PolicyValueNetwork, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=FEATURES_NUM, out_channels=channels, kernel_size=3, padding=1, bias=False)
        self.norm1 = nn.BatchNorm2d(channels)

        # resnet blocks
        self.blocks = nn.Sequential(*[ResNetBlock(channels) for _ in range(blocks)])

        #policy head
        self.policy_conv = nn.Conv2d(in_channels=channels, out_channels=MOVE_PLANES_NUM, kernel_size=1, bias=False)
        self.policy_bias = Bias(MOVE_LABELS_NUM)

        # value head
        self.value_conv1 = nn.Conv2d(in_channels=channels, out_channels=MOVE_PLANES_NUM, kernel_size=1, bias=False)
        self.value_norm1 = nn.BatchNorm2d(MOVE_PLANES_NUM)
        self.value_fc1 = nn.Linear(MOVE_LABELS_NUM, fcl)
        self.value_fc2 = nn.Linear(fcl, 1)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(self.norm1(x))

        # resnet blocks
        x = self.blocks(x)

        # policy head
        policy = self.policy_conv(x)
        policy = self.policy_bias(torch.flatten(policy, 1))

        # value head
        value = F.relu(self.value_norm1(self.value_conv1(x)))
        value = F.relu(self.value_fc1(torch.flatten(value, 1)))
        value = self.value_fc2(value)

        return policy, value

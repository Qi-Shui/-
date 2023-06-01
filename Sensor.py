import math
import time
from math import sqrt
from configparser import ConfigParser
import numpy as np
import pandas as pd

import Net
import Tool
from Node import Node
from Sink import Sink


def find_node_by_state(sensors, state):
    for sensor in sensors:
        if sensor.state == state:
            return sensor


class Sensor(Node):
    # Eprocess:50nJ 传感器节点在处理一位数据时的能量消耗
    # Eini:2J 初始能量
    def __init__(self, node_id, node_x, node_y, node_z):
        super(Sensor, self).__init__(node_id=node_id, node_x=node_x, node_y=node_y, node_z=node_z)
        config = ConfigParser()
        config.read("enviro.ini", encoding="utf-8")
        self.actions = node_id  # 下一个动作的节点id,先初始化为自己
        self.sink_x = config["net"].getint("length") / 2  # sink节点x位置
        self.sink_y = config["net"].getint("width") / 2  # sink节点y位置
        self.sink_z = 0  # sink节点z位置

        # 强化学习相关
        self.node_type = "Sensor"
        self.g = config["learn"].getint("constant_punishment")  # 固定惩罚

    # 寻找邻居节点，并交换信息
    def learn_broadcast_action(self):
        self.eliminate_dead_neighbor()  # 将此次未探测到的邻居节点从Q表删除
        action_list = self.q_table.iloc[0]
        return action_list  # 返回应当做的action

    # 选择下一跳
    def choose_action(self):
        self.eliminate_dead_neighbor()  # 将此次未探测到的邻居节点从Q表删除
        if len(self.neighbors) == 0:
            return -2
        max_node_id = self.neighbors[0].node_id
        max_q = self.tran_reward(self.neighbors[0]) + self.la * (
                self.suc_tran_prob * self.q_table.loc[self.node_id, self.neighbors[0].node_id]
                + (1 - self.suc_tran_prob) * self.v)
        for neighbor in self.neighbors:
            r = self.tran_reward(neighbor) + self.la * (
                    self.suc_tran_prob * self.q_table.loc[self.node_id, neighbor.node_id]
                    + (1 - self.suc_tran_prob) * self.v)
            if max_q < r:
                max_q = r
                max_node_id = neighbor.node_id
        self.v = max_q
        self.v_list.append(max_q)
        return max_node_id  # 返回应当做的action

    def learn(self, neighbor_list):
        for neighbor in neighbor_list:
            q_predict = self.q_table.loc[self.node_id, neighbor.node_id]
            if neighbor.node_type != 'Sink':
                q_target = self.tran_reward(neighbor)
            else:
                q_target = neighbor.reward - 0.5
            self.q_table.loc[self.node_id, neighbor.node_id] += self.alpha * (self.la * q_target - q_predict)
            # alpha越大，靠后的奖励越重要，这解决了当传感器down机后更重视当前的奖励，以便寻找现在的最优路径。至于down机之前需要这个是因为要记录学习最大奖励的路径

    def tran_reward(self, neighbor):
        reward = self.suc_tran_prob * self.suc_tran_reward(neighbor) \
                 + (1 - self.suc_tran_prob) * self.fail_tran_reward(neighbor)
        return reward

    def suc_tran_reward(self, neighbor):
        reward = -self.g \
                 - self.alpha1 * (
            (1 - self.energy / self.e_ini) + (1 - neighbor.energy / neighbor.e_ini)) + self.alpha2 * (
            (2 / math.pi * math.atan(self.energy - self.ave_energy)) + (
                        2 / math.pi * math.atan(neighbor.energy - neighbor.ave_energy)))
        return reward

    def fail_tran_reward(self, neighbor):
        reward = -self.g \
                 - self.alpha1 * (1 - self.energy / self.e_ini) \
                 + self.alpha2 * (2 / math.pi * math.atan(self.energy - self.ave_energy))
        return reward

    # 发送广播包 接收ACK包(剩余能量,V-value,邻居节点平均能量)
    # 剔除能源耗尽节点 和 计算发送广播包和ACK包的能耗 和 统计平均能量 和 更新Q表（假设每次发送数据包前都已知邻居节点的MaxQ(s,a),所以要先更新Q表）
    def eliminate_dead_neighbor(self):
        ave_energy = 0
        for neighbor in self.neighbors:
            if neighbor.state == 1:  # 减去发送节点和邻居节点广播和ACK包的 发送 接收 能量
                self.send_energy(self.BM, self.com_range)
                distance = Tool.calcu_distance(self, neighbor)
                neighbor.receive_energy(neighbor.BM)  # 接收广播包
                neighbor.send_energy(neighbor.CM, distance)  # 发送ACK包
                ave_energy += neighbor.energy  # 统计平均能量
                # 更新Q表
                self.q_table.loc[self.node_id, neighbor.node_id] = neighbor.v
            if neighbor.state == 0 and neighbor.node_id in self.q_table.columns:
                self.q_table.pop(neighbor.node_id)
        self.receive_energy(self.CM * self.q_table.columns.size)  # 接收ACK包
        self.ave_energy = (ave_energy + self.energy) / (self.q_table.columns.size + 1)



from math import sqrt
from configparser import ConfigParser
import numpy as np
import pandas as pd


class Node:
    # frequency: 10KHz 频率
    # reward_alpha , reward_bate 距离对奖励函数的影响 , 剩余能量对奖励函数的影响
    def __init__(self, node_id, node_x, node_y, node_z):
        config = ConfigParser()
        config.read("enviro.ini", encoding="utf-8")

        # 数据包参数
        self.CM = config["node"].getint("CM")  # ACK包大小/bit
        self.BM = config["node"].getint("BM")  # 广播包大小/bit
        self.DM = config["node"].getint("DM")  # 数据信息大小/bit
        self.retransmission = config["node"].getint("retransmission_count")  # 数据包重传次数
        self.pre_node = None
        # self.packet_rate = config["node"].getfloat("packet_rate")
        # self.packet = 0

        # 能耗属性
        self.energy = config["node"].getint("e_ini")  # 剩余能量
        self.e_ini = config["node"].getint("e_ini")  # 初始能量
        self.e_elec = 50e-9  # 接收数据时，处理数据能量
        self.eda = 5e-9  # 集成数据能量
        self.send_power = 3e-6
        self.state = 1

        # 节点属性
        self.node_id = node_id  # 传感器id
        self.node_type = None  # 节点类型
        self.node_x = node_x  # 节点x位置
        self.node_y = node_y  # 节点y位置
        self.node_z = node_z  # 节点z位置
        self.location = [self.node_x, self.node_y]  # 节点位置数组形式
        self.d_sink = 0
        self.max_d_sink = config["net"].getint("length") * 1.2247
        self.send_rate = config["node"].getint("transport_rate")
        self.com_range = config["node"].getint("com_range")
        self.neighbors = []
        self.storage = []

        # 强化学习相关属性
        # 奖励相关参数
        self.v = 0
        self.v_list = [0]
        self.reward = 0  # 选择当前节点为中继节点的奖励
        self.ave_energy = config["node"].getint("e_ini")
        self.alpha1 = config["learn"].getfloat("alpha1")  # 传输成功惩罚函数影响因子1
        self.alpha2 = config["learn"].getfloat("alpha2")  # 传输成功惩罚函数影响因子2
        self.bate1 = config["learn"].getfloat("bate1")  # 传输失败惩罚函数影响因子1
        self.bate2 = config["learn"].getfloat("bate2")  # 传输失败惩罚函数影响因子2

        self.reward_alpha = config["learn"].getfloat("reward_alpha")
        self.reward_bate = config["learn"].getfloat("reward_bate")
        self.alpha = config["learn"].getfloat("learning_rate")  # 学习率，用于更新Q_table的值
        self.la = config["learn"].getfloat("la")
        self.suc_tran_prob = config["learn"].getfloat("suc_tran_prob")  # 数据传输成功的概率
        self.q_table = pd.DataFrame(np.zeros((1, 1)), index=[node_id], columns=[self.node_id], dtype=np.float64)

    # 向距离d的节点发送data bit数据所消耗的能量
    def send_energy(self, data, d):
        # data / self.send_rate
        consume_energy = data / self.send_rate * self.send_power * pow(d * 1e-3, 1.5) * pow(1.3143, d * 1e-3)
        self.energy -= consume_energy
        # self.update_reward()
        # if self.energy <= 0:
        #     self.state = 0
        #     consume_energy = -1
        return consume_energy

    def send_energy_suc(self, data, d, node, package_id):
        self.send_energy(data, d)
        node.storage.append(package_id)

    # 接收data bit数据所消耗的能量
    def receive_energy(self, data):
        consume_energy = data * self.e_elec
        self.energy -= consume_energy
        # self.update_reward()
        # if self.energy <= 0:
        #     self.state = 0
        #     consume_energy = -1
        return consume_energy

    # 融合data bit数据所消耗的能量
    def integrate_energy(self, data):
        consume_energy = data * self.eda
        self.energy -= consume_energy
        # self.update_reward()
        # if self.energy <= 0:
        #     self.state = 0
        #     consume_energy = -1
        return consume_energy

    def find_alive_neighbor(self):
        for neighbor in self.neighbors:
            if neighbor.state == 1:
                self.check_neighbor_qtable(neighbor)

    def check_neighbor_qtable(self, neighbor):
        if neighbor.node_id not in self.q_table.columns:
            self.q_table[neighbor.node_id] = 0
        if self.node_id in self.q_table.columns:
            self.q_table.pop(self.node_id)

    # def update_reward(self):
    #     self.reward = self.reward_alpha * (
    #             1 - self.d_sink / self.max_d_sink) + self.reward_bate * self.energy / self.e_ini

import time
from configparser import ConfigParser

import Tool
from Net import NetWork
import Net

config = ConfigParser()
config.read("enviro.ini", encoding="utf-8")


def v_list_ave():
    v_list = []
    for i in range(0, net.round_first_dead):
        count = 0
        v = 0
        for node in net.nodes[1:]:
            if len(node.v_list) > i:
                count += 1
                v += node.v_list[i]
        v_list.append(v / count)
    Tool.show_v_ave_change(v_list)


if __name__ == '__main__':
    net = NetWork()
    net.init_node()
    # for node in net.nodes:
    #     print(node.node_id, node.node_x, node.node_y, node.node_z)
    Tool.show_image(net.nodes_map)
    net.find_neighbor()
    net.transmission(config["net"].getint("trans_round"))
    Tool.show_image(net.nodes_map)
    Tool.all_node_energy_image()
    print(net.miss_package)
    print("Package Rate: ", (net.all_package - net.miss_package) / net.all_package)

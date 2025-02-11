import node
import sys
import tkinter as tk
from tkinter import filedialog
import os

def read_txt_centerline(nodes_centerline,filepath):
    if not os.path.isfile(filepath):
            print(f"Error: '{filepath}' does not exist.")
            sys.exit()
    with open(filepath, 'r') as file:
        lines = file.readlines()
    index = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'): 
            parts = line.split() 
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2]) 
            node_centerline = node.NodeCenterline(index, x, y, z)
            nodes_centerline.append(node_centerline)
            index += 1
    print(f"info_myio  : centerline nodes count is {len(nodes_centerline.nodes_centerline)}")
    print("info_myio  : please ignore. centerline_node_sample =  ",nodes_centerline.nodes_centerline[6])

def read_txt_edgeradii(filepath):
    if not os.path.isfile(filepath):
            print(f"Error: '{filepath}' does not exist.")
            sys.exit()
    edgeradii = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            edgeradii.append(float(line))
    print(f"info_myio    : num of edges is {len(edgeradii)}")
    return edgeradii

def read_msh_tetra():
    filepath = os.path.join("output", "bgm.msh")
    if not os.path.isfile(filepath):
        print(f"Error: '{filepath}' does not exist.")
        sys.exit()
    tetra_list = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 9 and columns[1] == '4':
                tetra = [int(columns[i]) for i in range(5, 9)]
                tetra_list.append(tetra)
    print("info_myio    : num of tetra is",len(tetra_list))
    return tetra_list

def write_pos_bgm(tetra_list,nodeany_dict):
    filepath = os.path.join("output", "bgm.pos")
    with open(filepath, 'w') as f:
        f.write('View "background mesh" {\n')
        coords_list=[]
        scalars_list=[]
        for tetra in tetra_list:
            coords=[]
            scalars=[]
            for i in range(len(tetra)):
                coords.append(nodeany_dict[tetra[i]].x)
                coords.append(nodeany_dict[tetra[i]].y)
                coords.append(nodeany_dict[tetra[i]].z)
                scalars.append(nodeany_dict[tetra[i]].scalar_forbgm)
            coords_list.append(coords)
            scalars_list.append(scalars)
        for i in range(len(tetra_list)):
            c = coords_list[i]
            s = scalars_list[i]
            f.write(f"SS({c[0]},{c[1]},{c[2]},{c[3]},{c[4]},{c[5]},{c[6]},{c[7]},{c[8]},{c[9]},{c[10]},{c[11]})"
                    f"{{{s[0]:.2f},{s[1]:.2f},{s[2]:.2f},{s[3]:.2f}}};\n")
        f.write('};')

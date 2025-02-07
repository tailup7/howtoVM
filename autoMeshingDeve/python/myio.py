import node
import sys
import tkinter as tk
from tkinter import filedialog

def read_txt_centerline(nodes_centerline):
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        title="Select centerline data (*.txt)", 
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        print("No file selected. Exiting program.")
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

def read_txt_edgeradii():
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        title=" Select targetRadius data (*.txt)", 
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        print("No file selected. Exiting program.")
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
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        title="Select tetra mesh data (*.msh)", 
        filetypes=[("Mesh Files", "*.msh"), ("All Files", "*.*")]
    )
    if not filepath:
        print("No file selected. Exiting program.")
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

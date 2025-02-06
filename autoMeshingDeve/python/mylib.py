import gmsh
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

class IO:
    # 半径情報を作成するためのSTLファイルを選択
    def selectFile_stl_target():
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Select target surface data to make radius data(*.stl)", 
            filetypes=[("STL Files", "*.stl"), ("All Files", "*.*")]
        )
        if not filepath:
            print("No file selected. Exiting program.")
            sys.exit()
        return filepath

    # STLファイルを選択
    def selectFile_stl_before():
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Select original surface data (*.stl)", 
            filetypes=[("STL Files", "*.stl"), ("All Files", "*.*")]
        )
        if not filepath:
            print("No file selected. Exiting program.")
            sys.exit()
        return filepath

    '''
    中心線点群.txtを読み込む。
    [id, x座標, y座標, z座標] のリストを返す。
    '''
    @staticmethod
    def read_txt_centerline():
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Select centerline data (*.txt)", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            print("No file selected. Exiting program.")
            sys.exit()
        centerlineNodes = []  
        with open(filepath, 'r') as file:
            lines = file.readlines()
        index = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'): 
                parts = line.split() 
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2]) 
                centerlineNodes.append([index, x, y, z])
                index += 1
        print(f"mylib_info  : centerline nodes count is {len(centerlineNodes)}")
        return centerlineNodes



    # 変形させたい形状の中心線ファイルを選択
    def selectFile_centerline_before():
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Select original centerline data (*.txt)", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            print("No file selected. Exiting program.")
            sys.exit()
        return filepath

    # 半径情報ファイルを選択
    def selectFile_radius():
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title=" Select targetRadius data (*.txt)", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            print("No file selected. Exiting program.")
            sys.exit()
        return filepath

class math:
    # 表面Nodeを中心線Edgeへ射影する。どのEdgeにも収まらない場合はNoneを返し、対応するEdgeがあるときはEdgeまでの距離と垂線の足の座標を返す。
    def surfaceNode_to_Edge(P, A, B): # P : 表面Node    A, B : 中心線Node
        AB = np.array([B[1] - A[1], B[2] - A[2], B[3] - A[3]]) 
        AP = np.array([P[1] - A[1], P[2] - A[2], P[3] - A[3]]) 
        AB_square = np.dot(AB, AB)

        # AP の ABへの射影
        t = np.dot(AP, AB) / AB_square

        if t<0 or t>1:
            return None
    
        H = np.array([A[1], A[2], A[3]]) + t * AB
        P_vector = np.array([P[1],P[2],P[3]]) 

        return np.linalg.norm(P_vector - H) , H 

class PostProcessGmsh:
    @staticmethod
    def coords_to_nodes(coord):
        node=[]
        nodes=[]
        if len(coord)%3!=0:
            print("mylib_info   : error. 座標成分の総数が3の倍数になりません")
            sys.exit()
        else:
            for i in range(len(coord)):
                if i%3==0:
                    node.append(i%3)
                    node.append(float(coord[i]))
                elif (i+1)%3==0:
                    node.append(float(coord[i]))
                    nodes.append(node)
                    node=[]
                else:
                    node.append(float(coord[i]))
        print(f"mylib_info   : node count after postprocess gmsh is {len(nodes)}")
        return nodes


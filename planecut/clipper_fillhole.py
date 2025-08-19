import vtk
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

# 埋めたい穴の直径より少し大きい数値を設定
hole_radius = 10

class Node:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Triangle:
    def __init__(self, id, node0, node1, node2, normal):
        self.id=id
        self.node0   = node0
        self.node1   = node1
        self.node2   = node2
        self.normal  = normal

    def calc_centroid(self, node0, node1, node2):
        self.centroid = np.array([ (node0.x + node1.x + node2.x)/3, 
                                    (node0.y + node1.y + node2.y)/3,
                                    (node0.z + node1.z + node2.z)/3 ]) 

def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw() 
    filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return filepath

def read_csv_centerline(filepath):
    df = pd.read_csv(filepath)
    centerlineNodes = []
    for _, row in df.iterrows():
        x, y, z = float(row['x']), float(row['y']), float(row['z'])
        centerlineNodes.append([x, y, z])
    return centerlineNodes

def clip_mesh(reader_or_filter, originPoint, vector, inside_out=True):
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(reader_or_filter.GetOutputPort())
    plane = vtk.vtkPlane()
    plane.SetOrigin(originPoint)
    plane.SetNormal(vector)
    if inside_out:
        clipper.InsideOutOn()
    else:
        clipper.InsideOutOff()
    clipper.SetClipFunction(plane)
    clipper.Update()
    return clipper

def clipper(hole_radius):
    csv_path = select_file("中心線CSVファイルを選択", [("CSV files", "*.csv")])
    centerlineNodes = read_csv_centerline(csv_path)
    stl_path = select_file("STLファイルを選択", [("STL files", "*.stl")])
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stl_path)
    reader.Update()

    # メッシュのクリッピング（始点側）
    originPoint = centerlineNodes[0]
    originPoint_pre = centerlineNodes[1]
    normal = [originPoint[i] - originPoint_pre[i] for i in range(3)]
    firstClip = clip_mesh(reader, originPoint, normal, inside_out=True)

    # メッシュのクリッピング（終点側）
    originPoint = centerlineNodes[-1]
    originPoint_pre = centerlineNodes[-2]
    normal = [originPoint[i] - originPoint_pre[i] for i in range(3)]
    secondClip = clip_mesh(firstClip, originPoint, normal, inside_out=True)

    # smoothing
    smooth_filter = vtk.vtkSmoothPolyDataFilter()
    smooth_filter.SetInputConnection(secondClip.GetOutputPort())
    smooth_filter.SetNumberOfIterations(50)
    smooth_filter.Update()

    # fill hole（端面を閉じる）
    fill_filter = vtk.vtkFillHolesFilter()
    fill_filter.SetInputConnection(smooth_filter.GetOutputPort())
    fill_filter.SetHoleSize(hole_radius)  # 穴の最大サイズ（大きめにしてすべて塞ぐ）
    fill_filter.Update()

    # output
    writer = vtk.vtkSTLWriter()
    writer.SetFileName('WALL_cut_filled.stl')
    writer.SetInputConnection(fill_filter.GetOutputPort())
    writer.Write()
    print("WALL_cut_filled.stl を出力しました。")
    filepath = "WALL_cut_filled.stl"
    return filepath, centerlineNodes

def parse_ascii_stl(filepath):
    triangles = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    i = 0
    tri_id = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("facet normal"):
            parts = line.split()
            normal = np.array([float(parts[2]), float(parts[3]), float(parts[4])])
            i += 2 
            v0 = list(map(float, lines[i].strip().split()[1:]))
            v1 = list(map(float, lines[i+1].strip().split()[1:]))
            v2 = list(map(float, lines[i+2].strip().split()[1:]))
            node0 = Node(*v0)
            node1 = Node(*v1)
            node2 = Node(*v2)
            triangle = Triangle(tri_id, node0, node1, node2, normal)
            triangle.calc_centroid(node0, node1, node2)
            triangles.append(triangle)
            tri_id += 1
            i += 5  
        else:
            i += 1
    return triangles

def find_triangles_around_inlet(
        *,
        hole_radius : float, 
        triangles   : list[Triangle], 
        inlet       : np.ndarray,
        ) -> list[Triangle]:
    count_inlet=0
    for triangle in triangles:
        distance_from_inlet = np.linalg.norm(triangle.centroid - inlet)
        if distance_from_inlet <= hole_radius :
            outer_vector = np.array(centerlineNodes[0]) - np.array(centerlineNodes[1])
            outer_vector = outer_vector / np.linalg.norm(outer_vector)
            cos_theta = np.dot(triangle.normal, outer_vector)
            if cos_theta < -0.5:
                count_inlet += 1
                triangle.normal = - triangle.normal
                triangle.node1, triangle.node2 = triangle.node2, triangle.node1
    print("num of inlet faces is :", count_inlet)
    return triangles

def find_triangles_around_outlet(
        *,
        hole_radius : float, 
        triangles   : list[Triangle], 
        outlet       : np.ndarray,
        ) -> list[Triangle]:
    count_outlet=0
    for triangle in triangles:
        distance_from_outlet = np.linalg.norm(triangle.centroid - outlet)
        if distance_from_outlet <= hole_radius :
            outer_vector = np.array(centerlineNodes[-1]) - np.array(centerlineNodes[-2])
            outer_vector = outer_vector / np.linalg.norm(outer_vector)
            cos_theta = np.dot(triangle.normal, outer_vector)
            if cos_theta < -0.5:
                count_outlet += 1
                triangle.normal = - triangle.normal
                triangle.node1, triangle.node2 = triangle.node2, triangle.node1
    print("num of outlet faces is :", count_outlet)
    return triangles

def write_ascii_stl(triangles: list, filename: str, solid_name: str = "output") -> None:
    with open(filename, 'w') as f:
        f.write(f"solid {solid_name}\n")
        for tri in triangles:
            n = tri.normal
            v0 = tri.node0
            v1 = tri.node1
            v2 = tri.node2
            f.write(f" facet normal {n[0]} {n[1]} {n[2]}\n")
            f.write("  outer loop\n")
            f.write(f"   vertex {v0.x} {v0.y} {v0.z}\n")
            f.write(f"   vertex {v1.x} {v1.y} {v1.z}\n")
            f.write(f"   vertex {v2.x} {v2.y} {v2.z}\n")
            f.write("  endloop\n")
            f.write(" endfacet\n")
        f.write(f"endsolid {solid_name}\n")


if __name__ == "__main__":
    filepath,centerlineNodes = clipper(hole_radius)
    triangles = parse_ascii_stl(filepath)
    print(len(triangles))
    inlet  = np.array([centerlineNodes[0]])
    outlet = np.array([centerlineNodes[-1]])

    triangles = find_triangles_around_inlet(
        hole_radius = hole_radius,
        triangles = triangles,
        inlet = inlet
    )
    triangles = find_triangles_around_outlet(
        hole_radius = hole_radius,
        triangles = triangles,
        outlet = outlet
    )

    write_ascii_stl(
        triangles = triangles,
        filename  = "wall_cut_filled_reversed.stl",
        solid_name = "output"
    )
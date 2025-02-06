import gmsh
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import node 
import myio
import mylib
import utility

gmsh.initialize(sys.argv)
meshSize = 0.5 
# GmshのGUIの設定
# 1がON/0がOFF
# 2次元メッシュの可視化ON/OFF
gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
# ?
gmsh.option.setNumber("Mesh.Lines", 1)
# 0次元のEntityの可視化ON?OFF
gmsh.option.setNumber("Geometry.PointLabels", 1)
# メッシュの線の太さを指定
gmsh.option.setNumber("Mesh.LineWidth", 4)
# gmshではマウスのホイールのズーンオン/ズームオフがparaviewとは逆なので、paraviewと一緒にする
gmsh.option.setNumber("General.MouseInvertZoom", 1)
# モデルのサイズが簡単に確認できるように、モデルを囲む直方体メモリを表示
gmsh.option.setNumber("General.Axes", 3)
# ?
gmsh.option.setNumber("General.Trackball", 0)
# GUIが表示された時の、目線の方向を(0,0,0)に指定
gmsh.option.setNumber("General.RotationX", 0)
gmsh.option.setNumber("General.RotationY", 0)
gmsh.option.setNumber("General.RotationZ", 0)
# gmshのターミナルに情報を表示
gmsh.option.setNumber("General.Terminal", 1)

# ディレクトリやファイルのパスのOSごとの差を吸収
path = os.path.dirname(os.path.abspath(__file__))
# stlの読み込み
gmsh.merge(os.path.join(path, "WALL.stl"))    ##################################################################
# 読み込んだ形状を設定した角度で分解
# forReparametrizationをTrueにしないとメッシングで時間がかかる
gmsh.model.mesh.classifySurfaces(angle = 40 * np.pi / 180, boundary=True, forReparametrization=True)
# classifySurfacesとセットで用いる
gmsh.model.mesh.createGeometry()
gmsh.model.geo.synchronize()
# メッシュオプション
gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)
gmsh.option.setNumber("Mesh.OptimizeThreshold", 0.9)
gmsh.option.setNumber('Mesh.Algorithm', 1)
gmsh.option.setNumber("Mesh.MeshSizeMin", meshSize)
gmsh.option.setNumber("Mesh.MeshSizeMax", meshSize)
wall = gmsh.model.getEntities(2)
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
wall_id = [e[1] for e in wall]
print("wall=",wall)
print("wall_id=",wall_id)

boundary_curv = gmsh.model.getBoundary(wall)
print("boundary_curv=",boundary_curv)
boundary_curv_id = [e[1] for e in boundary_curv]
print("boundary_curv_id=",boundary_curv_id)

boundary_curv_id_list = gmsh.model.geo.addCurveLoops(boundary_curv_id)
print("boundary_curv_id_list=",boundary_curv_id_list)

eachClosedSurface=[]
boundary_surface=[]
for i in boundary_curv_id_list:
    eachClosedSurface=[]
    eachClosedSurface.append(i)
    a=gmsh.model.geo.addPlaneSurface(eachClosedSurface)
    print("a=",a)

gmsh.model.geo.synchronize()  # これを使うことで、a(つまり[2,10]) が追加される
check = gmsh.model.getEntities(2)
print(check)
surfaceAll_id = [e[1] for e in check]
print("surfaceAll_id=",surfaceAll_id)
surfaceLoop=gmsh.model.geo.addSurfaceLoop(surfaceAll_id)
gmsh.model.geo.synchronize()
gmsh.model.geo.addVolume([surfaceLoop])
gmsh.model.geo.synchronize()  ## ここにこれを入れないと、print(len(nodes))が、表面Nodeのときに出力したprint(len(nodes))と同じ値になってしまう。
gmsh.model.mesh.generate(3)  ###  しかし、generate(3)は、synchronize() しなくても、正常に処理される
#gmsh.model.geo.synchronize()
nodes, coords, _ = gmsh.model.mesh.getNodes()
gmsh.write("tetraMeshOriginal.vtk")
gmsh.write("tetraMeshOriginal.stl")
gmsh.write("tetraMeshOriginal.msh")


###################################################################################################################################################################
nodes_centerline = node.NodesCenterline()
myio.read_txt_centerline(nodes_centerline)
nodes_any = node.NodesAny()
utility.PostProcessGmsh.coords_to_nodes(coords,nodes_any)
print("info_main    : please ignore. nodes_any sample =",nodes_any.nodes_any[2])
print("info_main    : please ignore. nodes_any sample x =", nodes_any.nodes_any[2].x)
for node_any in nodes_any.nodes_any:
    node_any.append_correspondcenterlinenodeid(nodes_centerline.nodes_centerline)
print("info_main    : please ignore. node_any sample correspond centerline id is ",nodes_any.nodes_any[2].correspond_centerlinenode_id)
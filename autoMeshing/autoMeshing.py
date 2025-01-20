import gmsh
import math
import os
import sys
import numpy as np
import tkinter as tk
from tkinter import filedialog

gmsh.initialize(sys.argv)
# ===========================================================================================================
# Gmshを利用し、任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するpythonコード
# 入力STLは端面が開放されているものを前提にしている
# 形状はメッシングに際して領域分けが必要ないもの、つまり極端に細くなったり太くなったりする部分がないものを前提としている
# ===========================================================================================================

# **********************************************************************************************************
# パラメータ。書き換えるのはここだけ。
meshSize = 0.5 # mesh size (Gmshに単位は無いので、STLの座標スケールから適切に設定する)
N = 6          # 境界層の層数
r = 1.2        # 境界層の厚みの増加率
h = 0.05       # 境界層の最初の層(一番外側)の厚さ

# 流入面と流出面の大体の中心座標 (中心線情報があれば、その始点・終点の座標を使うのがシンプル)。INLET及びOUTLETを割り当てるときに参照する。
inletSurface_center  = np.array([ 111.748276, 251.652390, 204.930370 ])   
outletSurface_center = np.array([ 108.240890, 288.927400, 110.285000 ])

# 流入面や流出面の半径程度に設定。流入面(流出面)の重心からこの距離以内に重心がある2次元エンティティは、流入面(流出面)とみなしてINLET(OUTLET)とする。
judgeDistance = 4.0   
# **********************************************************************************************************

# ===============================================
# グローバル変数
surface_real_wall = []
surface_fake_wall = []
surface_inlet_outlet = []
inletList  = []
outletList = []
# ===============================================

# ===============================================
# gmshのGUIの表示の設定
def OptionSetting():
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
# ===============================================


# ===============================================
# stlの読み込み
def ImportStl():
    root = tk.Tk()
    root.withdraw() 
    filepath = filedialog.askopenfilename(title="Select an STL file", filetypes=[("STL Files", "*.stl")])
    if not filepath:
        print("STL file was not selected.")
        sys.exit()
    # stlの読み込み
    gmsh.merge(filepath)

    # 読み込んだ形状を設定した角度で分解
    # forReparametrizationをTrueにしないとメッシングで時間がかかる
    # 法線ベクトル同士のなす角が40°を超える三角形パッチは別の面とみなす
    gmsh.model.mesh.classifySurfaces(angle = 40 * math.pi / 180, boundary=True, forReparametrization=True)
    # classifySurfacesとセットで用いる
    gmsh.model.mesh.createGeometry()

    # gmsh.model.mesh.createTopology()

    s_first = gmsh.model.getEntities(2)
    for i in range(len(s_first)):
        surface_real_wall.append(s_first[i][1])

    Syncronize()
    return filepath
# ===============================================


# ===============================================
# 境界層の作成や、境界層より内側のテトラメッシュを領域に対してVolumeを設定するなどの形状作成
def ShapeCreation():
    gmsh.option.setNumber("Geometry.ExtrudeReturnLateralEntities", 0)

    # 注意
    # 境界層の厚さが一枚ごとの厚さではなく、基準線からの距離
    # なので、t[i] += t[i - 1]で、その層以下の総和をしている
    n = np.linspace(1, 1, N) # [1, 1, 1, 1, 1]
    t = np.full(N, h) # distance from the reference line
    for i in range(0, N):
        t[i] = t[i] * r ** i
    for i in range(1, N):
        t[i] += t[i - 1]

    # 境界層の作成
    # -tに注意
    # tにすると表面の外側に境界層が張られる
    e = gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), n, -t, True)

    # 境界層を作成したときに積層された中で最も最後に積層された層の表面を取得
    top_ent = [s for s in e if s[0] == 2]
    for t in top_ent:
        surface_fake_wall.append(t[1])
    Syncronize()

    bnd_ent = gmsh.model.getBoundary(top_ent)
    bnd_curv = [c[1] for c in bnd_ent]


    # 流出入部の断面の内側の、閉曲面の輪郭を定義
    closedSurfaceInletOutletInside = gmsh.model.geo.addCurveLoops(bnd_curv)
    print("closedSurfaceInletOutletInside = ", closedSurfaceInletOutletInside)
    for i in closedSurfaceInletOutletInside:
        # 上記で作成された輪郭に閉曲面を張る
        eachClosedSurface = gmsh.model.geo.addPlaneSurface([i])

        surface_fake_wall.append(eachClosedSurface)
        surface_inlet_outlet.append(eachClosedSurface)

    # surface_fake_wallはテトラメッシュを作成する領域を囲む表面(2次元Entity)の集合
    innerSurfaceLoop = gmsh.model.geo.addSurfaceLoop(surface_fake_wall)
    # 上記で作った領域に、実際の体積を割り当て
    gmsh.model.geo.addVolume([innerSurfaceLoop])
    Syncronize()
    #===============================================================
    # エンティティを知りたいとき使えるかも。
    # gmsh.model.geo.synchronize()
    # entities = gmsh.model.getEntities()
    # gmsh.option.setNumber("Geometry.PointLabels", 1)   # 点ラベルを有効化
    # gmsh.option.setNumber("Geometry.CurveLabels", 1)   # 線ラベル
    # gmsh.option.setNumber("Geometry.SurfaceLabels", 1) # 面ラベル
    # gmsh.option.setNumber("Geometry.VolumeLabels", 1)  # 体積ラベル
    # gmsh.fltk.run()
    # sys.exit()
    #================================================================
# ===============================================

# ===============================================
# メッシュ作成
def Meshing():
    gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)
    # メッシュ最適化の閾値を設定
    # 0が最適化なし
    # 1が最適化最大
    gmsh.option.setNumber("Mesh.OptimizeThreshold", 0.9)
    # メッシュのアルゴリズムを設定
    gmsh.option.setNumber('Mesh.Algorithm', 1)
    # 最適化を何回繰り返すか->なぜか品質わるくなる
    # gmsh.option.setNumber("Mesh.Optimize", 10)
    # 全体的なメッシュの制御
    # MinとMaxではさむ
    # 基本的にMaxを基準に切られる
    # Minは意味ないかも
    gmsh.option.setNumber("Mesh.MeshSizeMin", meshSize)
    gmsh.option.setNumber("Mesh.MeshSizeMax", meshSize)
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.optimize()
    print("finish meshing")
# ===============================================

# ===============================================
# OpenFOAMで境界条件を設定するために、モデルの面や壁に体積に名前をつける
def NamingBoundary():
    s_second = gmsh.model.getEntities(2)
    surfaceAll = []
    for i in range(len(s_second)):
        surfaceAll.append(s_second[i][1])
    surface_another = list(set(surfaceAll) - set(surface_real_wall) - set(surface_inlet_outlet))
    print(surface_another)
    # python set 対称差
    something = list(set(surface_another) ^ set(surface_fake_wall))
    print("something=",something)

    # 引数1:「2」次元エンティティを対象にする  引数2: 「2」次元エンティティの「ID」 引数3: True
    # 返値1: そのエンティティに属する全NodeのID 返値2: そのエンティティに属する全Nodeの座標 返値3: ? 
    node_tags, node_coords, number_of_nodes = gmsh.model.mesh.getNodes(2,something[0],True)

    for i in range(len(something)):
        node_tags, node_coords, number_of_nodes = gmsh.model.mesh.getNodes(2,something[i],True)
        center_x = 0.0
        center_y = 0.0
        center_z = 0.0
        for j in range(len(node_coords)):
            if j%3==0:
                center_x+=node_coords[j]
            elif j%3==1:
                center_y+=node_coords[j]
            else:
                center_z+=node_coords[j]
        center_x=float(center_x/len(node_tags))
        center_y=float(center_y/len(node_tags))
        center_z=float(center_z/len(node_tags))
        center=[center_x,center_y,center_z]
        distance_fromInlet = np.linalg.norm(inletSurface_center-np.array(center))
        distance_fromOutlet = np.linalg.norm(outletSurface_center-np.array(center))
        if distance_fromInlet < judgeDistance:
            inletList.append(something[i])
        if distance_fromOutlet < judgeDistance:
            outletList.append(something[i])
    print("INLET entities are ",inletList)
    print("OUTLET entities are ",outletList)
    if inletList == []:
        print("please set inletSurface_center correctly.")
        sys.exit()
    if outletList == []:
        print("please set outletSurface_center correctly.")
        sys.exit()

    gmsh.model.addPhysicalGroup(2, inletList, 20)
    gmsh.model.setPhysicalName(2, 20, "INLET")

    gmsh.model.addPhysicalGroup(2, outletList, 30)
    gmsh.model.setPhysicalName(2, 30, "OUTLET")

    wall = surface_real_wall
    gmsh.model.addPhysicalGroup(2, wall, 10)
    gmsh.model.setPhysicalName(2, 10, "WALL")

    volumeAll = gmsh.model.getEntities(3)
    three_dimension_list = []
    for i in range(len(volumeAll)):
        three_dimension_list.append(volumeAll[i][1])
    gmsh.model.addPhysicalGroup(3, three_dimension_list, 100)
    gmsh.model.setPhysicalName(3, 100, "INTERNAL")

    Syncronize()
# ===============================================

# ===============================================
# 完成したメッシュをGUIで確認するため
# 性能が低いPCで大規模なメッシュを可視化しようとすると重くなるか、最悪クラッシュする
def ConfirmMesh():
    if "-nopopup" not in sys.argv:
        gmsh.fltk.run()
# ===============================================


# ===============================================
# ファイル出力
# write("~~~~.拡張子")
# 拡張子によって、その拡張子用にメッシュが出力される
# OpenFOAMに用いるのは.mshファイル
# .mshをOpneFOAMで用いるには、.mshのファイルフォーマットバージョンを2.2にする必要がある
# paraviewで見るように.vtkファイルも出力
def OutputMshVtk(filepath):
    filename_withoutExt = os.path.splitext(os.path.basename(filepath))[0]
    msh_filename = f"{filename_withoutExt}_gmsh.msh"
    vtk_filename = f"{filename_withoutExt}_gmsh.vtk"
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(msh_filename)
    gmsh.write(vtk_filename)
# ===============================================

# ===============================================
# 定義した形状などをgmshの形状カーネル？に反映
# 何度も使うので関数化
def Syncronize():
    gmsh.model.geo.synchronize()
# ===============================================

OptionSetting()
filepath = ImportStl()
ShapeCreation()
Meshing()
NamingBoundary()
OutputMshVtk(filepath)
ConfirmMesh()
gmsh.finalize()

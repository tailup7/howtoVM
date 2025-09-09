import os
import sys
import numpy as np
import tkinter as tk
from tkinter import filedialog
import gmsh
import vtk

# ===========================================================================================================
# Gmshを利用し、任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するpythonコード
# 入力STLは端面が開放されているものを前提にしている
# 形状はメッシングに際して領域分けが必要ないもの、つまり極端に細くなったり太くなったりする部分がないものを前提としている
# z座標が大きい(上側にある)面がINLET, 小さい(下側にある)面がOUTLETになる。(コード実行中に逆にできる)
# ===========================================================================================================

# *************************************************************************************
# パラメータ。書き換えるのはここだけ。
meshSize = 0.5 # mesh size (Gmshに単位は無いので、STLの座標スケールから適切に設定する)
N = 6          # 境界層の層数
r = 1.2        # 境界層の厚みの増加率
h = 0.05       # 境界層の最初の層(一番外側)の厚さ
# *************************************************************************************

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
    gmsh.option.setNumber("Mesh.LineWidth", 3)
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

def GetSTLfilepath():
    root = tk.Tk()
    root.withdraw() 
    filepath = filedialog.askopenfilename(title="Select an STL file", filetypes=[("STL Files", "*.stl")])
    if not filepath:
        print("STL file was not selected.")
        sys.exit()
    return filepath

# ===============================================
# stlの読み込み
def ImportStl(filepath):
    # stlの読み込み
    gmsh.merge(filepath)

    # 読み込んだ形状を設定した角度で分解
    # forReparametrizationをTrueにしないとメッシングで時間がかかる
    # 法線ベクトル同士のなす角が40°を超える三角形パッチは別の面とみなす
    gmsh.model.mesh.classifySurfaces(angle = 40 * np.pi / 180, boundary=True, forReparametrization=True)
    # classifySurfacesとセットで用いる
    gmsh.model.mesh.createGeometry()

    # gmsh.model.mesh.createTopology()

    s_first = gmsh.model.getEntities(2)
    for i in range(len(s_first)):
        surface_real_wall.append(s_first[i][1])

    Syncronize()
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


# INLET と OUTLET の Naming を逆にしたいか聞く ==================================================
def askRename(inletSurface_center, outletSurface_center):
    print(f"Now, INLET  surface position is around {inletSurface_center}, \n")
    print(f"     OUTLET surface position is around {outletSurface_center}")
    ans = input("Do you want to reverse INLET OUTLET？ [y/n]: ").strip().lower()
    wantToReverse = ans in ("y", "yes")
    return wantToReverse
# ============================================================================================


# ===============================================
# OpenFOAMで境界条件を設定するために、モデルの面や壁に体積に名前をつける
def NamingBoundary(inletSurface_center, judgeDistance_inlet, outletSurface_center, judgeDistance_outlet):
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
        distance_fromInlet = np.linalg.norm(inletSurface_center - np.array(center))
        distance_fromOutlet = np.linalg.norm(outletSurface_center - np.array(center))
        if distance_fromInlet < judgeDistance_inlet:
            inletList.append(something[i])
        if distance_fromOutlet < judgeDistance_outlet:
            outletList.append(something[i])
    print("INLET entities are ",inletList)
    print("OUTLET entities are ",outletList)
    if inletList == []:
        print("please set inletSurface_center correctly.")
        sys.exit()
    if outletList == []:
        print("please set outletSurface_center correctly.")
        sys.exit()

    ToF = askRename(inletSurface_center, outletSurface_center)
    if ToF == False:
        gmsh.model.addPhysicalGroup(2, inletList, 20)
        gmsh.model.setPhysicalName(2, 20, "INLET")
        gmsh.model.addPhysicalGroup(2, outletList, 30)
        gmsh.model.setPhysicalName(2, 30, "OUTLET")
    elif ToF == True:
        gmsh.model.addPhysicalGroup(2, outletList, 20)
        gmsh.model.setPhysicalName(2, 20, "INLET")
        gmsh.model.addPhysicalGroup(2, inletList, 30)
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
def VisualizeMesh():
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

# ===================================================================================================
# vtkを使い、穴の開いたチューブから境界線edgeを抽出し、境界面の重心座標、及び最大径を求める関数
def CalcBoundaryCentroid(filepath):
    r = vtk.vtkSTLReader()
    r.SetFileName(filepath)
    r.Update()
    cl = vtk.vtkCleanPolyData()
    cl.SetInputData(r.GetOutput())
    cl.Update()
    poly = cl.GetOutput()
    fe = vtk.vtkFeatureEdges()
    fe.SetInputData(poly)
    fe.BoundaryEdgesOn()
    fe.FeatureEdgesOff()
    fe.ManifoldEdgesOff()
    fe.NonManifoldEdgesOff()
    fe.Update()
    st = vtk.vtkStripper() 
    st.SetInputData(fe.GetOutput()) 
    st.Update()
    pd = st.GetOutput()
    lines, pts = pd.GetLines(), pd.GetPoints()
    loops = []
    if not pts or not lines: 
        return loops
    ids = vtk.vtkIdList()
    lines.InitTraversal()
    while lines.GetNextCell(ids):
        n = ids.GetNumberOfIds()
        if n < 3: continue
        NodesOnBoundaryLoop = np.array([pts.GetPoint(ids.GetId(i)) for i in range(n)], float)
        # stripperの結果が開いていることもあるので、必要なら明示的に閉じる
        if np.linalg.norm(NodesOnBoundaryLoop[0] - NodesOnBoundaryLoop[-1]) > 1e-12:  
            NodesOnBoundaryLoop = np.vstack([NodesOnBoundaryLoop, NodesOnBoundaryLoop[0]])
        loops.append(NodesOnBoundaryLoop)    # 2つある想定
    if len(loops) == 0:
        print("There is no boundary loop（Input mesh maybe closed surface）."); return
    if len(loops) >= 3:
        print("There is more than 3 boundary loops（Input mesh file maybe broken）."); return
    for i, nbl in enumerate(loops, 1):    # nbl ... NodesOnBoundaryLoop
        Q = nbl[:-1]
        ctr = Q.mean(0)
        Q0 = Q - ctr
        _,_,Vt = np.linalg.svd(Q0, full_matrices=False) 
        ux, uy = Vt[0], Vt[1]
        uv = np.c_[Q0@ux, Q0@uy]
        uv = np.vstack([uv, uv[0]])
        area = 0.0 
        acc = np.zeros(2)
        # 退化三角形を避ける
        M = len(uv)
        for j in range(1, M-2):  
            p0, p1, p2 = uv[0], uv[j], uv[j+1]
            A = 0.5 * ((p1[0]-p0[0])*(p2[1]-p0[1]) - (p2[0]-p0[0])*(p1[1]-p0[1]))
            area += A
            acc += A * (p0 + p1 + p2) / 3.0
        # 面積が小さいときは “線重心” にフォールバック
        if abs(area) < 1e-12:
            a = nbl[:-1]; b = nbl[1:]
            w = np.linalg.norm(b - a, axis=1)
            L = w.sum()
            if L < 1e-12:
                face_centroid = nbl.mean(axis=0)
            mid = 0.5 * (a + b)
            face_centroid = (mid * w[:, None]).sum(axis=0) / L
        c2 = acc / area
        face_centroid = ctr + c2[0]*ux + c2[1]*uy
        Q = nbl[:-1]
        c = np.asarray(face_centroid)  # 念のため
        d = np.linalg.norm(Q - c[None, :], axis=1)
        k = int(np.argmax(d))
        rmax = float(d[k])

        if i == 1:
            inletSurface_center = face_centroid
            judgeDistance_inlet = rmax
        else:
            outletSurface_center = face_centroid
            judgeDistance_outlet = rmax
    # z座標が上の方を端面をinletにする
    if inletSurface_center[2] >= outletSurface_center[2]:
        return inletSurface_center, judgeDistance_inlet, outletSurface_center, judgeDistance_outlet
    else:
        return outletSurface_center, judgeDistance_outlet, inletSurface_center, judgeDistance_inlet,
# ========================================================================================================


#########    main    #########
gmsh.initialize(sys.argv)
filepath = GetSTLfilepath()
ImportStl(filepath)
ShapeCreation()
Meshing()
inletSurface_center, judgeDistance_inlet, outletSurface_center, judgeDistance_outlet = CalcBoundaryCentroid(filepath)
NamingBoundary(inletSurface_center, judgeDistance_inlet, outletSurface_center, judgeDistance_outlet) 
OutputMshVtk(filepath)
OptionSetting()
VisualizeMesh()
gmsh.finalize()
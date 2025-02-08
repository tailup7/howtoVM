import gmsh
import os
import numpy as np
import sys

# generate background mesh
def generate_bgm(meshsize, filepath):
    gmsh.initialize(sys.argv)
    # ディレクトリやファイルのパスのOSごとの差を吸収
    path = os.path.dirname(os.path.abspath(__file__))
    # stlの読み込み
    gmsh.merge(os.path.join(path, filepath))    ##################################################################
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
    gmsh.option.setNumber("Mesh.MeshSizeMin", meshsize)
    gmsh.option.setNumber("Mesh.MeshSizeMax", meshsize)
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

    for i in boundary_curv_id_list:
        a=gmsh.model.geo.addPlaneSurface([i])
        print("a=",a)

    gmsh.model.geo.synchronize()  # これを使うことで、a(つまり[2,10]) が追加される
    check = gmsh.model.getEntities(2)
    print(check)
    surfaceAll_id = [e[1] for e in check]
    print("surfaceAll_id=",surfaceAll_id)
    surfaceLoop=gmsh.model.geo.addSurfaceLoop(surfaceAll_id)
    gmsh.model.geo.addVolume([surfaceLoop])
    gmsh.model.geo.synchronize()  ## ここにこれを入れないと、print(len(nodes))が、表面Nodeのときに出力したprint(len(nodes))と同じ値になってしまう。
    gmsh.model.mesh.generate(3)  ###  しかし、generate(3)は、synchronize() しなくても、正常に処理される
    #gmsh.model.geo.synchronize()
    nodeids, coords, _ = gmsh.model.mesh.getNodes()
    gmsh.write("bgm.vtk")
    gmsh.write("bgm.stl")
    gmsh.write("bgm.msh")

    gmsh.finalize()

    return nodeids, coords

def tetraprism_mutable(filepath):
    gmsh.initialize()
    path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join(path, filepath))

    # 読み込んだ形状を設定した角度で分解
    # forReparametrizationをTrueにしないとメッシングで時間がかかる
    gmsh.model.mesh.classifySurfaces(angle = 40 * np.pi / 180, boundary=True, forReparametrization=True)
    # classifySurfacesとセットで用いる
    gmsh.model.mesh.createGeometry()

    gmsh.model.geo.synchronize()
    check = gmsh.model.getEntities(2)
    surfaceAll_id = [e[1] for e in check]
    print("surfaceAll_id =", surfaceAll_id)
    surfaceLoop=gmsh.model.geo.addSurfaceLoop(surfaceAll_id)
    gmsh.model.geo.addVolume([surfaceLoop])
    gmsh.model.geo.synchronize()

    gmsh.merge(os.path.join(path,'bgm.pos'))  ## 一瞬消す
    bg_field = gmsh.model.mesh.field.add("PostView")     ###  **** 1   ###########一瞬消す
    gmsh.model.mesh.field.setNumber(bg_field, "ViewIndex", 0) ###### *** 2      ###########一瞬消す
    gmsh.model.mesh.field.setAsBackgroundMesh(bg_field) ######## **** 3       ###########一瞬消す
    # Apply the view as the current background mesh size field:

    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber('Mesh.Algorithm', 1)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)       ###  ***** 4
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)     ###  ***** 5
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0) 
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    # gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)

    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.optimize()
    gmsh.write("tetraprism_mutable.msh")
    gmsh.write("tetraprism_mutable.vtk")
    gmsh.write("tetraprism_mutable.stl")

    GUI_setting()
    gmsh.fltk.run()
    
    gmsh.finalize()

def GUI_setting():
    # 1がON/0がOFF
    # 2次元メッシュの可視化ON/OFF
    gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
    
    gmsh.option.setNumber("Mesh.Lines", 1)
    # 0次元のEntityの可視化ON?OFF
    gmsh.option.setNumber("Geometry.PointLabels", 1)
    # メッシュの線の太さを指定
    gmsh.option.setNumber("Mesh.LineWidth", 4)
    # gmshではマウスのホイールのズーンオン/ズームオフがparaviewとは逆なので、paraviewと一緒にする
    gmsh.option.setNumber("General.MouseInvertZoom", 1)
    # モデルのサイズが簡単に確認できるように、モデルを囲む直方体メモリを表示
    gmsh.option.setNumber("General.Axes", 3)
    
    gmsh.option.setNumber("General.Trackball", 0)
    # GUIが表示された時の、目線の方向を(0,0,0)に指定
    gmsh.option.setNumber("General.RotationX", 0)
    gmsh.option.setNumber("General.RotationY", 0)
    gmsh.option.setNumber("General.RotationZ", 0)
    # gmshのターミナルに情報を表示
    gmsh.option.setNumber("General.Terminal", 1)
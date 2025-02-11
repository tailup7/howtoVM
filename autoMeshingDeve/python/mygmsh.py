import gmsh
import os
import numpy as np
import sys

# generate background mesh
def generate_bgm(meshsize, filepath):
    gmsh.initialize(sys.argv)

    path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join(path, filepath))  
    
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

    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    vtk_file = os.path.join(output_folder, "bgm.vtk")
    msh_file = os.path.join(output_folder, "bgm.msh")
    gmsh.write(vtk_file)
    gmsh.write(msh_file)

    gmsh.finalize()

    return nodeids, coords

def tetraprism_mutable(filepath,N,r,h):
    gmsh.initialize()

    path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join(path, filepath))
    
    # 読み込んだ形状を設定した角度で分解
    # forReparametrizationをTrueにしないとメッシングで時間がかかる
    gmsh.model.mesh.classifySurfaces(angle = 40 * np.pi / 180, boundary=True, forReparametrization=True)
    # classifySurfacesとセットで用いる
    gmsh.model.mesh.createGeometry()

    surface_real_wall = []
    surface_fake_wall = []
    surface_inlet_outlet = []
    s_first = gmsh.model.getEntities(2)
    for i in range(len(s_first)):
        surface_real_wall.append(s_first[i][1])
    gmsh.model.geo.synchronize()
    gmsh.option.setNumber("Geometry.ExtrudeReturnLateralEntities", 0)
    # ジオメトリオプションを設定して、押出し操作で lateral entities（側面のエンティティ）を返さないようにする

    # 注意
    # 境界層の厚さが一枚ごとの厚さではなく、基準線(形状の表面)からの距離
    # なので、t[i] += t[i - 1]で、その層以下の総和をしている
    n = np.linspace(1, 1, N) # [1, 1, 1, 1, 1]   (初期値、終値、等分数(初期値、終値を計2点と数えて))
    t = np.full(N, h) # distance from the reference line  # np.full(N,h)は、要素数Nの配列を用意して、その全てにhを格納する
    for i in range(0, N):
        t[i] = t[i] * r ** i
    for i in range(1, N):
        t[i] += t[i - 1]

    e = gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), n, -t, True)
    top_ent = [s for s in e if s[0] == 2]    
    for t in top_ent:     
        surface_fake_wall.append(t[1]) 
    gmsh.model.geo.synchronize()
    bnd_ent = gmsh.model.getBoundary(top_ent) 
    bnd_curv = [c[1] for c in bnd_ent] 
    closedSurfaceInletOutletInside = gmsh.model.geo.addCurveLoops(bnd_curv)
    for i in closedSurfaceInletOutletInside:
        # 上記で作成された輪郭に閉曲面を張る
        eachClosedSurface = gmsh.model.geo.addPlaneSurface([i])
        surface_fake_wall.append(eachClosedSurface)    
        surface_inlet_outlet.append(eachClosedSurface)
    innerSurfaceLoop = gmsh.model.geo.addSurfaceLoop(surface_fake_wall)
    gmsh.model.geo.addVolume([innerSurfaceLoop])
    gmsh.model.geo.synchronize()

    s_second = gmsh.model.getEntities(2) 
    surfaceAll = []                         
    for i in range(len(s_second)):             
        surfaceAll.append(s_second[i][1])  
    print("sufaceAll = ",surfaceAll)
    surface_another = list(set(surfaceAll) - set(surface_real_wall) - set(surface_inlet_outlet))  
    print("suface_fake_wall = ",surface_fake_wall)
    print("suface_another = ",surface_another)

    # python set 対称差
    something = list(set(surface_another) ^ set(surface_fake_wall)) 
    print("something = ",something)

    gmsh.model.addPhysicalGroup(2, something, 99)
    gmsh.model.setPhysicalName(2, 99, "SOMETHING") 

    wall = surface_real_wall
    gmsh.model.addPhysicalGroup(2, wall, 10)
    gmsh.model.setPhysicalName(2, 10, "WALL")

    volumeAll = gmsh.model.getEntities(3)
    three_dimension_list = []
    for i in range(len(volumeAll)):
        three_dimension_list.append(volumeAll[i][1])
    gmsh.model.addPhysicalGroup(3, three_dimension_list, 100)
    gmsh.model.setPhysicalName(3, 100, "INTERNAL")

    gmsh.model.geo.synchronize()

    gmsh.option.setNumber("Mesh.OptimizeThreshold", 0.9)
    # メッシュのアルゴリズムを設定
    gmsh.option.setNumber('Mesh.Algorithm', 1)
    # 最適化を何回繰り返すか->なぜか品質わるくなる
    gmsh.option.setNumber("Mesh.Optimize", 10)
    # path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join("output",'bgm.pos'))                                    # TODO : OSの違いに対応できているか
    bg_field = gmsh.model.mesh.field.add("PostView")    
    gmsh.model.mesh.field.setNumber(bg_field, "ViewIndex", 0) 
    gmsh.model.mesh.field.setAsBackgroundMesh(bg_field) 

    gmsh.model.geo.synchronize()
    # gmsh.option.setNumber('Mesh.Algorithm', 1)
    # gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)      
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)     
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0) 
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.model.mesh.generate(3)     
    gmsh.model.mesh.optimize()

    vtk_file = os.path.join("output", "tetraprism_mutable.vtk")
    msh_file = os.path.join("output", "tetraprism_mutable.msh")
    stl_file = os.path.join("output", "tetraprism_mutable.stl")
    gmsh.write(vtk_file)
    gmsh.write(msh_file)
    gmsh.write(stl_file)
    print("finish meshing")

    # GUI_setting()
    # gmsh.fltk.run()
    
    gmsh.finalize()

def surfacemesh(filepath_stl):
    gmsh.initialize()

    path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join(path, filepath_stl))

    # forReparametrizationをTrueにしないとメッシングで時間がかかる
    gmsh.model.mesh.classifySurfaces(angle = 40 * np.pi / 180, boundary=True, forReparametrization=True)
    # classifySurfacesとセットで用いる
    gmsh.model.mesh.createGeometry()
    gmsh.model.geo.synchronize()

    gmsh.option.setNumber("Mesh.OptimizeThreshold", 0.9)
    # メッシュのアルゴリズムを設定
    gmsh.option.setNumber('Mesh.Algorithm', 1)
    # 最適化を何回繰り返すか->なぜか品質わるくなる
    gmsh.option.setNumber("Mesh.Optimize", 10)
    # path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join("output",'bgm.pos'))                    # TODO : OSの違いに対応できているか
    bg_field = gmsh.model.mesh.field.add("PostView")    
    gmsh.model.mesh.field.setNumber(bg_field, "ViewIndex", 0) 
    gmsh.model.mesh.field.setAsBackgroundMesh(bg_field) 

    gmsh.model.geo.synchronize()

    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)      
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)     
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)

    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.optimize()
    output_folder = "output"
    vtk_file = os.path.join(output_folder, "surfacemesh.vtk")
    stl_file = os.path.join(output_folder, "surfacemesh.stl")
    gmsh.write(vtk_file)
    gmsh.write(stl_file)

    return vtk_file

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
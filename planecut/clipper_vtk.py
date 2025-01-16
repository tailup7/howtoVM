import vtk

def readFile_centerline(filepath):
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
    return centerlineNodes

def clip_mesh(reader, originPoint, vector, inside_out=True):
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(reader.GetOutputPort())
    plane = vtk.vtkPlane()
    plane.SetOrigin(originPoint)
    plane.SetNormal(vector)
    clipper.SetClipFunction(plane)
    clipper.InsideOutOn() if inside_out else clipper.InsideOutOff()  
    clipper.Update()
    return clipper  

centerlineNodes = readFile_centerline("centerline.txt")
reader = vtk.vtkSTLReader()
reader.SetFileName('stl.stl')

# メッシュのクリッピング（1つ目の平面）
originPoint = [centerlineNodes[0][1],centerlineNodes[0][2],centerlineNodes[0][3]]
originPoint_pre = [centerlineNodes[1][1],centerlineNodes[1][2],centerlineNodes[1][3]]
normal = [originPoint[i] - originPoint_pre[i] for i in range(len(originPoint))]
firstClip = clip_mesh(reader, originPoint, normal, inside_out=True)

# メッシュのクリッピング（2つ目の平面）
originPoint = [centerlineNodes[len(centerlineNodes)-1][1],centerlineNodes[len(centerlineNodes)-1][2],centerlineNodes[len(centerlineNodes)-1][3]]
originPoint_pre = [centerlineNodes[len(centerlineNodes)-2][1],centerlineNodes[len(centerlineNodes)-2][2],centerlineNodes[len(centerlineNodes)-2][3]]
normal = [originPoint[i] - originPoint_pre[i] for i in range(len(originPoint))]
secondClip = clip_mesh(firstClip, originPoint, normal, inside_out=True)

# 平滑化処理（切断面を滑らかにする）
smooth_filter = vtk.vtkSmoothPolyDataFilter()
smooth_filter.SetInputConnection(secondClip.GetOutputPort())
smooth_filter.SetNumberOfIterations(50)  # 平滑化回数
smooth_filter.Update()

writer = vtk.vtkSTLWriter()
writer.SetFileName('WALL.stl')
writer.SetInputConnection(smooth_filter.GetOutputPort())
writer.Write()
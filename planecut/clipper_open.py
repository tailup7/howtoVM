import vtk
import pandas as pd
import tkinter as tk
from tkinter import filedialog

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

# ---------- main ----------

# import csv file
csv_path = select_file("select centerline (*.csv)", [("CSV files", "*.csv")])
centerlineNodes = read_csv_centerline(csv_path)

# import stl file 
stl_path = select_file("select STL (*.stl)", [("STL files", "*.stl")])
reader = vtk.vtkSTLReader()
reader.SetFileName(stl_path)
reader.Update()

# clipping mesh (start point side)
originPoint = centerlineNodes[0]
originPoint_pre = centerlineNodes[1]
normal = [originPoint[i] - originPoint_pre[i] for i in range(3)]
firstClip = clip_mesh(reader, originPoint, normal, inside_out=True)

# clipping mesh (start point side)
originPoint = centerlineNodes[-1]
originPoint_pre = centerlineNodes[-2]
normal = [originPoint[i] - originPoint_pre[i] for i in range(3)]
secondClip = clip_mesh(firstClip, originPoint, normal, inside_out=True)

# smoothing
smooth_filter = vtk.vtkSmoothPolyDataFilter()
smooth_filter.SetInputConnection(secondClip.GetOutputPort())
smooth_filter.SetNumberOfIterations(50)
smooth_filter.Update()

# output
writer = vtk.vtkSTLWriter()
writer.SetFileName('WALL_cut.stl')
writer.SetInputConnection(smooth_filter.GetOutputPort())
writer.Write()
print("output WALL_cut.stl.")

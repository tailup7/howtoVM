using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows.Forms;
using System.Diagnostics;
using Kitware.VTK;
using System.IO;

namespace ActiViz.Examples
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            this.renderWindowControl1.Load += new System.EventHandler(this.renderWindowControl1_Load);
        }

        private void renderWindowControl1_Load(object sender, EventArgs e)
        {
            try
            {
                LoadAndProcessSTL();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Exception", MessageBoxButtons.OK);
            }
        }

        private void LoadAndProcessSTL()
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "STL Files (*.stl)|*.stl|All Files (*.*)|*.*";
            openFileDialog.Title = "Select STL File";

            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                string filePath = openFileDialog.FileName; 

                try
                {
                    // STLファイルを読み込む
                    vtkSTLReader stlReader = vtkSTLReader.New();
                    stlReader.SetFileName(filePath);
                    stlReader.Update();

                    if (stlReader.GetOutput() == null)
                    {
                        throw new Exception("Failed to load STL file.");
                    }

                    vtkPolyData input = stlReader.GetOutput(); // STLのデータをvtkPolyDataに格納

                    // FillHoles処理
                    vtkFillHolesFilter fillHolesFilter = vtkFillHolesFilter.New();
                    fillHolesFilter.SetInputConnection(input.GetProducerPort());
                    // サイズを調整。埋めたい穴のサイズと周囲のメッシュ1個の大きさから決める? (埋めたい穴の直径) / (周囲のメッシュサイズ) ？
                    fillHolesFilter.SetHoleSize(1000.0); 
                    fillHolesFilter.Update();  // 追加: フィルタを適用

                    // 出力ファイルのパスを決定
                    string outputFilePath = Path.Combine(Directory.GetCurrentDirectory(), "output", Path.GetFileNameWithoutExtension(filePath) + "_filled.stl");

                    SaveData(fillHolesFilter.GetOutput(), outputFilePath);

                    // GUIに表示する処理を追加することも可能
                    DisplayResult(input, fillHolesFilter.GetOutput());
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Error loading STL file: " + ex.Message, "File Load Error", MessageBoxButtons.OK);
                }
            }
        }

        private void SaveData(vtkPolyData polyData, string outputFilePath)
        {
            try
            {
                string projectRootDirectory = Path.GetFullPath(Path.Combine(Application.StartupPath, @"..\..\"));  

                string outputDir = Path.Combine(projectRootDirectory, "output");

                if (!Directory.Exists(outputDir))
                {
                    Directory.CreateDirectory(outputDir);
                }

                string finalOutputFilePath = Path.Combine(outputDir, Path.GetFileName(outputFilePath));

                // STL形式で保存
                string extension = Path.GetExtension(finalOutputFilePath).ToLower();

                if (extension == ".stl")
                {
                    vtkSTLWriter writer = vtkSTLWriter.New();
                    writer.SetFileName(finalOutputFilePath);
                    writer.SetInputConnection(polyData.GetProducerPort());
                    writer.Write();
                }
                else
                {
                    throw new Exception("Unsupported file format for saving: " + extension);
                }

                MessageBox.Show("Data saved to: " + finalOutputFilePath, "Save Success", MessageBoxButtons.OK);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error saving data: " + ex.Message, "Save Error", MessageBoxButtons.OK);
            }
        }

        private void DisplayResult(vtkPolyData originalPolyData, vtkPolyData filledPolyData)
        {
            // 処理前のデータ用のマッパーとアクターを作成
            vtkPolyDataMapper originalMapper = vtkPolyDataMapper.New();
            originalMapper.SetInputConnection(originalPolyData.GetProducerPort());

            vtkActor originalActor = vtkActor.New();
            originalActor.SetMapper(originalMapper);

            // 処理後のデータ用のマッパーとアクターを作成
            vtkPolyDataMapper filledMapper = vtkPolyDataMapper.New();
            filledMapper.SetInputConnection(filledPolyData.GetProducerPort());

            vtkActor filledActor = vtkActor.New();
            filledActor.SetMapper(filledMapper);

            vtkRenderWindow renderWindow = renderWindowControl1.RenderWindow;
            this.Size = new System.Drawing.Size(1200, 600);  

            double[] leftViewport = new double[] { 0.0, 0.0, 0.5, 1.0 };  
            double[] rightViewport = new double[] { 0.5, 0.0, 1.0, 1.0 };  

            // 左側のレンダラーを設定
            vtkRenderer leftRenderer = vtkRenderer.New();
            renderWindow.AddRenderer(leftRenderer);
            leftRenderer.SetViewport(leftViewport[0], leftViewport[1], leftViewport[2], leftViewport[3]);
            leftRenderer.SetBackground(.6, .5, .4);  // 背景色

            // 右側のレンダラーを設定
            vtkRenderer rightRenderer = vtkRenderer.New();
            renderWindow.AddRenderer(rightRenderer);
            rightRenderer.SetViewport(rightViewport[0], rightViewport[1], rightViewport[2], rightViewport[3]);
            rightRenderer.SetBackground(.4, .5, .6);  // 背景色

            // 左側に元の形状を表示
            leftRenderer.AddActor(originalActor);
            // 右側に処理後の形状を表示
            rightRenderer.AddActor(filledActor);

            // 両方のレンダラーのカメラをリセット
            leftRenderer.ResetCamera();
            rightRenderer.ResetCamera();

            // レンダリングを実行
            renderWindow.Render();
        }
    }
}

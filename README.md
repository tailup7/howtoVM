# 概要
このリポジトリは、血管形状のモデリングの際に必要となった作業について、覚書として残しておくためのリポジトリです。基本的に血流解析の前処理としての位置づけですが、チューブ形状の3DCG処理として、血管以外、流体解析以外でも広い用途で使えると思います。<br>
<br>
This repository is intended to keep a memorandum of the work that was required in Vascular Modeling. Basically, methods in this repository are intended as pre-processing for blood flow analysis,  
but they can be used for a wide range of applications as a 3DCG process for tubular geometry. 

## 環境や使用しているツールなど
* Windows 10 or higher (筆者は11を使用)
    * visual studio 2022
        * .NET Framework 4.8
        * VTKライブラリ (NuGetパッケージマージャーでActiviz.Net.x64(5.8.0)をインストール)
    * vmtk 1.4.0 (vmtkSetup参照)
    * Gmsh-4.13 (高機能なメッシュ生成ソフトウェア。C++やpythonなどの主要言語のAPIを提供している。)

### あると便利なもの
* meshmixer (stlファイルをすぐ開くため)
* paraview (3Dデータに関して、ほぼすべてのファイル形式を可視化できる)

## 各フォルダについて
 + vmtkSetup      ---------- vmtk のセットアップ方法を簡単にまとめた。
 + extractCenterline --- vmtk を利用して、STLデータから中心線を抽出するメソッド
 + fillHoles    -------  vtkを利用してSTLデータの表面の穴や、チューブ形状の端面を塞ぐためのメソッド。
 + planecut  ------ vtkを利用してSTLデータの不要な形状部分を中心線に対して垂直に切断・除去するメソッド。
 + autoMeshing -- Gmshを利用して任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するコード
 

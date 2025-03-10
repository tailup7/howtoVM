# 概要
血管形状のモデリングの際に必要となった作業や処理について、覚書として残しておくためのリポジトリです。基本的に血流解析の前処理としての位置づけですが、3D形状処理として、血管以外、流体解析以外で使える部分もあると思います。<br>
<br>
This repository is intended to keep a memorandum of the work that was required in Vascular Modeling. Basically, methods in this repository are intended as pre-processing for blood flow analysis,  
but they can be used for a wide range of applications as a 3DCG process for tubular geometry. 

<br>
※ 血管形状モデリングの一番最初の工程で、かつ全工程の中でも重要な位置を占めるのが、医用画像から血管領域を抽出し2D→3Dにする工程(セグメンテーション)ですが、研究室のインハウスソフトウェアを使用していることと、医用画像自体が個人情報とも言えるので、ここでは紹介しません。3Dスライサーなどのフリーソフトでもセグメンテーションできます。

## 使用している環境
* OS : Windows 11 
    * IDE : VScode
         * 言語 : 主にpython

### あると便利なもの
* paraview (ほぼすべてのファイル形式を可視化できる)
* meshmixer (stlファイルをすぐ可視化できる & スムージングや再メッシュ機能もあって便利)

### 紹介しているソフトウェア・ライブラリ
* vtk-examples (Kitwareが提供する、モデリング・可視化に関するライブラリ。C++やpython, javaなどの主要言語のAPIを提供している。)
* vmtk 1.4.0 (Vascular Modeling Toolkit の略。VTKから派生したもの。C++, python のAPIを提供している。CUI機能を提供しておりCUIで利用するのが便利かも)
* Gmsh-4.13 (フリーのメッシュ生成ソフトウェア。C++やpythonなどの主要言語のAPIを提供している。)

## 各ディレクトリについて
 + Gmsh   --------------- Gmsh の簡単な紹介。
 + autoMeshing -- Gmshを利用して任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するコード
 + extractCenterline --- vmtk を利用して、STLデータから中心線を抽出する方法。
 + fillHoles    -------  vtkを利用してSTLデータの表面の穴や、チューブ形状の端面を塞ぐためのメソッド。
 + planecut  ------ vtkを利用してSTLデータの不要な形状部分を中心線に対して垂直に切断・除去するメソッド。
 + vmtkSetup      ---------- vmtk のセットアップ方法を簡単にまとめた。
 

# 概要
このリポジトリは、血管形状のモデリングの際に必要となった作業について、覚書として残しておくためのリポジトリです。基本的に血流解析の前処理としての位置づけですが、3D形状処理として、血管以外、流体解析以外で使える部分もあると思います。<br>
<br>
This repository is intended to keep a memorandum of the work that was required in Vascular Modeling. Basically, methods in this repository are intended as pre-processing for blood flow analysis,  
but they can be used for a wide range of applications as a 3DCG process for tubular geometry. 

<br>
※ 血管形状モデリングの一番最初の工程で、かつ全工程の中でも重要な位置を占めるのが、医用画像から血管領域を抽出し2D→3Dにする工程ですが、研究室のインハウスソフトウェアを使用していることと、医用画像自体が個人情報とも言えるので、ここでは紹介しません。

## 環境や使用しているツール・言語など
* OS : Windows 10 or higher (筆者は11を使用)
    * IDE : VScode
         * 言語 : 主にpython

### あると便利なもの
* meshmixer (stlファイルをすぐ開くため)
* paraview (3Dデータに関して、ほぼすべてのファイル形式を可視化できる)

### 紹介しているソフトウェア・ライブラリ
* vtk examples (Kitwareが提供する、モデリング・可視化に関するライブラリ。C++やpython, javaなどの主要言語のAPIを提供している。)
* vmtk 1.4.0 (Vascular Modeling Toolkit の略。CUI機能を提供しておりCUIで利用する)
* Gmsh-4.13 (高機能だがフリーのメッシュ生成ソフトウェア。C++やpythonなどの主要言語のAPIを提供している。)

## 各ディレクトリについて
 + Gmsh   --------------- Gmsh の簡単な紹介。
 + vmtkSetup      ---------- vmtk のセットアップ方法を簡単にまとめた。
 + extractCenterline --- vmtk を利用して、STLデータから中心線を抽出するメソッド
 + fillHoles    -------  vtkを利用してSTLデータの表面の穴や、チューブ形状の端面を塞ぐためのメソッド。
 + planecut  ------ vtkを利用してSTLデータの不要な形状部分を中心線に対して垂直に切断・除去するメソッド。
 + autoMeshing -- Gmshを利用して任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するコード
 

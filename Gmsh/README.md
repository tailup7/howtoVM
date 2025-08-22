# Gmsh とは
Gmsh (https://gmsh.info/doc/texinfo/gmsh.html) はフリーのメッシュ生成ソフトウェアである。GmshのコアライブラリはC++で記述されているが、pythonやfortranなどの言語にもAPIを提供しており、その機能をスクリプトから簡単に利用できる。ドキュメントやチュートリアル問題が充実していて、非常に使いやすい。上のリンクの2章のチュートリアルを一通り実行すれば要領をつかむことができ、6章や (https://gitlab.onelab.info/gmsh/gmsh/-/tree/master/api?ref_type=heads) ページから、呼び出せるメソッドが確認できる。GUI機能もあるが、筆者は処理結果の確認のためのビューワとしてしか利用していない。
<br>

<br>

以下のリンク先にもAPIを利用したいくつかのサンプルコードが提供されており (https://gitlab.onelab.info/gmsh/gmsh/-/tree/gmsh_4_13_1/examples/api) 、そのうちの1つ```aneurysm.py```を実行した結果が1番下の図。

<br>
<br>
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/aneurysm_stl.png" alt="meshing" width="400"/>
</p>

上図は、元の表面形状のみのデータ ```aneurysm_data.stl```。このデータを読み込んで、トポロジカルな単純押し出しとメッシングによってテトラプリズム複合メッシュが作成される(下図)。

<br>
<br>
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/aneurysm_msh.png" alt="meshing" width="400"/>
</p>

上にもデータとコードを置いてある。簡単なのでローカルにコピーして試してみてほしい (pythonのインストール・パス通す、が終わっていれば)
```
$ pip install gmsh
```
でGmshのpythonバインディングをインストールした後、
```
$ python aneurysm.py
```
で実行できる。


## OpenFOAM側の対応
数値流体解析のためのオープンソースソフトウェアとして広く用いられているOpenFOAMは、ユーザ側で用意した形状を計算領域としたい場合には、その形状データをfluent形式(Ansys社が提供している形式)かgmsh形式で用意し、それをOpenFOAMで読める形式に変換することで可能になる。つまり、gmshのファイル形式(*.msh) はOpenFOAMに対応している。(*.msh)ファイルをテキストエディタで開くと分かるが、vtkと似た形式で記述されているが、vtkよりも読みやすい。一方でvtk形式はOpenFOAM側が対応していないため、数値計算したい形状データがvtk形式の場合、一度gmsh形式に変換してからOpenFOAMに読ませるというやり方が一般的。

## Paraview側は非対応
Gmshで作成したメッシュファイルの形式(*.msh)は、そのままではParaviewで読み込むことができない。Gmshは、(*.msh)形式で出力すると同時に(*.vtk)形式でも出力することができるので、メッシュ生成時に(*.vtk)形式でも出力するようにするか、OpenFOAMをインストールしていれば、(*.msh)を一度OpenFOAMにインポートして
```
$ gmshToFoam foo.msh
```
vtk形式に変換するOpenFOAMの機能
```
$ foamToVTK
```
で変換する方法などがある。

## (*.msh)形式と(*.vtk)形式の違い
TODO : それぞれのファイル形式の中身、physical name, entityなどの概念について説明

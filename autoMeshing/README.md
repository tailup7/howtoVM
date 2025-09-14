# Gmshを利用して、任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するpythonコード

<p align="center">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/beforeafter.png" alt="meshing" width="1000"/>
</p>

## Gmsh とは
Gmsh (https://gmsh.info/doc/texinfo/gmsh.html) はフリーのメッシュ生成ソフトウェアである。GmshのコアライブラリはC++で記述されているが、pythonやfortranなどの言語にもAPIを提供しており、その機能をスクリプトから簡単に利用できる。ドキュメントやチュートリアル問題が充実していて、非常に使いやすい。上のリンクの2章のチュートリアルを一通り実行すれば要領をつかむことができ、6章や (https://gitlab.onelab.info/gmsh/gmsh/-/tree/master/api?ref_type=heads) ページから、呼び出せるメソッドが確認できる。GUI機能もあるが、筆者は処理結果の確認のためのビューワとしてしか利用していない。

## 本コードの使い方
Gmshが必要です。Gmsh本体をインストールすることをおすすめしますが、面倒なら
```
$ pip install gmsh
```
でGmshのpythonバインディングをインストールするだけでも使えます。その場合、Gmshのビューワーは使えないため、コード中の下から2行目、 `VisualizeMesh()` をコメントアウトし、出力される .vtkファイルをParaviewなどで可視化して確認してください。
また、vtkライブラリも使用するため、インストールがまだなら
```
$ pip install vtk
```
でインストールしてください。
``` 
$ python autoMeshing.py
```
を実行してみて下さい。入力データとして、サンプル ``` WALL.stl ``` も載せています。<br>
<br>

``` autoMeshing.py ``` 内のパラメータ(メッシュのサイズやプリズム層の層数など)を変えることで、適切な解析モデルを得ることができます。また、メッシュサイズに関して、入力とするSTLの表面メッシュをそのまま内部に押し出して、テトラ・プリズムメッシュを生成することもできます(コード内のコメント部分参照)。<br>
本コードでは、INLET, OUTLETの区別について z成分を用いている(デフォルトではz軸上方にある面をINLETにする。コード実行中に逆にするか選べる)。<br>
入力データとするSTLファイルは、端面が開放されていて、メッシングに際し領域分けが必要ない (極端に細い or 太い部分がない) チューブ形状として下さい。

## 正しく Phisical naming されているか確認
Gmshは、各セルに物理的な意味を表す名前を持たせることができ、本コードでは、流体解析が可能なように流入面、流出面、管壁、内部(流体が流れる領域)に属するセルに, INLET, OUTLET, WALL, INTERNALと名前を与えている。<br>
メッシュファイルが出力できたら、vtkファイルをparaviewで開き、Threshold機能ですべてのセルに正しい EntityID (Physical name に割り当てた番号) が与えられているか確認してください。<br>
10:WALL(管壁), 20:INLET(流入面), 30:OUTLET(流出面), 100:INTERNAL(内部領域)
<br>
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/autoMeshing_output.png" alt="planecut_edge" width="400"/>
</p>
<br>
あるいは、 .msh ファイルをテキストエディタ(VScode)などで開き、

```
17386 2 2 20 16 17729 17722 17730
```
このように、4列目(Entity number) に正しく20や30などの番号が割り当てられていればOK.

## OpenFOAM で流体解析
Gmshで生成したメッシュファイルをOpenFOAMで扱うときの注意事項をいくつか書いておく。
Gmshで作成したメッシュファイルに対しては、以下のコマンドで形式変換する。
```
$ gmshToFoam aaa.msh
```
またGmshには単位がないため、入力STLの段階で mm 単位で座標を表していた場合には、OpenFOAMでの単位である m に直すため、以下のコマンドを使用する。
```
$ transformPoints -scale "(1e-3 1e-3 1e-3)"
```
<br>
<br>
↓ OpenFOAMで流体解析を行い、壁面せん断応力の分布を可視化した結果
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/autoMeshing_OpenFOAM_WSS.png" alt="WSS" width="400"/>
</p>

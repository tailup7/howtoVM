# Gmshを利用して、任意のチューブ形状に対してテトラ・プリズム複合メッシュを作成するpythonコード

<p align="center">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/beforeafter.png" alt="meshing" width="1000"/>
</p>

## Gmsh とは
Gmsh (https://gmsh.info/doc/texinfo/gmsh.html) はフリーのメッシュ生成ソフトウェアである。GUIで視覚的に3次元形状を作成・メッシュを生成することも可能だが、pythonAPIも提供しており、高度なメッシュ生成が可能である。

## 使い方
autoMeshing.py を実行してみて下さい。入力データとして、サンプル (WALL.stl) も載せています。<br>
<br>
autoMeshing.py 内のパラメータ(メッシュのサイズやプリズム層の層数など)を変えることで、適切な解析モデルを得ることができます。<br>
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

## OpenFOAM で流体解析
Gmshで生成したメッシュファイルをOpenFOAMで扱うときの注意事項をいくつか書いておく。
Gmshで作成したメッシュファイルに対しては、以下のコマンドで形式変換する。<br>
<br>
gmshToFoam aaa.msh <br>
<br>
またGmshには単位がないため、入力STLの段階で mm 単位で座標を表していた場合には、OpenFOAMでの単位である m に直すため、以下のコマンドを使用する。<br>
<br>
transformPoints -scale "(1e-3 1e-3 1e-3)"
<br>
<br>
<br>
↓ OpenFOAMで流体解析を行い、壁面せん断応力の分布を可視化した結果
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/autoMeshing_OpenFOAM_WSS.png" alt="WSS" width="400"/>
</p>

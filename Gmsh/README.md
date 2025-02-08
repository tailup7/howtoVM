# Gmsh とは

セットアップ方法、チュートリアル、提供ライブラリ一覧、GUI操作など含めたフルドキュメントはこちら。
https://gmsh.info/doc/texinfo/gmsh.html#t1
<br>
<br>
以下のリンク先にもAPIを利用したいくつかのサンプルコードが提供されており、そのうちの1つ(aneurysm.py)を実行した結果が下の図。
https://gitlab.onelab.info/gmsh/gmsh/-/tree/gmsh_4_13_1/examples/api

<p align="center">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/aneurysm_stl.png" alt="meshing" width="600"/>
</p>
上図は、元の表面形状のみのデータ(aneurysm_data.stl)。このデータを読み込んで、トポロジカルな単純押し出しとメッシングによってテトラプリズム複合メッシュを作成する(下図)。

<p align="center">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/aneurysm_msh.png" alt="meshing" width="600"/>
</p>

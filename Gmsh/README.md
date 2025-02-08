# Gmsh とは
Gmsh (https://gmsh.info/doc/texinfo/gmsh.html) はフリーのメッシュ生成ソフトウェアである。GmshのコアライブラリはC++で記述されているが、pythonやfortranなどの言語にもAPIを提供しており、その機能をスクリプトから簡単に利用できる。ドキュメントやチュートリアル問題が充実していて、非常に使いやすい。上のリンクの2章のチュートリアルを一通り実行すれば要領をつかむことができ、6章や (https://gitlab.onelab.info/gmsh/gmsh/-/tree/master/api?ref_type=heads) ページから、呼び出せるメソッドが確認できる。GUI機能もあるが、筆者は処理結果の確認のためのビューワとしてしか利用していない。
<br>

<br>
以下のリンク先にもAPIを利用したいくつかのサンプルコードが提供されており (https://gitlab.onelab.info/gmsh/gmsh/-/tree/gmsh_4_13_1/examples/api) 、そのうちの1つ(aneurysm.py)を実行した結果が下の図。

<br>
<br>
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/aneurysm_stl.png" alt="meshing" width="400"/>
</p>
上図は、元の表面形状のみのデータ(aneurysm_data.stl)。このデータを読み込んで、トポロジカルな単純押し出しとメッシングによってテトラプリズム複合メッシュを作成する(下図)。
<br>
<br>
<p align="left">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/aneurysm_msh.png" alt="meshing" width="400"/>
</p>

上にもデータとコードを置いてある。簡単なのでローカルにコピーして試してみてほしい(pythonが使えてパスを通していれば、「pip install gmsh」→「python aneurysm.py」だけで実行できるはず...)。

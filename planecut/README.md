# 中心線に合わせて端面を垂直にカットする

## 概要
下の図のような処理をする。<br>
<br>
入力 : STL、残したい部分の中心線 <br>
出力 : カットされたSTL<br>

<<<<<<< HEAD
=======
※ STLのファイル名は「stl.stl」に、中心線ファイルの名前は「centerline.txt」に、中心線データの形式はファイルを参照してください。
>>>>>>> 707da8e31658e3127d4fee553108af66660c7406
<br>

<p align="center">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/planecut.png" alt="planecut" width="600"/>
</p>

## 結果
<<<<<<< HEAD
下の図のように、表面メッシュはそのままに、切断面にだけedgeが追加されたSTLになる。端面を塞ぎたい場合は、clipper_fillhole.pyを使用して下さい。
=======
下の図のように、表面メッシュはそのままに、切断面にだけedgeが追加されたSTLになる。
>>>>>>> 707da8e31658e3127d4fee553108af66660c7406
<br>
<br>

<p align="center">
  <img src="https://github.com/tailup7/howtoVM/blob/main/pictures/planecut_edge.png" alt="planecut_edge" width="800"/>
</p>
<br>

# vmtk とは
vmtk(vascular modeling toolkit) は、血管形状モデルを扱う際のライブラリを提供している。

## インストール
setup.pptx に簡単にインストール手順を書いた。

## 試しに
vmtkのCLIに <br>
vmtkimagereader -ifile dicom_directory_path/first_dicom_file_in_the_series --pipe vmtkimageviewer <br>
と入力し・実行して医用画像を表示することができる。
<br>
assetsに、Willis動脈輪のCT画像データを入れてある。ローカルにインストールし、上のコマンドの一部をフォルダ内のデータ群の1番上の医用画像データのフルパスに変えると、次のようにDICOM形式の画像データを見ることができる。

<br>
<br>

<img src="../assets/Trim.gif" width="535" height="501" />

<br>
(※)このWillis動脈輪の医用画像は以下のサイトより提供されている。 <br>
https://3dicomviewer.com/dicom-library/

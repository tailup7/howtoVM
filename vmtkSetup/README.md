# vmtk とは
vmtk(vascular modeling toolkit) は、血管形状モデルを扱う際のライブラリを提供している。

## インストール
setup.pptx に簡単にインストール手順を書いた。

## 試しに
vmtkのCLIに <br>
vmtkimagereader -ifile dicom_directory_path/first_dicom_file_in_the_series --pipe vmtkimageviewer <br>
と入力し・実行して医用画像を表示することができる。
<br>
assetsに、Willis動脈輪のCT画像データを入れてある。ローカルにインストールし、上のコマンドの一部をフォルダ内のデータ群の1番上の医用画像データのフルパスに変えると、次のようにCT画像を見ることができる。
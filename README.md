# drone
Tello が　緑色のボールを追いかけます。　
と言うよりは・・・。緑色の動きに合わせてTelloが移動します・

上下、左右、に移動するパラメータはボールの座標です。

前後に動くパラメータは緑色のボールの直径です。

Tello_remo_control-camera.py はwebカメラで緑色のボールの座標を調べるプログラムです。
Telloの移動をコントロールするTello_remo_control.py のプログラムと合わせるため
Telloの制御プラグラムもそのまま残しコメントアウトしてあります。
webカメラを使う箇所とwebカメラの解像度1920 x 1080にする箇所だけ変更しています。

Tello_remo_contol.py は　緑色のボールを追いかけるよう、
up, down, right, left, forward, backward に移動します。
どちらに動くか音声でも教えてくれます。


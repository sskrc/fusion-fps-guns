# Fusion FPS Guns

Autodesk Fusion のスクリプトで作った、FPSゲーム向けの銃の3Dモデル集です。P230風ピストルは、Three.js で操作できる展示サイトにしてあります。

**サイト:** https://sskrc.github.io/fusion-fps-guns/

すべて表示用のモデルです。銃身は中実で、薬室や撃発機構などの内部は作っていません。発砲はアニメーションと合成音による演出です。

## サイトの操作

| 操作 | キー |
|---|---|
| 発砲 | Space / F |
| マガジンを抜く・入れる | M |
| リロード | R |
| スライドを引く・戻す | S |
| デコック | D |
| 分解・組み立て | X |

ドラッグで回転、ホイールでズームできます。

## モデル

| モデル | 場所 | 内容 |
|---|---|---|
| P230風ピストル | `models/P230` | GLB / FBX、2Kテクスチャ、ボーン8本、アニメーション9種 |
| サブマシンガン VX-9 Wasp | `models/SMG_VX9_Wasp` | GLB / FBX（可動部なし） |
| ショットガン HR-12 Breaker | `models/Shotgun_HR12_Breaker` | GLB / FBX（可動部なし） |
| スナイパー LR-X Longshot | `models/Sniper_LRX_Longshot` | GLB / FBX（可動部なし） |

P230 のアニメーション（30fps）: `Idle` `Trigger_DA_Dry` `Fire_DA` `Fire_SA` `Fire_SA_Last` `Reload_Empty` `Reload_Tactical` `Decock` `Slide_Rack`

## 作り方

1. `source/fusion` のフォルダを Fusion のスクリプトとして実行すると、新規ドキュメントに形状が作られ、スクリプトと同じ場所の `out` にパーツ別STLと `manifest.json` が書き出されます。
2. `source/blender` のスクリプトをヘッドレスの Blender で実行すると、UV展開、テクスチャの焼き込み、ボーン、アニメーション、干渉チェックを行い、GLB / FBX を書き出します。

```
blender -b --python source/blender/convert_guns.py -- <銃のoutフォルダ>
blender -b --python source/blender/p230_finish.py -- <P230のoutフォルダ> <出力先> res=2048
```

形状の寸法や色は `gun_data.py` と `p230_data.py` の数値で決まります。

## ローカルでサイトを動かす

```
python -m http.server 8765
```

`http://localhost:8765/` を開きます。three.js とフォントはCDNから読み込みます。

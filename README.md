# POSシステム

**私自身なんで動いているかわかりません！動作保証できません！**

各種勉強目的で作成していたPOSシステムを公開用にしたものです。
一切を自己責任でお願いします。

**このプロジェクトは、[mizunoshota2001](https://github.com/mizunoshota2001) 氏作成の [tutorial-CSJWindowsPOSSDK-for-python](tutorial-CSJWindowsPOSSDK-for-python) を使用しています。**

## はじめに

### 必要なもの

[]内は私の環境です

- Windows(とりあえず10以上) [Windows11]
- Python 3.11ぐらい [Python 3.11.5]
- Reactが動かせる環境 [node v20.18.0]
- 何らかのデータベース [MySQL 8.0]
- citizen製レシートプリンター(Citizen Systems 株式会社 Windows POS Print SDKに対応したもの)(プリンターの接続にBluetoothを使用) [CT-S281BD]
- VOICEVOXエンジン [GPU版 0.20.0]
- (ローカルネットワーク内のデバイスでも接続できます)

初回は`install.bat`を実行してください。
たぶんうごきます。

### SDKの入手及び配置

以下より入手したSDKは`backend/csjwindowspossdk/Library`に配置してください。

Citizen Systems 株式会社 Windows POS Print SDK
[CSJWindowsPOSSDK_V206J.zip](https://www.citizen-systems.co.jp/cms/c-s/printer/download/sdk-print/CSJWindowsPOSSDK_V206J.zip)

### プリンターの接続

`backend/config`内で接続設定を行っています。環境に従い、接続を指定してください。

### データベースの作成

MySQLを想定しています。データベースを作成、起動し、`backend/config`内のURLを調整してください。

### VOICEVOXについて

呼び出しにVOICEVOXエンジンを使用します。以下より入手、起動してください。

[VOICEVOX](https://voicevox.hiroshiba.jp/)

## つかいかた

よくわかりません。がんばってわかりやすくします。

### サーバサイド

`start.py`をrunしたら動くかも。

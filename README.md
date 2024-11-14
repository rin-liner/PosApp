# POSシステム

**私自身なんで動いているかわかりません！動作保証できません！**

*作成していたPOSシステムを公開用にしたものです。*
*一切を自己責任でお願いします。*

**このプロジェクトは、[mizunoshota2001](https://github.com/mizunoshota2001) 氏作成の [tutorial-CSJWindowsPOSSDK-for-python](tutorial-CSJWindowsPOSSDK-for-python) を使用しています。**

## はじめに

`backend`内で`pip install -r requirements.txt`を行ってください。

`frontend`内で`npm install socket.io-client`を行ってください。

ここら辺は一度に行えるようにしたいです。

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

がんばってわかりやすくします。

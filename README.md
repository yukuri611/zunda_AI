# ずんだもんボイスの生成AI

## セットアップ
以下の公式GitHubに書いてある手順どおりに進めればOK。Dockerでvoicevoxの音声合成機能を提供するAPIサーバーのコンテナを立ち上げる。

### DockerからVOICEVOXのコンテナを取得し、APIサーバーを立てる
#### CPU
```bash
docker pull voicevox/voicevox_engine:nvidia-latest
docker run --rm --gpus all -p '127.0.0.1:50021:50021' voicevox/voicevox_engine:nvidia-latest
```

#### GPU
```bash
docker pull voicevox/voicevox_engine:nvidia-latest
docker run --rm --gpus all -p '127.0.0.1:50021:50021' voicevox/voicevox_engine:nvidia-latest
```
なお、GPU版を使うには、先にNVIDIA Container Toolkitをインストールしておく必要があるのでそちらもインストールしておく。
dockerでAPIサーバーを立てなくても、VOICEVOXアプリを立ち上げることで自動的にエンジンが立ち上がり、127.0.0.1の50021ポートからAPIサーバーにアクセスすることができる。ただし、WSL2を使用している場合、Ngrokなどを使用して、windows側での127.0.0.1:50021にアクセスする方法を確立する必要がある（Dockerで構築するのが一番簡単なのでそちらがおすすめ！）

### pythonの環境構築
python3.12.3を使用
requirements.txtに書かれているパッケージを以下のコマンドでインストール
```bash
pip install -r requirements.txt
```

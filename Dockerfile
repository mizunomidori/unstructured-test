# ベースイメージとしてPythonを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    poppler-utils \
    cmake \
    build-essential \
    libprotobuf-dev \
    protobuf-compiler \
    libgl1-mesa-dev \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 必要なPythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# スクリプトをコンテナ内にコピー
COPY unstructured-test/ .

# スクリプトを実行
CMD ["python", "pdf-parser.py"]

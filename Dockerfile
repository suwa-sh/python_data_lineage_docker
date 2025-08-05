FROM python:3.6-slim

# OpenJDK 8を公式イメージからコピー
COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8

# 環境変数設定
ENV JAVA_HOME=/usr/local/openjdk-8
ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /app

# JPypeのビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

ENTRYPOINT ["python3", "server.py"]
CMD []

FROM python:3.6-slim

WORKDIR /app

# OpenJDK 11と、JPypeのビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# JAVA_HOMEを設定
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir JPype1==1.3.0

COPY . /app/

EXPOSE 8000

CMD ["python3", "-m", "http.server", "8000", "--directory", "widget"]

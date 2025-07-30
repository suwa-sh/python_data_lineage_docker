FROM openjdk:8-jdk

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir JPype1

COPY . /app/

EXPOSE 8000

CMD ["python3", "-m", "http.server", "8000", "--directory", "widget"]


FROM python:3.12-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ttyd ncurses-term && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir questionary && \
    useradd --create-home player && \
    chown -R player:player /app

USER player

ENV TERM=xterm-256color
ENV PYTHONUNBUFFERED=1

EXPOSE 7681

CMD ["sh", "-c", "exec ttyd -W -p \"${PORT:-7681}\" python3 -u game.py"]

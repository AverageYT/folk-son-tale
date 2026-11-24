
FROM ghcr.io/tsl0922/ttyd:1.7.8

# Install Python and terminal support
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    ncurses-term && \
    rm -rf /var/lib/apt/lists/*

# Create a Python environment
RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV TERM=xterm-256color
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
RUN pip install --no-cache-dir questionary

# Set up the game
WORKDIR /app
COPY . .

# Run the game without root privileges
RUN useradd -m player && \
    chown -R player:player /app

USER player

EXPOSE 7681

# Start browser terminal and Python game
CMD ["sh", "-c", "exec ttyd -W -i 0.0.0.0 -p \"${PORT:-7681}\" python3 -u game.py"]

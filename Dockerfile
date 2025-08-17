FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium and ChromeDriver for ARM64/AMD64 compatibility
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for Selenium compatibility
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome \
    && ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver

# Set executable permissions
RUN chmod +x /usr/bin/chromedriver /usr/local/bin/chromedriver

COPY . .

# Default command uses an environment variable or argument
ENTRYPOINT ["python"]
CMD ["main.py"]  # Default script; override with docker run my-image your_script.py
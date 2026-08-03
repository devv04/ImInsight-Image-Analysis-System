FROM python:3.10-slim

# Install system dependencies required by OpenCV and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend app files
COPY . .

# Create uploads folder with write permissions
RUN mkdir -p static/uploads && chmod -R 777 static/uploads

# Hugging Face Spaces default port is 7860
EXPOSE 7860

# Run Flask backend with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "180", "app:app"]

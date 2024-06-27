# Gunakan image dasar Python
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

# Buat direktori kerja
WORKDIR /app

# Salin requirements.txt ke direktori kerja
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Salin kode aplikasi dan wait-for-it script ke dalam direktori kerja
COPY . /app/
COPY wait-for-it.sh /app/wait-for-it.sh

# Berikan permission untuk eksekusi wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Jalankan wait-for-it.sh dan kemudian jalankan script Python
CMD ["./wait-for-it.sh", "db:5432", "--", "python", "save_json_pdf.py"]

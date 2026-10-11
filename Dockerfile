# Same minor version as my local venv (3.12); slim = Debian without compilers/docs
FROM python:3.12-slim

# All following commands run from /app; created if missing
WORKDIR /app

# Dependencies first: this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code last: it changes often, so only the layers below this line rebuild
COPY . .

# Documentation only: Flask listens on 5000. Publishing happens with -p at run time
EXPOSE 5000

# Inside a container 127.0.0.1 is the container's own loopback; 0.0.0.0 = all interfaces,
# which is what Docker's port mapping connects to
ENV FLASK_HOST=0.0.0.0

# The database lives in /data, a folder meant to be mounted as a volume (docker run -v)
ENV DB_PATH=/data/expense.db
RUN mkdir /data

# init_db.py is idempotent (CREATE TABLE IF NOT EXISTS), so a fresh empty volume gets its
# table on first start. exec makes Python PID 1 so docker stop reaches it directly.
CMD ["sh", "-c", "python init_db.py && exec python app.py"]

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

CMD ["python", "app.py"]

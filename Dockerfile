FROM public.ecr.aws/docker/library/python:3.9-slim-bullseye

WORKDIR /frontend

# Copy and install Python requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 80
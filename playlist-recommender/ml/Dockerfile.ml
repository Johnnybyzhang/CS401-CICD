FROM quay.io/johnnybyzhang/uv-ml-base:latest
WORKDIR /app
COPY train_model.py .
CMD ["uv", "run", "python", "train_model.py"]
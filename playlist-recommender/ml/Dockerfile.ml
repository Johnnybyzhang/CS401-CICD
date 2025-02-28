FROM quay.io/johnnybyzhang/uv-ml-base:latest
WORKDIR /app
COPY 2023_spotify_ds1.csv /app/data/dataset.csv
COPY train_model.py .
VOLUME /app/data
CMD ["uv", "run", "python", "train_model.py"]
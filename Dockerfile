FROM ubuntu:jammy AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get install -y software-properties-common gdal-bin libgdal-dev && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM base AS build

RUN pip install opencv-python

COPY . .

RUN pip install -r requirements.txt

FROM build AS runner


CMD ["python3", "main.py"]

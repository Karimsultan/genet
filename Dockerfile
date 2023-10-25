FROM python:3.11.4-bullseye

RUN apt-get update && \
apt-get upgrade -y && \
apt-get -y install gcc git libgdal-dev libgeos-dev libspatialindex-dev curl coinor-cbc &&  \
rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_17.x | bash -
RUN apt-get -y install nodejs && node --version && npm --version &&  \
rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --no-cache-dir --compile --upgrade pip

COPY . .

RUN pip3 install cmake>=3
RUN pip3 install --no-cache-dir --compile -e . && pip cache purge


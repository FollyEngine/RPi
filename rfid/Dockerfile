
# too painful - pyscard pip install needs gcc etc
#FROM python:2.7
FROM debian:stretch

WORKDIR /app

# get pyscard
RUN apt-get update \
    && apt-get install -yq python-pyscard python-pip pcscd git python-setuptools libpcsclite-dev python-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./main.py"]
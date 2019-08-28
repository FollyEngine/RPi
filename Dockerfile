FROM debian

RUN apt-get update -yq \
    && apt-get install -yq python3-pyscard python3-pip pcsc-tools pcscd git python3-setuptools libpcsclite-dev python3-dev \
			mosquitto-clients mosquitto scratch python-pygame \
			python3-serial python-serial python-pip python-pyscard \
			vim sudo

WORKDIR /src
COPY . /src

RUN ./setup.sh

CMD /bin/bash

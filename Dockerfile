FROM debian

RUN apt-get update -yq \
    && apt-get install -yq python3-pyscard python3-pip pcsc-tools pcscd git python3-setuptools libpcsclite-dev python3-dev \
			mosquitto-clients mosquitto scratch python-pygame \
			python3-serial python-serial python-pip python-pyscard \
			vim sudo

WORKDIR /src

# install the mqtt libs
COPY mqtt /src/mqtt/
RUN pip install --no-cache-dir -r /src/mqtt/requirements.txt \
    && pip3 install --no-cache-dir -r /src/mqtt/requirements.txt

# audio
COPY audio /src/audio/
RUN pip install --no-cache-dir -r /src/audio/requirements.txt \
    && pip3 install --no-cache-dir -r /src/audio/requirements.txt


# neopixels
COPY neopixels /src/neopixels/
RUN pip install --no-cache-dir -r /src/neopixels/requirements.txt \
    && pip3 install --no-cache-dir -r /src/neopixels/requirements.txt \
    && /src/neopixels/setup.sh


# and now the remainder of the modules
COPY . /src

#RUN ./setup.sh

CMD /bin/bash

FROM debian


# lets try only python3...
RUN apt-get update -yq \
    && apt-get install -yq python3-pip \
			mosquitto-clients \
			git vim sudo

WORKDIR /src

# install the mqtt libs
COPY mqtt /src/mqtt/
RUN pip3 install --no-cache-dir -r /src/mqtt/requirements.txt
COPY ping /src/ping/

COPY config.yml /src/
COPY run.py /src/
COPY *.sh /src/

RUN ./setup.sh

CMD /src/run.py

# not in the base image
#            python3-setuptools python3-dev \
# # neopixels
# COPY neopixels /src/neopixels/
# RUN pip install --no-cache-dir -r /src/neopixels/requirements.txt \
#     && pip3 install --no-cache-dir -r /src/neopixels/requirements.txt \
#     && /src/neopixels/setup.sh


# for RFID:
# python3-pyscard pcsc-tools pcscd libpcsclite-dev python-pyscard

# for audio:
# scratch python-pygame

# serial?
# python3-serial python-serial


# # and now the remainder of the modules
# COPY . /src

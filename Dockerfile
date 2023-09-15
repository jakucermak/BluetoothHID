FROM debian:bullseye

RUN apt-get update && apt-get install -y \
								bluez \
								dbus \
								python3 \
								pip \
								python3-dbus \
								procps \
								sudo 

WORKDIR /usr/src/hid
COPY ./src/ ./
COPY ./entrypoint.sh ./

RUN pip install -r requirements.txt

# COPY ./src/pi.conf /etc/dbus-1/system.d/
COPY ./src/config/bluetooth/org.jc.btkbservice.conf /etc/dbus-1/system.d/
RUN useradd -m pi && adduser pi sudo

RUN passwd -d pi

USER pi

ENTRYPOINT [ "./entrypoint.sh" ]

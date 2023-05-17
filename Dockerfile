FROM python:3.9-bullseye

RUN apt-get update && apt-get install -y \
								bluez \
								dbus \
								pip

WORKDIR /usr/src/hid
COPY ./* ./

RUN pip install -r requirements.txt

CMD ./entrypoint.sh
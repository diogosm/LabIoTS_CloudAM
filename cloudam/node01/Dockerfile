FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV NODE_ID=${NODE_ID}
ENV NAME=${NAME}

## add netem pro pumba
MAINTAINER LABIOTS/UFAM

RUN sed 's/archive.ubuntu.com/mirror.ufam.edu.br/g' -i /etc/apt/sources.list; \
	sed 's/security.ubuntu.com/mirror.ufam.edu.br/g' -i /etc/apt/sources.list; \
	apt-get update && apt-get install -y --no-install-recommends cron; \
    ln -fs /usr/share/zoneinfo/America/Manaus /etc/localtime; \
    echo "America/Manaus" > /etc/timezone; \
    dpkg-reconfigure -f noninteractive tzdata;

RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive; \
	apt-get install -y iproute2 iputils-ping; \
    apt-get clean;


CMD ["python", "main.py"]


FROM debian:bookworm-slim

RUN apt update && apt install -y tzdata sane-utils scanbd

RUN mkdir -p /etc/scanbd/scripts

ADD scanbd.conf /etc/scanbd/
ADD scan.sh /etc/scanbd/scripts/
ADD run.sh /

CMD ["/run.sh"]

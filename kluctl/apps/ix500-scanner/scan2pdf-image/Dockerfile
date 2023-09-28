FROM jbarlow83/ocrmypdf:v14.4.0

USER root

RUN apt-get update \
	&& apt-get install -y tzdata img2pdf inotify-tools exactimage \
	&& rm -rf /var/lib/apt/lists/*

ADD *.sh /usr/bin/

ENV INPUT_DIR=/pdfs/tiffs
ENV OUTPUT_DIR=/pdfs/pdfs
ENV ARCHIVE_DIR=/pdfs/archive
ENV START_MARKER=.scan-done
ENV DONE_MARKER=.pdf-done

ENTRYPOINT []
CMD ["run.sh"]

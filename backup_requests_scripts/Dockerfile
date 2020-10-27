FROM ubuntu:latest
RUN mkdir -p /scripts
WORKDIR scripts
RUN apt-get update && apt-get install python3 -y && apt-get install iputils-ping -y
COPY . .
ENTRYPOINT ["/bin/bash"]
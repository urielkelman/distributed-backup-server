FROM ubuntu:latest
RUN mkdir -p /scripts
WORKDIR scripts
RUN apt-get update && apt-get install python3 -y
COPY register_node.py .
COPY unregister_node.py .
COPY consult_backups.py .
COPY client_test.py .
ENTRYPOINT ["/bin/bash"]
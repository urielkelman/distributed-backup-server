FROM python:3.8
RUN mkdir -p /scripts
WORKDIR scripts
COPY . .
RUN pip install tabulate
ENTRYPOINT ["/bin/bash"]
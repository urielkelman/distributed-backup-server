import sys

USAGE_MESSAGE = '''usage: python3 docker_compose_generator -c N -w N -wp N
                    Arguments:
                    -c N: N is the number of company servers that exists in the cluster.
                    -w N: N is the number of backup workers that will handle backups.
                    -wp N: N is the number of processes that will run concurrently in each backup worker. '''

FILE_NAME = "docker-compose-dev.yaml"

INITIAL_SEGMENT_DOCKER_COMPOSE = '''version: '3'
services:
  server:
    container_name: backup_server
    image: backup-server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - SERVER_IP=backup_server
      - BACKUP_REQUESTS_PORT=12345
      - NODE_REGISTER_PORT=12346
      - BACKUP_INFO_PORT=12347
      - SERVER_LISTEN_BACKLOG=5
    networks:
      - company_net
    volumes:
    - "./volumes/backup_server:/backups"
      '''

COMPANY_SEGMENT_DOCKER_COMPOSE = '''
  company_server_{0}:
    container_name: company_server_{0}
    image: company-server:latest
    entrypoint: python3 /main.py
    environment:
      - BACKUP_REQUESTS_PORT=12345
      - COMPANY_LISTEN_BACKLOG=5
    networks:
      - company_net
    volumes:
    - "./volumes/company_server_{0}:/files"
    '''

BACKUP_WORKERS_SEGMENT_DOCKER_COMPOSE = '''
  backuper_worker_{0}:
    container_name: backuper_worker_{0}
    image: backuper-worker:latest
    entrypoint: python3 /main.py
    environment:
      - SERVER_IP=backup_server
      - SERVER_NODE_REGISTER_PORT=12346
      - WORKER_ALIAS=backuper_worker_{0}
      - WORKER_INITIAL_PORT=12345
      - WORKER_PROCESSES={1}
      - WORKER_LISTEN_BACKLOG=5
      - LAST_BACKUP_FILES=10
    networks:
      - company_net
    volumes:
    - "./volumes/backupers/worker_{0}:/backups"
    depends_on:
      - server
      '''

FINAL_SEGMENT_DOCKER_COMPOSE = '''
networks:
  company_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24'''


def generate_file(number_of_company_servers, number_of_backup_workers,
                  number_of_processes_by_worker):
    with open(FILE_NAME, "w") as docker_compose_file:
        docker_compose_file.write(INITIAL_SEGMENT_DOCKER_COMPOSE)
        for x in range(number_of_company_servers):
            docker_compose_file.write(COMPANY_SEGMENT_DOCKER_COMPOSE.format(x + 1))
        for x in range(number_of_backup_workers):
            docker_compose_file.write(
                BACKUP_WORKERS_SEGMENT_DOCKER_COMPOSE.format(x + 1, number_of_processes_by_worker))
        docker_compose_file.write(FINAL_SEGMENT_DOCKER_COMPOSE)


def main():
    if len(sys.argv) != 7 or sys.argv[1] != '-c' or sys.argv[3] != '-w' or sys.argv[5] != '-wp':
        print(USAGE_MESSAGE)
    else:
        try:
            number_of_company_servers = int(sys.argv[2])
            number_of_backup_workers = int(sys.argv[4])
            number_of_processes_by_worker = int(sys.argv[6])
            generate_file(number_of_company_servers, number_of_backup_workers,
                          number_of_processes_by_worker)
        except ValueError:
            print(USAGE_MESSAGE)


if __name__ == "__main__":
    main()

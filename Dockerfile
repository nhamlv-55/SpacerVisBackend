FROM ubuntu:18.04
#folder structure
#/SpacerBackend/
#├── chc-tools
#├── Dockerfile
#├── pobvis
#│   └── app
#│       ├── exp_db
#│       ├── main.py
#│       ├── media
#│       ├── reinit_db.sh
#│       ├── settings.py
#│       ├── start_server.sh
#│       └── utils
#└── z3s
RUN apt update && apt install -y wget unzip
RUN wget https://github.com/Z3Prover/z3/releases/download/z3-4.8.9/z3-4.8.9-x64-ubuntu-16.04.zip -O z3s.zip
RUN unzip z3s.zip -d z3s/
#install other stuffs
RUN apt update && apt install -y vim python3-pip apt-transport-https

COPY ./pobvis /SpacerBackend/pobvis
COPY ./chc-tools /SpacerBackend/chc-tools

RUN pip3 install -r /SpacerBackend/chc-tools/requirements.txt
RUN pip3 install -r /SpacerBackend/pobvis/requirements.txt
RUN bash /SpacerBackend/pobvis/app/reinit_db.sh
ENV PYTHONPATH "${PYTHONPATH}:/SpacerBackend/chc-tools:/SpacerBackend/z3s/NhamZ3/build/python"
WORKDIR /SpacerBackend/pobvis/app/

ENTRYPOINT python3 main.py -z3 /z3s/bin/z3 

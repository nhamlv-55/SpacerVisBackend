FROM ubuntu:18.04
RUN apt update && apt install -y vim python3-pip 
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
COPY ./z3 /SpacerBackend/z3s/NhamZ3
COPY ./pobvis /SpacerBackend/pobvis
COPY ./chc-tools /SpacerBackend/chc-tools
RUN pip3 install -r /SpacerBackend/chc-tools/requirements.txt
RUN pip3 install -r /SpacerBackend/pobvis/requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/SpacerBackend/chc-tools:/SpacerBackend/z3s/NhamZ3/build/python"
WORKDIR /SpacerBackend/pobvis/app/

docker run -dit --network="host" -p 5000:5000 --name SpacerBackend levn/spacer_backend:latest
cd pobvis/
docker cp requirements.txt SpacerBackend:/SpacerBackend/pobvis/requirements.txt
docker exec -it SpacerBackend bash -c "pip3 install -r /SpacerBackend/pobvis/requirements.txt"
cd app/
docker cp main.py SpacerBackend:/SpacerBackend/pobvis/app/main.py
docker cp .env SpacerBackend:/SpacerBackend/pobvis/app/.env
docker exec -it SpacerBackend bash -c "python3 main.py -z3 /SpacerBackend/z3s/NhamZ3/build/z3"


This is the backend server to use with the frontend hosted [here](https://nhamlv-55.github.io/saturation-visualization/#/)

__Note__: because of the docker network interface on Mac, this instruction only works on Linux.
# Using Docker
## 1. Start the container

```
 docker run -dit --network="host" -p 5000:5000 --name SpacerBackend levn/spacer_backend:latest

```
(However, I recommend trying the `dev` image for the latest features and bug fixes
```
 docker run -dit --network="host" -p 5000:5000 --name SpacerBackend levn/spacer_backend:latest

```
Arguments breakdown:
```
-dit: to run the container in detached mode.
--network="host": map docker's localhost to the host
--name: name the container for easy management
-p: to map the port 5000 of host to container's. The frontend access the server through port 5000, so this is needed.

```
## 2.a. Start the backend server, using the default z3 
```
 docker exec -it SpacerBackend bash -c "python3 main.py -z3 /SpacerBackend/z3s/NhamZ3/build/z3"
``` 
Arguments breakdown:
```
-z3: path to the z3 binary, relative to the container's folder structure.
The folder structure inside the container:
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
```
To stop the server, just hit Ctrl-C
## 2.b. Start the backend server, using your customed Z3
For example, you have your own Z3 at `~/opt/z3squashed/`, your binary is at `~/opt/z3squashed/build/z3`
```
 docker cp ~/opt/z3squashed/ SpacerBackend:/SpacerBackend/z3s/
 docker exec -it SpacerBackend bash -c "python3 main.py -z3 /SpacerBackend/z3s/z3squashed/build/z3"
```

## 3. Update the image to the latest version
When the backend is updated, you can update it as follows:
### 3.1 Backup the current database
Before updating the image, we should backup the current database.

Assume that we want to backup the database to `/home/workspace/`
```
docker cp SpacerBackend:/SpacerBackend/exp_db /home/workspace/
docker cp SpacerBackend:/SpacerBackend/media /home/workspace/
```
### 3.2 Update the image
```
docker kill SpacerBackend
docker rm SpacerBackend
docker run -dit --network="host" -p 5000:5000 --name SpacerBackend levn/spacer_backend:latest
```
Then re run the server using either 2.a or 2.b. 
### 3.3 Recover the database (if we backed it up earlier using 3.1)
```
docker cp /home/workspace/exp_db SpacerBackend:/SpacerBackend/exp_db
docker cp /home/workspace/media/ SpacerBackend:/SpacerBackend/
```



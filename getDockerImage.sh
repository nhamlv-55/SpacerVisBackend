if [ "$#" -ne 1 ]; then
    echo "usage: ./getDockerImage branch"
    exit 1
fi

docker run -dit --network="host" -p 5000:5000 --name SpacerBackend levn/spacer_backend:$1

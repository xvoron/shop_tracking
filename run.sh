#!/usr/bin/bash

DATAPATH=/usr/src/shopapp/data/
ERRMSG=$'[Error] Add a path to files in full path format.
\tExample: $./run.sh ~/path/to/directory/'


if [ -z $1 ]
then
    echo "$ERRMSG"
else
    echo "[Info] Path to files is $1"
    echo "[Info] Starting pytest"
    cd track/ && pytest -v . && cd ..
    cd visual/ && pytest -v . && cd .. \
    && echo "[Info] Test done"

    docker image build -t shop:visual visual/
    docker image build -t shop:track track/
    docker network create shopnet || echo "[Info] Network Done"
    docker run -d --network=shopnet -v $1:$DATAPATH --rm --name \
        shop_visual_container --user $(id -u):$(id -g) -it shop:visual
    docker run --network=shopnet -v $1:$DATAPATH --rm --name \
        shop_track_container --user $(id -u):$(id -g) -it shop:track
fi && echo "[Info] Video saved to $1"

#!/usr/bin/bash

DATAPATH=/usr/src/shopapp/data/

if [ -z $1 ]
then
    echo "[Error] Add a path to files"
else
    echo "[Info] Path to files is $1"
    docker image build -t shop:visual visual/ || \
        sudo docker image build -t shop:visual visual/

    docker image build -t shop:track track/ || \
        sudo docker image build -t shop:track track/

    docker network create shopnet || sudo docker network create shopnet || echo "[Info] Network Done"

    docker run --network=shopnet -v $1:$DATAPATH --rm --name \
        shop_visual_container -t shop:visual || \
    sudo docker run --network=shopnet -v $1:$DATAPATH --rm --name \
        shop_visual_container -t shop:visual


    docker run --network=shopnet -v $1:$DATAPATH --rm --name \
        shop_track_container -t shop:track || \
    sudo docker run --network=shopnet -v $1:$DATAPATH --rm --name \
        shop_track_container -t shop:track

fi

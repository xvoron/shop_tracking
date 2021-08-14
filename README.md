# Shop Tracking

# Install
Install docker form official repository:
- https://docs.docker.com/get-docker/

# Run
There are two options to run application using script `run.sh` or manually
enter commands line-by-line.

## Using `run.sh`
```bash
./run.sh ~/path/to/files/
```
## Manually

Build docker images of Visual and Tracking components; create a virtual
network to provide communication between them:
```bash
docker image build -t shop:visual visual/   # Build Visual component image
docker image build -t shop:track track/     # Build Tracking component image

docker network create shopnet   # Create a network to communication
```

Run images in the separate terminals; change **<~/path/to/data>**:
```bash
# terminal 1
docker run --network=shopnet -v <~/path/to/data>:/usr/src/shopapp/data/ --rm --name \
    shop_visual_container --user $(id -u):$(id -g) -it shop:visual

# terminal 2
docker run --network=shopnet -v <~/path/to/data>:/usr/src/shopapp/data/ --rm --name \
    shop_track_container --user $(id -u):$(id -g) -it shop:track
```

# Output
Output video file `shop_tracking_video.avi` is saved in
**<~/path/to/files/>**.

# Troubleshooting
## root privileges of output video file
```bash
sudo chown $(whoami):$(whoami) shop_tracking_video.avi
```

# Contacts
- artemvoronin95@gmail.com

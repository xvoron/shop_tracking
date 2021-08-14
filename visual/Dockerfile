FROM python:3.8-slim
LABEL maintainer="artemvoronin95@gmail.com"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
COPY . /tmp/
WORKDIR /usr/src/shopapp/
RUN mkdir -p /usr/src/shopapp/data/
COPY . .
EXPOSE 9999
#RUN usermod -u 1000 /usr/src/shopapp/data/shop_tracking_video.avi
#RUN usermod -G staff /usr/src/shopapp/data/shop_tracking_video.avi
ENTRYPOINT ["python3", "visual.py"]

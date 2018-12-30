FROM resin/raspberry-pi-alpine-node:8.0.0-slim
LABEL maintainer="utsavanand2@gmail.com"
COPY . /pod-status
WORKDIR /pod-status
RUN npm install
ENV NODE=kube-worker4
ENTRYPOINT ["node", "pod.js"]
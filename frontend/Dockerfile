FROM node:lts-alpine

ARG NITRO_PRESET=node-cluster

COPY docker-entrypoint.sh /usr/local/bin
COPY . /home/node

WORKDIR /home/node

RUN \
    apk add --no-cache --virtual .build-deps \
        git \
    && \
    npm install -g pnpm && \
    pnpm install --force && \
    pnpm build && \
    apk del --no-cache .build-deps

CMD ["node", ".output/server/index.mjs"]

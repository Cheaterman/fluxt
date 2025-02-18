FROM node:lts-alpine

ENV NITRO_UNIX_SOCKET=/run/nuxt.sock
# FIXME: listhen checks a different env var than nitro
ENV NITRO_SOCKET=/run/nuxt.sock
ENV NITRO_PRESET=node-cluster

COPY docker-entrypoint.sh /usr/local/bin
COPY . /home/node

WORKDIR /home/node

RUN \
    apk add --no-cache --virtual .build-deps \
        git \
    && \
    sh -c " \
        npm install -g pnpm && \
        pnpm install && \
        pnpm build \
    " && \
    apk del --no-cache .build-deps

CMD ["node", ".output/server/index.mjs"]

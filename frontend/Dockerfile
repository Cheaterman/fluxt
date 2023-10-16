FROM node:lts-alpine

ENV NITRO_UNIX_SOCKET=/run/nuxt.sock

COPY docker-entrypoint.sh /usr/local/bin
COPY . /home/node

WORKDIR /home/node

RUN sh -c " \
        npm install -g pnpm && \
        pnpm install && \
        NITRO_PRESET=node-cluster pnpm build \
    "

CMD ["node", ".output/server/index.mjs"]

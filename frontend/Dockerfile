FROM node:lts-alpine

ENV NITRO_UNIX_SOCKET=/run/nuxt.sock
# FIXME: listhen checks a different env var than nitro
ENV NITRO_SOCKET=/run/nuxt.sock
ENV NITRO_PRESET=node-cluster

COPY docker-entrypoint.sh /usr/local/bin
COPY . /home/node

WORKDIR /home/node

RUN sh -c " \
        npm install -g pnpm && \
        pnpm install && \
        pnpm build \
    "

CMD ["node", ".output/server/index.mjs"]

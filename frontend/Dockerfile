FROM node:alpine
COPY docker-entrypoint.sh /usr/local/bin
COPY . /home/node
WORKDIR /home/node
# See https://github.com/vercel/next.js/issues/30078#issuecomment-947338268
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN sh -c " \
        yarn install && \
        yarn build \
    "
CMD ["yarn", "start"]

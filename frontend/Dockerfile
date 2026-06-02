FROM node:lts-alpine AS build
ARG NITRO_PRESET=node-cluster
WORKDIR /build

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:lts-alpine
WORKDIR /app
COPY --from=build /build/.output .output

CMD ["node", ".output/server/index.mjs"]

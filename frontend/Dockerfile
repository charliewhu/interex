FROM node:18-alpine

# install pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /frontend

# copy dependencies to workdir
COPY package.json pnpm-lock.yaml /frontend/

# install dependencies as stated in lockfile
RUN pnpm install

# copy project to workdir
COPY . /frontend/

# build app
# RUN pnpm build

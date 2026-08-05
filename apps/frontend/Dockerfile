FROM node:22-bookworm-slim AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

FROM node:22-bookworm-slim AS builder

WORKDIR /app

ARG INTERNAL_API_URL=http://127.0.0.1:8000
ENV INTERNAL_API_URL=${INTERNAL_API_URL}

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

FROM node:22-bookworm-slim AS runner

ENV NODE_ENV=production

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install --omit=dev

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000

FROM node:22-bookworm-slim AS dev

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 3000

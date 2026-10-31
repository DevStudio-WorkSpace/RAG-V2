# Frontend Dockerfile (Next.js)
FROM node:20-alpine AS builder

WORKDIR /app

# URL pública de la API inyectada en tiempo de BUILD (code cliente Next.js)
ARG NEXT_PUBLIC_API_URL=/backend
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]

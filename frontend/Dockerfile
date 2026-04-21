# ── Stage 1: Builder ──────────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files first (better layer caching)
COPY package*.json ./
RUN npm ci --only=production

COPY . .

# ── Stage 2: Final image ──────────────────────────────────
FROM node:20-slim

WORKDIR /app

# Non-root user (node image has one built in)
COPY --from=builder /app /app
RUN chown -R node:node /app
USER node

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', r => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "src/index.js"]

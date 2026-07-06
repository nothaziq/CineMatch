FROM node:22-slim AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# PORT: Railway assigns this dynamically; defaults to 80 to match
# docker-compose.yml's "80:80" mapping when running locally.
# BACKEND_HOST: docker-compose's internal DNS name locally; override to
# "backend.railway.internal:8000" via a Railway service variable in prod.
ENV PORT=80
ENV BACKEND_HOST=backend:8000

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD sh -c "wget -q -O /dev/null http://localhost:${PORT}/ || exit 1"

# nginx's own image already templates /etc/nginx/templates/*.template ->
# /etc/nginx/conf.d/ via envsubst on startup (docker-entrypoint.d/20-envsubst...),
# substituting every $VAR it finds — which is why nginx.conf.template only
# uses ${PORT} and ${BACKEND_HOST} inside literal ${...} braces and never
# writes nginx's own $host/$remote_addr/etc. in that brace form.
CMD ["nginx", "-g", "daemon off;"]

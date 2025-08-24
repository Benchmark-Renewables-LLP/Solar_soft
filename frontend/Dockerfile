FROM node:20
WORKDIR /app/frontend
COPY package.json package-lock.json* ./
RUN npm ci --include=dev --silent
COPY . .
CMD ["npm", "run", "dev"]
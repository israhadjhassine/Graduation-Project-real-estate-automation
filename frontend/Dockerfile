# Use Node.js 20+ as required by Nuxt 4
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port Nuxt runs on
EXPOSE 3000

# Set environment variables for Nuxt
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Start the application in development mode
CMD ["npm", "run", "dev"]

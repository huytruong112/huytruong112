FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 3000

# Set environment for database path
ENV DB_PATH=/app/data/database.sqlite

# Start application
CMD ["node", "server.js"]

# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Install serve globally to serve the built files
RUN npm install -g serve

# Expose port (Railway will set PORT environment variable)
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "dist", "-l", "3000"]


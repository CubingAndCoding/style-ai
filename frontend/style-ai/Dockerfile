# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm install

# Copy source code
COPY . .

# Build the application with environment variables
# Vite needs these variables at build time to embed them in the static files
ARG VITE_STRIPE_PUBLISHABLE_KEY
ARG VITE_API_URL
ARG VITE_APP_NAME
ARG VITE_APP_VERSION

# Set environment variables for the build process
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_VERSION=$VITE_APP_VERSION

# Build the application
RUN npm run build

# Install serve globally to serve the built files
RUN npm install -g serve

# Remove dev dependencies to reduce image size
RUN npm prune --omit=dev

# Expose port (Railway will set PORT environment variable)
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "dist", "-l", "3000"]


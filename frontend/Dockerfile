# Use official lightweight Node image
FROM node:22-alpine

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the port Vite runs on
EXPOSE 5173

# Command to run the Vite dev server, exposing it to the network
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
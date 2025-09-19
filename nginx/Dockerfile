# Use the Nginx image from Docker Hub
FROM nginx:latest

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy a configuration file from the current directory
COPY nginx.conf /etc/nginx/conf.d/

# Optionally copy over static assets from your app build process
# COPY static_assets /usr/share/nginx/html/

# Expose ports
EXPOSE 80

# Start Nginx when the container has provisioned
CMD ["nginx", "-g", "daemon off;"]
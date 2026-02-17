# Pixel Notes Frontend - Dockerfile
# Flutter Web build

FROM dart:stable AS build

# Set working directory
WORKDIR /app

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git -b stable --depth 1 /flutter
ENV PATH="/flutter/bin:${PATH}"

# Enable web
RUN flutter config --enable-web

# Copy pubspec files
COPY pubspec.yaml pubspec.lock ./

# Get dependencies
RUN flutter pub get

# Copy source code
COPY . .

# Build web
RUN flutter build web --release

# Production stage with nginx
FROM nginx:alpine

# Copy built web app
COPY --from=build /app/build/web /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 58437

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

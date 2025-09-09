#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
npm install

# Create necessary directories if they don't exist
mkdir -p src/public/images

# Create placeholder images
echo "Creating placeholder images..."
# Logo placeholder
convert -size 200x100 -background transparent -fill "#e63946" -gravity center -font "Arial" label:"Rotax\nJetting Pro" src/public/images/logo-placeholder.png

# Hero image placeholder
convert -size 600x400 -background "#1d3557" -fill "#f1faee" -gravity center -font "Arial" -pointsize 24 label:"Rotax Kart Racing" src/public/images/hero-placeholder.png

# About image placeholder
convert -size 500x300 -background "#457b9d" -fill "#f1faee" -gravity center -font "Arial" -pointsize 20 label:"About Rotax Jetting Pro" src/public/images/about-placeholder.jpg

# Testimonial placeholders
convert -size 100x100 -background "#a8dadc" -fill "#1d3557" -gravity center -font "Arial" -pointsize 16 label:"User 1" src/public/images/testimonial-1.jpg
convert -size 100x100 -background "#a8dadc" -fill "#1d3557" -gravity center -font "Arial" -pointsize 16 label:"User 2" src/public/images/testimonial-2.jpg
convert -size 100x100 -background "#a8dadc" -fill "#1d3557" -gravity center -font "Arial" -pointsize 16 label:"User 3" src/public/images/testimonial-3.jpg

# Start the server
echo "Starting server..."
node src/backend/server.js
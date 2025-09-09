#!/bin/bash

# This script prepares and deploys the Rotax Jetting Pro application

# Set environment to production
export NODE_ENV=production

# Install dependencies
echo "Installing dependencies..."
npm install --production

# Build the application
echo "Building application..."
npm run build

# Create a deployment package
echo "Creating deployment package..."
mkdir -p deploy
cp -r src/backend deploy/
cp -r src/public deploy/
cp -r node_modules deploy/
cp package.json deploy/
cp .env deploy/

# Create a zip file of the deployment package
echo "Creating zip archive..."
cd deploy
zip -r ../rotax-jetting-pro.zip .
cd ..

echo "Deployment package created: rotax-jetting-pro.zip"
echo "You can now upload this package to your hosting provider."

# Instructions for different hosting options
echo ""
echo "Deployment Instructions:"
echo "1. For AWS Elastic Beanstalk:"
echo "   - Upload rotax-jetting-pro.zip through the AWS console"
echo "   - Or use the AWS CLI: aws elasticbeanstalk create-application-version --application-name RotaxJettingPro --version-label v1 --source-bundle S3Bucket=your-bucket,S3Key=rotax-jetting-pro.zip"
echo ""
echo "2. For Heroku:"
echo "   - Use the Heroku CLI: heroku create rotax-jetting-pro"
echo "   - git push heroku main"
echo ""
echo "3. For traditional hosting:"
echo "   - Upload and extract rotax-jetting-pro.zip to your server"
echo "   - Install Node.js if not already installed"
echo "   - Run 'npm start' to start the application"
echo "   - Consider using PM2 or similar for process management: pm2 start src/backend/server.js --name rotax-jetting-pro"
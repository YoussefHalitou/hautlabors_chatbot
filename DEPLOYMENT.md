# Deployment Guide for Haut Labor Chatbot

This guide explains how to deploy the Haut Labor Chatbot on Render.com.

## Prerequisites

Before deploying, make sure you have:
1. A Render.com account
2. OpenAI API key
3. Supabase project with database configured

## Environment Variables

You need to set the following environment variables in your Render.com dashboard:

### Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key

### Optional Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_DEBUG`: Set to `False` for production deployment

## Deployment Steps

### 1. Connect to Render.com

1. Go to [Render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository

### 2. Configure the Service

- **Name**: `haut-labor-chatbot` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Plan**: Free (or choose a paid plan for better performance)

### 3. Set Environment Variables

In the Render dashboard, go to your service settings and add the environment variables listed above.

### 4. Deploy

Click "Create Web Service" and wait for the deployment to complete.

## Local Development

To run the application locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_SERVICE_KEY=your_supabase_service_key_here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to `http://localhost:8080`

## Features

The deployed application includes:

- **Chatbot Widget**: Interactive chat interface for clinic inquiries
- **Image Upload**: Ability to upload skin images for analysis
- **AI Integration**: Powered by your existing clinic AI expert system
- **Responsive Design**: Works on desktop and mobile devices
- **Session Management**: Maintains conversation history per session

## Health Check

The application includes a health check endpoint at `/health` that returns a JSON response indicating the service status.

## Troubleshooting

### Common Issues

1. **Environment Variables Not Set**: Make sure all required environment variables are configured in Render.com
2. **Build Failures**: Check that all dependencies are listed in `requirements.txt`
3. **API Errors**: Verify that your OpenAI and Supabase credentials are correct

### Logs

Check the logs in your Render.com dashboard for any error messages or debugging information.

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive configuration
- The application includes CORS configuration for web security
- Image uploads are validated for file type and size

## Support

For issues with the deployment, check:
1. Render.com documentation
2. Application logs in the Render dashboard
3. Environment variable configuration 
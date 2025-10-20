# Heroku Deployment Guide

## Step 1: Install Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

## Step 2: Prepare for Heroku

1. **Create Procfile** (already included):
   ```
   web: python app.py
   ```

2. **Create runtime.txt** (already included):
   ```
   python-3.11.0
   ```

## Step 3: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create purple-patch-farms

# Set Python buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku master

# Open your app
heroku open
```

## Step 4: Configure Database
```bash
# Add PostgreSQL addon (free tier)
heroku addons:create heroku-postgresql:hobby-dev

# Check database URL
heroku config:get DATABASE_URL
```

## Heroku Benefits:
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy scaling
- ✅ Add-ons marketplace
- ✅ Git-based deployments

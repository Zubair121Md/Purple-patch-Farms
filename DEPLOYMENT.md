# Deployment Guide - Purple Patch Farms

This guide covers multiple deployment options for the Purple Patch Farms Cost Allocation System.

## Quick Deploy Options

### 1. Railway (Recommended - Easiest)

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up
2. **Connect Repository**: 
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository: `Zubair121Md/Purple-patch-Farms`
3. **Configure**:
   - Railway will auto-detect the `Procfile` and `railway.json`
   - Root Directory: Keep as `/` (root)
   - Build Command: Auto-detected from `railway.json`
   - Start Command: Auto-detected from `Procfile`
4. **Deploy**: Railway will automatically deploy and provide a URL

**Railway Settings:**
- Uses `Procfile` and `railway.json` automatically
- Environment variables: Set `PORT` (auto-set by Railway)
- Database: SQLite file persists in Railway's filesystem

---

### 2. Render

1. **Create Render Account**: Go to [render.com](https://render.com) and sign up
2. **New Web Service**:
   - Connect your GitHub repository
   - Select repository: `Zubair121Md/Purple-patch-Farms`
3. **Configure**:
   - **Name**: `purple-patch-farms`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `/` (keep default)
   - **Plan**: Free tier available
4. **Deploy**: Click "Create Web Service"

**Note**: Render.yaml is included for automated configuration.

---

### 3. Heroku

1. **Install Heroku CLI**: [Download here](https://devcenter.heroku.com/articles/heroku-cli)
2. **Login**:
   ```bash
   heroku login
   ```
3. **Create App**:
   ```bash
   heroku create purple-patch-farms
   ```
4. **Deploy**:
   ```bash
   git push heroku master
   ```
   (or `git push heroku main` if your branch is `main`)

**Heroku Settings:**
- Uses `Procfile` automatically
- `PORT` environment variable is auto-set
- Free tier: No longer available (paid plans only)

---

### 4. DigitalOcean App Platform

1. **Create Account**: Go to [digitalocean.com](https://www.digitalocean.com)
2. **Create App**:
   - Select your GitHub repository
   - Configure:
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Run Command**: `cd backend && python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
     - **Environment**: Python
     - **Plan**: Basic ($5/month minimum)
3. **Deploy**: Click "Create Resources"

---

### 5. VPS Deployment (Ubuntu/Debian)

1. **SSH into your server**:
   ```bash
   ssh user@your-server-ip
   ```

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx git
   ```

3. **Clone repository**:
   ```bash
   git clone https://github.com/Zubair121Md/Purple-patch-Farms.git
   cd Purple-patch-Farms
   ```

4. **Install Python dependencies**:
   ```bash
   cd backend
   pip3 install -r requirements.txt
   ```

5. **Run with PM2 (Process Manager)**:
   ```bash
   npm install -g pm2
   pm2 start "cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000" --name purple-patch
   pm2 save
   pm2 startup
   ```

6. **Configure Nginx** (optional, for domain):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Restart Nginx**:
   ```bash
   sudo systemctl restart nginx
   ```

---

## Environment Variables

Currently, no environment variables are required. The app uses:
- **Database**: SQLite (file-based, no setup needed)
- **Port**: Automatically set by hosting platform via `$PORT` or defaults to `8000`

---

## Post-Deployment

1. **Access the app**: Visit the URL provided by your hosting platform
2. **Upload data**: Use the Excel upload feature to import your sales data
3. **Upload P&L**: Use the P&L upload feature to import cost data
4. **Run allocation**: Click "Run Allocation" to generate reports

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure all dependencies are in `backend/requirements.txt` and installed correctly.

### Issue: Port already in use
**Solution**: Ensure `$PORT` environment variable is set by your hosting platform, or change the port in the start command.

### Issue: Database not persisting (Railway/Render)
**Solution**: For SQLite, the database file persists in the filesystem. For production, consider migrating to PostgreSQL.

### Issue: Build fails
**Solution**: Check build logs. Ensure Python version matches `runtime.txt` (3.11.9).

---

## Files Included

- `Procfile`: For Heroku/Railway
- `railway.json`: Railway-specific configuration
- `render.yaml`: Render-specific configuration
- `runtime.txt`: Python version specification
- `backend/requirements.txt`: All Python dependencies

---

## Support

For deployment issues, check:
- Railway: [docs.railway.app](https://docs.railway.app)
- Render: [render.com/docs](https://render.com/docs)
- Heroku: [devcenter.heroku.com](https://devcenter.heroku.com)

---

**Last Updated**: April 2025


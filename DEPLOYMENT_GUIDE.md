# 🚀 Purple Patch Farms - Deployment Guide

This guide covers multiple deployment options for the Purple Patch Farms Cost Allocation Dashboard.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Git** installed
- **Internet connection**
- **GitHub account** (for cloud deployments)

## 🏠 Option 1: Local Deployment (Recommended for Testing)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/Zubair121Md/Purple-patch-Farms.git
cd Purple-patch-Farms

# Run the deployment script
./deploy.sh
```

### Manual Setup
```bash
# Clone the repository
git clone https://github.com/Zubair121Md/Purple-patch-Farms.git
cd Purple-patch-Farms

# Install dependencies
cd backend
pip install -r requirements.txt

# Start the application
python app.py
```

**Access:** `http://localhost:8000`

---

## ☁️ Option 2: Railway Deployment (Easiest Cloud Option)

### Why Railway?
- ✅ **Free tier** available
- ✅ **Automatic HTTPS**
- ✅ **Easy GitHub integration**
- ✅ **Automatic deployments**

### Steps:
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your Purple-patch-Farms repository
6. Click "Deploy"

**Result:** Your dashboard will be live at a Railway URL!

---

## ☁️ Option 3: Heroku Deployment

### Why Heroku?
- ✅ **Free tier** available
- ✅ **Automatic HTTPS**
- ✅ **Easy scaling**
- ✅ **Add-ons marketplace**

### Steps:
```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# Or download from https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create purple-patch-farms

# Deploy
git push heroku master

# Open your app
heroku open
```

---

## ☁️ Option 4: DigitalOcean App Platform

### Why DigitalOcean?
- ✅ **Pay-as-you-scale** pricing
- ✅ **Automatic HTTPS**
- ✅ **Built-in monitoring**
- ✅ **Professional support**

### Steps:
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your GitHub account
4. Select your Purple-patch-Farms repository
5. Click "Create Resources"

**Result:** Your dashboard will be live at a DigitalOcean URL!

---

## 🖥️ Option 5: VPS Deployment (Advanced)

### Why VPS?
- ✅ **Full control**
- ✅ **Custom domain**
- ✅ **SSL certificates**
- ✅ **Cost-effective for high traffic**

### Steps:
1. **Setup Ubuntu/Debian server**
2. **Install dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv nginx -y
   ```
3. **Clone and setup:**
   ```bash
   git clone https://github.com/Zubair121Md/Purple-patch-Farms.git
   cd Purple-patch-Farms
   python3 -m venv venv
   source venv/bin/activate
   cd backend
   pip install -r requirements.txt
   ```
4. **Configure Nginx** (see VPS_DEPLOYMENT.md)
5. **Setup SSL** with Let's Encrypt

---

## 🔧 Configuration Files Included

The repository includes all necessary configuration files:

- **`Procfile`** - For Heroku deployment
- **`runtime.txt`** - Python version specification
- **`railway.json`** - Railway deployment config
- **`.do/app.yaml`** - DigitalOcean App Platform config
- **`deploy.sh`** - Local deployment script

---

## 🌐 Domain Setup (Optional)

### Custom Domain
1. **Purchase domain** from any registrar
2. **Point DNS** to your deployment platform
3. **Configure SSL** (automatic on most platforms)

### Subdomain Examples:
- `dashboard.purplepatchfarms.com`
- `costs.purplepatchfarms.com`
- `analytics.purplepatchfarms.com`

---

## 📊 Post-Deployment Checklist

### ✅ Verify Deployment
- [ ] Dashboard loads correctly
- [ ] All tabs work (Products, Sales, Costs, etc.)
- [ ] Charts display properly
- [ ] Add/Edit/Delete functions work
- [ ] Export functionality works
- [ ] Database reset works

### ✅ Security Considerations
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] Regular backups configured

### ✅ Performance Optimization
- [ ] Static files cached
- [ ] Database optimized
- [ ] CDN configured (if needed)
- [ ] Monitoring setup

---

## 🆘 Troubleshooting

### Common Issues:

#### **Port Already in Use**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

#### **Dependencies Not Installing**
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

#### **Database Issues**
```bash
# Reset database (if needed)
curl -X POST http://localhost:8000/api/reset-database
```

#### **Frontend Not Loading**
- Check browser console for errors
- Verify static files are served correctly
- Check CORS settings

---

## 📞 Support

### Getting Help:
1. **Check logs** in your deployment platform
2. **Review error messages** in browser console
3. **Test locally** first to isolate issues
4. **Create GitHub issue** for bugs

### Useful Commands:
```bash
# Check application status
ps aux | grep python

# View logs
tail -f /var/log/nginx/error.log  # VPS
heroku logs --tail                # Heroku
railway logs                      # Railway

# Test API endpoints
curl http://localhost:8000/api/products
```

---

## 🎯 Recommended Deployment Strategy

### For Development/Testing:
- **Local deployment** using `./deploy.sh`

### For Production (Small Scale):
- **Railway** (free tier, easy setup)

### For Production (Medium Scale):
- **DigitalOcean App Platform** (professional features)

### For Production (Large Scale):
- **VPS deployment** (full control, custom setup)

---

**Purple Patch Farms** - Growing Excellence, One Harvest at a Time 🌱

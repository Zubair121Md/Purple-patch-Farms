# VPS Deployment Guide (Ubuntu/Debian)

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv nginx -y

# Install Node.js (for frontend if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Step 2: Clone and Setup Application

```bash
# Clone repository
git clone https://github.com/Zubair121Md/Purple-patch-Farms.git
cd Purple-patch-Farms

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

## Step 3: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/purple-patch-farms

# Add this configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/purple-patch-farms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 4: Setup Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/purple-patch-farms.service

# Add this configuration:
[Unit]
Description=Purple Patch Farms Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Purple-patch-Farms/backend
Environment=PATH=/path/to/Purple-patch-Farms/venv/bin
ExecStart=/path/to/Purple-patch-Farms/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable purple-patch-farms
sudo systemctl start purple-patch-farms
```

## Step 5: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## VPS Benefits:
- ✅ Full control
- ✅ Custom domain
- ✅ SSL certificates
- ✅ Professional setup
- ✅ Cost-effective for high traffic

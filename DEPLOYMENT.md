# Deployment Guide

This guide covers deploying the REST API Library executable in production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Database Setup](#database-setup)
- [Deployment Methods](#deployment-methods)
- [Configuration](#configuration)
- [Running as a Service](#running-as-a-service)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+, CentOS 7+, macOS 10.15+
- **RAM**: 512 MB minimum, 1 GB recommended
- **Disk**: 100 MB for executable + database storage
- **Network**: Port 8000 (default) or custom port

### Database Requirements

Choose one:
- **SQLite**: Built-in, no installation needed
- **PostgreSQL**: Version 12+
- **MySQL/MariaDB**: Version 8.0+ / 10.5+

## Database Setup

### Option 1: SQLite (Simplest)

No setup required! SQLite is embedded in the executable.

```bash
# Configuration (.env file)
DATABASE_URL=sqlite:///./app.db
```

**Pros**: Zero configuration, portable  
**Cons**: Single connection, not ideal for high concurrency

### Option 2: PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE apidb;
CREATE USER apiuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE apidb TO apiuser;
\q
```

Configuration:
```env
DATABASE_URL=postgresql://apiuser:secure_password@localhost/apidb
```

### Option 3: MySQL

```bash
# Install MySQL
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
sudo systemctl start mysqld

# Create database and user
mysql -u root -p
CREATE DATABASE apidb;
CREATE USER 'apiuser'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON apidb.* TO 'apiuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Configuration:
```env
DATABASE_URL=mysql+pymysql://apiuser:secure_password@localhost/apidb
```

## Deployment Methods

### Method 1: Direct Execution

Simplest method for testing and small deployments.

```bash
# 1. Copy executable to server
scp dist/rest-api-library user@server:/opt/api/

# 2. SSH to server
ssh user@server

# 3. Create configuration
cd /opt/api
nano .env
# Add your DATABASE_URL and settings

# 4. Run
./rest-api-library
```

### Method 2: Systemd Service (Linux)

Run as a background service with auto-restart.

**Create service file** `/etc/systemd/system/rest-api.service`:

```ini
[Unit]
Description=REST API Library
After=network.target

[Service]
Type=simple
User=apiuser
WorkingDirectory=/opt/api
ExecStart=/opt/api/rest-api-library
Restart=always
RestartSec=10

# Environment
Environment="DATABASE_URL=postgresql://user:pass@localhost/apidb"
Environment="HOST=0.0.0.0"
Environment="PORT=8000"

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable rest-api
sudo systemctl start rest-api
sudo systemctl status rest-api
```

**Manage service:**

```bash
sudo systemctl stop rest-api      # Stop
sudo systemctl restart rest-api   # Restart
sudo systemctl status rest-api    # Check status
journalctl -u rest-api -f        # View logs
```

### Method 3: Docker Container

Even though we have an executable, you can containerize it:

**Dockerfile:**
```dockerfile
FROM ubuntu:22.04

WORKDIR /app
COPY dist/rest-api-library /app/
COPY .env.example /app/.env

RUN chmod +x /app/rest-api-library

EXPOSE 8000

CMD ["/app/rest-api-library"]
```

**Build and run:**
```bash
docker build -t rest-api-library .
docker run -d -p 8000:8000 --name api rest-api-library
```

## Configuration

### Environment Variables

Create `.env` file in the same directory as the executable:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/apidb

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# API
API_TITLE=My API
API_VERSION=1.0.0
```

### Production Settings

**Important**: Set `DEBUG=False` in production!

```env
DEBUG=False
HOST=0.0.0.0  # Listen on all interfaces
PORT=8000
```

## Running as a Service

### Linux (systemd) - Detailed

```bash
# 1. Create user for the service
sudo useradd -r -s /bin/false apiuser

# 2. Create directory structure
sudo mkdir -p /opt/api
sudo mkdir -p /var/log/api

# 3. Copy executable
sudo cp dist/rest-api-library /opt/api/
sudo chmod +x /opt/api/rest-api-library

# 4. Create .env file
sudo nano /opt/api/.env
# Add configuration

# 5. Set permissions
sudo chown -R apiuser:apiuser /opt/api
sudo chown -R apiuser:apiuser /var/log/api

# 6. Create systemd service (shown above)

# 7. Start
sudo systemctl start rest-api
```

## Security

### 1. Use Reverse Proxy

**Nginx** example:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Apache** example:

```apache
<VirtualHost *:80>
    ServerName api.example.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

### 2. Enable HTTPS

Use **Certbot** for free SSL:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.example.com
```

### 3. Firewall Rules

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 4. Database Security

- Use strong passwords
- Enable SSL connections
- Restrict database user permissions
- Regular backups

```sql
-- PostgreSQL: Restrict permissions
REVOKE ALL ON DATABASE apidb FROM apiuser;
GRANT CONNECT ON DATABASE apidb TO apiuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO apiuser;
```

### 5. Application Security

```env
# .env - Production settings
DEBUG=False  # Never True in production!
DATABASE_URL=postgresql://...  # Use connection pooling
```

## Monitoring

### 1. Health Checks

```bash
# Check if API is running
curl http://localhost:8000/health

# Automated monitoring
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart rest-api
```

### 2. Log Monitoring

**systemd logs:**
```bash
journalctl -u rest-api -f
journalctl -u rest-api --since today
journalctl -u rest-api -p err
```

**File-based logs:**
```bash
tail -f /var/log/api/output.log
tail -f /var/log/api/error.log
```

### 3. Performance Monitoring

Use tools like:
- **htop** - System resources
- **pg_stat_statements** - PostgreSQL queries
- **Prometheus + Grafana** - Metrics visualization

### 4. Uptime Monitoring

External services:
- UptimeRobot
- Pingdom
- StatusCake

## Load Balancing

For high traffic, run multiple instances:

### Nginx Load Balancer

```nginx
upstream api_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://api_backend;
    }
}
```

Run multiple instances:
```bash
# Instance 1
PORT=8001 ./rest-api-library &

# Instance 2
PORT=8002 ./rest-api-library &

# Instance 3
PORT=8003 ./rest-api-library &
```

## Backup and Recovery

### Database Backups

**PostgreSQL:**
```bash
# Backup
pg_dump -U apiuser apidb > backup.sql

# Automated daily backup
0 2 * * * pg_dump -U apiuser apidb > /backups/api-$(date +\%Y\%m\%d).sql
```

**MySQL:**
```bash
# Backup
mysqldump -u apiuser -p apidb > backup.sql

# Automated
0 2 * * * mysqldump -u apiuser -p apidb > /backups/api-$(date +\%Y\%m\%d).sql
```

### Application Backups

```bash
# Backup configuration
cp /opt/api/.env /backups/env-$(date +%Y%m%d)

# Backup SQLite database (if using)
cp /opt/api/app.db /backups/db-$(date +%Y%m%d).db
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl -u rest-api -n 50

# Check permissions
ls -la /opt/api
namei -l /opt/api/rest-api-library

# Test manually
sudo -u apiuser /opt/api/rest-api-library
```

### Database Connection Errors

```bash
# Test connection
psql -U apiuser -d apidb -h localhost

# Check DATABASE_URL format
# PostgreSQL: postgresql://user:pass@host/db
# MySQL: mysql+pymysql://user:pass@host/db
# SQLite: sqlite:///./app.db

# Verify database is running
sudo systemctl status postgresql
sudo systemctl status mysql
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process or change port
PORT=8001 ./rest-api-library
```

### High Memory Usage

```bash
# Check memory
free -h
ps aux | grep rest-api

# Restart service
sudo systemctl restart rest-api
```

## Updating

### Update Executable

```bash
# 1. Stop service
sudo systemctl stop rest-api

# 2. Backup current version
cp /opt/api/rest-api-library /opt/api/rest-api-library.backup

# 3. Copy new version
cp dist/rest-api-library /opt/api/

# 4. Restart service
sudo systemctl start rest-api

# 5. Verify
curl http://localhost:8000/health
```

### Rollback

```bash
# Restore backup
sudo systemctl stop rest-api
cp /opt/api/rest-api-library.backup /opt/api/rest-api-library
sudo systemctl start rest-api
```

## Best Practices

1. ✅ Always set `DEBUG=False` in production
2. ✅ Use a reverse proxy (Nginx/Apache)
3. ✅ Enable HTTPS with valid certificates
4. ✅ Regular database backups
5. ✅ Monitor logs and health endpoints
6. ✅ Use strong database passwords
7. ✅ Keep firewall rules restrictive
8. ✅ Run service as non-root user
9. ✅ Set up monitoring and alerts
10. ✅ Document your deployment

## Next Steps

- Set up monitoring
- Configure backups
- Implement CI/CD
- Add rate limiting
- Set up logging aggregation

For more information, see:
- [README.md](README.md) - General documentation
- [BUILD.md](BUILD.md) - Building executables
- [QUICKSTART.md](QUICKSTART.md) - Getting started

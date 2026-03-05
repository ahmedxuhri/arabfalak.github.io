# Auto-Deployment Setup for arabfalak.com

## Overview
The website is now set up to automatically deploy changes to GitHub Pages whenever posts are generated or changes are made.

## How It Works

### Systemd Service & Timer
- **Service**: `arabfalak-deploy.service` - Runs the deployment script
- **Timer**: `arabfalak-deploy.timer` - Triggers the service automatically

### Deployment Schedule
- Runs **5 minutes after system boot**
- Then runs **every 1 hour** to check for and deploy any changes
- Only commits and pushes if there are actual changes (no empty commits)

## Files Created

```
/root/arabfalak/scripts/deploy.sh                   # Deployment script
/etc/systemd/system/arabfalak-deploy.service       # Systemd service unit
/etc/systemd/system/arabfalak-deploy.timer         # Systemd timer unit
```

## Commands to Manage Deployment

### View timer status
```bash
sudo systemctl status arabfalak-deploy.timer
sudo systemctl list-timers arabfalak-deploy.timer
```

### View deployment logs
```bash
sudo journalctl -u arabfalak-deploy.service -f
sudo journalctl -u arabfalak-deploy.timer -f
```

### Manually trigger deployment
```bash
sudo systemctl start arabfalak-deploy.service
```

### Disable/Enable automatic deployment
```bash
sudo systemctl disable arabfalak-deploy.timer
sudo systemctl enable arabfalak-deploy.timer
```

## Workflow

1. **Post Generated** → `generate_post.py` creates new post files
2. **Changes Detected** → `arabfalak-deploy.timer` runs at scheduled times
3. **Auto-Deploy** → `arabfalak-deploy.service` commits and pushes to GitHub
4. **Live Site Updates** → GitHub Pages deploys changes automatically

## Manual Deployment

You can still use the existing publish script manually:
```bash
/root/arabfalak/scripts/publish.sh "Custom commit message"
```

## Git Configuration

The deployment script uses these git credentials:
- Author: GitHub Copilot
- Email: 223556219+Copilot@users.noreply.github.com

These are configured in the systemd service environment variables.

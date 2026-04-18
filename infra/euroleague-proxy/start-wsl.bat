@echo off
wsl -u root -e bash -c "systemctl start tinyproxy tailscaled"

#!/bin/bash
# install_surface_dial_daemon.sh
# Installs the Surface Dial Daemon as a systemd service (system-wide, for public use)
set -e

SERVICE_NAME=surface_dial.service
INSTALL_DIR=/opt/surface_dial

# 1. Copy project files to /opt/surface_dial
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r ./* "$INSTALL_DIR/"

# 2. Install Python dependencies if requirements.txt exists
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    sudo python3 -m pip install --upgrade pip
    sudo python3 -m pip install -r "$INSTALL_DIR/requirements.txt"
fi

# 3. Copy the systemd service file
sudo cp "$INSTALL_DIR/$SERVICE_NAME" "/etc/systemd/system/$SERVICE_NAME"

# 4. Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Surface Dial Daemon installed and started."

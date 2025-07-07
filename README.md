# Surface Dial Music

This project provides a systemd daemon for controlling music/media playback and system volume with the surface dial.

## Features

- **Rotate** the dial to adjust system volume
- **Tap** the dial to play/pause music or media
- **Double-tap** the dial to skip to the next song or media track

## Installation

1. Clone and Install

```sh
# Clone the repository and run the install script
 git clone https://github.com/jarvisMonke/surface_dial.git
 cd surface_dial
 ./install_surface_dial_daemon.sh
```

This will:

- Copy the project to `/opt/surface_dial`
- Install Python dependencies (if `requirements.txt` exists)
- Install and enable the systemd service

2. Service Management

- Start: `sudo systemctl start surface_dial.service`
- Stop: `sudo systemctl stop surface_dial.service`
- Status: `sudo systemctl status surface_dial.service`
- Enable on boot: `sudo systemctl enable surface_dial.service`

## Uninstall

```sh
sudo systemctl stop surface_dial.service
sudo systemctl disable surface_dial.service
sudo rm /etc/systemd/system/surface_dial.service
sudo rm -rf /opt/surface_dial
sudo systemctl daemon-reload
```

## Notes

- The service runs as root by default. To run as a specific user, edit the `User=` line in `surface_dial.service`.
- Make sure your user has access to input devices (may require adding to the `input` group).
- The `Environment=PYTHONUNBUFFERED=1` line in the service file is optional; it ensures logs are written immediately. You can remove it if you don't need unbuffered output.

## License

MIT

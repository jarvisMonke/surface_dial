
import evdev
from evdev import InputDevice, ecodes
import subprocess
import dbus
import time
import os
import notify2

# Initialize variables for volume adjustment

volume_step = 3  # Adjust the volume increment/decrement step as needed

# Time threshold for double tap (in seconds)
DOUBLE_TAP_THRESHOLD = 0.5

volume_step = 5

def notify(title, message):
    notify2.init("Surface Dial Monitor")
    n = notify2.Notification(title, message)
    n.set_timeout(5000)  # Set timeout to 5 seconds
    n.show()
    
def parse_input_devices():
    devices = []
    device = {}
    
    with open('/proc/bus/input/devices', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                if device:
                    devices.append(device)
                    device = {}
            elif line.startswith('I:'):
                device['info'] = line
            elif line.startswith('N:'):
                device['name'] = line.split('=')[1].strip('"')
            elif line.startswith('P:'):
                device['phys'] = line.split('=')[1].strip('"')
            elif line.startswith('H:'):
                device['handlers'] = line.split('=')[1].split()
            elif line.startswith('B:'):
                if 'bits' not in device:
                    device['bits'] = []
                device['bits'].append(line)
        if device:
            devices.append(device)
    return devices

def find_surface_dial_proc():
    devices = parse_input_devices()
    for device in devices:
        if 'Surface Dial' in device['name']:
            handlers = device.get('handlers', [])
            for handler in handlers:
                if handler.startswith('event'):
                    return f'/dev/input/{handler}'
    return None


def find_media_player_service():
    bus = dbus.SessionBus()
    for service in bus.list_names():
        if ".MediaPlayer" in service:
            print(service)
            return service
    return None

def toggle_play_pause(dbus_service):
    subprocess.run([
        "dbus-send",
        "--print-reply",
        "--dest=" + dbus_service,
        "/org/mpris/MediaPlayer2",
        "org.mpris.MediaPlayer2.Player.PlayPause",
    ])

def skip_next(service):
    subprocess.run(
        [
            "dbus-send",
            "--print-reply",
            "--dest={}".format(service),
            "/org/mpris/MediaPlayer2",
            "org.mpris.MediaPlayer2.Player.Next",
        ],
    )



# Function to adjust system volume
def adjust_volume(direction):
    # Replace this with your system-specific volume adjustment logic
    # Example: using amixer for ALSA-based systems
    import os
    if direction > 0:
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{volume_step}%"])
    else:
        os.system(f"amixer -D pulse sset Master {volume_step}%-")

      

# Event codes for Surface Dial events (replace with actual codes)
BTN_TAP = 0x100  
REL_DEL = 0x007
# Main event loop for Surface Dial
def handle_surface_dial_events(dial):
    volume_adjustment = 0
    last_rotation_time = time.time()
    rotation_accumulation_time = 0.1  # Adjust this time window as needed (in seconds)
    last_tap_time = 0
    for event in dial.read_loop():
        if event.type == ecodes.EV_KEY and event.code == BTN_TAP and event.value == 1:
            current_time = time.time()
            if current_time - last_tap_time < DOUBLE_TAP_THRESHOLD:
                print("Double tap detected")
                dbus_service = find_media_player_service()
                if dbus_service:
                    skip_next(dbus_service)
                else:
                    print("No media player service found")
            else:
                print("Single tap detected")
                dbus_service = find_media_player_service()
                if dbus_service:
                    toggle_play_pause(dbus_service)
                else:
                    print("No media player service found")
            last_tap_time = current_time

      
        elif event.type == ecodes.EV_REL and event.code == REL_DEL:
            # Accumulate rotation over a short period
            current_time = time.time()
            if current_time - last_rotation_time > rotation_accumulation_time:
                # Adjust volume based on accumulated rotation direction
                if volume_adjustment > 0:
                    adjust_volume(1)
                elif volume_adjustment < 0:
                    adjust_volume(-1)
                volume_adjustment = 0  # Reset volume adjustment after adjustment
                last_rotation_time = current_time  # Update last rotation time

            # Accumulate rotation direction
            if event.value > 0:
                volume_adjustment += 1
            elif event.value < 0:
                volume_adjustment -= 1

    
# Main function to initialize and run the daemon
def main():
    while True:
        device_path = find_surface_dial_proc()
        if device_path:
            notify("Surface Dial", "Connected")
            print(f"Surface Dial connected: {device_path}")
            dial = evdev.InputDevice(device_path)
            try:
                handle_surface_dial_events(dial)
            except KeyboardInterrupt:
                print("Daemon stopped by user.")
                break
            except Exception as e:
                print(f"Error handling events: {e}")
            finally:
                dial.close()
        else:
            print("Surface Dial not found. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
    
    



# XArm Move and Teach

A Python application for controlling xArm robotic arms using an Xbox controller with move and teach functionality.

## 🚀 Features

- **Manual Control**: Control xArm movement using Xbox controller joysticks
- **Step Mode**: Precise incremental movements
- **Velocity Mode**: Continuous velocity-based control
- **Teach Mode**: Record positions and create movement sequences
- **GOTO Mode**: Execute saved position sequences for pickup/dropoff operations
- **Gripper Control**: Open/close gripper using controller buttons

## 📋 Requirements

- xArm robotic arm
- Xbox controller
- Python 3.7+
- Required packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd XArm-move-teach
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update xArm IP address**:
   Edit `main.py` and change the IP address to match your xArm:
   ```python
   controller = XArmController(ip="192.168.1.210")  # Change this IP
   ```

## 🎮 Xbox Controller Layout

- **Left Stick**: X/Y axis movement
- **Right Stick**: Z axis (Y) and rotation (X) 
- **A Button**: Close gripper
- **B Button**: Open gripper
- **Back Button**: Stop/exit controller mode

## 🚀 Usage

Run the application:
```bash
python main.py
```

### Control Modes

1. **Manual Move Mode**:
   - Choose between Step or Velocity control
   - Adjust increment size (for step mode) or velocity
   - Use Xbox controller to move the arm
   - Press "Go Home" to return to home position

2. **Teach Mode**:
   - Start from home position
   - Use manual move to position the arm
   - Add positions to create a sequence
   - Save the sequence with a custom name

3. **GOTO Mode**:
   - Select saved position sequences
   - Execute pickup or dropoff operations
   - Automatically follows the recorded path

## 📁 Project Structure

```
XArm-move-teach/
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── xbox_controller.png         # Controller reference image
├── xArm positions.xlsx         # Saved positions database
└── src/
    └── XArm_move_teach/
        ├── __init__.py         # Package initialization
        ├── __about__.py        # Package metadata
        └── xarm_controller.py  # Main controller class
```

## 🎯 Configuration

### Home Position
The default home position is defined in `main.py`. Modify as needed:
```python
home_position = [-159.3, -193.5, 329.4, 180, 0, -90]
```

### Movement Parameters
- **Step Increment**: Default 5mm (adjustable in UI)
- **Velocity**: Default 100mm/s (adjustable in UI)
- **Gripper Positions**: 
  - Open: 850
  - Closed: 270

## 📊 Position Data

Taught positions are saved in `xArm positions.xlsx` with the following structure:
- Each column represents a named sequence
- Each cell contains position coordinates `[x, y, z, roll, pitch, yaw]`
- Reverse sequences are automatically generated for return paths

## 🔧 Safety Features

- **Home Position Return**: Always returns to safe home position when exiting
- **Manual Stop**: Xbox controller back button provides immediate stop
- **Position Validation**: Ensures arm stays within safe operating limits

## 🐛 Troubleshooting

### Common Issues

1. **No Xbox controller detected**:
   - Ensure controller is connected via USB
   - Check controller is recognized by the system

2. **Cannot connect to xArm**:
   - Verify IP address is correct
   - Check network connectivity
   - Ensure xArm is powered on and in ready state

3. **Position file not found**:
   - The Excel file is created automatically on first teach operation
   - Ensure write permissions in the project directory

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

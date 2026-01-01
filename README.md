# Human–Robot Interaction (HRI) xArm Drawing Robot

# NOTE: THIS REPO IS NOT THE MOST RECENT VERSION OF THE PROJECT
**Continue to for the most up to date version:https://github.com/harrymartens/AI-Robot-Artist**

Generative AI meets a 6‑axis xArm to draw, edit, and erase images on an acrylic canvas using AprilTag‑based alignment.

## 1) Requirements
- **OS**: macOS or Linux (Windows may work but is untested in this repo)
- **Python**: 3.10–3.12 recommended
- **Hardware**:
  - UFACTORY xArm with network access
  - USB camera pointed at the canvas
  - Optional gamepad/joystick for manual control
  - Four AprilTags (tag25h9 family) placed at the canvas corners
- **Accounts/API**:
  - OpenAI API key for image generation/editing

## 2) One‑line install (recommended)
From the repo root:

```bash
bash install.sh
```

What it does:
- Ensures Python 3 is installed
- On macOS, installs Homebrew dependencies including `portaudio` (needed for audio)
- Creates and activates `.venv`
- Prompts for and writes `OPENAI_API_KEY` to `.env`
- Installs `requirements.txt`

After it finishes, activate the environment when you start a new shell:

```bash
source .venv/bin/activate
```

## 3) Manual install (alternative)
```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the repo root with:

```bash
OPENAI_API_KEY=sk-...your_key...
```

### macOS notes
- If `PyAudio` fails to build, install PortAudio with Homebrew first:
  ```bash
  brew install portaudio
  ```
- If the camera doesn’t appear, grant Terminal full Camera permissions in System Settings → Privacy & Security → Camera.

## 4) Configure robot IP
- `scripts/xarm_remote_control.py` → `ROBOT_IP = "192.168.1.239"` for the big robot

Update both to your xArm’s IP. To reach the xArm web UI, connect via Ethernet and open:
`http://192.168.1.239:18333` (replace with your robot’s IP if different). Consider setting a static IP on your host Ethernet if needed.

## 5) Data and markers
- Place four AprilTags (`tag25h9` family) at the canvas corners. The `identifyMarkers.py` flow detects the tags and crops/perspective‑warps the canvas automatically.
- Example input images are under `Images/InputImages/`.

## 6) Running the main scripts
Activate the venv first: `source .venv/bin/activate`

### A) Generate and draw a new image
Generates via OpenAI, vectorizes, then draws with the robot.

```bash
python scripts/draw_image.py
```

Flow:
- Prompts: “What would you like to draw?”
- Shows the vectorized preview
- Moves the arm to safe positions and executes drawing

### B) Edit the existing drawing (erase → redraw)
Captures the current canvas, asks for an edit prompt, uses OpenAI image editing, erases, then redraws.

```bash
python scripts/edit_image.py
```

Flow:
- Attach eraser when prompted, then later re‑attach marker
- Camera capture → AprilTag crop → edit → vectorize → erase → draw

### C) Erase the canvas only

```bash
python scripts/erase_image.py
```

Prompts to attach the eraser, captures and crops the canvas, then performs a raster‑style erase pass.

### D) Voice/agent assistant (experimental)
Conversational assistant that can call tools to generate/edit drawings. Uses audio output with low‑latency TTS.

```bash
python scripts/agenticCreativeAssistant.py
```

Tip: On first run, macOS may ask for microphone and audio output permissions.

### E) Manual joystick control (optional)
Use a fightstick/PS4‑style controller to jog the arm.

```bash
python scripts/xarm_remote_control.py
```

You will be prompted to choose a profile. Ensure `ROBOT_IP` at the top of the file matches your robot.

## 7) Repository layout (high‑level)
- `scripts/` – entry points for drawing, editing, erasing, agent, and manual control
- `Utils/ImageGeneration/` – OpenAI image generation/editing
- `Utils/ImageToVectorConversion/` – image → line vector conversion and OpenCV helpers
- `Utils/PhotoCapture/` – camera capture and AprilTag‑based cropping
- `Utils/RoboticPathMovement/` – xArm control, motion planning, and configuration
- `Utils/UserInput/` – CLI input helpers

## 8) Troubleshooting
- **Robot doesn’t move / API errors**: Verify IP consistency between `robotConfig.py` and `xarm_remote_control.py`. Confirm the robot is reachable (ping its IP). Use the xArm web UI to clear faults and enable motion.
- **Singularity or non‑zero return codes**: The `RoboticArm.set_position` method retries via subdivided paths and joint‑space fallbacks. If persistent, reposition the arm to a safer pose in the xArm UI and retry.
- **Camera/AprilTags not detected**: Ensure four `tag25h9` AprilTags are visible and well‑lit. Adjust camera exposure. Confirm permissions on macOS.
- **PyAudio install issues**: Install `portaudio` (see macOS notes) and re‑install requirements in the venv.
- **OpenAI errors**: Check `.env` contains a valid `OPENAI_API_KEY` and you have network connectivity.

## 9) Quick start TL;DR
```bash
git clone <this repo>
cd HRIxArm
bash install.sh
source .venv/bin/activate
python scripts/draw_image.py
```

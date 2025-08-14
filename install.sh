#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Starting robot setup..."

# ─────────────────────────────────────────────────────────────
# 1. Ensure Python 3 is present (and Homebrew on macOS)
# ─────────────────────────────────────────────────────────────
install_python_macos() {
  # Install Homebrew if missing
  if ! command -v brew &>/dev/null; then
    echo "🍺 Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi

  # Make sure Python 3 and PortAudio headers/libs are available
  brew install python portaudio
}

install_python_linux() {
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip portaudio19-dev
}

if ! command -v python3 &>/dev/null; then
  echo "⚠️ Python3 not found. Installing..."
  case "$OSTYPE" in
    darwin*) install_python_macos ;;
    linux*)  install_python_linux ;;
    *)       echo "❌ Unsupported OS. Please install Python manually." && exit 1 ;;
  esac
else
  # For macOS ensure PortAudio even if Python already exists
  [[ "$OSTYPE" == darwin* ]] && install_python_macos
  [[ "$OSTYPE" == linux*  ]] && sudo apt install -y portaudio19-dev
fi

# ─────────────────────────────────────────────────────────────
# 2. Prompt for OpenAI API key if .env absent
# ─────────────────────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
  read -rp "🔑 Enter your OpenAI API key: " OPENAI_API_KEY
  echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
else
  echo "ℹ️ .env file already exists. Skipping API key prompt."
fi

# ─────────────────────────────────────────────────────────────
# 3. Create & activate virtual environment (.venv)
# ─────────────────────────────────────────────────────────────
VENV_DIR=".venv"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "🐍 Creating virtual environment in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# ─────────────────────────────────────────────────────────────
# 4. Install Python dependencies
# ─────────────────────────────────────────────────────────────
echo "📦 Installing requirements..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete. Activate the environment with:"
echo "   source $VENV_DIR/bin/activate"

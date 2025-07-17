#!/bin/bash
set -e

echo "🔧 Starting robot setup..."

# Step 1: Check/install Python
if ! command -v python3 &>/dev/null; then
  echo "⚠️ Python3 not found. Installing..."
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &>/dev/null; then
      echo "Homebrew not found. Installing..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
  else
    echo "❌ Unsupported OS. Please install Python manually."
    exit 1
  fi
fi

# Step 2: Set OpenAI API key
if [ ! -f ".env" ]; then
  echo "🔑 Enter your OpenAI API key:"
  read -r OPENAI_API_KEY
  echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
else
  echo "ℹ️ .env file already exists. Skipping API key prompt."
fi

# Step 3: Create and activate venv
if [ ! -d "venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

# Step 4: Install dependencies
echo "📦 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete. You can now run the application."

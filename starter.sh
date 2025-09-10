#!/bin/bash
set -e  # stop on first error

# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools and Python (system-wide)
sudo apt install -y python3.12-venv
sudo apt install build-essential cmake python3-dev

# Clone the project repo if not already present
if [ ! -d "/home/ubuntu/server-d-llm-inference" ]; then
    git clone https://github.com/Olasunkanmi-O/server-d-llm-inference.git /home/ubuntu/server-d-llm-inference
fi

# Create models directory
mkdir -p /home/ubuntu/server-d-llm-inference/models

# Install llama-cpp-python globally
#
#sudo pip3 install llama-cpp-python --break-system-packages

# Download the quantized model (if not already present)
MODEL_FILE="/home/ubuntu/server-d-llm-inference/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf \
        -O "$MODEL_FILE"
fi

echo " Setup complete. You can now run inference with llama-cpp-python or llama.cpp."

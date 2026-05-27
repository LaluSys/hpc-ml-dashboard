#!/bin/bash
# Einmalig auf dem Cluster ausführen, um ein user-venv mit extra packages anzulegen.
# Nutzung: bash setup_cluster_venv.sh
# Das venv wird unter ~/.ml-venv angelegt und von den Job-Templates automatisch aktiviert.

set -e

module load python/3.13.0/gcc-14.2.0

echo "Erstelle venv unter ~/.ml-venv ..."
python3 -m venv ~/.ml-venv
source ~/.ml-venv/bin/activate

echo "Installiere zusätzliche Pakete ..."
pip install --upgrade pip
pip install \
    datasets \
    accelerate \
    evaluate \
    peft \
    tqdm \
    wandb \
    matplotlib \
    seaborn \
    tensorboard

echo ""
echo "Fertig! Das venv wird automatisch von den Job-Templates aktiviert."
echo "Manuell aktivieren: source ~/.ml-venv/bin/activate"

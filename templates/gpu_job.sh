#!/bin/bash
#SBATCH --job-name={{ job_name }}
#SBATCH --partition=pub23gpu
#SBATCH --time={{ time }}
#SBATCH --mem={{ mem }}
#SBATCH --cpus-per-task={{ cpus }}
#SBATCH --output={{ workdir }}/logs/%j_{{ job_name }}.out
#SBATCH --error={{ workdir }}/logs/%j_{{ job_name }}.err

{% for mod in modules %}
module load {{ mod }}
{% endfor %}

{% if use_venv %}
[ -f ~/.ml-venv/bin/activate ] && source ~/.ml-venv/bin/activate
{% endif %}

echo "=== Job gestartet: $(date) ==="
echo "=== Node: $HOSTNAME ==="
echo "=== GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'n/a') ==="

python {{ script }} {{ args }}

echo "=== Job beendet: $(date) ==="

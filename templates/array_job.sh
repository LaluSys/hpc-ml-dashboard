#!/bin/bash
#SBATCH --job-name={{ job_name }}
#SBATCH --partition={{ partition }}
#SBATCH --array=0-7              # Anzahl der Array-Tasks anpassen
#SBATCH --time={{ time }}
#SBATCH --mem={{ mem }}
#SBATCH --cpus-per-task={{ cpus }}
#SBATCH --output={{ workdir }}/logs/%j_%a_{{ job_name }}.out
#SBATCH --error={{ workdir }}/logs/%j_%a_{{ job_name }}.err

{% for mod in modules %}
module load {{ mod }}
{% endfor %}

{% if use_venv %}
[ -f ~/.ml-venv/bin/activate ] && source ~/.ml-venv/bin/activate
{% endif %}

# Lernraten-Grid für Array-Job
LR_VALUES=(0.1 0.01 0.001 0.0001 0.00001 0.000001 0.0000001 0.00000001)
LR=${LR_VALUES[$SLURM_ARRAY_TASK_ID]}

echo "=== Array-Task ${SLURM_ARRAY_TASK_ID}: lr=${LR} ==="
echo "=== Node: $HOSTNAME, $(date) ==="

python {{ script }} --lr $LR {{ args }}

echo "=== Task beendet: $(date) ==="

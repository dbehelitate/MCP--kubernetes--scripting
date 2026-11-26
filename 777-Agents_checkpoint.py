'''
Some agents execute workflows that span hours or even days. 

The idea is simple.  
"Checkpointing for saving the intermediate results."

After completing each major step in the workflow, the agent saves
a checkpoint containing its current state and progress.

If pod crashes,
    agent resume from checkpoint 

This pattern is especially valuable on Kubernetes where pods are ephemeral
and can be rescheduled at any time.
'''

import json
from pathlib import Path


def save_checkpoint(step: int, state: dict):
    # Store checkpoints on a PersistentVolume mounted at /data
    checkpoint_dir = Path("/data/checkpoints")
    checkpoint_dir.mkdir(exist_ok=True)

    # Save state as JSON with a sequential step number
    (checkpoint_dir / f"step_{step:03d}.json").write_text(json.dumps(state))


def load_latest_checkpoint() -> tuple[int, dict]:
    checkpoint_dir = Path("/data/checkpoints")

    # Find all existing checkpoints and sort by filename
    checkpoints = sorted(checkpoint_dir.glob("step_*.json"))

    if not checkpoints:
        # Start from scratch if no checkpoints exist
        return 0, {}

    latest = checkpoints[-1]
    step = int(latest.stem.split("_")[1])
    return step, json.loads(latest.read_text())


'''
In your Kubernetes job manifest, configure pod with
restartPolicy:OnFailure 
and mount PersistentVolumeClaim to /data.

When pod starts: load_latest_checkpoint() 
to determine where to resume.

after processing a batch of documents or completing a phase 
save_checkpoint() to record progress. 

If the pod fails or is evicted, Kubernetes restarts it, 
and the agent picks up from checkpoint.

Inspect checkpoint directory to understand 
what the agent was thinking at each step.

    +-----------+  load_latest_checkpoint()  +---------------------+
    | Pod start | -------------------------> | PVC mounted at /data |
    +-----------+                            |  /checkpoints        |
          |                                  |   step_001.json      |
          v                                  |   step_002.json      |
    +-----------+  save_checkpoint()         |   step_003.json      |
    | Work step | -------------------------> |   ...                |
    +-----------+                            +---------------------+

    restartPolicy: OnFailure

    +-----+     +--------+     +-------------+     +-----------+
    | run | --> | save   | --> | FAIL / EVICT| --> | Kubernetes|
    |     |     | step N |     |             |     | restarts  |
    +-----+     +--------+     +-------------+     +-----------+
       ^                                                 |
       +------------ resume from step N

'''
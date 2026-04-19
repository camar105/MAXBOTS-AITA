# nanoGPT Phase

This folder contains the MAE301 Phase 2 deliverables for a small character-level GPT model inspired by the Karpathy nanoGPT workflow.

## Contents

- `model.py` - transformer model definition
- `train.py` - training and experiment runner
- `sample.py` - sample generation from a saved checkpoint
- `configs/experiments.json` - three experiment configurations
- `data/` - tiny Shakespeare dataset download location
- `outputs/` - metrics, checkpoints, plots, and generated samples
- `report.md` - experiment summary and reflection

## Dataset

The training script downloads the public-domain Tiny Shakespeare corpus automatically if it is not already present.

## Tokenization Strategy

This implementation is character-level. The vocabulary is built directly from the unique characters present in the dataset.

## Running Experiments

```powershell
python -m pip install -r requirements.txt
python train.py --all-configs
```

To train a single configuration:

```powershell
python train.py --config-name baseline
```

To sample from a checkpoint:

```powershell
python sample.py --config-name baseline --max-new-tokens 400
```

## Runtime Expectations

On the current CPU-only verification run, the measured runtimes were approximately:

- `baseline`: 7 seconds
- `wider`: 12 seconds
- `deeper_context`: 22 seconds

These numbers make the experiment set practical for local iteration without GPU access.

## Running Tests

```powershell
pytest
```

## Notes

- The experiments are sized to be CPU-friendly.
- Loss curves, metrics, checkpoints, and text samples are written to `outputs/`.
- The best validation loss from the completed experiment set was `2.2269` from the `wider` configuration.

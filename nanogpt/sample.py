from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from model import GPTConfig, NanoGPT


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate text from a trained nanoGPT checkpoint.")
    parser.add_argument("--config-name", required=True, help="Checkpoint prefix to load from outputs/.")
    parser.add_argument("--max-new-tokens", type=int, default=400, help="Number of characters to sample.")
    return parser.parse_args()


def load_checkpoint(config_name: str) -> dict[str, object]:
    checkpoint_path = OUTPUTS_DIR / f"{config_name}_checkpoint.pt"
    if not checkpoint_path.exists():
        raise SystemExit(f"Checkpoint not found: {checkpoint_path}")
    return torch.load(checkpoint_path, map_location="cpu")


def main() -> None:
    args = parse_args()
    checkpoint = load_checkpoint(args.config_name)
    model_config = GPTConfig(**checkpoint["model_config"])
    model = NanoGPT(model_config)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    itos = {int(key): value for key, value in checkpoint["itos"].items()}
    context = torch.zeros((1, 1), dtype=torch.long)
    sample_tokens = model.generate(context, max_new_tokens=args.max_new_tokens)[0].tolist()
    sample_text = "".join(itos[int(token)] for token in sample_tokens)
    print(sample_text)


if __name__ == "__main__":
    main()

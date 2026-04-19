from __future__ import annotations

import argparse
import json
import time
import urllib.request
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from torch import optim

from model import GPTConfig, NanoGPT


DATA_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CONFIG_PATH = BASE_DIR / "configs" / "experiments.json"
DATASET_PATH = DATA_DIR / "tinyshakespeare.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a tiny GPT model on Tiny Shakespeare.")
    parser.add_argument("--config-name", default="baseline", help="Name of the experiment config to run.")
    parser.add_argument("--all-configs", action="store_true", help="Run every config listed in experiments.json.")
    return parser.parse_args()


def load_experiments() -> dict[str, dict[str, int | float]]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def ensure_dataset() -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATASET_PATH.exists():
        urllib.request.urlretrieve(DATA_URL, DATASET_PATH)
    return DATASET_PATH.read_text(encoding="utf-8")


def build_vocab(text: str) -> tuple[dict[str, int], dict[int, str], torch.Tensor, torch.Tensor]:
    chars = sorted(set(text))
    stoi = {char: index for index, char in enumerate(chars)}
    itos = {index: char for char, index in stoi.items()}
    data = torch.tensor([stoi[char] for char in text], dtype=torch.long)
    split_index = int(0.9 * len(data))
    return stoi, itos, data[:split_index], data[split_index:]


def get_batch(split: str, train_data: torch.Tensor, val_data: torch.Tensor, config: dict[str, int | float], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    source = train_data if split == "train" else val_data
    block_size = int(config["block_size"])
    batch_size = int(config["batch_size"])
    indexes = torch.randint(len(source) - block_size, (batch_size,))
    x = torch.stack([source[index : index + block_size] for index in indexes])
    y = torch.stack([source[index + 1 : index + block_size + 1] for index in indexes])
    return x.to(device), y.to(device)


@torch.no_grad()
def estimate_loss(model: NanoGPT, train_data: torch.Tensor, val_data: torch.Tensor, config: dict[str, int | float], device: torch.device) -> dict[str, float]:
    model.eval()
    out: dict[str, float] = {}
    eval_iters = int(config["eval_iters"])
    for split in ("train", "val"):
        losses = torch.zeros(eval_iters)
        for iteration in range(eval_iters):
            inputs, targets = get_batch(split, train_data, val_data, config, device)
            _, loss = model(inputs, targets)
            losses[iteration] = loss.item()
        out[split] = round(losses.mean().item(), 4)
    model.train()
    return out


def decode(tokens: torch.Tensor, itos: dict[int, str]) -> str:
    return "".join(itos[int(token)] for token in tokens)


def plot_curve(config_name: str, history: list[dict[str, float]]) -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = OUTPUTS_DIR / f"{config_name}_curve.png"
    x_axis = [item["iteration"] for item in history]
    train_loss = [item["train_loss"] for item in history]
    val_loss = [item["val_loss"] for item in history]

    plt.figure(figsize=(7, 4))
    plt.plot(x_axis, train_loss, label="train")
    plt.plot(x_axis, val_loss, label="val")
    plt.xlabel("Iteration")
    plt.ylabel("Loss")
    plt.title(f"Loss Curve - {config_name}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_path)
    plt.close()
    return figure_path


def train_experiment(config_name: str, config: dict[str, int | float], text: str) -> dict[str, object]:
    torch.manual_seed(int(config["seed"]))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    stoi, itos, train_data, val_data = build_vocab(text)
    model_config = GPTConfig(
        vocab_size=len(stoi),
        block_size=int(config["block_size"]),
        n_embed=int(config["n_embed"]),
        n_head=int(config["n_head"]),
        n_layer=int(config["n_layer"]),
        dropout=float(config["dropout"]),
    )
    model = NanoGPT(model_config).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=float(config["learning_rate"]))

    history: list[dict[str, float]] = []
    max_iters = int(config["max_iters"])
    eval_interval = int(config["eval_interval"])
    start_time = time.perf_counter()

    for iteration in range(max_iters + 1):
        if iteration % eval_interval == 0 or iteration == max_iters:
            losses = estimate_loss(model, train_data, val_data, config, device)
            history.append(
                {
                    "iteration": iteration,
                    "train_loss": losses["train"],
                    "val_loss": losses["val"],
                }
            )
            print(f"[{config_name}] step {iteration}: train {losses['train']:.4f} | val {losses['val']:.4f}")

        inputs, targets = get_batch("train", train_data, val_data, config, device)
        _, loss = model(inputs, targets)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    elapsed_seconds = round(time.perf_counter() - start_time, 2)
    context = torch.zeros((1, 1), dtype=torch.long, device=device)
    sample_tokens = model.generate(context, max_new_tokens=int(config["max_new_tokens"]))[0].tolist()
    sample_text = decode(torch.tensor(sample_tokens), itos)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    curve_path = plot_curve(config_name, history)
    sample_path = OUTPUTS_DIR / f"{config_name}_sample.txt"
    sample_path.write_text(sample_text, encoding="utf-8")

    checkpoint_path = OUTPUTS_DIR / f"{config_name}_checkpoint.pt"
    torch.save(
        {
            "config_name": config_name,
            "config": dict(config),
            "model_config": asdict(model_config),
            "model_state": model.state_dict(),
            "stoi": stoi,
            "itos": itos,
        },
        checkpoint_path,
    )

    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    result = {
        "config_name": config_name,
        "device": str(device),
        "params": parameter_count,
        "elapsed_seconds": elapsed_seconds,
        "best_train_loss": min(item["train_loss"] for item in history),
        "best_val_loss": min(item["val_loss"] for item in history),
        "final_train_loss": history[-1]["train_loss"],
        "final_val_loss": history[-1]["val_loss"],
        "history": history,
        "curve_path": str(curve_path.relative_to(BASE_DIR)),
        "sample_path": str(sample_path.relative_to(BASE_DIR)),
        "checkpoint_path": str(checkpoint_path.relative_to(BASE_DIR)),
    }

    metrics_path = OUTPUTS_DIR / f"{config_name}_metrics.json"
    metrics_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def write_aggregate_summary(config_names: list[str] | None = None) -> list[dict[str, object]]:
    metrics_by_name: dict[str, dict[str, object]] = {}
    for metrics_path in OUTPUTS_DIR.glob("*_metrics.json"):
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        metrics_by_name[str(payload["config_name"])] = payload

    ordered_names = config_names or sorted(metrics_by_name)
    summary = [metrics_by_name[name] for name in ordered_names if name in metrics_by_name]
    summary_path = OUTPUTS_DIR / "experiment_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    experiments = load_experiments()
    text = ensure_dataset()

    config_names = list(experiments) if args.all_configs else [args.config_name]
    for name in config_names:
        if name not in experiments:
            raise SystemExit(f"Unknown config: {name}")

    summary: list[dict[str, object]] = []
    for name in config_names:
        summary.append(train_experiment(name, experiments[name], text))

    write_aggregate_summary(list(experiments))


if __name__ == "__main__":
    main()

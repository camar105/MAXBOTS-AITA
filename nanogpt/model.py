from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(slots=True)
class GPTConfig:
    vocab_size: int
    block_size: int
    n_embed: int
    n_head: int
    n_layer: int
    dropout: float = 0.1


class Head(nn.Module):
    def __init__(self, head_size: int, n_embed: int, block_size: int, dropout: float) -> None:
        super().__init__()
        self.key = nn.Linear(n_embed, head_size, bias=False)
        self.query = nn.Linear(n_embed, head_size, bias=False)
        self.value = nn.Linear(n_embed, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, time_steps, channels = x.shape
        key = self.key(x)
        query = self.query(x)
        weights = query @ key.transpose(-2, -1) * channels**-0.5
        weights = weights.masked_fill(self.tril[:time_steps, :time_steps] == 0, float("-inf"))
        weights = F.softmax(weights, dim=-1)
        weights = self.dropout(weights)
        value = self.value(x)
        return weights @ value


class MultiHeadAttention(nn.Module):
    def __init__(self, n_head: int, n_embed: int, block_size: int, dropout: float) -> None:
        super().__init__()
        head_size = n_embed // n_head
        self.heads = nn.ModuleList([Head(head_size, n_embed, block_size, dropout) for _ in range(n_head)])
        self.projection = nn.Linear(n_embed, n_embed)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.cat([head(x) for head in self.heads], dim=-1)
        out = self.projection(out)
        return self.dropout(out)


class FeedForward(nn.Module):
    def __init__(self, n_embed: int, dropout: float) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embed, 4 * n_embed),
            nn.ReLU(),
            nn.Linear(4 * n_embed, n_embed),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Block(nn.Module):
    def __init__(self, n_embed: int, n_head: int, block_size: int, dropout: float) -> None:
        super().__init__()
        self.self_attention = MultiHeadAttention(n_head, n_embed, block_size, dropout)
        self.feed_forward = FeedForward(n_embed, dropout)
        self.layer_norm_1 = nn.LayerNorm(n_embed)
        self.layer_norm_2 = nn.LayerNorm(n_embed)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.self_attention(self.layer_norm_1(x))
        x = x + self.feed_forward(self.layer_norm_2(x))
        return x


class NanoGPT(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding_table = nn.Embedding(config.vocab_size, config.n_embed)
        self.position_embedding_table = nn.Embedding(config.block_size, config.n_embed)
        self.blocks = nn.Sequential(
            *[Block(config.n_embed, config.n_head, config.block_size, config.dropout) for _ in range(config.n_layer)]
        )
        self.layer_norm = nn.LayerNorm(config.n_embed)
        self.language_model_head = nn.Linear(config.n_embed, config.vocab_size)
        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, index: torch.Tensor, targets: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor | None]:
        batch_size, time_steps = index.shape
        token_embeddings = self.token_embedding_table(index)
        positions = torch.arange(time_steps, device=index.device)
        position_embeddings = self.position_embedding_table(positions)
        x = token_embeddings + position_embeddings
        x = self.blocks(x)
        x = self.layer_norm(x)
        logits = self.language_model_head(x)

        loss = None
        if targets is not None:
            batch, time_steps, channels = logits.shape
            logits = logits.view(batch * time_steps, channels)
            targets = targets.view(batch * time_steps)
            loss = F.cross_entropy(logits, targets)
        return logits, loss

    @torch.no_grad()
    def generate(self, index: torch.Tensor, max_new_tokens: int) -> torch.Tensor:
        for _ in range(max_new_tokens):
            cropped = index[:, -self.config.block_size :]
            logits, _ = self(cropped)
            logits = logits[:, -1, :]
            probabilities = F.softmax(logits, dim=-1)
            next_index = torch.multinomial(probabilities, num_samples=1)
            index = torch.cat((index, next_index), dim=1)
        return index

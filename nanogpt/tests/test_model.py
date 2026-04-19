import torch

from model import GPTConfig, NanoGPT


def test_forward_shapes_and_loss():
    config = GPTConfig(vocab_size=20, block_size=8, n_embed=16, n_head=4, n_layer=2, dropout=0.1)
    model = NanoGPT(config)
    index = torch.randint(0, 20, (4, 8))
    targets = torch.randint(0, 20, (4, 8))

    logits, loss = model(index, targets)
    assert logits.shape == (32, 20)
    assert loss is not None
    assert loss.item() > 0


def test_generate_extends_sequence():
    config = GPTConfig(vocab_size=20, block_size=8, n_embed=16, n_head=4, n_layer=2, dropout=0.1)
    model = NanoGPT(config)
    start = torch.zeros((1, 1), dtype=torch.long)
    generated = model.generate(start, max_new_tokens=10)
    assert generated.shape[1] == 11

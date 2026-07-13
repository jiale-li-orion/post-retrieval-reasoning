import torch

from readout.core import compute_paired_readouts


class FakeLens:
    source_layers = [0, 1]

    def __init__(self):
        self.seen = []

    def transport(self, residual, layer):
        self.seen.append((layer, residual.clone()))
        return residual + 10


class FakeModel:
    def unembed(self, residual):
        return torch.stack((residual[..., 0], residual[..., 1]), dim=-1)


def test_j_and_logit_readouts_share_the_exact_captured_activation() -> None:
    activations = {
        0: torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
        1: torch.tensor([[5.0, 6.0], [7.0, 8.0]]),
        2: torch.tensor([[9.0, 10.0], [11.0, 12.0]]),
    }
    lens = FakeLens()

    rows = compute_paired_readouts(
        activations,
        positions={"P_q": 0, "P_a0": 1},
        lens=lens,
        model=FakeModel(),
        target_layer=2,
    )

    assert len(rows) == 6
    assert lens.seen[0][1].tolist() == [[1.0, 2.0], [3.0, 4.0]]
    first = rows[0]
    assert first["logit_logits"].tolist() == [1.0, 2.0]
    assert first["j_logits"].tolist() == [11.0, 12.0]
    final = rows[-1]
    assert final["layer"] == 2
    assert final["readout_kind"] == "final_identity"
    assert final["j_logits"].tolist() == final["logit_logits"].tolist()


def test_readout_rejects_generated_positions_in_primary_call() -> None:
    try:
        compute_paired_readouts(
            {0: torch.ones(1, 2)},
            positions={"generated_1": 0},
            lens=FakeLens(),
            model=FakeModel(),
            target_layer=2,
        )
    except ValueError as exc:
        assert "generated" in str(exc)
    else:
        raise AssertionError("generated positions must not enter primary readout")

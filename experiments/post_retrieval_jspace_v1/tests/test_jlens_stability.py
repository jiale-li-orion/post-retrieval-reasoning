import torch
import pytest

import jlens
from jacobian_analysis.evaluate_stability import matrix_cosines, topk_set_overlap


def _lens(matrix):
    return jlens.JacobianLens(jacobians={0: matrix}, n_prompts=1, d_model=2)


def test_matrix_cosine_is_one_for_identical_lenses() -> None:
    matrix = torch.eye(2)
    assert matrix_cosines(_lens(matrix), _lens(matrix))[0] == pytest.approx(1.0)


def test_topk_overlap_is_intersection_fraction() -> None:
    first = torch.tensor([5.0, 4.0, 0.0])
    second = torch.tensor([5.0, 0.0, 4.0])

    assert topk_set_overlap(first, second, 2) == 0.5

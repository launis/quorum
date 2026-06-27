import pytest

from scripts.diff_executions import (
    calculate_cohens_kappa,
    calculate_entropy,
    calculate_fleiss_kappa,
    calculate_pairwise_consistency,
)


def test_calculate_entropy() -> None:
    # Täysin vakaat tilat -> entropia 0.0
    assert calculate_entropy(["true", "true", "true"]) == 0.0
    assert calculate_entropy(["false", "false"]) == 0.0
    assert calculate_entropy([]) == 0.0

    # Kaksi eri tilaa 50/50 jakaumalla -> shannon-entropia (base 2) on tasan 1.0
    assert calculate_entropy(["true", "false"]) == 1.0
    assert calculate_entropy(["true", "true", "false", "false"]) == 1.0


def test_calculate_pairwise_consistency() -> None:
    # Täysin yhtenäinen
    assert calculate_pairwise_consistency(["true", "true", "true"]) == 1.0
    assert calculate_pairwise_consistency(["false", "false"]) == 1.0
    assert calculate_pairwise_consistency(["true"]) == 1.0
    assert calculate_pairwise_consistency([]) == 1.0

    # 50/50 jakauma, kaksi arvoa -> parittainen sopivuus 0.0
    assert calculate_pairwise_consistency(["true", "false"]) == 0.0

    # Kolme arvoa, joista 2 samaa ja 1 eri -> 3 mahdollista paria, joista 1 täsmää (koko 1/3)
    # (true, true), (true, false), (true, false) -> vain 1 pari sopii
    assert pytest.approx(calculate_pairwise_consistency(["true", "true", "false"])) == 1 / 3


def test_calculate_cohens_kappa_perfect_agreement() -> None:
    # Täydellinen sopivuus kahdelle arvioijalle (M = 2)
    states = [["true", "true"], ["true", "true"], ["false", "false"], ["false", "false"]]
    categories = ["true", "false"]
    kappa = calculate_cohens_kappa(states, categories)
    assert kappa == 1.0


def test_calculate_cohens_kappa_partial_agreement() -> None:
    # Osittainen sopivuus
    # Run 1: true, true, false, false
    # Run 2: true, false, false, true
    states = [
        ["true", "true"],  # Sopii
        ["true", "false"],  # Eri mieltä
        ["false", "false"],  # Sopii
        ["false", "true"],  # Eri mieltä
    ]
    categories = ["true", "false"]

    # N = 4
    # Observed agreement = 2/4 = 0.5
    # Run 1: true=2 (0.5), false=2 (0.5)
    # Run 2: true=2 (0.5), false=2 (0.5)
    # Expected agreement = 0.5*0.5 + 0.5*0.5 = 0.5
    # Kappa = (0.5 - 0.5) / (1 - 0.5) = 0.0
    kappa = calculate_cohens_kappa(states, categories)
    assert kappa == 0.0


def test_calculate_cohens_kappa_invalid_inputs() -> None:
    # Pitää heittää ValueError jos arvioijia ei ole tasan 2
    with pytest.raises(ValueError, match="Cohenin kappa vaatii tasan kaksi"):
        calculate_cohens_kappa([["true", "true", "true"]], ["true", "false"])


def test_calculate_fleiss_kappa_perfect_agreement() -> None:
    # Täydellinen sopivuus Fleissin kappalla useammalla ajolla
    states = [["true", "true", "true"], ["false", "false", "false"]]
    categories = ["true", "false"]
    kappa = calculate_fleiss_kappa(states, categories)
    assert kappa == 1.0

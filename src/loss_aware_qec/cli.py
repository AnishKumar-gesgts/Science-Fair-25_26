"""Command-line interface for running a loss-probability sweep."""

from argparse import ArgumentParser
from collections.abc import Sequence

from .experiment import DecoderMetrics, ExperimentConfig, run_experiment


def _percent(value: float | None) -> str:
    return "n/a" if value is None else f"{100.0 * value:6.2f}%"


def _row(loss: float, name: str, metrics: DecoderMetrics) -> str:
    return (
        f"{loss:5.2f}  {name:<12}  {_percent(metrics.success_rate):>8}  "
        f"{_percent(metrics.coverage):>8}  "
        f"{_percent(metrics.conditional_accuracy):>12}"
    )


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Compare majority and loss-aware decoding of amplitude damping."
    )
    parser.add_argument(
        "--loss",
        type=float,
        nargs="+",
        default=[0.0, 0.1, 0.2, 0.3, 0.5, 0.8],
        help="one or more per-qubit amplitude-damping probabilities",
    )
    parser.add_argument("--false-positive", type=float, default=0.01)
    parser.add_argument("--false-negative", type=float, default=0.01)
    parser.add_argument("--shots", type=int, default=5_000, help="shots per input")
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    print(" loss  decoder        success  coverage  accuracy|decoded")
    print("-----  ------------  --------  --------  ----------------")
    for loss_probability in args.loss:
        result = run_experiment(
            ExperimentConfig(
                loss_probability=loss_probability,
                false_positive_probability=args.false_positive,
                false_negative_probability=args.false_negative,
                shots_per_input=args.shots,
                seed=args.seed,
            )
        )
        print(_row(loss_probability, "majority", result.standard))
        print(_row(loss_probability, "loss-aware", result.loss_aware))


if __name__ == "__main__":
    main()

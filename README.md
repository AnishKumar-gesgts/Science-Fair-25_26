# Loss-Aware Hardware-Ancilla Decoding

[![tests](https://github.com/AnishKumar-gesgts/Loss-Aware-Hardware-Ancilla-Decoding/actions/workflows/tests.yml/badge.svg)](https://github.com/AnishKumar-gesgts/Loss-Aware-Hardware-Ancilla-Decoding/actions/workflows/tests.yml)

This educational Qiskit project tests a simple idea: **can a decoder recover a
stored logical bit more often if hardware sensors report which qubits experienced
amplitude damping?**

The simulation compares an ordinary majority-vote decoder with a loss-aware
decoder. Both receive the same three measured data bits, but the loss-aware
decoder also receives one loss flag per qubit.

## Research question

> **To what extent can ancilla-provided flags that identify amplitude-damping
> jumps improve recovery of a repetition-encoded logical bit over standard
> majority decoding, and how is that advantage affected by sensor false
> positives and false negatives?**

This question matches what the repository actually measures. The simulation does
not measure the fidelity of an arbitrary quantum state or model a specific
photonic device. Instead, it measures how often each decoder correctly recovers
a known logical `0` or `1`.

## How the model works

One logical bit is stored in three data qubits:

```text
Logical 0 -> |000>
Logical 1 -> |111>
```

Each data qubit has a sensor ancilla. The data qubit and sensor interact as:

```text
|0>|0_sensor> -> |0>|0_sensor>
|1>|0_sensor> -> sqrt(1-p)|1>|0_sensor>
                 + sqrt(p)|0>|1_sensor>
```

Here, `p` is the amplitude-damping probability. The `|1_sensor>` branch identifies
a damping jump: the data qubit relaxed from `|1>` to `|0>`.

The circuit creates this transformation with a controlled `RY` rotation followed
by a sensor-controlled `X` gate. This is a unitary system-and-environment model
of the amplitude-damping channel, also called a Stinespring dilation.

The sensor is an idealized model of hardware that can reveal energy relaxation.
It is not a design for a physical sensor.

## The two decoders

### Standard majority decoder

The standard decoder uses all three measured data bits:

```text
0 0 1 -> logical 0
0 1 1 -> logical 1
```

It does not know which measurements may have changed because of damping.

### Loss-aware decoder

The loss-aware decoder removes every measurement whose matching sensor reports a
jump. It then takes a strict majority of the remaining values.

```text
Data:       0 0 1
Flags:      1 1 0
Trusted:        1
Output:         1
```

If no trusted values remain, or the remaining vote is tied, the decoder
**abstains** instead of guessing.

## What one experiment does

For each requested loss probability, the program:

1. Runs the same number of logical-`0` and logical-`1` trials.
2. Encodes each input into three data qubits.
3. Couples each data qubit to its sensor ancilla.
4. Measures the data qubits and sensors.
5. Adds configurable false-positive and false-negative sensor reports.
6. Applies both decoders to the same measurement outcomes.
7. Compares each decoded value with the known input.

Testing both inputs is important because amplitude damping is asymmetric:
`|1>` can relax to `|0>`, while `|0>` does not relax to `|1>` in this model.
Testing only logical `0` would make performance look unrealistically good.

## Figures of merit

The program reports three values.

### Success

```text
correct decisions / all trials
```

This is the main comparison. Abstentions count as unsuccessful trials.

### Coverage

```text
trials with a decoder answer / all trials
```

Coverage shows how often a decoder has enough information to answer.

### Accuracy when decoded

```text
correct decisions / trials with a decoder answer
```

This value can be high when a decoder abstains on difficult trials, so it should
always be read together with success and coverage.

## Expected results with perfect sensors

For balanced logical inputs and perfect sensor reports, the expected success
rates are:

```text
Standard majority:  1 - (3/2)p^2 + p^3
Loss-aware:         1 - (1/2)p^3
```

At `p = 0.5`, the expected success rates are:

```text
Standard majority:  75.00%
Loss-aware:         93.75%
```

With perfect sensors, the loss-aware decoder is correct whenever it answers. It
abstains when all useful information is gone—for example, when all three `1`s
relax and all three sensors flag them.

Imperfect sensors reduce this advantage. A false negative can leave a damaged
bit in the vote, while a false positive can remove a valid bit.

## Run the project

Python 3.10 or newer is required.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS or Linux
source .venv/bin/activate

python -m pip install -e ".[dev]"
python -m pytest
python -m loss_aware_qec
```

Run a custom experiment:

```bash
python -m loss_aware_qec \
  --loss 0.0 0.2 0.5 0.8 \
  --false-positive 0.01 \
  --false-negative 0.01 \
  --shots 10000 \
  --seed 7
```

The results are sampled, so exact percentages may change with the seed and
number of shots.

## Repository structure

```text
src/loss_aware_qec/
|-- circuit.py       # encoding, damping interaction, and sensor noise
|-- decoders.py      # standard and loss-aware decoders
|-- experiment.py    # simulation and performance metrics
|-- cli.py           # command-line parameter sweep
`-- __main__.py      # supports: python -m loss_aware_qec

tests/               # automated correctness tests
pyproject.toml       # dependencies and Python project settings
```

The tests check the decoder rules, circuit structure, Qiskit bit ordering,
boundary cases, and metric calculations. They verify that the code behaves as
designed; the command-line experiment is what compares decoder performance.

## Scope and limitations

- This benchmark stores computational-basis information: logical `0` and
  logical `1`. It does not show that an arbitrary state
  `alpha|0> + beta|1>` is preserved.
- The project therefore reports logical-bit success and conditional accuracy,
  not full quantum-state fidelity.
- The simulated sensors provide information about amplitude-damping jumps. This
  is different from detecting the physical loss of an entire qubit.
- The sensor model is platform-independent. The project may motivate questions
  about photonic or other hardware, but it does not simulate a particular
  photonic architecture.
- Encoding gates, data measurement, and data-qubit readout are ideal. The model
  includes amplitude damping and sensor readout errors only.
- A simulation can show the possible decoding benefit of reliable flags, but it
  cannot demonstrate that suitable hardware is practical.

## Use of AI and project disclaimer

Generative AI was used to write and edit parts of the code, tests, documentation,
and repository structure. AI-assisted material may contain mistakes. The project
owner is responsible for reviewing the implementation, checking the scientific
claims, and understanding any results presented from this repository.

The simulation is an educational proof of concept, not peer-reviewed research or
evidence of performance on real quantum hardware. Results should be reproduced
with the documented environment, parameters, seed, and shot count. Any report,
presentation, or resume entry based on this work should describe the model's
limits and should not claim arbitrary-state quantum error correction or
experimental hardware validation.

## Possible extensions

- Use a code designed to protect arbitrary states from amplitude damping.
- Add gate errors, data-readout errors, reset errors, and sensor backaction.
- Compare maximum-likelihood and soft-decision decoders.
- Study correlated damping instead of independent per-qubit damping.
- Run several seeds and report uncertainty intervals.
- Build a hardware-specific model only after choosing a real sensor mechanism
  and physical platform.

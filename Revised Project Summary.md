# Simulating Improved Logical-Bit Recovery Through Loss-Aware Ancilla Decoding

**By: Anish Kumar**  
[GitHub Repository](https://github.com/AnishKumar-gesgts/Loss-Aware-Hardware-Ancilla-Decoding)

## To those familiar with QEC:

This project simulates the possible benefit of external hardware sensors that
detect amplitude-damping jumps and provide that information to a decoder. The
simulation does not attempt to design this hardware. Instead, it asks how useful
accurate loss information could be if a physical system were able to produce one
flag for each affected qubit.

We aimed to answer the question: **To what extent can ancilla-provided flags that
identify amplitude-damping jumps improve recovery of a repetition-encoded
logical bit over standard majority decoding, and how is that advantage affected
by sensor false positives and false negatives?**

The simulation was created in Qiskit Aer and uses a three-qubit repetition code
to store a logical `0` as `|000>` or a logical `1` as `|111>`. Three additional
ancilla qubits act as idealized loss sensors, giving a total of six qubits. Each
data qubit is paired with one sensor. Instead of comparing a damaged qubit with
an untouched copy, the simulation directly couples each data qubit to its sensor
through a controlled `RY` rotation followed by a sensor-controlled `X` gate.

Two major types of error are considered. The first is independent amplitude
damping on each data qubit. The second is imperfect sensor readout. Sensor errors
are divided into false positives, in which a sensor reports a jump that did not
occur, and false negatives, in which a real jump is not reported. Both rates can
be changed from the command line.

Two decoding methods are compared. The standard decoder applies a majority vote
to all three data measurements. The loss-aware decoder completely excludes any
data measurement whose matching sensor reports a jump, then applies a strict
majority vote to the remaining measurements. If all measurements are excluded,
or if the remaining measurements are tied, the loss-aware decoder abstains
instead of making a random guess.

The experiment runs equal numbers of logical-`0` and logical-`1` inputs and
compares every decoded output with the known input for that trial. This is
important because comparing only the total number of measured zeroes and ones
can hide individual decoding errors, especially when the inputs are evenly
balanced.

Three figures of merit are reported. Overall success is the percentage of all
trials that produce the correct logical output, with abstentions counted as
unsuccessful. Coverage is the percentage of trials for which the decoder
produces an answer. Conditional accuracy is the percentage of non-abstained
answers that are correct. Conditional accuracy must be viewed alongside
coverage, since a decoder could otherwise appear highly accurate by refusing toanswer difficult cases.

With perfect sensors and balanced logical inputs, the expected success of the
standard majority decoder is

```text
1 - (3/2)p^2 + p^3,
```

while the expected success of the loss-aware decoder is

```text
1 - (1/2)p^3.
```

At an amplitude-damping probability of 50%, these expressions predict 75%
success for standard majority decoding and 93.75% success for loss-aware
decoding. With perfect sensors, every answer produced by the loss-aware decoder
is correct; its unsuccessful trials occur when the original information has
been completely removed and the decoder must abstain. False positives lower
coverage by discarding valid data, while false negatives can lower accuracy by
allowing damaged data into the vote.

The goal of this project is to show how access to error-location information can
improve a decoder, not to show that a complete hardware solution has already
been developed. Although loss sensing may be relevant to photonic and other
quantum-computing platforms, this simulation is platform-independent and does
not use measured error rates or a device model from a particular photonic
computer. It also tests recovery of computational-basis logical information,
not the fidelity of an arbitrary quantum state. A future version could use an
amplitude-damping code that protects both amplitude and phase, include realistic
gate and measurement noise, or model a specific physical sensor.

## In simpler terms:

Quantum information is easily affected by its environment. One possible error
is amplitude damping, in which an excited qubit in the state `|1>` loses energy
and relaxes to `|0>`. This error is different from a symmetric bit flip because
the reverse change from `|0>` to `|1>` does not occur in the low-temperature
amplitude-damping model used here.

To reduce errors, one bit of information can be stored across three qubits. A
logical `1`, for example, is stored as `111`. A normal majority decoder looks at
the three final measurements and selects whichever value appears most:

```text
111 -> 1
101 -> 1
100 -> 0
```

This method can handle one incorrect measurement, but it fails when two of the
three `1`s decay to `0`.

The main idea of this project is that hardware may be able to provide more
information than the data measurements alone. If a sensor reports that a
particular qubit lost energy, the decoder can stop treating that qubit's new `0`
as a trustworthy vote.

For example:

```text
Measured data: 0 0 1
Sensor flags:  1 1 0
```

A normal decoder sees two zeroes and returns `0`, even if the original logical
value was `1`. The loss-aware decoder removes the two flagged measurements and
uses the surviving `1`, allowing it to recover the original value.

However, the loss-aware decoder cannot recover information that no longer
exists. If all three data qubits relax and all three are correctly flagged, no
trusted value remains. The decoder reports that it cannot answer instead of
guessing. For this reason, the project measures both how often the decoder is
correct and how often it is able to provide an answer.

The sensors are also allowed to make mistakes. A false positive removes a good
measurement, while a false negative keeps a damaged measurement. The simulation
can change these sensor error rates to determine when loss information remains
useful and when unreliable sensors remove its advantage.

This project therefore does not prove that a new quantum computer or correction
device is ready to be built. It demonstrates, through a controlled simulation,
that knowing where amplitude-damping jumps occurred can improve recovery of a
stored logical bit. It also shows that the quality of the sensor information is
just as important as the decoding rule that uses it.

## Disclaimer

This repository is an educational simulation and has not been validated on real
quantum hardware or through peer review. Generative AI was used to write and
edit parts of the code, tests, documentation, and project summary. The project
owner is responsible for reviewing the implementation, understanding the model,
and checking all scientific claims before presenting the results. This project
should not be described as demonstrating arbitrary-state quantum error
correction, a working hardware sensor, or verified performance on a photonic
quantum computer.

# VTEAM/RRAM Binary Memristor Research Model

This model is selected as the first implemented memristor layer for the project.

## Scope

The file defines an architecture-level behavioral model for a memristor-based Hamming encoder. It is used to evaluate XOR truth-table correctness, crossbar parity scheduling, approximate energy, approximate latency, pulse count, and Monte Carlo sensitivity to process variation.

It is not a foundry-calibrated memristor compact model and does not claim fabricated-silicon behavior.

## State Mapping

| Logic value | Memristor state | Nominal resistance |
|---|---|---:|
| 0 | HRS | 1 Mohm |
| 1 | LRS | 10 kohm |

## Nominal Parameters

| Parameter | Value |
|---|---:|
| Ron | 10 kohm |
| Roff | 1 Mohm |
| Read voltage | 0.2 V |
| Logic/write pulse voltage | 1.0 V |
| Read time | 0.5 ns |
| Logic pulse time | 1.0 ns |
| Write time | 1.0 ns |
| Sense time | 0.5 ns |

## XOR Primitive Selected

The implemented primitive is `PIM_XOR_3M_CONSERVATIVE`.

It uses two operand cells and one destination/scratch cell. This is deliberately more conservative than the earlier two-memristor target because the project needs evidence that is easier to defend scientifically. The two-memristor XOR remains a future optimization target, while the three-memristor abstraction provides an implementable baseline for truth-table verification and Monte Carlo stress.

## Reliability Variables

Monte Carlo experiments vary:

- Ron.
- Roff.
- Switching threshold.
- Switching time.
- Read noise.

The first acceptance gate is that the read-margin ratio remains above 8 and the logic error rate remains below 0.1% under the tested variation profile.

## Relationship to the Current CMOS/FS-GDI Project

The current repository's Hybrid-B result is the measured speed-oriented transistor-level baseline. The memristor model is compared against it at the encoded-word level. The comparison includes energy per encoded word, latency per encoded word, equivalent active device count, and pulse count.

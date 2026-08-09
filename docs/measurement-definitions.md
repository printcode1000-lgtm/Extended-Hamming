# Measurement Definitions

- **Average power:** time average of positive power drawn from VSUP, calculated as `AVG(-V(VDD)*I(VSUP))`.
- **tpLH / tpHL:** elapsed time from the 50% input crossing to the corresponding 50% output crossing.
- **Propagation delay:** arithmetic mean of tpLH and tpHL.
- **PDP:** average power multiplied by propagation delay; recalculated in Python rather than copied manually.
- **Energy per encoding operation:** average encoder power divided by the input-word rate used by the activity pattern.
- **Energy per encoded bit:** energy per operation divided by 11 or 12, consistently by codeword length.
- **Output swing:** maximum measured output minus minimum measured output.
- **Hardware complexity:** transistor count from the instantiated cell topology. It is not layout area.


# `faer-kernels` on `zen5-cpu`

- t4a-faer (fork, measured) commit: `71b25ffb7ae3ce038ec25b35c91e526be41b9a63`
- t4a-faer version: `0.27.1`
- upstream faer commit: `0539947ffb757a739d7e703a7d2fa0c792a909c1`
- upstream faer ref/version: `faer-v0.24.4` / `0.24.4`
- features: `std, rayon`
- faer rows: `faer-fork` (the provider in the measured revision; see library and upstream above); `faer-upstream` (the provider in the measured revision; see library and upstream above)
- harness commit: `eeeaa36388c515a992d5056f4211e4a6cb92ba54`
- toolkit commit: `74e50e8199cb2c2f07e810744a0943fc3a8c1170`
- measured binary SHA-256: `26fd51c0c7d17f7f862ea3ddf8fc46f34fcd96e4fa6b3abb6fece93cc431e090`
- hardware profile: `zen5-cpu`
- host role: `development` — **provisional**: recorded on a development host, superseded by the measurement host's dataset
- timestamp: `2026-11-01T00:51:03.540807Z`
- timing policy: v2, median of 5 reps, priming 250 ms (time-based, identical on every row)
- guards: idle window 3 s, max busy 5.0% including SMT siblings, 3 attempts
- command: `scripts/record_run.py zen5-cpu faer-kernels --checkout /home/shinaoka/.local/state/faer-measurement-checkouts/71b25ffb7ae3ce038ec25b35c91e526be41b9a63/t4a-faer --upstream extern/upstream-faer --vendor mkl --engines faer-fork,faer-upstream,lapack-mkl --threads 1,4,8 --dtypes f64,c64 --reps 5 --aa 3 --prime-ms 250 --label pub-71b25ffb-20261031-mkl --no-publish`
- raw data: `data/results/zen5-cpu/faer-kernels/20261031T224040Z-pub-71b25ffb-20261031-mkl/`

## What was measured

- **Workload** — Direct calls into one faer revision: square and rectangular dense matrices, C (row-major) and F (column-major) order, `f64` and `c64`. A shape is `N` for square, `MxN` for rectangular, or `MxKxN` for `gemm`, which is a three-index operation and cannot be written as two. Sizes are the matrix dimensions, not a memory budget, so a case name says exactly what was factored. `gemm` measures `linalg::matmul::matmul` into a caller-prepared destination with `Accum::Replace`; there is no operator path, so one shape is one work.
  Source: The fork's own public API (`faer/src/linalg`): `matmul`, the QR factor and composite, `upgrade_householder_factor`, the block/sequence Householder apply, LU and full-pivot LU, Cholesky, triangular solve, solve, thin SVD, singular values and the symmetric/nonsymmetric eigensolvers. Inputs are seeded from the case, so `verify` and `run` measure the same matrices and a rerun is reproducible.
  Known blind spot: Only the faer entry points are measured. tlinalg's packing, batch loop and lane policy, tenferro's tensor construction and dtype dispatch, and the small-`m` decode-projection shapes are other repositories' rows (tlinalg-benchmark, tenferro-benchmark).
  Known blind spot: Vendor C-order cells use CBLAS/LAPACKE row-major entry points. Workspace allocation or layout conversion internal to those APIs remains timed; these are not prepared-column-major or transpose measurements.
  Known blind spot: `gemm` covers the tall class's two Householder legs (a 16-wide basis and a 240-column target over 4096 rows: the reduction and the write-back) beside a vendor `?gemm` on the same leg. A single leg beside a vendor gemm is a diagnostic reference, not the equivalent implementation of the whole update, and the row is labelled accordingly.
  Known blind spot: `householder_apply` measures block apply and the one-block sequence form as two distinct rows, labelled with basis width min(m,n) and target width n. QR fixture preparation is outside timing. Independently varied basis/target widths and multi-panel sequences are not covered.
  Known blind spot: Allocation performed inside the measured call stays inside the clock. The fork's two row splits allocate their partial buffers inside the public call, and the public scratch function does not expose them; the campaign reports that as it is instead of changing faer's API to make the boundary look cleaner.
  Known blind spot: `cholesky`, `eigh`, `solve` and `triangular_solve` are measured on square shapes only: the matrix they factor or solve with is square by definition (self-adjoint for the first two, a triangular factor for the last). `lu` and `full_piv_lu` are not gated that way -- they take the declared rectangular shapes too, with `min(m, n)` pivots and a trapezoidal `L` or `U`, which is what `dgetrf` does as well -- so a rectangular LU cell is measured in both orders beside its square one.
  Known blind spot: `f32`/`c32` are declared and measured as of `docs/harness-dtype-axis.md`; the vendor arm has a route for `gemm` in those two dtypes and reports the LAPACK families as skipped for them. The large regime's 1024 shapes, BLIS, sparse, iterative and GPU arms are later declarations, not machinery built now.
  Known blind spot: A vendor arm records the library it linked. Only OpenBLAS reports the kernel its runtime dispatched to; MKL names no kernel and no processor count, so its manifest leaves both empty rather than inferring them.
- **Rows** — one row per engine in every table below:
  - `faer-fork` — The measured library: the tensor4all fork (`t4a-faer`, `[lib] name = "faer"`) at the checkout the harness linked by path. This is the row the campaign exists for; the fork's three perf experiments and the two correctness changes land here.
    Identity: the fork revision in this run's manifest (`library.commit`), pinned by `pins/t4a-faer.rev`
    Caveat: Both faer crates declare `[lib] name = "faer"`. They are distinct dependency keys (`faer_fork = { package = "t4a-faer" }`, `faer_upstream = { package = "faer" }`) and therefore distinct Rust crate identities, but their `Mat`, `Par` and trait types are not interchangeable: every adapter is written per arm, and shared transitive dependencies can unify Cargo features, so both arms declare equivalent feature sets and the resolved lock is recorded.
    As measured: `faer-fork` (the provider in the measured revision; see library and upstream above)
  - `faer-upstream` — Upstream `faer` at the tag the fork is based on, in the same binary as the fork row. The baseline that says whether a fork change moved the number.
    Identity: the upstream revision in this run's manifest (`upstream.commit`), pinned by `pins/upstream-faer.rev`
    Caveat: Same crate-name and feature-unification caveat as `faer-fork`. A change to upstream at a fixed fork revision produces a different page rather than overwriting one.
    As measured: `faer-upstream` (the provider in the measured revision; see library and upstream above)
  - `lapack-mkl` — The same calls against Intel oneAPI MKL, linked from the installation `MKLROOT` names. One binary links one vendor library, so this row is measured by its own build of the harness and recorded as its own run; no page carries two vendor arms. The LP64 interface layer and the threading layer are pinned by the harness before the first MKL call, because MKL otherwise lets the environment choose them and the interface layer is an ABI.
    Identity: the MKL build recorded in this run's manifest (`providers[mkl]`)
    Caveat: MKL reports no dispatched-kernel name and no processor count, so its manifest records neither rather than inferring them. Its threading is vendor-owned, as for OpenBLAS.
    As measured: linked shared; mkl 2026.2; kernel not reported by the vendor

## Hardware

- CPU: `AMD Ryzen AI 9 HX 470`
- logical CPUs: `24`
- L3: `24 MiB (2 instances)`
- L3 domains: `0-3: 16 MiB shared; 4-11: 8 MiB shared`
- OS / arch: `Linux 7.0.0-38-generic` / `x86_64`
- hostname: `shinaoka-EVO-X1Pro`
- CPU sets: 1T -> `4`, 4T -> `4-7`, 8T -> `4-11`

Every timed cell matches a successful verification census, including operation variants.
Each cell is median of process medians ± sample SD of those medians; W is the median
within-process sample SD. All values are milliseconds. These are descriptive spreads,
not confidence intervals. The between-process spread includes the rotating-order schedule.
Each process retains 5 chronological calls; 3 complete process sets are recorded.
Spread guide (computed from this run's own rows): per-engine between-start range median 1.02%, worst 8160.25% among cells of 1 us or more (a sub-microsecond row is timer and scheduler jitter, not kernel time); 328 of 3684 engine cells exceed 5% and carry `!`; median within-process relative SD 0.44%. A cell whose `±`, `!` or `p` is as large as the difference you are reading is not evidence of a regression.
The `vs faer-fork` column is the rotation-averaged ratio
exp(mean over starts of log(engine median / faer-fork median)),
with the per-start ratios beside it: `R > 1`
means the engine was slower than that first-declared row in that start. It removes a
row-position
effect only under one position effect shared by the engines and stable across starts,
and only where every declared engine has a measured row (`*` marks a cell where one has
no row, so no ratio there is position-balanced). `!` marks a cell where some engine's own
per-start median range exceeds 5% of its median, and `p` a balanced cell whose estimated
position-effect ratio exceeds 1.05. Flagged cells are retained, not discarded; the
between-start variation can exceed the difference being compared.
The `vs` columns mark only differences larger than the spread this run recorded for those
two rows (combined between-start SD, floored at 5%), always with the measured library as the subject:
`🔵 <row> X faster than <row>` / `🔴 <row> X slower than <row>` (the subject is the first column of the table, the compared row is named in
the cell, not only in the column header), `·` inside the band, `-` that row is not
measured in this arm. `notes` carries the cell warnings (`*` a declared row has no measurement,
`!` between-start range over 5%, `p` position effect over 5%, dispatch-dominated means the
row is under 20 us so 4T/8T pay thread-region start-up). Per-start ratios and every
chronological sample are in the run directory named at the top of this page (`run*.csv`).
These describe the recorded revisions; they are not a regression claim.

## gemm-small, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002344 ± 5.50757e-06 (W 1.63799e-05) | 0.002354 ± 3.66106e-05 (W 1.73263e-05) | 0.004469 ± 2.5632e-05 (W 2.69666e-05) | · | 🔵 faer-fork 1.91× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.017092 ± 8.67583e-05 (W 2.08854e-05) | 0.017072 ± 9e-05 (W 2.07364e-05) | 0.024155 ± 0.000319511 (W 8.28855e-05) | · | 🔵 faer-fork 1.41× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.056826 ± 0.000310217 (W 0.00137029) | 0.057016 ± 0.000172018 (W 0.00163458) | 0.062687 ± 0.000345515 (W 7.25272e-05) | · | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |

## gemm-small, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002405 ± 6.11583e-05 (W 1.62265e-05) | 0.003917 ± 0.000138564 (W 0.000118025) | 0.0054 ± 0.000291994 (W 0.000175727) | 🔵 faer-fork 1.63× faster than `faer-upstream` | 🔵 faer-fork 2.25× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.011312 ± 8.62168e-05 (W 0.000207623) | 0.019857 ± 0.000672534 (W 0.00100756) | 0.013886 ± 0.000221075 (W 0.000119454) | 🔵 faer-fork 1.76× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.022973 ± 0.00026839 (W 0.00025559) | 0.064711 ± 0.000841714 (W 0.00163254) | 0.022612 ± 0.000443217 (W 0.000127984) | 🔵 faer-fork 2.82× faster than `faer-upstream` | · |  |

## gemm-small, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002405 ± 2e-05 (W 3.07945e-05) | 0.004168 ± 5.7735e-07 (W 0.000189392) | 0.004669 ± 0.000312507 (W 0.000229481) | 🔵 faer-fork 1.73× faster than `faer-upstream` | 🔵 faer-fork 1.94× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.009758 ± 2.3094e-05 (W 9.86068e-05) | 0.01104 ± 0.00034356 (W 0.0002986) | 0.009688 ± 0.000267644 (W 0.000278017) | 🔵 faer-fork 1.13× faster than `faer-upstream` | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.020328 ± 3e-05 (W 9.30054e-05) | 0.02146 ± 6.245e-05 (W 6.75737e-05) | 0.014798 ± 0.000172705 (W 0.000149884) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |

## gemm-small, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002335 ± 5.19615e-06 (W 5.59464e-06) | 0.002385 ± 2.0664e-05 (W 1.76153e-05) | 0.004429 ± 1.47309e-05 (W 2.30716e-05) | · | 🔵 faer-fork 1.90× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.017142 ± 0.000126623 (W 2e-05) | 0.017072 ± 5.61278e-05 (W 3.26221e-05) | 0.024265 ± 0.000131074 (W 2.18906e-05) | · | 🔵 faer-fork 1.42× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.056735 ± 0.000231569 (W 0.00130937) | 0.057006 ± 0.00018374 (W 3.29272e-05) | 0.062778 ± 0.000221962 (W 9.49063e-05) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |

## gemm-small, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002414 ± 3.15753e-05 (W 1.53721e-05) | 0.003877 ± 6.60328e-05 (W 0.000195597) | 0.00511 ± 0.000200749 (W 0.000153246) | 🔵 faer-fork 1.61× faster than `faer-upstream` | 🔵 faer-fork 2.12× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.011211 ± 0.000229122 (W 7.82943e-05) | 0.019266 ± 0.00107615 (W 0.00112922) | 0.013986 ± 0.000166233 (W 0.000182995) | 🔵 faer-fork 1.72× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5%; dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.022983 ± 0.000201222 (W 0.000267374) | 0.06445 ± 0.0137988 (W 0.0100971) | 0.022452 ± 0.000121244 (W 0.000162961) | 🔵 faer-fork 2.80× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |

## gemm-small, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002395 ± 1.09697e-05 (W 3.03677e-05) | 0.004268 ± 0.000109697 (W 0.000286684) | 0.004619 ± 0.00020664 (W 0.000138327) | 🔵 faer-fork 1.78× faster than `faer-upstream` | 🔵 faer-fork 1.93× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.009829 ± 0.000160376 (W 5.26526e-05) | 0.01072 ± 0.000369506 (W 0.000984722) | 0.009718 ± 0.000221886 (W 9.87234e-05) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.020227 ± 0.000100135 (W 9.81896e-05) | 0.021319 ± 6.40859e-05 (W 0.000160407) | 0.014857 ± 0.000296784 (W 0.000117827) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |

## gemm-small, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.008827 ± 1.57162e-05 (W 2.04768e-05) | 0.008816 ± 3.60555e-05 (W 1.97535e-05) | 0.011231 ± 3.05505e-05 (W 0.000130557) | · | 🔵 faer-fork 1.27× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.067747 ± 0.000229239 (W 0.00196583) | 0.067766 ± 0.000362111 (W 0.00149752) | 0.082614 ± 0.000372578 (W 0.00156163) | · | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `gemm/96x96x96/b1` | 0.227455 ± 0.000311433 (W 0.00142776) | 0.226933 ± 3.71663e-05 (W 0.00182894) | 0.271647 ± 0.00291684 (W 0.00350359) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## gemm-small, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.009959 ± 0.00025064 (W 0.000221658) | 0.008826 ± 2.02567e-05 (W 2.73185e-05) | 0.013455 ± 0.000196571 (W 0.000146384) | 🔴 faer-fork 1.13× slower than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.028724 ± 2.60832e-05 (W 0.000205292) | 0.040486 ± 0.000803145 (W 0.0020537) | 0.035846 ± 0.000401478 (W 0.00049739) | 🔵 faer-fork 1.41× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `gemm/96x96x96/b1` | 0.078276 ± 0.00086549 (W 0.00037677) | 0.094927 ± 0.00138281 (W 0.00289792) | 0.099015 ± 0.000616075 (W 0.00227723) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |

## gemm-small, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.009909 ± 0.000156238 (W 0.000106978) | 0.008836 ± 3.05505e-05 (W 1.89816e-05) | 0.022482 ± 0.000166433 (W 0.00016074) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 2.27× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.02692 ± 0.000111355 (W 5.30396e-05) | 0.027812 ± 0.000265141 (W 0.000163646) | 0.01591 ± 0.000104484 (W 0.000155694) | · | 🔴 faer-fork 1.69× slower than `lapack-mkl` |  |
| `gemm/96x96x96/b1` | 0.039985 ± 7.45453e-05 (W 9.91373e-05) | 0.040706 ± 0.000171555 (W 0.000172436) | 0.042439 ± 0.000119304 (W 0.000346179) | · | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |

## gemm-small, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.008817 ± 1.12694e-05 (W 2.23652e-05) | 0.008817 ± 3.76431e-05 (W 1.87083e-05) | 0.011091 ± 5.2915e-05 (W 0.000108305) | · | 🔵 faer-fork 1.26× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.067826 ± 6.55769e-05 (W 5.89763e-05) | 0.067816 ± 0.000177962 (W 2.76442e-05) | 0.082284 ± 0.000277887 (W 0.00204324) | · | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `gemm/96x96x96/b1` | 0.226853 ± 0.000756318 (W 0.00167265) | 0.226943 ± 0.000792173 (W 0.00133558) | 0.269354 ± 0.00445331 (W 0.00425569) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## gemm-small, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.009858 ± 0.000149332 (W 0.000206824) | 0.008787 ± 2.25167e-05 (W 1.10589e-05) | 0.013405 ± 0.000377783 (W 0.000161038) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.029054 ± 0.000195705 (W 0.000196861) | 0.038962 ± 0.000467042 (W 0.00086855) | 0.035847 ± 0.000354034 (W 0.000438019) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` |  |
| `gemm/96x96x96/b1` | 0.078567 ± 0.000341263 (W 0.000463767) | 0.09661 ± 0.0022044 (W 0.00441383) | 0.099806 ± 0.00193853 (W 0.00140253) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |

## gemm-small, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.009858 ± 7e-05 (W 0.000125009) | 0.008867 ± 5.68624e-05 (W 1.10136e-05) | 0.022372 ± 0.000461676 (W 0.000143221) | 🔴 faer-fork 1.11× slower than `faer-upstream` | 🔵 faer-fork 2.27× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.02675 ± 5.68624e-05 (W 0.00107461) | 0.028063 ± 0.000179834 (W 0.000186628) | 0.01604 ± 0.000161967 (W 0.000154258) | · | 🔴 faer-fork 1.67× slower than `lapack-mkl` |  |
| `gemm/96x96x96/b1` | 0.039654 ± 0.000178979 (W 6.6778e-05) | 0.040827 ± 0.000251078 (W 0.000136272) | 0.042319 ± 0.000334605 (W 0.00119509) | · | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |

## gemm-mid, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.132897 ± 0.000727957 (W 0.000130431) | 0.133058 ± 0.000479585 (W 0.000227183) | 0.167232 ± 0.000918639 (W 0.00195942) | · | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `gemm/192x192x192/b1` | 0.450991 ± 0.00361063 (W 0.0018941) | 0.453536 ± 0.00260612 (W 0.00216436) | 0.481177 ± 0.000596192 (W 0.0030758) | · | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 1.06873 ± 0.00687495 (W 0.00301269) | 1.07155 ± 0.00418383 (W 0.00109331) | 1.19902 ± 0.00844305 (W 0.00196984) | · | 🔵 faer-fork 1.12× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 3.59567 ± 0.0177392 (W 0.00411279) | 3.60181 ± 0.00802665 (W 0.00393829) | 3.71311 ± 0.0166323 (W 0.00178845) | · | · |  |
| `gemm/512x512x512/b1` | 8.57472 ± 0.0293139 (W 0.0105855) | 8.56984 ± 0.0817205 (W 0.00945925) | 9.87747 ± 0.0174087 (W 0.0108782) | · | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 29.2772 ± 0.0596253 (W 0.0407723) | 29.2501 ± 0.262353 (W 0.027885) | 30.5058 ± 0.0607789 (W 0.0361679) | · | · |  |

## gemm-mid, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.045555 ± 0.000259474 (W 0.000456142) | 0.073057 ± 0.0087725 (W 0.0120172) | 0.055644 ± 0.0783 (W 0.00056254) | 🔵 faer-fork 1.60× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/192x192x192/b1` | 0.119392 ± 0.00136958 (W 0.0017853) | 0.162303 ± 0.000794102 (W 0.00217585) | 0.135743 ± 0.000960027 (W 0.000221044) | 🔵 faer-fork 1.36× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 0.289981 ± 0.0010457 (W 0.0020082) | 0.307854 ± 0.00992944 (W 0.00825499) | 0.342999 ± 0.00262801 (W 0.00212549) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/384x384x384/b1` | 0.913193 ± 0.000949788 (W 0.00230004) | 0.915912 ± 0.00118852 (W 0.00174234) | 1.00919 ± 0.00502192 (W 0.00358815) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 2.20997 ± 0.00661606 (W 0.00451201) | 2.20784 ± 0.0105604 (W 0.00755017) | 2.86345 ± 0.074087 (W 0.00709408) | · | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 7.51683 ± 0.0245092 (W 0.00971891) | 7.5132 ± 0.0248484 (W 0.0118919) | 8.48458 ± 0.0145303 (W 0.0217991) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |

## gemm-mid, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.032741 ± 0.000616767 (W 0.000723855) | 0.106979 ± 0.0223666 (W 0.0236961) | 0.031419 ± 0.000293343 (W 0.00119508) | 🔵 faer-fork 3.27× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/192x192x192/b1` | 0.08603 ± 0.000678503 (W 0.00122383) | 0.186387 ± 0.00525274 (W 0.0220126) | 0.07533 ± 0.000962456 (W 0.00027325) | 🔵 faer-fork 2.17× faster than `faer-upstream` | 🔴 faer-fork 1.14× slower than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/256x256x256/b1` | 0.164847 ± 0.00049887 (W 0.00166466) | 0.228056 ± 0.0163672 (W 0.0268901) | 0.179766 ± 0.00175534 (W 0.00242396) | 🔵 faer-fork 1.38× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/384x384x384/b1` | 0.478983 ± 0.000671379 (W 0.00212561) | 0.561196 ± 0.00467122 (W 0.00617396) | 0.51519 ± 0.00496456 (W 0.00229182) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 1.13966 ± 0.00467544 (W 0.00298366) | 1.1815 ± 0.00863609 (W 0.00889111) | 1.51345 ± 0.0179616 (W 0.00456435) | · | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 3.91603 ± 0.0117571 (W 0.0116431) | 3.91422 ± 0.0109069 (W 0.00761093) | 4.66838 ± 0.0456674 (W 0.0318416) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## gemm-mid, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.132918 ± 0.00039945 (W 0.00117538) | 0.133048 ± 0.000524863 (W 0.000148296) | 0.166281 ± 0.000998174 (W 0.00110478) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `gemm/192x192x192/b1` | 0.449638 ± 0.00269598 (W 0.00246033) | 0.450029 ± 0.00104851 (W 0.00204322) | 0.481438 ± 0.00449876 (W 0.00258267) | · | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 1.07365 ± 0.00340851 (W 0.00163452) | 1.07041 ± 0.00725401 (W 0.000757551) | 1.19243 ± 0.00611525 (W 0.00350264) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 3.59355 ± 0.0122984 (W 0.00310545) | 3.59612 ± 0.0275954 (W 0.00409646) | 3.71814 ± 0.0152188 (W 0.00142835) | · | · |  |
| `gemm/512x512x512/b1` | 8.58466 ± 0.0364581 (W 0.007699) | 8.58278 ± 0.0647225 (W 0.0160505) | 9.85134 ± 0.0808629 (W 0.0222645) | · | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 29.3167 ± 0.0668542 (W 0.0231108) | 29.2957 ± 0.280131 (W 0.0181427) | 30.44 ± 0.0818322 (W 0.0387357) | · | · |  |

## gemm-mid, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.045305 ± 0.000205322 (W 0.000292876) | 0.082164 ± 0.00328485 (W 0.0131087) | 0.054903 ± 0.000706507 (W 0.000244672) | 🔵 faer-fork 1.81× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/192x192x192/b1` | 0.118932 ± 0.000887352 (W 0.00133971) | 0.16066 ± 0.000620074 (W 0.00399782) | 0.135873 ± 0.00169493 (W 0.00166456) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 0.292056 ± 0.00228595 (W 0.00234495) | 0.308155 ± 0.00356514 (W 0.00993796) | 0.34353 ± 0.00277349 (W 0.00174755) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 0.915471 ± 0.00178914 (W 0.00407863) | 0.916259 ± 0.000355579 (W 0.00257684) | 1.00549 ± 0.00184655 (W 0.00284003) | · | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 2.21636 ± 0.00907325 (W 0.00602354) | 2.21146 ± 0.0048531 (W 0.00456921) | 2.87127 ± 0.0751134 (W 0.00480512) | · | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 7.48902 ± 0.0302888 (W 0.0113882) | 7.50434 ± 0.0330132 (W 0.01045) | 8.44795 ± 0.0403851 (W 0.01589) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |

## gemm-mid, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.032701 ± 0.000359639 (W 0.00115143) | 0.070362 ± 0.000100583 (W 0.0224731) | 0.03198 ± 0.000541942 (W 0.000297969) | 🔵 faer-fork 2.15× faster than `faer-upstream` | · |  |
| `gemm/192x192x192/b1` | 0.086802 ± 0.00063365 (W 0.0010982) | 0.190194 ± 0.0118449 (W 0.0336701) | 0.074899 ± 0.000793034 (W 0.000688386) | 🔵 faer-fork 2.19× faster than `faer-upstream` | 🔴 faer-fork 1.16× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/256x256x256/b1` | 0.165689 ± 0.00233536 (W 0.00146498) | 0.262539 ± 0.0347151 (W 0.0347115) | 0.179575 ± 0.00070724 (W 0.00170367) | 🔵 faer-fork 1.58× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/384x384x384/b1` | 0.47641 ± 0.00350481 (W 0.00225053) | 0.56342 ± 0.00240905 (W 0.00489173) | 0.513137 ± 0.00173289 (W 0.00343864) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 1.13881 ± 0.00515058 (W 0.00162279) | 1.1833 ± 0.00490862 (W 0.00807889) | 1.50062 ± 0.0184942 (W 0.00537466) | · | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 3.91016 ± 0.00933566 (W 0.00563237) | 3.91726 ± 0.0142789 (W 0.0110496) | 4.67393 ± 0.010434 (W 0.022868) | · | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |

## gemm-mid, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.535298 ± 0.0050888 (W 0.00279256) | 0.537563 ± 0.00236438 (W 0.00211626) | 0.649244 ± 0.000486248 (W 0.00376143) | · | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `gemm/192x192x192/b1` | 1.80221 ± 0.00725572 (W 0.00235408) | 1.81371 ± 0.00917912 (W 0.00249996) | 2.14314 ± 0.00957274 (W 0.00596358) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 4.26682 ± 0.0165727 (W 0.00566653) | 4.26768 ± 0.0131605 (W 0.00450429) | 5.11641 ± 0.0266543 (W 0.0113326) | · | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 14.3877 ± 0.076922 (W 0.00916096) | 14.4298 ± 0.120479 (W 0.0177286) | 17.0858 ± 0.0475219 (W 0.0315431) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 34.2457 ± 0.110622 (W 0.0226608) | 34.4129 ± 0.135667 (W 0.0553557) | 40.5731 ± 0.125695 (W 0.134754) | · | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 116.026 ± 0.359091 (W 0.424383) | 116.174 ± 0.315652 (W 0.0842478) | 138.053 ± 0.272978 (W 0.123177) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## gemm-mid, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.152695 ± 0.000819403 (W 0.000241057) | 0.169476 ± 0.000578476 (W 0.00212935) | 0.231663 ± 0.000568707 (W 0.00271861) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `gemm/192x192x192/b1` | 0.457543 ± 0.00130384 (W 0.00243796) | 0.457904 ± 0.00101062 (W 0.00315514) | 0.745793 ± 0.00672984 (W 0.0065225) | · | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 1.10986 ± 0.00110181 (W 0.00244685) | 1.11117 ± 0.00437283 (W 0.00271414) | 1.79576 ± 0.0210365 (W 0.00609914) | · | 🔵 faer-fork 1.62× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 3.62873 ± 0.0117977 (W 0.00724404) | 3.62217 ± 0.0102315 (W 0.00519365) | 5.79083 ± 0.0243135 (W 0.00726426) | · | 🔵 faer-fork 1.60× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 8.66132 ± 0.0334035 (W 0.0068077) | 8.67666 ± 0.0407121 (W 0.0111124) | 13.7864 ± 0.0433124 (W 0.0406785) | · | 🔵 faer-fork 1.59× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 29.3824 ± 0.10403 (W 0.0281345) | 29.4368 ± 0.118849 (W 0.0226755) | 46.4717 ± 0.182079 (W 0.105885) | · | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |

## gemm-mid, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.103323 ± 0.000454513 (W 0.000625329) | 0.119904 ± 0.0123441 (W 0.014199) | 0.095429 ± 0.000326676 (W 0.00098649) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔴 faer-fork 1.08× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/192x192x192/b1` | 0.236172 ± 3.61985e-05 (W 0.00182546) | 0.276786 ± 0.00239469 (W 0.00212594) | 0.29488 ± 0.00419563 (W 0.00161766) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 0.581965 ± 0.0038584 (W 0.00211046) | 0.610288 ± 0.00215074 (W 0.00247241) | 0.693062 ± 0.00869469 (W 0.00406472) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 1.83397 ± 0.00364152 (W 0.00515087) | 1.82847 ± 0.0125414 (W 0.00837465) | 2.29172 ± 0.0096485 (W 0.00857292) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 4.45801 ± 0.0189573 (W 0.0137263) | 4.45853 ± 0.00927827 (W 0.010526) | 5.55652 ± 0.0163307 (W 0.0285914) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 15.0401 ± 0.0376806 (W 0.0140529) | 15.0029 ± 0.0432042 (W 0.0122527) | 18.5798 ± 0.133986 (W 0.104802) | · | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |

## gemm-mid, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.537212 ± 0.00411227 (W 0.00239288) | 0.539295 ± 0.00238465 (W 0.00211789) | 0.649244 ± 0.00581661 (W 0.00483967) | · | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `gemm/192x192x192/b1` | 1.80278 ± 0.006699 (W 0.00397147) | 1.81076 ± 0.00484572 (W 0.00240502) | 2.14772 ± 0.0120864 (W 0.0150988) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 4.26817 ± 0.0140537 (W 0.00551828) | 4.27491 ± 0.0113863 (W 0.00303202) | 5.09583 ± 0.0406104 (W 0.0139815) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 14.3817 ± 0.0505759 (W 0.0164937) | 14.3957 ± 0.118852 (W 0.0212422) | 17.1172 ± 0.0461135 (W 0.0390736) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 34.2472 ± 0.12389 (W 0.0417914) | 34.2518 ± 0.106211 (W 0.0191013) | 40.6063 ± 0.241331 (W 0.246683) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 116.085 ± 0.221949 (W 0.0756599) | 116.256 ± 0.25824 (W 0.0898979) | 137.556 ± 0.426116 (W 0.160108) | · | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |

## gemm-mid, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.153937 ± 0.0009611 (W 0.000524043) | 0.168905 ± 0.00501146 (W 0.00419396) | 0.231583 ± 0.00105142 (W 0.00322783) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/192x192x192/b1` | 0.457413 ± 0.000894118 (W 0.00303166) | 0.457724 ± 0.0014278 (W 0.00270654) | 0.741001 ± 0.00367319 (W 0.00479606) | · | 🔵 faer-fork 1.62× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 1.10823 ± 0.0038796 (W 0.00275685) | 1.11119 ± 0.00524643 (W 0.00247934) | 1.81007 ± 0.0230419 (W 0.00513289) | · | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 3.63474 ± 0.0158964 (W 0.00717325) | 3.62284 ± 0.0172155 (W 0.00460386) | 5.79122 ± 0.0270862 (W 0.010698) | · | 🔵 faer-fork 1.59× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 8.65322 ± 0.0329498 (W 0.0148907) | 8.66808 ± 0.0508405 (W 0.0133582) | 13.8033 ± 0.055444 (W 0.0236655) | · | 🔵 faer-fork 1.60× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 29.4121 ± 0.142317 (W 0.0260535) | 29.3831 ± 0.161442 (W 0.0207836) | 46.1784 ± 0.448546 (W 0.0537569) | · | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |

## gemm-mid, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.102301 ± 0.000247266 (W 0.00055157) | 0.120715 ± 0.0126751 (W 0.013514) | 0.094687 ± 0.000206786 (W 0.000706497) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔴 faer-fork 1.08× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/192x192x192/b1` | 0.23585 ± 0.000207172 (W 0.00210915) | 0.276536 ± 0.00162706 (W 0.00272159) | 0.297355 ± 0.00110539 (W 0.00215269) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `gemm/256x256x256/b1` | 0.582425 ± 0.00356945 (W 0.00152409) | 0.609777 ± 0.0023461 (W 0.00206433) | 0.699814 ± 0.00652101 (W 0.0030243) | · | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `gemm/384x384x384/b1` | 1.83527 ± 0.00449759 (W 0.00367566) | 1.83662 ± 0.00166216 (W 0.00258649) | 2.28051 ± 0.00376998 (W 0.00914268) | · | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `gemm/512x512x512/b1` | 4.45709 ± 0.010946 (W 0.0135363) | 4.4741 ± 0.0192586 (W 0.0116618) | 5.52173 ± 0.0245162 (W 0.0123309) | · | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `gemm/768x768x768/b1` | 14.9901 ± 0.0180868 (W 0.0197432) | 14.9922 ± 0.0317673 (W 0.0185361) | 18.6541 ± 0.059096 (W 0.0753274) | · | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |

## gemm-tall, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.24885 ± 0.0573866 (W 0.00601855) | 1.25418 ± 0.070031 (W 0.00740415) | 1.62521 ± 0.101937 (W 0.00598915) | · | 🔵 faer-fork 1.30× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/4096x16x240/b1` | 1.07007 ± 0.00979529 (W 0.0107843) | 1.06973 ± 0.00571151 (W 0.00791902) | 1.52296 ± 0.0077903 (W 0.00624497) | · | 🔵 faer-fork 1.42× faster than `lapack-mkl` |  |
| `gemm/4096x64x64/b1` | 1.08267 ± 0.00289252 (W 0.00233727) | 1.08562 ± 0.0019038 (W 0.00270869) | 1.54755 ± 0.0115855 (W 0.00357299) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |

## gemm-tall, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.42384 ± 0.00248337 (W 0.00410269) | 0.427097 ± 0.00136546 (W 0.00468258) | 0.437846 ± 0.00543065 (W 0.0050722) | · | · |  |
| `gemm/4096x16x240/b1` | 0.308134 ± 0.00451122 (W 0.0026438) | 0.309629 ± 0.00319496 (W 0.00251641) | 0.42376 ± 0.00157401 (W 0.00332076) | · | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `gemm/4096x64x64/b1` | 0.275605 ± 0.00193237 (W 0.00166216) | 0.29966 ± 0.001481 (W 0.00327002) | 0.38607 ± 0.00333889 (W 0.00215053) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |

## gemm-tall, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.422489 ± 0.00147363 (W 0.00301539) | 0.426005 ± 0.00236157 (W 0.00270993) | 0.269583 ± 0.003329 (W 0.00326108) | · | 🔴 faer-fork 1.57× slower than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 0.186407 ± 0.000767524 (W 0.00117162) | 0.188521 ± 0.00122887 (W 0.00434976) | 0.287185 ± 0.000759957 (W 0.00161808) | · | 🔵 faer-fork 1.54× faster than `lapack-mkl` |  |
| `gemm/4096x64x64/b1` | 0.141594 ± 0.00114752 (W 0.00184366) | 0.198952 ± 0.00591839 (W 0.0060355) | 0.199262 ± 0.004628 (W 0.00194676) | 🔵 faer-fork 1.41× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` | `!` between-start range over 5% |

## gemm-tall, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.03941 ± 0.00914722 (W 0.00281818) | 1.04067 ± 0.00769216 (W 0.0030846) | 2.59038 ± 0.0359799 (W 0.015264) | · | 🔵 faer-fork 2.49× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 1.08183 ± 0.0182029 (W 0.00860359) | 1.08266 ± 0.0121361 (W 0.00490646) | 1.54423 ± 0.050204 (W 0.00758832) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/4096x64x64/b1` | 1.12855 ± 0.00428971 (W 0.00409825) | 1.12744 ± 0.000595468 (W 0.00280042) | 1.2486 ± 0.00722689 (W 0.004313) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |

## gemm-tall, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.325166 ± 0.000558607 (W 0.00485178) | 0.71365 ± 0.00474646 (W 0.00557253) | 0.632208 ± 0.00291124 (W 0.00358041) | 🔵 faer-fork 2.19× faster than `faer-upstream` | 🔵 faer-fork 1.94× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 0.299128 ± 0.00191227 (W 0.00287603) | 0.295331 ± 0.000744713 (W 0.00208828) | 0.423319 ± 0.000660213 (W 0.00345506) | · | 🔵 faer-fork 1.42× faster than `lapack-mkl` |  |
| `gemm/4096x64x64/b1` | 0.296063 ± 0.000355703 (W 0.00156081) | 0.293929 ± 0.000725758 (W 0.00268043) | 0.333672 ± 0.00402218 (W 0.00244915) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |

## gemm-tall, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.201346 ± 0.00189201 (W 0.00434096) | 1.13838 ± 0.00314335 (W 0.0184241) | 0.340184 ± 0.00506185 (W 0.0045958) | 🔵 faer-fork 5.65× faster than `faer-upstream` | 🔵 faer-fork 1.69× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 0.180036 ± 0.00038093 (W 0.00258002) | 0.180136 ± 0.00157799 (W 0.0019423) | 0.290181 ± 0.0015434 (W 0.00204681) | · | 🔵 faer-fork 1.61× faster than `lapack-mkl` |  |
| `gemm/4096x64x64/b1` | 0.158927 ± 1.60882 (W 0.00200103) | 0.158155 ± 0.000955948 (W 0.0020357) | 0.174856 ± 0.00354071 (W 0.00158304) | · | · | `!` between-start range over 5%; `p` position effect over 5% |

## gemm-tall, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 4.13793 ± 0.0191572 (W 0.00817727) | 4.13579 ± 0.00504769 (W 0.0120227) | 5.73459 ± 0.0519674 (W 0.0183341) | · | 🔵 faer-fork 1.39× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 4.34641 ± 0.0138149 (W 0.00669097) | 4.31469 ± 0.0347461 (W 0.00422482) | 6.25384 ± 0.0176926 (W 0.04059) | · | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `gemm/4096x64x64/b1` | 4.38278 ± 0.0193051 (W 0.0112631) | 4.39342 ± 0.00807548 (W 0.0133127) | 5.22604 ± 0.0262938 (W 0.0116389) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## gemm-tall, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.65069 ± 0.00708044 (W 0.00345165) | 1.65356 ± 0.00972238 (W 0.0048875) | 1.95325 ± 0.0119522 (W 0.00664858) | · | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 1.15301 ± 0.00650465 (W 0.00443797) | 1.14623 ± 0.005162 (W 0.00569016) | 2.02107 ± 0.0662628 (W 0.0237509) | · | 🔵 faer-fork 1.75× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/4096x64x64/b1` | 1.11961 ± 0.00393301 (W 0.00145806) | 1.13102 ± 0.00561025 (W 0.00258063) | 2.051 ± 0.0201089 (W 0.00202517) | · | 🔵 faer-fork 1.83× faster than `lapack-mkl` |  |

## gemm-tall, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.90105 ± 0.0200255 (W 0.00510225) | 0.896942 ± 0.00285884 (W 0.00515966) | 0.955832 ± 0.0033117 (W 0.00446467) | · | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 0.61128 ± 2.92194 (W 0.00192068) | 0.593246 ± 0.00849905 (W 0.00285883) | 0.967804 ± 0.0318345 (W 0.0155255) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/4096x64x64/b1` | 0.573148 ± 0.0024596 (W 0.0033109) | 0.616288 ± 0.0229408 (W 0.0111771) | 0.766219 ± 0.00607332 (W 0.00312844) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` | `!` between-start range over 5% |

## gemm-tall, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 4.06356 ± 0.0154864 (W 0.0103419) | 4.05157 ± 0.0164564 (W 0.0123785) | 5.68519 ± 0.0214909 (W 0.0176956) | · | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 4.38465 ± 0.0211013 (W 0.00800789) | 4.37183 ± 0.0362644 (W 0.00588791) | 6.04987 ± 0.310436 (W 0.0925646) | · | 🔵 faer-fork 1.38× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/4096x64x64/b1` | 4.43461 ± 0.0041664 (W 0.00986216) | 4.43057 ± 0.0103877 (W 0.00850237) | 5.82369 ± 0.0120059 (W 0.0215321) | · | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |

## gemm-tall, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.18277 ± 0.00334541 (W 0.00233039) | 1.94276 ± 0.00674246 (W 0.0177075) | 36.5778 ± 0.0791836 (W 0.0134975) | 🔵 faer-fork 1.64× faster than `faer-upstream` | 🔵 faer-fork 30.93× faster than `lapack-mkl` |  |
| `gemm/4096x16x240/b1` | 1.16698 ± 0.00576751 (W 0.00417547) | 1.14895 ± 0.00604868 (W 0.00314692) | 2.07932 ± 0.181183 (W 0.0649109) | · | 🔵 faer-fork 1.78× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/4096x64x64/b1` | 1.18951 ± 0.00961478 (W 0.0113413) | 1.17848 ± 0.012677 (W 0.0102822) | 2.03693 ± 0.0304703 (W 0.00944321) | · | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |

## gemm-tall, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.663607 ± 0.0034071 (W 0.00343737) | 2.56446 ± 0.0238866 (W 0.0305601) | 9.94555 ± 0.371323 (W 0.00541521) | 🔵 faer-fork 3.86× faster than `faer-upstream` | 🔵 faer-fork 14.99× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/4096x16x240/b1` | 0.600299 ± 0.00500174 (W 0.00185169) | 0.601101 ± 0.00716244 (W 0.00349364) | 1.59372 ± 0.0618323 (W 0.0150047) | · | 🔵 faer-fork 2.65× faster than `lapack-mkl` | `!` between-start range over 5% |
| `gemm/4096x64x64/b1` | 0.582356 ± 0.00667613 (W 0.00542671) | 0.586614 ± 0.00672458 (W 0.00483672) | 1.13541 ± 0.0152233 (W 0.0704074) | · | 🔵 faer-fork 1.95× faster than `lapack-mkl` |  |

## gemm-wide, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.12457 ± 0.0030222 (W 0.00315569) | 1.1289 ± 0.00550883 (W 0.00481255) | 1.24626 ± 0.00929736 (W 0.00347127) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |

## gemm-wide, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.294961 ± 0.00170451 (W 0.00187819) | 0.294369 ± 0.00324504 (W 0.0022284) | 0.32722 ± 0.00378177 (W 0.00177255) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |

## gemm-wide, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.156071 ± 1.61638 (W 0.00102863) | 0.156682 ± 0.00159926 (W 0.00172195) | 0.169306 ± 0.00356518 (W 0.0021529) | · | · | `!` between-start range over 5%; `p` position effect over 5% |

## gemm-wide, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.08213 ± 0.0057304 (W 0.00201354) | 1.08069 ± 0.00674574 (W 0.00287324) | 1.53645 ± 0.0108543 (W 0.00505971) | · | 🔵 faer-fork 1.42× faster than `lapack-mkl` |  |

## gemm-wide, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.276135 ± 0.0015623 (W 0.00157112) | 0.301853 ± 0.00111685 (W 0.00345161) | 0.38632 ± 0.0052119 (W 0.00289626) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |

## gemm-wide, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.142776 ± 0.000257935 (W 0.00236455) | 0.202498 ± 0.0103411 (W 0.0038335) | 0.206345 ± 0.00450346 (W 0.00312537) | 🔵 faer-fork 1.42× faster than `faer-upstream` | 🔵 faer-fork 1.45× faster than `lapack-mkl` | `!` between-start range over 5% |

## gemm-wide, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 4.42392 ± 0.00645061 (W 0.0136606) | 4.42862 ± 0.020387 (W 0.00863481) | 5.67114 ± 0.0154767 (W 0.0201578) | · | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |

## gemm-wide, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.17383 ± 0.0111228 (W 0.0058424) | 1.17334 ± 0.00150066 (W 0.00365068) | 2.04273 ± 0.0234139 (W 0.0129868) | · | 🔵 faer-fork 1.74× faster than `lapack-mkl` |  |

## gemm-wide, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.577438 ± 0.00582166 (W 0.0053794) | 0.582266 ± 0.00443681 (W 0.0043148) | 1.16223 ± 0.0306489 (W 0.0635508) | · | 🔵 faer-fork 2.01× faster than `lapack-mkl` | `!` between-start range over 5% |

## gemm-wide, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 4.39017 ± 0.0165339 (W 0.013043) | 4.39334 ± 0.0255446 (W 0.00823128) | 5.23293 ± 0.0235227 (W 0.0210389) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## gemm-wide, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.11615 ± 0.00334501 (W 0.00310115) | 1.12358 ± 0.00881644 (W 0.0030774) | 2.06024 ± 0.0097486 (W 0.00274996) | · | 🔵 faer-fork 1.85× faster than `lapack-mkl` |  |

## gemm-wide, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.568811 ± 0.00166617 (W 0.00156164) | 0.596092 ± 0.0224656 (W 0.0185776) | 0.765118 ± 0.00123858 (W 0.00272936) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5% |

## linalg-small, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003166 ± 0 (W 2.68328e-05) | 0.003386 ± 0.000144015 (W 1.96545e-05) | 0.004288 ± 6.245e-05 (W 4.65833e-05) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014748 ± 8.01686e-05 (W 3.26542e-05) | 0.013926 ± 0.00170242 (W 5.9869e-05) | 0.017172 ± 0.000197445 (W 8.87694e-05) | · | 🔵 faer-fork 1.16× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.031128 ± 0.000208399 (W 5.89084e-05) | 0.029996 ± 0.000859332 (W 6.72622e-05) | 0.048841 ± 0.00018735 (W 0.00165367) | · | 🔵 faer-fork 1.57× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.113 ± 0.000935811 (W 0.00176752) | 0.113712 ± 0.000377002 (W 0.00129681) | 0.098143 ± 0.000525399 (W 0.000157509) | · | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.495144 ± 0.000649058 (W 0.00319287) | 0.485476 ± 0.000814519 (W 0.00278893) | 0.389537 ± 0.00246351 (W 0.0029279) | · | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.19696 ± 0.00241444 (W 0.00345688) | 1.15881 ± 0.00195631 (W 0.00348979) | 0.898815 ± 0.00410974 (W 0.00181697) | · | 🔴 faer-fork 1.33× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.012714 ± 0.000132578 (W 0.000120554) | 0.010549 ± 0.000239396 (W 6.01664e-05) | - | 🔴 faer-fork 1.21× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.05369 ± 0.000499691 (W 0.000682272) | 0.046887 ± 0.000378021 (W 0.00019442) | - | 🔴 faer-fork 1.15× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.142325 ± 0.000562608 (W 0.00195729) | 0.129842 ± 0.000373579 (W 0.00129367) | - | 🔴 faer-fork 1.10× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.008416 ± 0.000104213 (W 5.33592e-05) | 0.008236 ± 3.84318e-05 (W 5.33226e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.008466 ± 4.62637e-05 (W 3.64692e-05) | 0.008195 ± 2.94449e-05 (W 3.94487e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.040977 ± 0.000302987 (W 0.000138413) | 0.040386 ± 0.000218749 (W 7.45339e-05) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.041197 ± 0.000225775 (W 0.000356701) | 0.040716 ± 0.000164621 (W 0.000126338) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.122178 ± 0.000704415 (W 0.00193797) | 0.119673 ± 0.000346541 (W 0.00140789) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.122949 ± 0.0010959 (W 0.000163084) | 0.120244 ± 0.000462169 (W 0.000583378) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.008897 ± 8.35484e-05 (W 5.7239e-05) | 0.007474 ± 0.000185599 (W 0.000158209) | 0.013726 ± 2.51661e-05 (W 0.00011726) | 🔴 faer-fork 1.19× slower than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.031388 ± 0.000423935 (W 0.000214984) | 0.02665 ± 7.81025e-05 (W 0.000147541) | 0.046587 ± 0.00023596 (W 0.000181001) | 🔴 faer-fork 1.18× slower than `faer-upstream` | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.072706 ± 0.00242896 (W 0.000418487) | 0.066123 ± 0.00254283 (W 0.000283841) | 0.110145 ± 0.000178401 (W 0.000412752) | 🔴 faer-fork 1.10× slower than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n32/b1` | 0.032871 ± 0.000175519 (W 0.000172332) | 0.03238 ± 8.54225e-05 (W 0.000145654) | 0.027211 ± 0.0308675 (W 0.000144421) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n64/b1` | 0.118972 ± 0.000662572 (W 0.00182551) | 0.120755 ± 0.000734664 (W 0.000559367) | 0.136515 ± 0.00129791 (W 0.00222621) | · | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.272598 ± 0.00140466 (W 0.00312986) | 0.282377 ± 0.00269686 (W 0.00424308) | 0.408693 ± 0.00334488 (W 0.0104639) | · | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.024135 ± 6.65833e-05 (W 0.000105024) | 0.028673 ± 2.46374e-05 (W 0.0001679) | 0.014417 ± 0.000112398 (W 6.14427e-05) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.67× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.085549 ± 5.17397e-05 (W 0.000403343) | 0.133008 ± 0.00087453 (W 0.00149048) | 0.282387 ± 0.124443 (W 0.00214809) | 🔵 faer-fork 1.55× faster than `faer-upstream` | 🔵 faer-fork 3.30× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n96/b1` | 0.183473 ± 0.00108128 (W 0.00178783) | 0.290282 ± 0.00129684 (W 0.00215797) | 0.202679 ± 0.00144884 (W 0.00174688) | 🔵 faer-fork 1.58× faster than `faer-upstream` | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.010009 ± 3.4641e-05 (W 8.00144e-05) | 0.008356 ± 0.000124231 (W 0.000142988) | 0.014156 ± 0.000183058 (W 0.000122822) | 🔴 faer-fork 1.20× slower than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.032461 ± 0.000427541 (W 0.000114766) | 0.027832 ± 0.000361156 (W 0.000139521) | 0.045705 ± 0.000348833 (W 0.000102451) | 🔴 faer-fork 1.17× slower than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.083305 ± 0.000621821 (W 0.00237054) | 0.06981 ± 0.00020939 (W 0.0018918) | 0.108763 ± 0.000491034 (W 0.0002056) | 🔴 faer-fork 1.19× slower than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.169276 ± 0.00116679 (W 0.000251903) | 0.184825 ± 0.00137432 (W 0.00173438) | 0.176319 ± 0.00100215 (W 0.00200644) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · |  |
| `svd_thin/n64/b1` | 0.86295 ± 0.0100875 (W 0.0023943) | 0.923932 ± 0.00902396 (W 0.000503533) | 0.706819 ± 0.00215411 (W 0.00290395) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.22× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.08475 ± 0.028037 (W 0.0051328) | 2.22166 ± 0.0126788 (W 0.00486526) | 1.65307 ± 0.0511883 (W 0.00338176) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.26× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/n32/b1` | 0.067456 ± 0.000447001 (W 0.00015776) | 0.141804 ± 0.000505629 (W 0.0015536) | 0.063869 ± 0.0383615 (W 0.00159323) | 🔵 faer-fork 2.10× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n64/b1` | 0.237643 ± 0.00168207 (W 0.00234418) | 0.518406 ± 0.0040807 (W 0.00199877) | 0.259684 ± 0.00121418 (W 0.00206026) | 🔵 faer-fork 2.18× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.546039 ± 0.0015623 (W 0.00239276) | 1.18415 ± 0.0052488 (W 0.00471845) | 0.614557 ± 0.00321103 (W 0.00285468) | 🔵 faer-fork 2.17× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.000722 ± 1.47309e-05 (W 1.31643e-05) | 0.000691 ± 5.7735e-07 (W 2.59075e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.001593 ± 2e-05 (W 2.2698e-05) | 0.001482 ± 5.53203e-05 (W 1.69204e-05) | - | 🔴 faer-fork 1.07× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.002705 ± 3.21455e-05 (W 1.54013e-05) | 0.002554 ± 2.47049e-05 (W 1.81659e-05) | - | 🔴 faer-fork 1.06× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003196 ± 5.7735e-06 (W 4.08656e-05) | 0.003407 ± 0.000178401 (W 5.01926e-05) | 0.004318 ± 7e-05 (W 4.74342e-05) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014757 ± 5.87963e-05 (W 4.46464e-05) | 0.016782 ± 0.00201834 (W 0.00129342) | 0.017122 ± 0.000146277 (W 8.60366e-05) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔵 faer-fork 1.16× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.031118 ± 0.00015885 (W 9.47629e-05) | 0.036608 ± 0.000754389 (W 0.000307937) | 0.049081 ± 0.000654753 (W 0.000121862) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `eigh/n32/b1` | 0.113371 ± 0.000604247 (W 0.000243116) | 0.11276 ± 0.000517353 (W 0.000218477) | 0.103233 ± 0.000490437 (W 0.0016683) | · | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.487129 ± 0.00145312 (W 0.00341423) | 0.480296 ± 0.00235791 (W 0.0019718) | 0.269563 ± 0.00174578 (W 0.00235842) | · | 🔴 faer-fork 1.81× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.16727 ± 0.00272682 (W 0.00365762) | 1.12451 ± 0.00315753 (W 0.0016705) | 0.591012 ± 0.000945339 (W 0.00245183) | · | 🔴 faer-fork 1.98× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.013786 ± 0.000127671 (W 0.00016368) | 0.010279 ± 9.0185e-05 (W 0.000195431) | - | 🔴 faer-fork 1.34× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.055513 ± 0.000620418 (W 0.000167864) | 0.046556 ± 0.00012779 (W 0.000185813) | - | 🔴 faer-fork 1.19× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.158135 ± 0.00173746 (W 0.000920594) | 0.132527 ± 0.00123409 (W 0.000378841) | - | 🔴 faer-fork 1.19× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.006572 ± 0.000446458 (W 0.000278516) | 0.008426 ± 0.000100664 (W 0.00115589) | - | 🔵 faer-fork 1.28× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.007113 ± 0.000182008 (W 0.000281963) | 0.008396 ± 4.3589e-05 (W 9.76847e-05) | - | 🔵 faer-fork 1.18× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.019657 ± 0.000341635 (W 0.000268487) | 0.018976 ± 0.000303096 (W 0.000280108) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.021109 ± 0.000291959 (W 0.000574719) | 0.020628 ± 0.000232265 (W 0.000571578) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.046546 ± 0.000697769 (W 0.000676708) | 0.045425 ± 0.00030627 (W 0.000383377) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.046226 ± 0.000315273 (W 0.000568237) | 0.046015 ± 0.000337244 (W 0.000882859) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.009127 ± 0.000141539 (W 0.000101341) | 0.007234 ± 0.000192959 (W 6.4933e-05) | 0.013786 ± 0.000125033 (W 0.000109079) | 🔴 faer-fork 1.26× slower than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.031218 ± 0.000171144 (W 0.000110287) | 0.030066 ± 0.00023516 (W 0.00113642) | 0.046467 ± 0.000294228 (W 0.00036705) | · | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.072746 ± 0.00211517 (W 0.000533879) | 0.072445 ± 0.000481139 (W 0.00308715) | 0.093825 ± 7.57188e-05 (W 0.000357149) | · | 🔵 faer-fork 1.29× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n32/b1` | 0.034324 ± 0.000210792 (W 0.000137088) | 0.045976 ± 0.000352898 (W 0.00042186) | 0.08097 ± 0.0312206 (W 0.000102559) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔵 faer-fork 2.36× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n64/b1` | 0.112028 ± 0.00136786 (W 0.00150714) | 0.183893 ± 0.00247274 (W 0.0011705) | 0.147696 ± 0.000933931 (W 0.00167739) | 🔵 faer-fork 1.64× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.241179 ± 0.0106494 (W 0.00193324) | 0.369419 ± 0.00517586 (W 0.0019173) | 0.341757 ± 0.00288597 (W 0.00695092) | 🔵 faer-fork 1.53× faster than `faer-upstream` | 🔵 faer-fork 1.42× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n32/b1` | 0.025848 ± 0.000451021 (W 7.0214e-05) | 0.04272 ± 0.000265908 (W 0.000674879) | 0.014617 ± 0.000109697 (W 6.53452e-05) | 🔵 faer-fork 1.65× faster than `faer-upstream` | 🔴 faer-fork 1.77× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.077695 ± 0.00190086 (W 0.000301042) | 0.206144 ± 0.00319263 (W 0.0020634) | 0.067355 ± 0.124334 (W 0.00012938) | 🔵 faer-fork 2.65× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n96/b1` | 0.15055 ± 0.00290546 (W 0.000708662) | 0.425493 ± 0.00958453 (W 0.00251926) | 0.90714 ± 0.00461082 (W 0.00283673) | 🔵 faer-fork 2.83× faster than `faer-upstream` | 🔵 faer-fork 6.03× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.0106 ± 0.000170098 (W 0.000115197) | 0.008365 ± 2.25167e-05 (W 5.0707e-05) | 0.014247 ± 5.08626e-05 (W 6.73892e-05) | 🔴 faer-fork 1.27× slower than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.033502 ± 0.000361 (W 0.000140817) | 0.030877 ± 0.000143377 (W 0.000574496) | 0.045424 ± 0.000419835 (W 0.00177851) | 🔴 faer-fork 1.09× slower than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.084789 ± 0.00121046 (W 0.00338587) | 0.066103 ± 0.000761086 (W 0.000540611) | 0.092522 ± 0.000112073 (W 0.00173587) | 🔴 faer-fork 1.28× slower than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.17153 ± 0.00111941 (W 0.0019508) | 0.185866 ± 0.0019496 (W 0.00202355) | 0.185024 ± 0.000983709 (W 0.00155065) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 0.853382 ± 0.00216201 (W 0.00278487) | 0.905399 ± 0.00434086 (W 0.00288966) | 0.673195 ± 0.0049537 (W 0.00341977) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.05393 ± 0.00922231 (W 0.00268955) | 2.08887 ± 0.00316337 (W 0.00498303) | 1.46722 ± 0.0209639 (W 0.00501075) | · | 🔴 faer-fork 1.40× slower than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.068839 ± 0.000261031 (W 0.000167518) | 0.141754 ± 0.00100176 (W 0.00164509) | 0.130083 ± 0.0386601 (W 0.00207507) | 🔵 faer-fork 2.06× faster than `faer-upstream` | 🔵 faer-fork 1.89× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n64/b1` | 0.242842 ± 0.000538534 (W 0.00195139) | 0.520351 ± 0.000544011 (W 0.00214419) | 0.265194 ± 0.000295794 (W 0.00224319) | 🔵 faer-fork 2.14× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.578368 ± 0.00285706 (W 0.0022987) | 1.17604 ± 0.00633803 (W 0.00164843) | 0.59577 ± 0.00368651 (W 0.00265998) | 🔵 faer-fork 2.03× faster than `faer-upstream` | · |  |
| `triangular_solve/n32/b1` | 0.000962 ± 9.50438e-06 (W 3.04959e-05) | 0.000661 ± 6.08276e-06 (W 2.34585e-05) | - | 🔴 faer-fork 1.46× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002104 ± 1e-05 (W 1.28141e-05) | 0.001483 ± 2.08167e-05 (W 3.08221e-05) | - | 🔴 faer-fork 1.42× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003536 ± 8.77895e-05 (W 1.96545e-05) | 0.002555 ± 4.3589e-05 (W 3.50714e-05) | - | 🔴 faer-fork 1.38× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003226 ± 5.85947e-05 (W 3.14992e-05) | 0.003416 ± 0.000162287 (W 3.10693e-05) | 0.004278 ± 3.60555e-05 (W 6.34035e-05) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014908 ± 6.40859e-05 (W 3.97492e-05) | 0.014977 ± 5.00033e-05 (W 4.72229e-05) | 0.017002 ± 0.000117758 (W 3.36348e-05) | · | 🔵 faer-fork 1.14× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.031158 ± 0.00157571 (W 9.62575e-05) | 0.03764 ± 0.000404348 (W 0.000217034) | 0.049222 ± 0.000401042 (W 0.000137295) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.113722 ± 0.000366011 (W 0.000156446) | 0.11275 ± 0.0002916 (W 0.00185949) | 0.103843 ± 0.000355922 (W 0.00163274) | · | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.486827 ± 0.0029883 (W 0.00202575) | 0.481758 ± 0.000738734 (W 0.00245417) | 0.260485 ± 0.000738798 (W 0.00213812) | · | 🔴 faer-fork 1.87× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.16337 ± 0.0025228 (W 0.00237192) | 1.13799 ± 0.00191982 (W 0.00432026) | 0.570103 ± 0.0183855 (W 0.00233643) | · | 🔴 faer-fork 2.04× slower than `lapack-mkl` | `!` between-start range over 5% |
| `full_piv_lu/n32/b1` | 0.013776 ± 0.000140571 (W 0.0001039) | 0.010129 ± 2.08167e-05 (W 0.000167114) | - | 🔴 faer-fork 1.36× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.054892 ± 0.000691527 (W 0.000267297) | 0.046627 ± 0.000211 (W 0.000118488) | - | 🔴 faer-fork 1.18× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.165979 ± 0.00137691 (W 0.00147525) | 0.133359 ± 0.000821421 (W 0.00138809) | - | 🔴 faer-fork 1.24× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.006372 ± 0.000544114 (W 0.000168137) | 0.008426 ± 3.56417e-05 (W 9.96609e-05) | - | 🔵 faer-fork 1.32× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.006221 ± 0.000261969 (W 0.000155188) | 0.008395 ± 9.09414e-05 (W 0.000102534) | - | 🔵 faer-fork 1.35× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.014707 ± 0.000228649 (W 0.000255416) | 0.018936 ± 0.000429516 (W 0.000407174) | - | 🔵 faer-fork 1.29× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.016771 ± 0.000261401 (W 0.000372713) | 0.020348 ± 0.00015201 (W 0.00043551) | - | 🔵 faer-fork 1.21× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.032701 ± 0.000724184 (W 0.00041918) | 0.057147 ± 0.000881027 (W 0.000803516) | - | 🔵 faer-fork 1.75× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.032611 ± 0.000532536 (W 0.000213095) | 0.056816 ± 0.0010721 (W 0.00123963) | - | 🔵 faer-fork 1.74× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.008947 ± 6.0803e-05 (W 9.08697e-05) | 0.007204 ± 5.34821e-05 (W 0.000201048) | 0.013805 ± 8.66622e-05 (W 0.000110821) | 🔴 faer-fork 1.24× slower than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.031529 ± 9.34719e-05 (W 0.00013216) | 0.030587 ± 0.000136297 (W 0.000813089) | 0.046226 ± 0.000508931 (W 0.000315048) | · | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.073297 ± 0.00231512 (W 0.000373311) | 0.073878 ± 0.000480715 (W 0.0018412) | 0.091841 ± 0.000393303 (W 0.000501691) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n32/b1` | 0.034645 ± 0.000366934 (W 0.000105576) | 0.053971 ± 0.000601682 (W 0.000711999) | 0.08029 ± 0.0309286 (W 0.000221878) | 🔵 faer-fork 1.56× faster than `faer-upstream` | 🔵 faer-fork 2.32× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n64/b1` | 0.110015 ± 0.000315311 (W 0.000668219) | 0.229107 ± 0.00228585 (W 0.00209195) | 0.158826 ± 0.00167443 (W 0.00175177) | 🔵 faer-fork 2.08× faster than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.235749 ± 0.0115335 (W 0.00178696) | 0.462612 ± 0.0145396 (W 0.00296529) | 0.345113 ± 0.00217986 (W 0.00981039) | 🔵 faer-fork 1.96× faster than `faer-upstream` | 🔵 faer-fork 1.46× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n32/b1` | 0.024766 ± 0.000639303 (W 9.70835e-05) | 0.050193 ± 0.000654738 (W 0.00105962) | 0.014737 ± 9.61787e-05 (W 4.08069e-05) | 🔵 faer-fork 2.03× faster than `faer-upstream` | 🔴 faer-fork 1.68× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.078226 ± 0.00169255 (W 0.000171182) | 0.243664 ± 0.000687446 (W 0.00354441) | 0.067697 ± 0.12403 (W 0.00257587) | 🔵 faer-fork 3.11× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n96/b1` | 0.143578 ± 0.000414138 (W 0.000392503) | 0.49911 ± 0.00631734 (W 0.00391053) | 0.902743 ± 0.00158547 (W 0.00144721) | 🔵 faer-fork 3.48× faster than `faer-upstream` | 🔵 faer-fork 6.29× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.01078 ± 0.000105832 (W 8.66152e-05) | 0.008335 ± 0.000241868 (W 0.000178273) | 0.014157 ± 5.72742e-05 (W 6.5202e-05) | 🔴 faer-fork 1.29× slower than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.033132 ± 0.000140678 (W 0.000159269) | 0.031118 ± 0.000224225 (W 0.000362113) | 0.045555 ± 5.85947e-05 (W 9.94947e-05) | 🔴 faer-fork 1.06× slower than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.087102 ± 0.000646546 (W 0.00302617) | 0.067596 ± 0.00130816 (W 0.000556006) | 0.090198 ± 0.00031577 (W 0.000849884) | 🔴 faer-fork 1.29× slower than `faer-upstream` | · |  |
| `svd_thin/n32/b1` | 0.170888 ± 0.00128181 (W 0.000294588) | 0.185276 ± 0.00215296 (W 0.00188211) | 0.186497 ± 0.000383859 (W 0.00167791) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 0.84768 ± 0.00407418 (W 0.00217328) | 0.910026 ± 0.00130034 (W 0.00283119) | 0.664047 ± 0.0138943 (W 0.00266343) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.28× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.05354 ± 0.0365793 (W 0.00273827) | 2.10747 ± 0.00630526 (W 0.00300887) | 1.41543 ± 0.0176988 (W 0.00543236) | · | 🔴 faer-fork 1.45× slower than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.068377 ± 0.000460479 (W 0.000227755) | 0.140852 ± 0.000969292 (W 0.00163567) | 0.130363 ± 0.0385959 (W 0.00171932) | 🔵 faer-fork 2.06× faster than `faer-upstream` | 🔵 faer-fork 1.91× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n64/b1` | 0.244215 ± 0.0014944 (W 0.00188547) | 0.514398 ± 0.00293958 (W 0.00218221) | 0.266026 ± 0.000576561 (W 0.00148658) | 🔵 faer-fork 2.11× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.592214 ± 0.00473487 (W 0.00168651) | 1.17958 ± 0.00491289 (W 0.0019741) | 0.587145 ± 0.00205008 (W 0.0028367) | 🔵 faer-fork 1.99× faster than `faer-upstream` | · |  |
| `triangular_solve/n32/b1` | 0.000952 ± 2.02567e-05 (W 2.94958e-05) | 0.000661 ± 1.1547e-05 (W 2.54951e-05) | - | 🔴 faer-fork 1.44× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002134 ± 2.64575e-05 (W 2.73532e-05) | 0.001533 ± 2.70247e-05 (W 1.51658e-05) | - | 🔴 faer-fork 1.39× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003667 ± 4.72582e-05 (W 2.94958e-05) | 0.002755 ± 4.72582e-05 (W 6.30079e-05) | - | 🔴 faer-fork 1.33× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003066 ± 5.7735e-06 (W 3.30787e-05) | 0.003246 ± 0.000208407 (W 3.0468e-05) | 0.003397 ± 4.20357e-05 (W 1.35757e-05) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014457 ± 7.82326e-05 (W 3.67723e-05) | 0.013545 ± 0.000842005 (W 6.11335e-05) | 0.013976 ± 1.73205e-05 (W 5.71839e-05) | 🔴 faer-fork 1.07× slower than `faer-upstream` | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.029986 ± 0.000151767 (W 4.49355e-05) | 0.029255 ± 0.000846443 (W 9.30065e-05) | 0.038051 ± 0.000303699 (W 8.43107e-05) | · | 🔵 faer-fork 1.27× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.112019 ± 0.000836374 (W 0.00163281) | 0.113722 ± 0.00401978 (W 0.00163649) | 0.096089 ± 0.000345876 (W 0.000105315) | · | 🔴 faer-fork 1.17× slower than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n64/b1` | 0.495574 ± 0.000915721 (W 0.00206813) | 0.485165 ± 0.00292291 (W 0.00232254) | 0.382653 ± 0.00059759 (W 0.00247136) | · | 🔴 faer-fork 1.30× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.20165 ± 0.00404216 (W 0.00489147) | 1.15749 ± 0.00271463 (W 0.00174618) | 0.876454 ± 0.00488913 (W 0.00272503) | · | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.011361 ± 0.00025865 (W 9.73139e-05) | 0.010389 ± 5.74195e-05 (W 3.3975e-05) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.04807 ± 0.000220681 (W 0.000287114) | 0.046026 ± 0.000486972 (W 0.000342004) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.130984 ± 0.000648324 (W 0.00189348) | 0.127879 ± 0.000638348 (W 0.000182016) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.008526 ± 5e-05 (W 4.87852e-05) | 0.008306 ± 7.08543e-05 (W 5.65703e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.008556 ± 3e-05 (W 4.08656e-05) | 0.008295 ± 2.36714e-05 (W 5.09902e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.040957 ± 0.00034595 (W 0.00165495) | 0.040074 ± 0.000300136 (W 0.000109728) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.041026 ± 5.7735e-07 (W 0.000131272) | 0.040285 ± 0.000226053 (W 0.00181897) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.124492 ± 0.000498365 (W 0.00160938) | 0.122619 ± 0.000532129 (W 0.000495067) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.125664 ± 0.00127698 (W 0.00278861) | 0.122849 ± 0.000696895 (W 0.000123095) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.007404 ± 9.34897e-05 (W 3.34664e-05) | 0.007143 ± 3.51188e-05 (W 5.01627e-05) | 0.011071 ± 0.000110092 (W 0.000113698) | · | 🔵 faer-fork 1.50× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.026299 ± 0.000384548 (W 0.000187556) | 0.025688 ± 0.000115803 (W 0.000154276) | 0.036347 ± 0.000180417 (W 0.000109087) | · | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.059501 ± 0.000101737 (W 0.00044454) | 0.05931 ± 0.000238685 (W 0.00024561) | 0.08052 ± 0.000462105 (W 0.00155165) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.031449 ± 0.000146289 (W 0.000106996) | 0.032049 ± 0.000180502 (W 0.000190705) | 0.021811 ± 0.000172715 (W 7.60474e-05) | · | 🔴 faer-fork 1.44× slower than `lapack-mkl` |  |
| `qr/n64/b1` | 0.110807 ± 0.000884137 (W 0.00176278) | 0.117699 ± 0.00126271 (W 0.000250024) | 0.116027 ± 0.00111465 (W 0.000332408) | 🔵 faer-fork 1.06× faster than `faer-upstream` | · |  |
| `qr/n96/b1` | 0.258021 ± 0.000610461 (W 0.00319993) | 0.276445 ± 0.00141795 (W 0.00543821) | 0.340616 ± 0.00238263 (W 0.00307691) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.017443 ± 4.95681e-05 (W 8.61974e-05) | 0.018284 ± 5.85947e-05 (W 0.000104059) | 0.011963 ± 9.34897e-05 (W 6.36396e-05) | · | 🔴 faer-fork 1.46× slower than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `qr_factor/n64/b1` | 0.07006 ± 0.000952295 (W 0.000285058) | 0.076823 ± 0.000136077 (W 0.000426836) | 0.271857 ± 0.0010376 (W 0.00188987) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 3.88× faster than `lapack-mkl` |  |
| `qr_factor/n96/b1` | 0.14997 ± 0.000878413 (W 0.0015115) | 0.167823 ± 0.00106496 (W 0.00160056) | 0.89044 ± 0.00339777 (W 0.00202251) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 5.94× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.008155 ± 5.50757e-05 (W 6.84105e-05) | 0.008165 ± 0.000330137 (W 0.000128141) | 0.010941 ± 8.35484e-05 (W 6.02769e-05) | · | 🔵 faer-fork 1.34× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.026489 ± 0.000258354 (W 9.11822e-05) | 0.026459 ± 0.000156771 (W 0.00158242) | 0.035226 ± 0.00022643 (W 8.62856e-05) | · | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.071232 ± 0.000397318 (W 0.00137085) | 0.067716 ± 0.000151438 (W 0.00261737) | 0.078266 ± 0.000594643 (W 0.00171727) | 🔴 faer-fork 1.05× slower than `faer-upstream` | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.171 ± 0.00043336 (W 0.00171266) | 0.186127 ± 0.00101771 (W 0.0013402) | 0.166481 ± 0.00100206 (W 0.00195413) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · |  |
| `svd_thin/n64/b1` | 0.906091 ± 0.0124301 (W 0.00216087) | 0.962464 ± 0.00383201 (W 0.00150384) | 0.685648 ± 0.00654597 (W 0.00211717) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.32× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.0415 ± 0.0247039 (W 0.0031388) | 2.1518 ± 0.0314895 (W 0.00714457) | 1.58146 ± 0.0452689 (W 0.00756968) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔴 faer-fork 1.29× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/n32/b1` | 0.066925 ± 0.000138924 (W 0.000284551) | 0.143768 ± 0.000753371 (W 0.00179417) | 0.058509 ± 0.000281484 (W 6.80904e-05) | 🔵 faer-fork 2.15× faster than `faer-upstream` | 🔴 faer-fork 1.14× slower than `lapack-mkl` |  |
| `svd_values/n64/b1` | 0.241871 ± 0.00197887 (W 0.00185037) | 0.537662 ± 0.00218715 (W 0.00234547) | 0.248923 ± 0.00070094 (W 0.00219138) | 🔵 faer-fork 2.22× faster than `faer-upstream` | · |  |
| `svd_values/n96/b1` | 0.551379 ± 0.00155068 (W 0.00262133) | 1.19148 ± 0.00459739 (W 0.0030947) | 0.593819 ± 0.00454954 (W 0.00268342) | 🔵 faer-fork 2.16× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.000762 ± 6.08276e-05 (W 1.92432e-05) | 0.000762 ± 1.12694e-05 (W 1.68018e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.001764 ± 0.000144627 (W 1.81989e-05) | 0.001723 ± 7.77839e-05 (W 2.5225e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003246 ± 0.00021443 (W 3.27109e-05) | 0.003085 ± 0.000320282 (W 2.28517e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003096 ± 4.67654e-05 (W 3.97492e-05) | 0.003327 ± 0.00022519 (W 2.16171e-05) | 0.003427 ± 4.59384e-05 (W 4.305e-05) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.11× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014457 ± 1.52753e-05 (W 1.92354e-05) | 0.015429 ± 0.000883047 (W 8.43801e-05) | 0.014126 ± 0.000196054 (W 5.42061e-05) | 🔵 faer-fork 1.07× faster than `faer-upstream` | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.030286 ± 0.000113271 (W 5.31977e-05) | 0.035466 ± 0.000739513 (W 0.00109263) | 0.037891 ± 0.000226276 (W 0.000126997) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `eigh/n32/b1` | 0.11233 ± 0.000592382 (W 0.000199595) | 0.11243 ± 0.000977938 (W 0.002239) | 0.101519 ± 0.0002582 (W 0.000302475) | · | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.488921 ± 0.0017987 (W 0.00269687) | 0.480706 ± 0.000980961 (W 0.00209155) | 0.262859 ± 0.000335446 (W 0.00155211) | · | 🔴 faer-fork 1.86× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.16896 ± 0.00222862 (W 0.0021644) | 1.13023 ± 0.00385245 (W 0.00166055) | 0.577596 ± 0.00198948 (W 0.00449375) | · | 🔴 faer-fork 2.02× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.012373 ± 0.000496076 (W 0.000153819) | 0.010039 ± 0.000149701 (W 4.13074e-05) | - | 🔴 faer-fork 1.23× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.050164 ± 0.000511277 (W 0.000274227) | 0.044944 ± 0.000555411 (W 0.000160029) | - | 🔴 faer-fork 1.12× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.147355 ± 0.00262941 (W 0.00109264) | 0.126937 ± 0.00139346 (W 0.000216486) | - | 🔴 faer-fork 1.16× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.006392 ± 0.000108583 (W 0.000203672) | 0.008356 ± 0.000112829 (W 7.12622e-05) | - | 🔵 faer-fork 1.31× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.006442 ± 0.000147422 (W 0.000168018) | 0.008446 ± 3.99625e-05 (W 5.45894e-05) | - | 🔵 faer-fork 1.31× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.019476 ± 0.000530586 (W 0.00040757) | 0.018995 ± 0.000308612 (W 0.000325393) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.019937 ± 5.62168e-05 (W 0.000194216) | 0.018986 ± 0.000206374 (W 0.000403872) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.044843 ± 0.000215704 (W 0.000309027) | 0.043612 ± 0.000246151 (W 0.000419113) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.044944 ± 0.00023388 (W 0.000224393) | 0.043571 ± 0.000211842 (W 0.000235805) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.007544 ± 0.000207196 (W 9.38083e-05) | 0.007053 ± 0.000125831 (W 5.61186e-05) | 0.010931 ± 0.000119709 (W 6.18409e-05) | 🔴 faer-fork 1.07× slower than `faer-upstream` | 🔵 faer-fork 1.45× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.026099 ± 0.000236679 (W 0.000103915) | 0.029154 ± 0.000119304 (W 0.000978985) | 0.035777 ± 0.000294965 (W 0.000178643) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.060683 ± 0.000415733 (W 0.000274692) | 0.070111 ± 0.0014615 (W 0.00256932) | 0.08034 ± 0.000188247 (W 0.000228801) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.032651 ± 0.000329673 (W 0.000123835) | 0.045675 ± 0.000244365 (W 0.000568521) | 0.02187 ± 3.4356e-05 (W 7.61925e-05) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔴 faer-fork 1.49× slower than `lapack-mkl` |  |
| `qr/n64/b1` | 0.104636 ± 0.000764115 (W 0.000374807) | 0.1821 ± 0.00232329 (W 0.00142434) | 0.129201 ± 0.0022292 (W 0.000546402) | 🔵 faer-fork 1.74× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.225 ± 0.0086029 (W 0.00329495) | 0.363167 ± 0.00457019 (W 0.00254396) | 0.302333 ± 0.00171586 (W 0.00261678) | 🔵 faer-fork 1.61× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n32/b1` | 0.018364 ± 0.0005345 (W 0.000359737) | 0.031299 ± 0.000790174 (W 0.000482903) | 0.011972 ± 0.0001 (W 7.86397e-05) | 🔵 faer-fork 1.70× faster than `faer-upstream` | 🔴 faer-fork 1.53× slower than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `qr_factor/n64/b1` | 0.071283 ± 0.00164775 (W 0.000188003) | 0.143788 ± 0.00241195 (W 0.00311487) | 0.273169 ± 0.00141232 (W 0.00172694) | 🔵 faer-fork 2.02× faster than `faer-upstream` | 🔵 faer-fork 3.83× faster than `lapack-mkl` |  |
| `qr_factor/n96/b1` | 0.136535 ± 0.00163696 (W 0.000455231) | 0.283519 ± 0.00522676 (W 0.00228341) | 0.893396 ± 0.0032873 (W 0.00172348) | 🔵 faer-fork 2.08× faster than `faer-upstream` | 🔵 faer-fork 6.54× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.008716 ± 5.50757e-05 (W 8.2845e-05) | 0.007864 ± 2.0664e-05 (W 4.84685e-05) | 0.01083 ± 9.86425e-05 (W 0.000117619) | 🔴 faer-fork 1.11× slower than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.027701 ± 0.000115717 (W 0.000118825) | 0.029435 ± 0.000857669 (W 0.000815269) | 0.035236 ± 0.000145029 (W 0.000129523) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.073447 ± 0.00164131 (W 0.00209791) | 0.06412 ± 0.000662058 (W 0.000812091) | 0.078095 ± 0.000303778 (W 0.000316823) | 🔴 faer-fork 1.15× slower than `faer-upstream` | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.173424 ± 0.000582234 (W 0.000463669) | 0.18764 ± 0.00222449 (W 0.00172643) | 0.175177 ± 0.000278837 (W 0.00173526) | 🔵 faer-fork 1.08× faster than `faer-upstream` | · |  |
| `svd_thin/n64/b1` | 0.895701 ± 0.00552249 (W 0.00273894) | 0.952917 ± 0.00452239 (W 0.00254346) | 0.626739 ± 0.0035272 (W 0.0025287) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.43× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 1.98987 ± 0.0356576 (W 0.00531643) | 2.08533 ± 0.00394945 (W 0.00301551) | 1.33634 ± 0.0484662 (W 0.00191982) | · | 🔴 faer-fork 1.49× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/n32/b1` | 0.067676 ± 0.000506667 (W 0.000186084) | 0.143237 ± 0.000902633 (W 0.0017016) | 0.05875 ± 0.000253202 (W 0.000108887) | 🔵 faer-fork 2.12× faster than `faer-upstream` | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `svd_values/n64/b1` | 0.246059 ± 0.000809378 (W 0.00136365) | 0.540228 ± 0.00169211 (W 0.0028005) | 0.253983 ± 0.00115677 (W 0.00232935) | 🔵 faer-fork 2.20× faster than `faer-upstream` | · |  |
| `svd_values/n96/b1` | 0.588717 ± 0.00250131 (W 0.00194897) | 1.18993 ± 0.0030592 (W 0.00331179) | 0.59607 ± 0.00279068 (W 0.00263071) | 🔵 faer-fork 2.02× faster than `faer-upstream` | · |  |
| `triangular_solve/n32/b1` | 0.001002 ± 2.64575e-05 (W 1.73205e-05) | 0.000741 ± 1.00167e-05 (W 1.33154e-05) | - | 🔴 faer-fork 1.35× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002305 ± 4.04145e-05 (W 3.42228e-05) | 0.001723 ± 1.73205e-05 (W 2.14756e-05) | - | 🔴 faer-fork 1.34× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003888 ± 3.05014e-05 (W 5.26707e-05) | 0.002866 ± 3.00056e-05 (W 1.33154e-05) | - | 🔴 faer-fork 1.36× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003096 ± 3.15753e-05 (W 4.49922e-05) | 0.003045 ± 0.000188283 (W 2.38747e-05) | 0.003396 ± 5.7735e-07 (W 4.18844e-05) | · | 🔵 faer-fork 1.10× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014507 ± 8.94446e-05 (W 2.96648e-05) | 0.014657 ± 8e-05 (W 6.33024e-05) | 0.014056 ± 0.000217095 (W 2.77489e-05) | · | · | dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.027691 ± 0.00165975 (W 0.000101341) | 0.036168 ± 0.000648743 (W 0.000312246) | 0.03775 ± 0.000245425 (W 9.17567e-05) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.113512 ± 0.000290552 (W 0.000216355) | 0.11288 ± 0.000251476 (W 0.00195699) | 0.102121 ± 0.000182511 (W 0.00191033) | · | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.485434 ± 0.000866506 (W 0.00213852) | 0.481948 ± 0.000808129 (W 0.00256225) | 0.25202 ± 0.00136949 (W 0.00254975) | · | 🔴 faer-fork 1.93× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.16301 ± 0.00432664 (W 0.00227206) | 1.13778 ± 0.00162986 (W 0.00324237) | 0.559353 ± 0.00510278 (W 0.00260789) | · | 🔴 faer-fork 2.08× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.012133 ± 0.000196868 (W 8.40315e-05) | 0.010049 ± 0.000116762 (W 5.63028e-05) | - | 🔴 faer-fork 1.21× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.049442 ± 0.000632173 (W 0.000261529) | 0.045474 ± 7.78267e-05 (W 6.73053e-05) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.154378 ± 0.00185028 (W 0.000943465) | 0.128229 ± 0.00113005 (W 0.000334015) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.005971 ± 0.000214735 (W 0.000188211) | 0.008485 ± 4.03361e-05 (W 7.30151e-05) | - | 🔵 faer-fork 1.42× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.006061 ± 0.000770192 (W 0.000111345) | 0.008466 ± 5.03322e-05 (W 0.000149432) | - | 🔵 faer-fork 1.40× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.014747 ± 0.000495684 (W 0.000386059) | 0.019417 ± 0.00024205 (W 0.000168731) | - | 🔵 faer-fork 1.32× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.014887 ± 4.0501e-05 (W 0.000182036) | 0.019376 ± 8.14453e-05 (W 0.000383379) | - | 🔵 faer-fork 1.30× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.030777 ± 0.000127307 (W 0.000427732) | 0.055303 ± 0.000743874 (W 0.000840596) | - | 🔵 faer-fork 1.80× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.030818 ± 0.000150965 (W 0.000395973) | 0.054992 ± 0.00103098 (W 0.00103198) | - | 🔵 faer-fork 1.78× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.007434 ± 0.000130128 (W 7.96003e-05) | 0.007043 ± 0.000123977 (W 5.76194e-05) | 0.01107 ± 1.51767e-05 (W 8.60233e-05) | 🔴 faer-fork 1.06× slower than `faer-upstream` | 🔵 faer-fork 1.49× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.026219 ± 0.000316165 (W 0.000189706) | 0.029555 ± 0.000222007 (W 0.00108609) | 0.036207 ± 8.5967e-05 (W 0.000158493) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.061074 ± 2.87738 (W 0.000257557) | 0.071774 ± 0.0130353 (W 0.00346801) | 0.080289 ± 0.000288722 (W 0.000180331) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n32/b1` | 0.032821 ± 0.00018393 (W 0.000128668) | 0.05339 ± 0.00124205 (W 0.000670649) | 0.02166 ± 0.000162973 (W 7.49947e-05) | 🔵 faer-fork 1.63× faster than `faer-upstream` | 🔴 faer-fork 1.52× slower than `lapack-mkl` |  |
| `qr/n64/b1` | 0.104234 ± 0.00104056 (W 0.00171318) | 0.227945 ± 0.00405094 (W 0.00208211) | 0.140061 ± 0.00283192 (W 0.00184693) | 🔵 faer-fork 2.19× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.220201 ± 0.00966052 (W 0.00380413) | 0.460068 ± 0.00620486 (W 0.00343003) | 0.312221 ± 0.00261301 (W 0.00220464) | 🔵 faer-fork 2.09× faster than `faer-upstream` | 🔵 faer-fork 1.42× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n32/b1` | 0.018454 ± 0.000528852 (W 0.000154131) | 0.039463 ± 0.000200575 (W 0.000664311) | 0.011872 ± 0.000110151 (W 4.44972e-05) | 🔵 faer-fork 2.14× faster than `faer-upstream` | 🔴 faer-fork 1.55× slower than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `qr_factor/n64/b1` | 0.070171 ± 0.000734662 (W 0.000366438) | 0.186278 ± 0.000593152 (W 0.00238757) | 0.272859 ± 0.00105654 (W 0.00173597) | 🔵 faer-fork 2.65× faster than `faer-upstream` | 🔵 faer-fork 3.89× faster than `lapack-mkl` |  |
| `qr_factor/n96/b1` | 0.13438 ± 0.00177416 (W 0.000440982) | 0.364209 ± 0.00603699 (W 0.00300668) | 0.889919 ± 0.00372241 (W 0.00319071) | 🔵 faer-fork 2.71× faster than `faer-upstream` | 🔵 faer-fork 6.62× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.008686 ± 3.59212e-05 (W 8.4233e-05) | 0.007785 ± 6.28517e-05 (W 8.48192e-05) | 0.0109 ± 1.0504e-05 (W 5.13342e-05) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.027491 ± 0.000124396 (W 0.000165204) | 0.029806 ± 0.000235649 (W 0.000146014) | 0.035306 ± 0.000249393 (W 7.65461e-05) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.074709 ± 0.000921741 (W 0.0023586) | 0.065862 ± 0.00107859 (W 0.000718158) | 0.079137 ± 0.000378194 (W 0.00143116) | 🔴 faer-fork 1.13× slower than `faer-upstream` | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.173313 ± 0.000423934 (W 0.00188161) | 0.18731 ± 0.0029832 (W 0.00179911) | 0.176279 ± 0.000388163 (W 0.00137643) | 🔵 faer-fork 1.08× faster than `faer-upstream` | · |  |
| `svd_thin/n64/b1` | 0.892503 ± 0.00325522 (W 0.00245172) | 0.953768 ± 0.00253414 (W 0.00132987) | 0.625527 ± 0.00551342 (W 0.0032449) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.43× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 1.99989 ± 0.0349271 (W 0.004045) | 2.10599 ± 0.00853601 (W 0.00196538) | 1.27962 ± 0.00239145 (W 0.00306125) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔴 faer-fork 1.56× slower than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.067686 ± 0.000658786 (W 0.000193936) | 0.142345 ± 0.00015102 (W 0.00198352) | 0.05856 ± 0.000637398 (W 0.000137954) | 🔵 faer-fork 2.10× faster than `faer-upstream` | 🔴 faer-fork 1.16× slower than `lapack-mkl` |  |
| `svd_values/n64/b1` | 0.247371 ± 0.00184713 (W 0.00219017) | 0.53681 ± 0.00127473 (W 0.00300497) | 0.254425 ± 0.00091008 (W 0.00257511) | 🔵 faer-fork 2.17× faster than `faer-upstream` | · |  |
| `svd_values/n96/b1` | 0.603315 ± 0.000101786 (W 0.00181574) | 1.18713 ± 0.00551464 (W 0.00106994) | 0.592214 ± 0.00474395 (W 0.0021159) | 🔵 faer-fork 1.97× faster than `faer-upstream` | · |  |
| `triangular_solve/n32/b1` | 0.000982 ± 1.1547e-05 (W 3.08221e-05) | 0.000761 ± 1.95021e-05 (W 1.50433e-05) | - | 🔴 faer-fork 1.29× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002244 ± 7.95005e-05 (W 3.1305e-05) | 0.001714 ± 1.21244e-05 (W 2.64443e-05) | - | 🔴 faer-fork 1.31× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003918 ± 3.05014e-05 (W 2.53831e-05) | 0.003256 ± 0.000140119 (W 2.28517e-05) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.00529 ± 2.3094e-05 (W 4.46565e-05) | 0.004919 ± 6.08276e-05 (W 4.10634e-05) | 0.008947 ± 1.95021e-05 (W 3.31089e-05) | 🔴 faer-fork 1.08× slower than `faer-upstream` | 🔵 faer-fork 1.69× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030727 ± 0.00263222 (W 0.000130051) | 0.029525 ± 0.000167094 (W 0.000205537) | 0.052087 ± 0.000284178 (W 0.00182258) | · | 🔵 faer-fork 1.70× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n96/b1` | 0.08599 ± 0.00400151 (W 0.00179099) | 0.082654 ± 0.000423202 (W 0.000169915) | 0.138528 ± 0.00119842 (W 0.00189617) | · | 🔵 faer-fork 1.61× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.141624 ± 0.000171389 (W 0.00192225) | 0.142546 ± 0.00122744 (W 0.00153915) | 0.14502 ± 0.000515171 (W 0.00203437) | · | · |  |
| `eigh/n64/b1` | 0.658828 ± 0.00125545 (W 0.00307504) | 0.650693 ± 0.00148127 (W 0.00223227) | 0.791808 ± 0.00232912 (W 0.00406083) | · | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.65393 ± 0.00766318 (W 0.00372229) | 1.6243 ± 0.00498988 (W 0.00332443) | 2.00955 ± 0.000180722 (W 0.00768064) | · | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.018945 ± 0.000314897 (W 0.000110318) | 0.015729 ± 0.000109302 (W 9.87436e-05) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.101319 ± 0.00036456 (W 0.000453097) | 0.092422 ± 9.55528e-05 (W 0.00024965) | - | 🔴 faer-fork 1.10× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.288067 ± 0.000541074 (W 0.00213682) | 0.268381 ± 0.00161433 (W 0.0020252) | - | 🔴 faer-fork 1.07× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.028664 ± 3.21455e-05 (W 0.000265064) | 0.028063 ± 9.90471e-05 (W 0.00010198) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.028603 ± 8.92767e-05 (W 0.000148823) | 0.028042 ± 0.000135463 (W 7.4191e-05) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.16093 ± 0.000676382 (W 0.00249804) | 0.159037 ± 0.000353695 (W 0.00204728) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.161431 ± 0.000669899 (W 0.000126449) | 0.160369 ± 0.000746006 (W 0.00111008) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.472571 ± 0.0026108 (W 0.00129507) | 0.465759 ± 0.00408491 (W 0.00191557) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.47231 ± 0.00347081 (W 0.00201962) | 0.469855 ± 0.00187318 (W 0.0029937) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.013695 ± 0.00030609 (W 6.37511e-05) | 0.011171 ± 0.000146243 (W 9.05439e-05) | 0.019506 ± 0.000105057 (W 9.94198e-05) | 🔴 faer-fork 1.23× slower than `faer-upstream` | 🔵 faer-fork 1.42× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.059501 ± 0.000219864 (W 0.000150736) | 0.052828 ± 0.000304523 (W 0.00188281) | 0.094186 ± 0.000514471 (W 0.00118982) | 🔴 faer-fork 1.13× slower than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.15551 ± 0.000633425 (W 0.00207147) | 0.138689 ± 0.000866408 (W 0.00175399) | 0.243023 ± 0.000941792 (W 0.00214131) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 1.56× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.068678 ± 0.000511 (W 0.000138886) | 0.070291 ± 0.000382806 (W 0.000410992) | 0.054251 ± 0.084668 (W 0.0016807) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n64/b1` | 0.31088 ± 0.000303515 (W 0.00273992) | 0.319156 ± 0.00240482 (W 0.00249677) | 0.339603 ± 0.00226688 (W 0.00288181) | · | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.760478 ± 0.00208266 (W 0.00278229) | 0.779996 ± 0.00330643 (W 0.00271324) | 0.993924 ± 0.00346224 (W 0.00401464) | · | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.039875 ± 0.000302947 (W 0.000325033) | 0.047399 ± 0.000145775 (W 0.000297052) | 0.028914 ± 0.000211369 (W 8.17313e-05) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.38× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.17168 ± 0.001183 (W 0.00201611) | 0.240237 ± 0.000706344 (W 0.00228262) | 0.163875 ± 0.000375581 (W 0.00199621) | 🔵 faer-fork 1.40× faster than `faer-upstream` | · |  |
| `qr_factor/n96/b1` | 0.406788 ± 0.00358234 (W 0.00215181) | 0.543444 ± 0.00655784 (W 0.00191832) | 0.505322 ± 0.000961516 (W 0.00344399) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.014898 ± 0.000454438 (W 7.50353e-05) | 0.012673 ± 0.00012779 (W 9.14183e-05) | 0.019887 ± 2.51661e-05 (W 3.65951e-05) | 🔴 faer-fork 1.18× slower than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.061615 ± 0.000284869 (W 0.000141264) | 0.055233 ± 0.000336125 (W 0.000150599) | 0.092202 ± 0.000105357 (W 0.00173322) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.159808 ± 0.00182039 (W 0.00147601) | 0.143999 ± 0.000602164 (W 0.00176574) | 0.237222 ± 0.00102133 (W 0.00235276) | 🔴 faer-fork 1.11× slower than `faer-upstream` | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.21973 ± 0.00241518 (W 0.00178817) | 0.236971 ± 0.00316967 (W 0.00238922) | 0.25181 ± 0.00132252 (W 0.00180135) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 1.16661 ± 0.0027225 (W 0.00336342) | 1.2318 ± 0.00484337 (W 0.00468749) | 1.33132 ± 0.00355598 (W 0.00266955) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 3.02868 ± 0.014343 (W 0.00637579) | 3.16357 ± 0.0105472 (W 0.00977464) | 3.43426 ± 0.0508459 (W 0.0100904) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.082584 ± 0.000483991 (W 0.00022411) | 0.161401 ± 0.000878713 (W 0.00182756) | 0.101039 ± 0.114072 (W 0.000418975) | 🔵 faer-fork 1.95× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n64/b1` | 0.342308 ± 0.000845401 (W 0.00280265) | 0.656525 ± 0.00235946 (W 0.00181647) | 0.481468 ± 0.000769868 (W 0.00239107) | 🔵 faer-fork 1.92× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.858 ± 0.00144107 (W 0.00318052) | 1.53946 ± 0.00158572 (W 0.00188621) | 1.34452 ± 0.00282261 (W 0.00674892) | 🔵 faer-fork 1.79× faster than `faer-upstream` | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.001172 ± 1e-05 (W 1.80638e-05) | 0.001082 ± 2.08167e-05 (W 1.92354e-05) | - | 🔴 faer-fork 1.08× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002876 ± 3.56417e-05 (W 2.2786e-05) | 0.002685 ± 3.05505e-05 (W 3.03315e-05) | - | 🔴 faer-fork 1.07× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.00529 ± 4.16333e-05 (W 4.03733e-05) | 0.00502 ± 5.05008e-05 (W 4.62309e-05) | - | 🔴 faer-fork 1.05× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.00528 ± 4.16333e-05 (W 0.00133457) | 0.004899 ± 2.08167e-05 (W 4.19905e-05) | 0.008957 ± 1.52753e-05 (W 7.09225e-05) | 🔴 faer-fork 1.08× slower than `faer-upstream` | 🔵 faer-fork 1.70× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030647 ± 0.000376865 (W 9.29801e-05) | 0.029154 ± 9.33292e-05 (W 0.000122556) | 0.051616 ± 0.000317513 (W 0.00020369) | · | 🔵 faer-fork 1.68× faster than `lapack-mkl` |  |
| `cholesky/n96/b1` | 0.079999 ± 0.000721271 (W 0.000469229) | 0.086011 ± 0.000847598 (W 0.001336) | 0.136794 ± 0.000440365 (W 0.00188688) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |
| `eigh/n32/b1` | 0.138338 ± 0.000836152 (W 0.00209671) | 0.141694 ± 0.000881892 (W 0.00204357) | 0.1502 ± 0.000384661 (W 0.00172006) | · | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.573719 ± 0.00280066 (W 0.00222359) | 0.617972 ± 0.00222905 (W 0.00174889) | 0.540048 ± 0.00413742 (W 0.00244941) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.36219 ± 0.00543757 (W 0.00585328) | 1.44565 ± 0.00554256 (W 0.00280064) | 1.12044 ± 0.00665492 (W 0.00290295) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.22× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.019937 ± 0.000219523 (W 0.000172242) | 0.015489 ± 0.000251462 (W 6.97854e-05) | - | 🔴 faer-fork 1.29× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.105006 ± 0.00102255 (W 0.000398868) | 0.091731 ± 0.000982743 (W 0.000546375) | - | 🔴 faer-fork 1.14× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.250247 ± 0.00532986 (W 0.00188193) | 0.266557 ± 0.000251774 (W 0.00209532) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.014347 ± 0.000138564 (W 0.000190959) | 0.028042 ± 0.000203634 (W 0.000116919) | - | 🔵 faer-fork 1.95× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.014637 ± 0.000186039 (W 0.000212422) | 0.028353 ± 0.000254775 (W 8.94103e-05) | - | 🔵 faer-fork 1.94× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.061775 ± 0.000525187 (W 0.000344848) | 0.060653 ± 0.000494237 (W 0.00139541) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.061705 ± 0.000226495 (W 0.00125406) | 0.061325 ± 0.000110726 (W 0.000280401) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.152505 ± 0.000137041 (W 0.00203309) | 0.14982 ± 0.000127005 (W 0.0014111) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.153707 ± 0.000796025 (W 0.00138951) | 0.150971 ± 0.000146186 (W 0.000692363) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.013776 ± 7.60723e-05 (W 0.000193159) | 0.011141 ± 0.000223214 (W 9.39745e-05) | 0.019577 ± 7.50555e-05 (W 8.04935e-05) | 🔴 faer-fork 1.24× slower than `faer-upstream` | 🔵 faer-fork 1.42× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.06431 ± 0.00220791 (W 0.000176116) | 0.052427 ± 0.00015972 (W 0.000371569) | 0.093665 ± 0.000369658 (W 0.000223119) | 🔴 faer-fork 1.23× slower than `faer-upstream` | 🔵 faer-fork 1.46× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/n96/b1` | 0.153206 ± 0.00191406 (W 0.00264628) | 0.137887 ± 0.00235364 (W 0.00223062) | 0.228786 ± 0.000503465 (W 0.00170062) | 🔴 faer-fork 1.11× slower than `faer-upstream` | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.063358 ± 0.000200301 (W 0.000423775) | 0.081613 ± 0.000304724 (W 0.00128962) | 0.200514 ± 0.0851236 (W 0.00162832) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 3.16× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n64/b1` | 0.195514 ± 0.000710342 (W 0.0018973) | 0.32172 ± 0.0017215 (W 0.00305522) | 0.308335 ± 0.000602535 (W 0.00184312) | 🔵 faer-fork 1.65× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.419312 ± 0.00158271 (W 0.0024491) | 0.618353 ± 0.00674184 (W 0.00276416) | 0.754446 ± 0.00478355 (W 0.00191667) | 🔵 faer-fork 1.47× faster than `faer-upstream` | 🔵 faer-fork 1.80× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.039574 ± 0.000458825 (W 0.000339375) | 0.05933 ± 0.000479 (W 0.000414194) | 0.028833 ± 5.23482e-05 (W 8.52367e-05) | 🔵 faer-fork 1.50× faster than `faer-upstream` | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.124723 ± 0.000768402 (W 0.000475538) | 0.290081 ± 0.00160043 (W 0.0023837) | 0.163795 ± 0.330208 (W 0.00202145) | 🔵 faer-fork 2.33× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n96/b1` | 0.264333 ± 0.00190279 (W 0.00244299) | 0.570984 ± 0.00542375 (W 0.00324692) | 2.39092 ± 0.00355192 (W 0.00236664) | 🔵 faer-fork 2.16× faster than `faer-upstream` | 🔵 faer-fork 9.05× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.015469 ± 0.00034253 (W 0.000104227) | 0.012925 ± 0.000172871 (W 0.000116225) | 0.019917 ± 4.3589e-05 (W 6.17187e-05) | 🔴 faer-fork 1.20× slower than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.063799 ± 0.00212016 (W 0.000154693) | 0.055173 ± 0.000180831 (W 0.000179202) | 0.090839 ± 0.000366544 (W 0.000710849) | 🔴 faer-fork 1.16× slower than `faer-upstream` | 🔵 faer-fork 1.42× faster than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.157504 ± 0.00094977 (W 0.00114133) | 0.142225 ± 0.000460186 (W 0.00174953) | 0.221804 ± 0.000575063 (W 0.00157682) | 🔴 faer-fork 1.11× slower than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.214951 ± 0.00146444 (W 0.00196323) | 0.234718 ± 0.000385664 (W 0.00200977) | 0.259954 ± 0.00149155 (W 0.00186588) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 1.00528 ± 0.00254336 (W 0.0016372) | 1.14697 ± 0.00297082 (W 0.00252) | 1.00448 ± 0.00513906 (W 0.00285096) | 🔵 faer-fork 1.14× faster than `faer-upstream` | · |  |
| `svd_thin/n96/b1` | 2.50633 ± 0.0117507 (W 0.00458752) | 2.80359 ± 0.0022264 (W 0.00516268) | 2.46046 ± 0.0163162 (W 0.00202742) | 🔵 faer-fork 1.12× faster than `faer-upstream` | · |  |
| `svd_values/n32/b1` | 0.083866 ± 0.000525586 (W 0.00180817) | 0.160439 ± 0.00159191 (W 0.00190178) | 0.297635 ± 0.114738 (W 0.00223929) | 🔵 faer-fork 1.91× faster than `faer-upstream` | 🔵 faer-fork 3.55× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n64/b1` | 0.353048 ± 0.00106317 (W 0.00215421) | 0.657896 ± 0.00136866 (W 0.00265756) | 0.481387 ± 0.00334529 (W 0.00230178) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.802126 ± 0.00349624 (W 0.0029692) | 1.5372 ± 0.0029838 (W 0.00398559) | 1.323 ± 0.0029632 (W 0.00303793) | 🔵 faer-fork 1.92× faster than `faer-upstream` | 🔵 faer-fork 1.65× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.001433 ± 1.0504e-05 (W 1.9756e-05) | 0.001082 ± 2.88675e-05 (W 1.81659e-05) | - | 🔴 faer-fork 1.32× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003436 ± 9.50438e-06 (W 1.89816e-05) | 0.002675 ± 2.51661e-05 (W 1.51658e-05) | - | 🔴 faer-fork 1.28× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.006151 ± 4.20357e-05 (W 2.49259e-05) | 0.00494 ± 4.14769e-05 (W 4.219e-05) | - | 🔴 faer-fork 1.25× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.00532 ± 7.2111e-05 (W 5.17687e-05) | 0.004899 ± 3e-05 (W 5.09333e-05) | 0.008836 ± 5.70117e-05 (W 5.40398e-05) | 🔴 faer-fork 1.09× slower than `faer-upstream` | 🔵 faer-fork 1.66× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030316 ± 0.000446163 (W 8.85681e-05) | 0.029134 ± 0.000180888 (W 0.000198867) | 0.051807 ± 0.00017088 (W 0.000257296) | · | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |
| `cholesky/n96/b1` | 0.080741 ± 8.77895e-05 (W 0.000373129) | 0.087383 ± 0.000106927 (W 0.000876996) | 0.140712 ± 0.000664953 (W 0.000428615) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.74× faster than `lapack-mkl` |  |
| `eigh/n32/b1` | 0.138328 ± 0.000556221 (W 0.00163578) | 0.142215 ± 0.000749818 (W 0.000176862) | 0.151622 ± 0.000924079 (W 0.00189401) | · | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.569591 ± 0.00136038 (W 0.00305412) | 0.619635 ± 0.00128609 (W 0.00172014) | 0.514419 ± 0.000690963 (W 0.00284561) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.33125 ± 0.00963139 (W 0.00415116) | 1.45478 ± 0.00426545 (W 0.00307061) | 0.997139 ± 0.00223157 (W 0.00194698) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.34× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.020087 ± 0.000160594 (W 0.000152844) | 0.015739 ± 9.29157e-05 (W 8.77969e-05) | - | 🔴 faer-fork 1.28× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n64/b1` | 0.110216 ± 0.0133941 (W 0.000836443) | 0.091661 ± 0.00048642 (W 0.000289863) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/n96/b1` | 0.254895 ± 0.00149355 (W 0.00214809) | 0.264613 ± 0.00129453 (W 0.00174703) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.010599 ± 0.000601931 (W 0.000125157) | 0.028323 ± 2.88675e-05 (W 0.000100191) | - | 🔵 faer-fork 2.67× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.011171 ± 0.000168306 (W 0.000259579) | 0.028413 ± 6.4291e-05 (W 0.00144836) | - | 🔵 faer-fork 2.54× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.036828 ± 0.000436521 (W 0.000364763) | 0.060292 ± 0.000266584 (W 0.000579145) | - | 🔵 faer-fork 1.64× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.03779 ± 0.000440194 (W 0.00020351) | 0.060603 ± 0.00031559 (W 0.000243014) | - | 🔵 faer-fork 1.60× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.08598 ± 0.000176353 (W 0.00104578) | 0.149729 ± 0.000520977 (W 0.00170671) | - | 🔵 faer-fork 1.74× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.087743 ± 0.000524325 (W 0.0013252) | 0.15059 ± 0.000252125 (W 0.0018616) | - | 🔵 faer-fork 1.72× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.013726 ± 5.00033e-05 (W 0.000124524) | 0.011101 ± 0.000174356 (W 0.000151063) | 0.019376 ± 4.04145e-05 (W 7.13253e-05) | 🔴 faer-fork 1.24× slower than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.06454 ± 0.000211235 (W 0.00236975) | 0.052357 ± 0.0001505 (W 0.000273834) | 0.093244 ± 0.000392616 (W 0.000313921) | 🔴 faer-fork 1.23× slower than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.156131 ± 0.000990577 (W 0.000236685) | 0.13911 ± 8.27063e-05 (W 0.00132916) | 0.229177 ± 0.00136801 (W 0.00232789) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.063759 ± 0.000407799 (W 0.000187657) | 0.089887 ± 0.000247954 (W 0.000762861) | 0.200433 ± 0.0846964 (W 0.00159086) | 🔵 faer-fork 1.41× faster than `faer-upstream` | 🔵 faer-fork 3.14× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n64/b1` | 0.184173 ± 0.00280731 (W 0.00281138) | 0.362726 ± 0.0019585 (W 0.00323763) | 0.283589 ± 0.00113568 (W 0.00301836) | 🔵 faer-fork 1.97× faster than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.364689 ± 0.00183029 (W 0.00292904) | 0.699274 ± 0.00387506 (W 0.00406863) | 0.694876 ± 0.00142871 (W 0.00298113) | 🔵 faer-fork 1.92× faster than `faer-upstream` | 🔵 faer-fork 1.91× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.038712 ± 0.0032183 (W 0.00139154) | 0.068368 ± 0.000706736 (W 0.00235443) | 0.028723 ± 0.000144212 (W 7.30842e-05) | 🔵 faer-fork 1.77× faster than `faer-upstream` | 🔴 faer-fork 1.35× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n64/b1` | 0.119853 ± 0.000808754 (W 0.000539052) | 0.319766 ± 0.00339888 (W 0.00699531) | 0.16133 ± 0.330737 (W 0.00171738) | 🔵 faer-fork 2.67× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n96/b1` | 0.237342 ± 0.00192351 (W 0.00168866) | 0.629063 ± 0.0112655 (W 0.0070687) | 2.38919 ± 0.0033831 (W 0.00506676) | 🔵 faer-fork 2.65× faster than `faer-upstream` | 🔵 faer-fork 10.07× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.015499 ± 7.57188e-05 (W 7.92465e-05) | 0.012764 ± 7.42765e-05 (W 8.91807e-05) | 0.019847 ± 7.0946e-05 (W 4.18473e-05) | 🔴 faer-fork 1.21× slower than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.067796 ± 0.000315817 (W 0.000250227) | 0.055023 ± 0.000280726 (W 0.000154189) | 0.091371 ± 0.000711589 (W 0.00157111) | 🔴 faer-fork 1.23× slower than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.15558 ± 0.000813313 (W 0.000516752) | 0.142786 ± 0.000738886 (W 0.000595067) | 0.221773 ± 0.00110744 (W 0.00145471) | 🔴 faer-fork 1.09× slower than `faer-upstream` | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.21472 ± 0.000435201 (W 0.00166052) | 0.235369 ± 0.00197152 (W 0.00200653) | 0.26249 ± 0.00172271 (W 0.00167561) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 0.995455 ± 0.00236908 (W 0.00288608) | 1.15725 ± 0.00137043 (W 0.00174948) | 0.960881 ± 0.00266932 (W 0.00213465) | 🔵 faer-fork 1.16× faster than `faer-upstream` | · |  |
| `svd_thin/n96/b1` | 2.4625 ± 0.0110096 (W 0.00452272) | 2.83008 ± 0.00920823 (W 0.00209009) | 2.27063 ± 0.00478314 (W 0.0022874) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔴 faer-fork 1.08× slower than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.083495 ± 0.000278299 (W 0.000165697) | 0.160329 ± 0.0071126 (W 0.00229996) | 0.296733 ± 0.113881 (W 0.00225757) | 🔵 faer-fork 1.92× faster than `faer-upstream` | 🔵 faer-fork 3.55× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n64/b1` | 0.360011 ± 0.000929508 (W 0.00199266) | 0.653087 ± 0.000656531 (W 0.00183173) | 0.47739 ± 0.00118095 (W 0.00187807) | 🔵 faer-fork 1.81× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.823795 ± 0.00733815 (W 0.00222105) | 1.53452 ± 0.00264206 (W 0.00245661) | 1.32119 ± 0.00523371 (W 0.00242223) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.60× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.001443 ± 1e-05 (W 2.19613e-05) | 0.001052 ± 1.52753e-05 (W 3.1305e-05) | - | 🔴 faer-fork 1.37× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003416 ± 5.85947e-05 (W 1.96774e-05) | 0.002665 ± 1.1547e-05 (W 1.51658e-05) | - | 🔴 faer-fork 1.28× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.006161 ± 8.01686e-05 (W 4.67472e-05) | 0.00493 ± 4.08697e-05 (W 5.89169e-05) | - | 🔴 faer-fork 1.25× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.00525 ± 5.19615e-05 (W 4.1833e-05) | 0.004899 ± 2.08167e-05 (W 2.76279e-05) | 0.007884 ± 6.30106e-05 (W 2.33088e-05) | 🔴 faer-fork 1.07× slower than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030297 ± 0.00294255 (W 0.000122422) | 0.029154 ± 0.000157608 (W 0.000750634) | 0.044113 ± 0.000529227 (W 0.000135204) | · | 🔵 faer-fork 1.46× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `cholesky/n96/b1` | 0.085239 ± 0.00366155 (W 0.00157395) | 0.081963 ± 0.000400075 (W 8.90505e-05) | 0.125904 ± 0.000140834 (W 0.00152176) | · | 🔵 faer-fork 1.48× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.141334 ± 0.000814288 (W 0.00151577) | 0.142095 ± 0.000849116 (W 0.00197095) | 0.143338 ± 0.000341938 (W 0.00162277) | · | · |  |
| `eigh/n64/b1` | 0.658489 ± 0.00427218 (W 0.00164113) | 0.650834 ± 0.00263723 (W 0.00211721) | 0.781679 ± 0.00408871 (W 0.00234427) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.65306 ± 0.00424511 (W 0.00308253) | 1.61881 ± 0.00582162 (W 0.00279767) | 1.98276 ± 0.00203411 (W 0.00195509) | · | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.017172 ± 0.000176693 (W 7.36023e-05) | 0.015719 ± 0.000111505 (W 6.68222e-05) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.094326 ± 0.000452681 (W 0.00139967) | 0.090549 ± 0.000367351 (W 0.000211425) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.271276 ± 0.00149251 (W 0.0019461) | 0.265676 ± 0.00153279 (W 0.00210053) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.028653 ± 6.4291e-05 (W 0.000105907) | 0.028043 ± 0.000134268 (W 8.4476e-05) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.028594 ± 0.000225958 (W 8.42692e-05) | 0.028062 ± 0.000206027 (W 0.000122558) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.158946 ± 0.000190832 (W 0.000123723) | 0.158315 ± 0.000718123 (W 0.00220285) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.158776 ± 0.000416943 (W 0.00148764) | 0.158175 ± 0.00048144 (W 0.000249851) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.462042 ± 0.00386219 (W 0.00285315) | 0.464155 ± 0.000682205 (W 0.0018222) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.465106 ± 0.0022625 (W 0.00195185) | 0.461702 ± 0.00341398 (W 0.0022386) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.011852 ± 5.7735e-05 (W 6.10672e-05) | 0.011241 ± 0.000113725 (W 5.68331e-05) | 0.017102 ± 4.3589e-05 (W 6.44764e-05) | 🔴 faer-fork 1.05× slower than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.052739 ± 0.000435982 (W 0.000211534) | 0.051246 ± 0.000438453 (W 0.000271424) | 0.083446 ± 0.000437662 (W 0.000133083) | · | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.139641 ± 0.000420002 (W 0.000407568) | 0.136264 ± 0.000972416 (W 0.00120844) | 0.210593 ± 7.53459e-05 (W 0.00191817) | · | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.066765 ± 0.000315511 (W 0.00158636) | 0.069931 ± 0.000214189 (W 0.000425048) | 0.049773 ± 0.000523681 (W 7.4027e-05) | · | 🔴 faer-fork 1.34× slower than `lapack-mkl` |  |
| `qr/n64/b1` | 0.304748 ± 0.0001605 (W 0.00198891) | 0.3166 ± 0.000827343 (W 0.00234399) | 0.318454 ± 0.00333058 (W 0.00230384) | · | · |  |
| `qr/n96/b1` | 0.743797 ± 0.00195258 (W 0.00241931) | 0.773863 ± 0.00204044 (W 0.00347739) | 0.92842 ± 0.00375712 (W 0.00147416) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.031578 ± 0.000157684 (W 0.000102261) | 0.035557 ± 0.000286654 (W 0.000276048) | 0.026379 ± 0.000284184 (W 9.68618e-05) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.20× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.151483 ± 0.00092819 (W 0.00156777) | 0.165749 ± 0.000320725 (W 0.00219504) | 0.726706 ± 0.00123923 (W 0.00216577) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 4.80× faster than `lapack-mkl` |  |
| `qr_factor/n96/b1` | 0.366474 ± 0.00277784 (W 0.00224662) | 0.400928 ± 0.00125673 (W 0.00279855) | 2.36693 ± 0.00586694 (W 0.00539992) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 6.46× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.012564 ± 0.000484256 (W 5.49545e-05) | 0.012553 ± 0.000141952 (W 6.59333e-05) | 0.017022 ± 4.58258e-05 (W 4.219e-05) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.054391 ± 0.0005205 (W 0.00014156) | 0.05356 ± 0.000515555 (W 0.000109441) | 0.081422 ± 0.000376246 (W 0.000270862) | · | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.142826 ± 0.000411656 (W 0.00177409) | 0.1395 ± 0.000872412 (W 0.00156956) | 0.203579 ± 0.00155688 (W 0.00198473) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.216514 ± 0.0030747 (W 0.0019215) | 0.235038 ± 0.00313608 (W 0.00211257) | 0.247522 ± 0.00080246 (W 0.00161417) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 1.19665 ± 0.005927 (W 0.00217056) | 1.25979 ± 0.00431166 (W 0.0026543) | 1.29814 ± 0.000537509 (W 0.00338033) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.9806 ± 0.00791835 (W 0.0029152) | 3.11999 ± 0.0141269 (W 0.00284342) | 3.36418 ± 0.0134511 (W 0.00309485) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.083546 ± 0.000559515 (W 0.000131275) | 0.159377 ± 0.000890928 (W 0.00188238) | 0.099616 ± 0.00119333 (W 0.00173793) | 🔵 faer-fork 1.91× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `svd_values/n64/b1` | 0.339864 ± 0.000806387 (W 0.00267103) | 0.633049 ± 0.00310951 (W 0.00217105) | 0.469285 ± 0.00319434 (W 0.00311286) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.857088 ± 0.00250499 (W 0.00396382) | 1.51788 ± 0.0073168 (W 0.00514424) | 1.31574 ± 0.00403925 (W 0.00295167) | 🔵 faer-fork 1.77× faster than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.001172 ± 2.08167e-05 (W 1.64317e-05) | 0.001213 ± 1.70392e-05 (W 1.68315e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002705 ± 6.08276e-06 (W 1.09545e-05) | 0.002926 ± 1.58219e-05 (W 1.85257e-05) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.004919 ± 0.000234159 (W 3.99525e-05) | 0.00529 ± 0.000127671 (W 2.07364e-05) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.00527 ± 3.60555e-05 (W 5.33854e-05) | 0.004879 ± 3.78594e-05 (W 4.80021e-05) | 0.007824 ± 0.000102357 (W 4.3188e-05) | 🔴 faer-fork 1.08× slower than `faer-upstream` | 🔵 faer-fork 1.48× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030226 ± 0.000170978 (W 0.000103664) | 0.028583 ± 0.000254808 (W 8.32238e-05) | 0.044032 ± 0.000745318 (W 0.00029117) | 🔴 faer-fork 1.06× slower than `faer-upstream` | 🔵 faer-fork 1.46× faster than `lapack-mkl` |  |
| `cholesky/n96/b1` | 0.079268 ± 0.000122202 (W 0.000403476) | 0.084828 ± 0.000813294 (W 0.00112635) | 0.125504 ± 0.000285365 (W 0.000214196) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `eigh/n32/b1` | 0.137887 ± 0.000528528 (W 0.000213986) | 0.141884 ± 0.000712159 (W 0.00179303) | 0.148556 ± 0.000834333 (W 0.00172742) | · | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.571846 ± 0.00114152 (W 0.0026107) | 0.615848 ± 0.00121166 (W 0.00326455) | 0.530118 ± 0.00202802 (W 0.00191469) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.08× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.3613 ± 0.00241425 (W 0.00394175) | 1.4432 ± 0.00486256 (W 0.0029554) | 1.10281 ± 0.00399121 (W 0.00264071) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.23× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.018244 ± 0.000200726 (W 9.52533e-05) | 0.015539 ± 0.000177043 (W 0.000177173) | - | 🔴 faer-fork 1.17× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.097592 ± 0.00183672 (W 0.000465523) | 0.089838 ± 0.000371543 (W 0.000366532) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.235769 ± 0.00478047 (W 0.00250197) | 0.263672 ± 0.000832521 (W 0.00293881) | - | 🔵 faer-fork 1.12× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.014988 ± 0.000175784 (W 0.00015448) | 0.028043 ± 0.000126729 (W 0.00013646) | - | 🔵 faer-fork 1.87× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.015088 ± 0.000155242 (W 0.000257809) | 0.028122 ± 0.000115902 (W 0.000139847) | - | 🔵 faer-fork 1.86× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.061835 ± 0.000583408 (W 0.00048787) | 0.060353 ± 0.000350552 (W 0.000487242) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.061976 ± 0.000587572 (W 0.000262182) | 0.060854 ± 0.000230775 (W 0.000257188) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.152735 ± 0.00112348 (W 0.00130496) | 0.148377 ± 0.000497488 (W 0.000909218) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.152805 ± 0.000438976 (W 0.00145667) | 0.149478 ± 0.000275712 (W 0.00191954) | - | · | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.011902 ± 5.68624e-05 (W 7.79102e-05) | 0.011511 ± 0.000223786 (W 0.000147361) | 0.017142 ± 4.16333e-05 (W 4.64898e-05) | · | 🔵 faer-fork 1.44× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.056926 ± 0.00178168 (W 0.00135338) | 0.051125 ± 0.000164257 (W 0.00161235) | 0.083165 ± 0.000440216 (W 0.000151955) | 🔴 faer-fork 1.11× slower than `faer-upstream` | 🔵 faer-fork 1.46× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/n96/b1` | 0.139861 ± 0.00198468 (W 0.0017331) | 0.134541 ± 0.0013558 (W 0.001756) | 0.209932 ± 0.00157484 (W 0.00197501) | · | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.061354 ± 0.000382318 (W 0.00173154) | 0.082474 ± 0.000721578 (W 0.00163805) | 0.048751 ± 0.000622857 (W 8.16774e-05) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔴 faer-fork 1.26× slower than `lapack-mkl` |  |
| `qr/n64/b1` | 0.187219 ± 0.00128035 (W 0.00196045) | 0.321139 ± 0.00327051 (W 0.00302226) | 0.288808 ± 0.000991994 (W 0.00266668) | 🔵 faer-fork 1.72× faster than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.405176 ± 0.00081974 (W 0.00321643) | 0.618282 ± 0.00572516 (W 0.00331861) | 0.725752 ± 0.000643741 (W 0.0021764) | 🔵 faer-fork 1.53× faster than `faer-upstream` | 🔵 faer-fork 1.79× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.030557 ± 0.000151327 (W 0.000204449) | 0.047388 ± 0.000216564 (W 0.000405235) | 0.026269 ± 0.000170098 (W 9.45637e-05) | 🔵 faer-fork 1.55× faster than `faer-upstream` | 🔴 faer-fork 1.16× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.114664 ± 0.000795729 (W 0.000258639) | 0.211985 ± 0.000861675 (W 0.00203865) | 0.725142 ± 0.00308552 (W 0.00255121) | 🔵 faer-fork 1.85× faster than `faer-upstream` | 🔵 faer-fork 6.32× faster than `lapack-mkl` |  |
| `qr_factor/n96/b1` | 0.243184 ± 0.00087759 (W 0.00200478) | 0.425142 ± 0.00139679 (W 0.00253012) | 2.36207 ± 0.00310103 (W 0.00399175) | 🔵 faer-fork 1.75× faster than `faer-upstream` | 🔵 faer-fork 9.71× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.013325 ± 0.00010116 (W 6.79279e-05) | 0.012514 ± 0.00022598 (W 0.000106866) | 0.017132 ± 9.66282e-05 (W 4.70351e-05) | 🔴 faer-fork 1.06× slower than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.059671 ± 0.00196926 (W 0.000302068) | 0.053269 ± 9.49052e-05 (W 0.000207187) | 0.08035 ± 0.00041675 (W 0.00186669) | 🔴 faer-fork 1.12× slower than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.140852 ± 0.000622564 (W 0.000740511) | 0.137887 ± 0.00220923 (W 0.00202319) | 0.202477 ± 0.000673939 (W 0.00215777) | · | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.210913 ± 0.00074746 (W 0.00187047) | 0.232543 ± 0.00115198 (W 0.00204044) | 0.255556 ± 0.00135278 (W 0.00173919) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 1.03794 ± 0.0019288 (W 0.0028441) | 1.17752 ± 0.00309411 (W 0.00547448) | 0.982621 ± 0.00692288 (W 0.00165516) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.46821 ± 0.00566996 (W 0.00384143) | 2.76061 ± 0.00906655 (W 0.00677902) | 2.44537 ± 0.0181008 (W 0.00483718) | 🔵 faer-fork 1.12× faster than `faer-upstream` | · |  |
| `svd_values/n32/b1` | 0.083867 ± 0.000492464 (W 0.00012938) | 0.159397 ± 0.00133864 (W 0.00215927) | 0.098914 ± 0.000738041 (W 0.00209326) | 🔵 faer-fork 1.90× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `svd_values/n64/b1` | 0.349111 ± 0.000946532 (W 0.00178335) | 0.629634 ± 0.00278768 (W 0.00211726) | 0.467422 ± 0.00160879 (W 0.00263751) | 🔵 faer-fork 1.80× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.800191 ± 0.00495224 (W 0.00305437) | 1.5086 ± 0.00627213 (W 0.00271246) | 1.31176 ± 0.00670374 (W 0.00448396) | 🔵 faer-fork 1.89× faster than `faer-upstream` | 🔵 faer-fork 1.64× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.001393 ± 2.08167e-05 (W 2.5006e-05) | 0.001193 ± 8.0829e-05 (W 1.28919e-05) | - | 🔴 faer-fork 1.17× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003257 ± 0.000140358 (W 4.14729e-05) | 0.002946 ± 3.06649e-05 (W 1.61957e-05) | - | 🔴 faer-fork 1.11× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.00566 ± 0.000200403 (W 3.5402e-05) | 0.00531 ± 8.12835e-05 (W 3.31662e-05) | - | 🔴 faer-fork 1.07× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n32/b1` | 0.0052 ± 9.06661e-05 (W 4.77493e-05) | 0.004929 ± 5.7735e-06 (W 3.70135e-05) | 0.007775 ± 7.40968e-05 (W 4.498e-05) | 🔴 faer-fork 1.05× slower than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.029915 ± 0.000459349 (W 0.000121162) | 0.028814 ± 0.000200176 (W 4.51254e-05) | 0.044252 ± 0.000443959 (W 0.000255301) | · | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `cholesky/n96/b1` | 0.079569 ± 0.00013642 (W 0.000320475) | 0.086221 ± 0.000228685 (W 0.000315617) | 0.125774 ± 0.00103838 (W 0.00211082) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `eigh/n32/b1` | 0.138759 ± 0.000344433 (W 0.0012851) | 0.141293 ± 0.000117205 (W 0.00259094) | 0.15003 ± 0.000541 (W 0.00196527) | · | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `eigh/n64/b1` | 0.566205 ± 0.00144035 (W 0.00250668) | 0.619865 ± 0.00115557 (W 0.0020978) | 0.502536 ± 0.00125096 (W 0.00366703) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.13× slower than `lapack-mkl` |  |
| `eigh/n96/b1` | 1.33412 ± 0.00408273 (W 0.00536982) | 1.4498 ± 0.00434389 (W 0.00333492) | 0.980227 ± 0.00436953 (W 0.00321868) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |
| `full_piv_lu/n32/b1` | 0.018044 ± 0.000170608 (W 8.43801e-05) | 0.015689 ± 0.000164925 (W 8.01704e-05) | - | 🔴 faer-fork 1.15× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.101038 ± 0.000367217 (W 0.000395509) | 0.089797 ± 0.000490531 (W 0.000130523) | - | 🔴 faer-fork 1.13× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.235319 ± 0.00627035 (W 0.00148719) | 0.264093 ± 0.000725184 (W 0.00264415) | - | 🔵 faer-fork 1.12× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.011071 ± 0.00019468 (W 0.000123572) | 0.028283 ± 4.0501e-05 (W 0.00112818) | - | 🔵 faer-fork 2.55× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.011141 ± 0.000163147 (W 0.000134113) | 0.028263 ± 3.19427e-05 (W 8.26027e-05) | - | 🔵 faer-fork 2.54× faster than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.038301 ± 0.000147422 (W 0.000817225) | 0.060523 ± 0.00026818 (W 0.000220459) | - | 🔵 faer-fork 1.58× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.038752 ± 0.000205508 (W 0.000251653) | 0.060723 ± 0.000471035 (W 0.000330811) | - | 🔵 faer-fork 1.57× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.088085 ± 0.000604501 (W 0.00065915) | 0.148186 ± 0.000738313 (W 0.00159599) | - | 🔵 faer-fork 1.68× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.088055 ± 0.000282064 (W 0.000574192) | 0.149449 ± 0.000539151 (W 0.00184651) | - | 🔵 faer-fork 1.70× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.011853 ± 5.67186e-05 (W 8.67179e-05) | 0.011301 ± 1.52753e-05 (W 0.000103775) | 0.016981 ± 2.13776e-05 (W 6.31134e-05) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.057398 ± 0.000396016 (W 0.00026085) | 0.050634 ± 0.000343235 (W 0.0016544) | 0.082594 ± 0.0002467 (W 0.000159607) | 🔴 faer-fork 1.13× slower than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `lu/n96/b1` | 0.140101 ± 0.00119918 (W 0.000971205) | 0.135934 ± 9.86577e-05 (W 0.00222791) | 0.208549 ± 0.000321865 (W 0.00205207) | · | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `qr/n32/b1` | 0.061454 ± 0.00040156 (W 0.000951406) | 0.090338 ± 0.000953784 (W 0.0011302) | 0.04843 ± 0.000121533 (W 0.000245582) | 🔵 faer-fork 1.47× faster than `faer-upstream` | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `qr/n64/b1` | 0.176339 ± 0.000224665 (W 0.000810663) | 0.362385 ± 0.000526689 (W 0.00225747) | 0.264624 ± 0.00145775 (W 0.00221974) | 🔵 faer-fork 2.06× faster than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `qr/n96/b1` | 0.349952 ± 0.00177613 (W 0.00235006) | 0.69775 ± 0.00613239 (W 0.0043877) | 0.663316 ± 0.0023836 (W 0.00239217) | 🔵 faer-fork 1.99× faster than `faer-upstream` | 🔵 faer-fork 1.90× faster than `lapack-mkl` |  |
| `qr_factor/n32/b1` | 0.030627 ± 0.000117758 (W 0.000284273) | 0.056245 ± 0.000738209 (W 0.000683681) | 0.026389 ± 0.000530709 (W 6.6778e-05) | 🔵 faer-fork 1.84× faster than `faer-upstream` | 🔴 faer-fork 1.16× slower than `lapack-mkl` |  |
| `qr_factor/n64/b1` | 0.111247 ± 0.00123731 (W 0.000318338) | 0.248974 ± 0.00221499 (W 0.00233633) | 0.722557 ± 0.0017367 (W 0.00239906) | 🔵 faer-fork 2.24× faster than `faer-upstream` | 🔵 faer-fork 6.50× faster than `lapack-mkl` |  |
| `qr_factor/n96/b1` | 0.226863 ± 7.05715e-05 (W 0.00231311) | 0.498418 ± 0.00800562 (W 0.00334107) | 2.3605 ± 0.0062574 (W 0.00387247) | 🔵 faer-fork 2.20× faster than `faer-upstream` | 🔵 faer-fork 10.40× faster than `lapack-mkl` |  |
| `solve/n32/b1` | 0.013375 ± 6.1101e-05 (W 6.7091e-05) | 0.012524 ± 0.000171407 (W 0.000117866) | 0.016962 ± 7.2111e-05 (W 8.00956e-05) | 🔴 faer-fork 1.07× slower than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.060232 ± 0.00029896 (W 0.000171567) | 0.053339 ± 0.000202527 (W 0.000105158) | 0.080159 ± 0.000129384 (W 0.00131673) | 🔴 faer-fork 1.13× slower than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `solve/n96/b1` | 0.14003 ± 0.000962873 (W 0.001893) | 0.140482 ± 0.000441611 (W 0.00211486) | 0.201225 ± 0.000254146 (W 0.00209131) | · | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `svd_thin/n32/b1` | 0.212205 ± 0.00189946 (W 0.00186359) | 0.232173 ± 0.00305141 (W 0.00208278) | 0.25695 ± 0.000324254 (W 0.00170719) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `svd_thin/n64/b1` | 1.0284 ± 0.0032243 (W 0.00357385) | 1.18757 ± 0.00322893 (W 0.00357061) | 0.944852 ± 0.00284633 (W 0.00122535) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔴 faer-fork 1.09× slower than `lapack-mkl` |  |
| `svd_thin/n96/b1` | 2.42333 ± 0.00796885 (W 0.00331595) | 2.78813 ± 0.000756472 (W 0.0027986) | 2.24919 ± 0.0126394 (W 0.00302979) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔴 faer-fork 1.08× slower than `lapack-mkl` |  |
| `svd_values/n32/b1` | 0.084047 ± 0.000433729 (W 0.000195079) | 0.158054 ± 0.000221736 (W 0.00209341) | 0.098513 ± 0.0011381 (W 0.00185741) | 🔵 faer-fork 1.88× faster than `faer-upstream` | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |
| `svd_values/n64/b1` | 0.358228 ± 0.00111872 (W 0.00214194) | 0.629273 ± 0.00232926 (W 0.00215066) | 0.468363 ± 0.00330146 (W 0.00325883) | 🔵 faer-fork 1.76× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `svd_values/n96/b1` | 0.829696 ± 0.00745957 (W 0.00257309) | 1.50523 ± 0.000158812 (W 0.00297591) | 1.31031 ± 0.00304359 (W 0.00287771) | 🔵 faer-fork 1.81× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `triangular_solve/n32/b1` | 0.001382 ± 1.52753e-05 (W 2.40479e-05) | 0.001182 ± 5.7735e-06 (W 1.54337e-05) | - | 🔴 faer-fork 1.17× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003266 ± 0.000106397 (W 2.53614e-05) | 0.002946 ± 3.05505e-05 (W 1.89816e-05) | - | 🔴 faer-fork 1.11× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.005641 ± 2.08167e-05 (W 2.90052e-05) | 0.00523 ± 3.60555e-05 (W 2.07364e-05) | - | 🔴 faer-fork 1.08× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

Not applicable to this population's shapes and reported as skipped: `eig/32`, `eig/64`, `eig/96`, `full_piv_lu/32`, `full_piv_lu/64`, `full_piv_lu/96`, `householder_apply/32`, `householder_apply/64`, `householder_apply/96`, `triangular_solve/32`, `triangular_solve/64`, `triangular_solve/96`, `upgrade_factor/32`, `upgrade_factor/64`, `upgrade_factor/96`.

## linalg-mid, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.066735 ± 0.000416463 (W 0.000471599) | 0.06997 ± 0.00235779 (W 0.000603684) | 0.115295 ± 0.000650478 (W 0.000538921) | · | 🔵 faer-fork 1.73× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n256/b1` | 0.387051 ± 0.00453729 (W 0.00293365) | 0.389827 ± 0.00693397 (W 0.00315221) | 0.636947 ± 0.00179557 (W 0.00565404) | · | 🔵 faer-fork 1.65× faster than `lapack-mkl` |  |
| `cholesky/n512/b1` | 2.53585 ± 0.0618341 (W 0.00678012) | 2.51999 ± 0.0124536 (W 0.00624261) | 3.95817 ± 0.0169505 (W 0.0306853) | · | 🔵 faer-fork 1.56× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.33816 ± 0.0214676 (W 0.00406498) | 2.2501 ± 0.0133222 (W 0.00882163) | 1.84676 ± 0.0047212 (W 0.00574243) | · | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 10.0607 ± 0.0298982 (W 0.0134345) | 9.76697 ± 0.0659382 (W 0.0192784) | 10.0044 ± 0.0465906 (W 0.021111) | · | · |  |
| `eigh/n512/b1` | 50.0813 ± 0.224544 (W 0.0820323) | 48.6175 ± 0.124196 (W 0.0452872) | 61.1585 ± 0.194675 (W 0.158269) | · | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.313174 ± 0.00168717 (W 0.00233117) | 0.313103 ± 0.00219027 (W 0.00307404) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.7064 ± 0.0178162 (W 0.00442343) | 2.76084 ± 0.0142369 (W 0.0134267) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 20.8014 ± 0.576987 (W 0.0363365) | 21.6152 ± 0.558973 (W 0.0345105) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.261327 ± 0.0012004 (W 0.00245375) | 0.261718 ± 0.00218623 (W 0.00369031) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.261367 ± 0.00133488 (W 0.00257374) | 0.258882 ± 0.00219277 (W 0.000523934) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.91351 ± 0.00410096 (W 0.005808) | 1.90645 ± 0.00717885 (W 0.00728693) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.9104 ± 0.0135416 (W 0.00400351) | 1.91498 ± 0.0108394 (W 0.0064071) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 16.034 ± 0.140508 (W 0.0335243) | 16.0029 ± 0.112205 (W 0.108163) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 15.898 ± 0.0197791 (W 0.0407876) | 15.8752 ± 0.0426156 (W 0.031105) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.133689 ± 0.0171505 (W 0.00183213) | 0.137506 ± 0.0151982 (W 0.00164352) | 0.191296 ± 0.0177856 (W 0.00212839) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.973595 ± 0.115973 (W 0.00245844) | 1.03446 ± 0.00468505 (W 0.00417006) | 0.986469 ± 0.133824 (W 0.00359018) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n512/b1` | 6.56409 ± 0.669727 (W 0.0193733) | 7.16546 ± 0.0125002 (W 0.0158483) | 6.02572 ± 0.541198 (W 0.0134626) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n128/b1` | 0.493229 ± 0.00271572 (W 0.00236729) | 0.516784 ± 0.000818513 (W 0.00237392) | 0.764756 ± 0.00475397 (W 0.00343033) | · | 🔵 faer-fork 1.55× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 2.81375 ± 0.0179368 (W 0.00595645) | 2.93344 ± 0.00535516 (W 0.00358195) | 4.39499 ± 0.015144 (W 0.0102053) | · | 🔵 faer-fork 1.56× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 18.1706 ± 0.971946 (W 0.0195274) | 19.1486 ± 1.02757 (W 0.0408672) | 30.9343 ± 0.0409732 (W 0.0832488) | · | 🔵 faer-fork 1.70× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n128/b1` | 0.316409 ± 0.00223883 (W 0.00153717) | 0.536741 ± 0.0033046 (W 0.00190748) | 0.374769 ± 0.00157338 (W 0.00325755) | 🔵 faer-fork 1.70× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 1.54266 ± 0.0087798 (W 0.00429815) | 2.87798 ± 0.00681028 (W 0.00955391) | 2.08508 ± 0.0168317 (W 0.00479835) | 🔵 faer-fork 1.87× faster than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 8.59515 ± 0.0798693 (W 0.039511) | 17.5044 ± 0.0530038 (W 0.0309466) | 14.3726 ± 0.045452 (W 0.0272591) | 🔵 faer-fork 2.04× faster than `faer-upstream` | 🔵 faer-fork 1.67× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.13396 ± 0.00135555 (W 0.00154701) | 0.136464 ± 0.00121257 (W 0.00248266) | 0.186157 ± 0.000835154 (W 0.00194906) | · | 🔵 faer-fork 1.39× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 0.754225 ± 0.00757817 (W 0.00449267) | 0.806423 ± 0.00387416 (W 0.00243176) | 0.983211 ± 0.00487689 (W 0.00188759) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `solve/n512/b1` | 6.544 ± 0.0194071 (W 0.0162753) | 7.17743 ± 0.0881601 (W 0.0144151) | 5.99025 ± 0.0141732 (W 0.0216783) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.09× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 3.38762 ± 0.019648 (W 0.00404503) | 3.6866 ± 0.00859513 (W 0.00764262) | 3.30198 ± 0.00398637 (W 0.00853112) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · |  |
| `svd_thin/n256/b1` | 16.8365 ± 0.0573459 (W 0.0227531) | 18.4246 ± 0.0615289 (W 0.0278817) | 17.7087 ± 0.138694 (W 0.0300467) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.05× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 94.6849 ± 0.39334 (W 0.143327) | 104.98 ± 1.14627 (W 0.117922) | 115.095 ± 0.92086 (W 0.384443) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.03229 ± 0.00537736 (W 0.00344989) | 2.6826 ± 0.00650588 (W 0.00874801) | 1.16849 ± 0.00313883 (W 0.00307897) | 🔵 faer-fork 2.60× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 6.33704 ± 0.0237575 (W 0.0100252) | 12.4207 ± 0.0165202 (W 0.0198042) | 6.89476 ± 0.0633681 (W 0.0110258) | 🔵 faer-fork 1.96× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 41.3574 ± 0.0564069 (W 0.0356924) | 66.7218 ± 0.196123 (W 0.0530011) | 48.3902 ± 0.559339 (W 0.101693) | 🔵 faer-fork 1.61× faster than `faer-upstream` | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.004208 ± 0.000159813 (W 2.71901e-05) | 0.004017 ± 4.32474e-05 (W 3.7659e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.011802 ± 0.000905962 (W 0.000128725) | 0.011311 ± 0.000953062 (W 3.87195e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.039223 ± 0.00496274 (W 0.000384228) | 0.039584 ± 0.00474038 (W 0.000512096) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.063789 ± 0.000143643 (W 0.000647337) | 0.081062 ± 0.00111744 (W 0.00170925) | 0.114644 ± 0.00175204 (W 0.00221635) | 🔵 faer-fork 1.27× faster than `faer-upstream` | 🔵 faer-fork 1.80× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.274431 ± 0.00355846 (W 0.00273887) | 0.370009 ± 0.00554923 (W 0.0170925) | 0.403613 ± 0.00392854 (W 0.00504303) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `cholesky/n512/b1` | 1.40668 ± 0.00828619 (W 0.00433948) | 1.56963 ± 0.0535725 (W 0.0326169) | 1.93884 ± 0.00609053 (W 0.0174277) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n128/b1` | 2.21323 ± 0.00673757 (W 0.0053262) | 2.15905 ± 0.00700938 (W 0.00324537) | 1.0708 ± 0.00381001 (W 0.0031464) | · | 🔴 faer-fork 2.07× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 6.36456 ± 0.0294481 (W 0.00600927) | 6.77104 ± 0.0432669 (W 0.0171502) | 4.75561 ± 0.0212623 (W 0.0130148) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.34× slower than `lapack-mkl` |  |
| `eigh/n512/b1` | 24.0251 ± 0.134157 (W 0.0319996) | 24.886 ± 0.087786 (W 0.0331723) | 21.4934 ± 0.0270891 (W 0.0297164) | · | 🔴 faer-fork 1.12× slower than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.339532 ± 0.0015171 (W 0.00311442) | 0.312914 ± 0.000590323 (W 0.00283768) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.02304 ± 0.00583944 (W 0.00838212) | 2.7784 ± 0.0312653 (W 0.00904774) | - | 🔵 faer-fork 1.37× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 12.881 ± 0.0756654 (W 0.0172806) | 15.3557 ± 0.0857877 (W 0.0230978) | - | 🔵 faer-fork 1.19× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.081692 ± 0.000581715 (W 0.00030586) | 0.080099 ± 0.000819861 (W 0.000616295) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.084768 ± 0.000516202 (W 0.000897396) | 0.082303 ± 5.2915e-05 (W 0.000773351) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.524467 ± 0.00289555 (W 0.00352612) | 0.52054 ± 0.00337605 (W 0.00256905) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.524358 ± 0.00608886 (W 0.00426842) | 0.513066 ± 0.00266637 (W 0.00144463) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 4.10404 ± 0.0139568 (W 0.0186247) | 4.05306 ± 0.0323344 (W 0.0105466) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 4.16243 ± 0.00940484 (W 0.00920789) | 4.09389 ± 0.0245611 (W 0.0098523) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.131846 ± 0.0190503 (W 0.00230054) | 0.152224 ± 0.000938097 (W 0.00480531) | 0.167201 ± 0.000685573 (W 0.00120327) | · | 🔵 faer-fork 1.27× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.79404 ± 0.120348 (W 0.00499308) | 0.773782 ± 0.00343462 (W 0.0163086) | 0.377123 ± 0.111094 (W 0.00185186) | · | 🔴 faer-fork 2.11× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n512/b1` | 4.21605 ± 0.0324722 (W 0.0052743) | 4.1129 ± 0.037336 (W 0.0804369) | 2.62102 ± 0.0130871 (W 0.00757857) | · | 🔴 faer-fork 1.61× slower than `lapack-mkl` |  |
| `qr/n128/b1` | 0.347908 ± 0.000939626 (W 0.00276952) | 0.572256 ± 0.00335218 (W 0.00485105) | 0.484953 ± 0.00213806 (W 0.0055364) | 🔵 faer-fork 1.64× faster than `faer-upstream` | 🔵 faer-fork 1.39× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 1.16945 ± 0.00380832 (W 0.00448134) | 1.95323 ± 0.0197282 (W 0.00591259) | 2.01739 ± 0.00246653 (W 0.00816928) | 🔵 faer-fork 1.67× faster than `faer-upstream` | 🔵 faer-fork 1.73× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 7.98226 ± 0.973243 (W 0.00598397) | 10.0107 ± 0.948157 (W 0.0158169) | 12.0917 ± 0.146658 (W 0.0356081) | 🔵 faer-fork 1.25× faster than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n128/b1` | 0.22528 ± 0.000227172 (W 0.00159392) | 0.700586 ± 0.00193904 (W 0.0029198) | 0.196276 ± 0.0019505 (W 0.00207023) | 🔵 faer-fork 3.11× faster than `faer-upstream` | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 0.662805 ± 0.00276159 (W 0.00339412) | 3.07228 ± 0.0143768 (W 0.0122147) | 0.664809 ± 0.00415118 (W 0.00252251) | 🔵 faer-fork 4.64× faster than `faer-upstream` | · |  |
| `qr_factor/n512/b1` | 3.16478 ± 0.0522163 (W 0.0150025) | 16.5905 ± 0.121432 (W 0.0644495) | 3.81868 ± 0.00521479 (W 0.0111246) | 🔵 faer-fork 5.24× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.134921 ± 0.000610282 (W 0.00137217) | 0.148828 ± 0.00243557 (W 0.00472037) | 0.165368 ± 0.000452714 (W 0.002003) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 0.565504 ± 0.00280888 (W 0.00267908) | 0.729839 ± 0.0212856 (W 0.00939973) | 0.363617 ± 0.000905091 (W 0.00301586) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔴 faer-fork 1.56× slower than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n512/b1` | 4.10794 ± 0.0273755 (W 0.0136683) | 3.71844 ± 0.0353525 (W 0.0790146) | 1.80235 ± 0.0213857 (W 0.00501067) | 🔴 faer-fork 1.10× slower than `faer-upstream` | 🔴 faer-fork 2.28× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 2.47925 ± 0.00503502 (W 0.00403482) | 2.81213 ± 0.00427518 (W 0.0157912) | 2.51654 ± 0.00513953 (W 0.00560804) | 🔵 faer-fork 1.13× faster than `faer-upstream` | · |  |
| `svd_thin/n256/b1` | 10.343 ± 0.0855256 (W 0.0179251) | 13.2631 ± 0.0772679 (W 0.0244585) | 12.0771 ± 0.0433681 (W 0.0170724) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 41.1336 ± 0.0885692 (W 0.0606607) | 55.6918 ± 0.0772047 (W 0.0480897) | 56.3973 ± 2.15915 (W 0.066225) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/n128/b1` | 1.0814 ± 0.00216942 (W 0.00283892) | 2.17646 ± 0.00889602 (W 0.0046869) | 1.11326 ± 0.00220377 (W 0.00344959) | 🔵 faer-fork 2.01× faster than `faer-upstream` | · |  |
| `svd_values/n256/b1` | 5.11196 ± 0.00974828 (W 0.0086457) | 10.4269 ± 0.0211425 (W 0.017221) | 6.09985 ± 0.0297736 (W 0.00807748) | 🔵 faer-fork 2.04× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 22.7708 ± 0.119062 (W 0.0244181) | 41.8937 ± 0.0319989 (W 0.0420135) | 25.7107 ± 0.178045 (W 0.0290191) | 🔵 faer-fork 1.84× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.00516 ± 0.000135031 (W 5.01817e-05) | 0.003687 ± 0.000212784 (W 2.88097e-05) | - | 🔴 faer-fork 1.40× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.012353 ± 0.000246131 (W 7.50953e-05) | 0.011351 ± 0.000985057 (W 4.70457e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.030036 ± 0.000837354 (W 0.000240269) | 0.028894 ± 0.00101004 (W 0.00170468) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.061836 ± 0.00104426 (W 0.000762123) | 0.073887 ± 0.000315868 (W 0.00052926) | 0.114964 ± 0.000674372 (W 0.00157716) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 1.86× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.273489 ± 0.00359326 (W 0.0043021) | 0.389792 ± 0.0170143 (W 0.0216333) | 0.362611 ± 0.00377772 (W 0.00470712) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n512/b1` | 1.25569 ± 0.01241 (W 0.00349925) | 1.47685 ± 0.00525095 (W 0.0254219) | 1.45276 ± 0.00321891 (W 0.019374) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔵 faer-fork 1.16× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.20208 ± 0.00832851 (W 0.00343468) | 2.17309 ± 0.00874836 (W 0.00590053) | 0.998109 ± 0.00694689 (W 0.00245699) | · | 🔴 faer-fork 2.21× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 6.15161 ± 0.00963438 (W 0.0050132) | 6.75993 ± 0.0180243 (W 0.0208703) | 3.9541 ± 0.0184723 (W 0.0129191) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.56× slower than `lapack-mkl` |  |
| `eigh/n512/b1` | 21.3781 ± 0.090106 (W 0.0251369) | 23.579 ± 0.0577569 (W 0.0396479) | 15.0848 ± 0.0277403 (W 0.0248076) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.42× slower than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.348935 ± 0.00334985 (W 0.00370123) | 0.313384 ± 0.00106688 (W 0.00293615) | - | 🔴 faer-fork 1.11× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 1.96061 ± 0.0137153 (W 0.0070451) | 2.76201 ± 0.0134917 (W 0.0141837) | - | 🔵 faer-fork 1.41× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 11.6506 ± 0.0603078 (W 0.0283614) | 14.4834 ± 0.019505 (W 0.0273192) | - | 🔵 faer-fork 1.24× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.055925 ± 0.000745246 (W 0.000337219) | 0.096551 ± 0.00144241 (W 0.00149381) | - | 🔵 faer-fork 1.73× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.058269 ± 0.0022496 (W 0.000673876) | 0.098965 ± 0.000583405 (W 0.00247352) | - | 🔵 faer-fork 1.70× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.279491 ± 0.00166965 (W 0.00123343) | 0.393643 ± 0.00616622 (W 0.0131969) | - | 🔵 faer-fork 1.41× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.285342 ± 0.00248103 (W 0.00361842) | 0.405395 ± 0.00800562 (W 0.0131981) | - | 🔵 faer-fork 1.42× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 2.22864 ± 0.0266005 (W 0.0130448) | 2.77161 ± 0.311715 (W 0.293935) | - | 🔵 faer-fork 1.24× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 2.23584 ± 0.00852352 (W 0.0134648) | 2.85881 ± 0.0641718 (W 0.329914) | - | 🔵 faer-fork 1.28× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.163134 ± 0.0172695 (W 0.000250793) | 0.146904 ± 0.000852805 (W 0.00266143) | 0.16637 ± 0.000918477 (W 0.00117495) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.791475 ± 0.119522 (W 0.00281986) | 0.769854 ± 0.00581234 (W 0.0211276) | 0.343971 ± 0.162159 (W 0.00405803) | · | 🔴 faer-fork 2.30× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n512/b1` | 3.98239 ± 0.0320522 (W 0.00651451) | 3.84082 ± 0.0628235 (W 0.0589902) | 2.41035 ± 0.129289 (W 0.0132591) | · | 🔴 faer-fork 1.65× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n128/b1` | 0.324619 ± 0.00195502 (W 0.00262513) | 0.701908 ± 0.0150527 (W 0.00381077) | 0.434299 ± 0.00285764 (W 0.00288968) | 🔵 faer-fork 2.16× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 1.00466 ± 0.00212743 (W 0.00287873) | 2.27126 ± 0.0359512 (W 0.0123635) | 1.82357 ± 0.0103399 (W 0.0101762) | 🔵 faer-fork 2.26× faster than `faer-upstream` | 🔵 faer-fork 1.82× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 5.75903 ± 0.0385461 (W 0.0100245) | 8.4629 ± 0.114926 (W 0.0518919) | 10.1761 ± 0.664144 (W 0.0304992) | 🔵 faer-fork 1.47× faster than `faer-upstream` | 🔵 faer-fork 1.77× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n128/b1` | 0.210672 ± 0.000317368 (W 0.00186288) | 0.827542 ± 0.0109785 (W 0.00542618) | 0.15446 ± 0.000689284 (W 0.00212662) | 🔵 faer-fork 3.93× faster than `faer-upstream` | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 0.612982 ± 0.0100501 (W 0.00345244) | 3.34149 ± 0.0297785 (W 0.00762695) | 0.57964 ± 0.00289577 (W 0.00220007) | 🔵 faer-fork 5.45× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 1.88052 ± 0.0645647 (W 0.00482637) | 17.0152 ± 0.112306 (W 0.0663312) | 2.29431 ± 0.00886215 (W 0.00489118) | 🔵 faer-fork 9.05× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n128/b1` | 0.135372 ± 0.00097406 (W 0.000324345) | 0.143297 ± 0.00165481 (W 0.00125203) | 0.160699 ± 0.000226858 (W 0.000342141) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 0.55825 ± 0.00364449 (W 0.00253159) | 0.734068 ± 0.00632179 (W 0.0237506) | 0.338511 ± 0.00319339 (W 0.00343789) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔴 faer-fork 1.65× slower than `lapack-mkl` |  |
| `solve/n512/b1` | 3.78139 ± 0.0412671 (W 0.0111176) | 3.57069 ± 0.0711737 (W 0.0521177) | 1.30822 ± 0.0163937 (W 0.00482534) | 🔴 faer-fork 1.06× slower than `faer-upstream` | 🔴 faer-fork 2.89× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 2.46937 ± 0.0114085 (W 0.00321556) | 2.81076 ± 0.00599535 (W 0.0101073) | 2.40522 ± 0.00565114 (W 0.00596103) | 🔵 faer-fork 1.14× faster than `faer-upstream` | · |  |
| `svd_thin/n256/b1` | 9.75505 ± 0.0414565 (W 0.00537742) | 13.3227 ± 0.00503617 (W 0.0292189) | 11.0812 ± 0.0511589 (W 0.0178425) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 35.3811 ± 0.146463 (W 0.0441453) | 52.2186 ± 0.027115 (W 0.0667458) | 47.1691 ± 2.85517 (W 0.0906996) | 🔵 faer-fork 1.48× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/n128/b1` | 1.11658 ± 0.00496295 (W 0.00297837) | 2.17854 ± 0.00680859 (W 0.00607464) | 1.0973 ± 0.00237321 (W 0.00436971) | 🔵 faer-fork 1.95× faster than `faer-upstream` | · |  |
| `svd_values/n256/b1` | 5.02481 ± 0.0185403 (W 0.0121886) | 10.4979 ± 0.0325219 (W 0.0113425) | 5.9472 ± 0.0278491 (W 0.008167) | 🔵 faer-fork 2.09× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 20.6074 ± 0.0144595 (W 0.0230256) | 40.1315 ± 0.128546 (W 0.0493206) | 22.2559 ± 0.160988 (W 0.0328216) | 🔵 faer-fork 1.95× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.00512 ± 0.000105548 (W 4.30732e-05) | 0.003737 ± 0.000321455 (W 4.06202e-05) | - | 🔴 faer-fork 1.37× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.011572 ± 4.50925e-05 (W 6.38616e-05) | 0.009768 ± 3.40637e-05 (W 6.02495e-05) | - | 🔴 faer-fork 1.18× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.028433 ± 0.00115676 (W 0.000140464) | 0.026719 ± 0.00128166 (W 0.000172381) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.060132 ± 0.000653592 (W 0.00170212) | 0.063218 ± 0.00103755 (W 0.000117993) | 0.093415 ± 0.000801013 (W 0.00276952) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔵 faer-fork 1.55× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.314907 ± 0.00346005 (W 0.00281558) | 0.324194 ± 0.0104236 (W 0.00264906) | 0.460077 ± 0.0124588 (W 0.00432653) | · | 🔵 faer-fork 1.46× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n512/b1` | 2.06401 ± 0.0167392 (W 0.00401098) | 2.05002 ± 0.0193116 (W 0.00340045) | 3.33848 ± 0.0517352 (W 0.018399) | · | 🔵 faer-fork 1.62× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.33589 ± 0.0132054 (W 0.00397067) | 2.25135 ± 0.0101887 (W 0.00369594) | 1.81289 ± 0.00812007 (W 0.00525047) | · | 🔴 faer-fork 1.29× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 10.0438 ± 0.0225353 (W 0.02451) | 9.73106 ± 0.0811662 (W 0.0169239) | 9.80763 ± 0.0331325 (W 0.0114626) | · | · |  |
| `eigh/n512/b1` | 49.6224 ± 0.185432 (W 0.0684323) | 48.2712 ± 0.194493 (W 0.0620247) | 60.024 ± 0.211053 (W 0.0393523) | · | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.294389 ± 0.00277911 (W 0.00162956) | 0.289579 ± 0.00114022 (W 0.00185153) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.62201 ± 0.0165394 (W 0.012364) | 2.6047 ± 0.0119672 (W 0.00966626) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 20.3993 ± 0.614662 (W 0.0371129) | 20.5327 ± 0.488753 (W 0.080103) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.255185 ± 0.000292524 (W 0.00285946) | 0.253923 ± 0.00159309 (W 0.00229299) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.255035 ± 0.00175448 (W 0.00205628) | 0.254104 ± 0.0029161 (W 0.00273385) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.87644 ± 0.0225283 (W 0.00261787) | 1.86065 ± 0.0348778 (W 0.00808986) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.87626 ± 0.00367025 (W 0.0078229) | 1.87506 ± 0.00645346 (W 0.00532775) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 15.8401 ± 0.161276 (W 0.0754235) | 15.8844 ± 0.12518 (W 0.0694619) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 15.7024 ± 0.0109156 (W 0.0308123) | 15.7679 ± 0.0613752 (W 0.037413) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.144469 ± 0.000730029 (W 0.00221816) | 0.145281 ± 0.00192575 (W 0.000430987) | 0.149148 ± 0.00120701 (W 0.00179417) | · | · |  |
| `lu/n256/b1` | 0.694945 ± 0.113031 (W 0.00387494) | 0.700476 ± 0.114637 (W 0.00215153) | 0.825369 ± 0.00414138 (W 0.00326112) | · | 🔵 faer-fork 1.19× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n512/b1` | 5.01973 ± 0.62071 (W 0.00778637) | 5.03502 ± 0.644327 (W 0.0143425) | 5.19724 ± 0.0483621 (W 0.0102718) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n128/b1` | 0.468503 ± 0.00197618 (W 0.00275647) | 0.496054 ± 0.00148824 (W 0.00337409) | 0.6872 ± 0.00636965 (W 0.00476615) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 2.68396 ± 0.01023 (W 0.005322) | 2.78361 ± 0.00658813 (W 0.0102078) | 4.37073 ± 0.0185963 (W 0.0140235) | · | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 17.8505 ± 0.865781 (W 0.0169168) | 18.0669 ± 0.983176 (W 0.0328217) | 30.3512 ± 0.0633816 (W 0.0504997) | · | 🔵 faer-fork 1.70× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n128/b1` | 0.258372 ± 0.00435091 (W 0.00202754) | 0.283258 ± 0.0010266 (W 0.00153088) | 0.336397 ± 0.00509166 (W 0.00293027) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 1.28721 ± 0.00744297 (W 0.00265671) | 1.37613 ± 0.0102719 (W 0.00439796) | 1.92264 ± 0.00393758 (W 0.0063977) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 7.65327 ± 0.0782261 (W 0.0155328) | 8.00059 ± 0.024491 (W 0.0153402) | 13.5242 ± 0.0314711 (W 0.0211003) | · | 🔵 faer-fork 1.77× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.111618 ± 0.000768512 (W 0.00177881) | 0.111928 ± 0.00119752 (W 0.000323308) | 0.147585 ± 0.000398611 (W 0.0020524) | · | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 0.662134 ± 0.00112156 (W 0.00256493) | 0.662345 ± 0.000921977 (W 0.0035809) | 0.824527 ± 0.00774534 (W 0.00197889) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `solve/n512/b1` | 6.02372 ± 0.0144137 (W 0.0142476) | 6.04514 ± 0.00776214 (W 0.0108836) | 5.21943 ± 0.0187618 (W 0.00746182) | · | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 3.37076 ± 0.0135206 (W 0.00530721) | 3.67788 ± 0.0090816 (W 0.00489806) | 3.22309 ± 0.014107 (W 0.00914558) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · |  |
| `svd_thin/n256/b1` | 16.7508 ± 0.0684372 (W 0.0281075) | 18.2961 ± 0.0597817 (W 0.0184161) | 17.3624 ± 0.056554 (W 0.0286791) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · |  |
| `svd_thin/n512/b1` | 94.0162 ± 0.342142 (W 0.47035) | 104.393 ± 0.757177 (W 0.123229) | 114.374 ± 0.399856 (W 0.474604) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.01143 ± 0.00479725 (W 0.0011862) | 2.60324 ± 0.009854 (W 0.00411467) | 1.13257 ± 0.00655202 (W 0.00353836) | 🔵 faer-fork 2.57× faster than `faer-upstream` | 🔵 faer-fork 1.12× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 6.2332 ± 0.0377582 (W 0.01349) | 12.2493 ± 0.0221356 (W 0.0204684) | 6.77301 ± 0.0078883 (W 0.0113091) | 🔵 faer-fork 1.97× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 40.2445 ± 0.119789 (W 0.0569291) | 65.5302 ± 0.23357 (W 0.0661857) | 48.0064 ± 0.406567 (W 0.0500094) | 🔵 faer-fork 1.63× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.004689 ± 0.000454045 (W 4.49144e-05) | 0.004829 ± 0.000370689 (W 6.39625e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.013114 ± 0.000144777 (W 2.94958e-05) | 0.012614 ± 0.00147593 (W 6.93051e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.044082 ± 0.00326325 (W 0.00129329) | 0.043351 ± 0.00607151 (W 0.000266487) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.055403 ± 0.000717682 (W 0.000675215) | 0.073718 ± 0.00132099 (W 0.00259463) | 0.09107 ± 0.00100559 (W 0.00203067) | 🔵 faer-fork 1.33× faster than `faer-upstream` | 🔵 faer-fork 1.64× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.215101 ± 0.001613 (W 0.00202725) | 0.308104 ± 0.00483759 (W 0.0116557) | 0.269502 ± 0.0143101 (W 0.021287) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n512/b1` | 0.936546 ± 0.00322188 (W 0.00298139) | 1.12394 ± 0.0232713 (W 0.0371316) | 1.43718 ± 0.0562399 (W 0.0850113) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.53× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n128/b1` | 2.21196 ± 0.00352417 (W 0.00497292) | 2.16315 ± 0.0100191 (W 0.00339646) | 1.04736 ± 0.00239504 (W 0.00270494) | · | 🔴 faer-fork 2.11× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 6.34912 ± 0.0290411 (W 0.0112073) | 6.73749 ± 0.0444068 (W 0.00972277) | 4.64568 ± 0.011603 (W 0.0105313) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |
| `eigh/n512/b1` | 23.5969 ± 0.0806482 (W 0.0283431) | 24.5471 ± 0.058556 (W 0.0279975) | 21.0894 ± 0.030375 (W 0.0426435) | · | 🔴 faer-fork 1.12× slower than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.321449 ± 0.0023326 (W 0.00556525) | 0.287476 ± 0.00206219 (W 0.00180591) | - | 🔴 faer-fork 1.12× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 1.93884 ± 0.00566446 (W 0.00890614) | 2.61681 ± 0.00815217 (W 0.00732431) | - | 🔵 faer-fork 1.35× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 12.4082 ± 0.0857875 (W 0.0223606) | 14.3322 ± 0.0118683 (W 0.0301121) | - | 🔵 faer-fork 1.16× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.082313 ± 0.0002045 (W 0.00124469) | 0.079558 ± 0.000201793 (W 0.00100995) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.083405 ± 0.00133648 (W 0.00185546) | 0.08063 ± 0.00106038 (W 0.000369006) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.522454 ± 0.00195461 (W 0.00230717) | 0.519177 ± 0.00510749 (W 0.00422705) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.525759 ± 0.00436758 (W 0.00307163) | 0.516904 ± 0.00825659 (W 0.00453721) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 4.05452 ± 0.019994 (W 0.0131323) | 4.03071 ± 0.0382916 (W 0.00737598) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 4.16247 ± 0.0209843 (W 0.0104364) | 4.15828 ± 0.0318614 (W 0.0112936) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.144309 ± 0.0178008 (W 0.0014537) | 0.133539 ± 0.00188401 (W 0.00423385) | 0.147074 ± 0.00147981 (W 0.00165471) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.515551 ± 0.115968 (W 0.00354919) | 0.634543 ± 0.00375328 (W 0.0128039) | 0.323312 ± 0.00193663 (W 0.00105277) | · | 🔴 faer-fork 1.59× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n512/b1` | 3.75505 ± 0.00719 (W 0.00860754) | 3.08503 ± 0.016708 (W 0.0775418) | 1.62225 ± 0.00958222 (W 0.00689154) | 🔴 faer-fork 1.22× slower than `faer-upstream` | 🔴 faer-fork 2.31× slower than `lapack-mkl` |  |
| `qr/n128/b1` | 0.320357 ± 0.00273426 (W 0.00173165) | 0.548112 ± 0.00197201 (W 0.00286552) | 0.497627 ± 0.0218253 (W 0.00310461) | 🔵 faer-fork 1.71× faster than `faer-upstream` | 🔵 faer-fork 1.55× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n256/b1` | 1.06314 ± 0.00466556 (W 0.00184398) | 1.804 ± 0.00895981 (W 0.00833343) | 2.21391 ± 0.0114112 (W 0.00713321) | 🔵 faer-fork 1.70× faster than `faer-upstream` | 🔵 faer-fork 2.08× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 7.39363 ± 0.918845 (W 0.0196914) | 8.95293 ± 0.170541 (W 0.0292622) | 13.2152 ± 0.169901 (W 0.0185037) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.79× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n128/b1` | 0.20421 ± 0.00118528 (W 0.00209532) | 0.419331 ± 0.00197851 (W 0.00256556) | 0.180817 ± 0.000901762 (W 0.00161228) | 🔵 faer-fork 2.05× faster than `faer-upstream` | 🔴 faer-fork 1.13× slower than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 0.57999 ± 0.0042054 (W 0.0016704) | 1.3219 ± 0.00349075 (W 0.00546192) | 0.610528 ± 0.00136429 (W 0.00333845) | 🔵 faer-fork 2.28× faster than `faer-upstream` | 🔵 faer-fork 1.05× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 2.94679 ± 0.0153656 (W 0.00589258) | 4.44021 ± 0.0240596 (W 0.0116481) | 3.6665 ± 0.0182612 (W 0.00710461) | 🔵 faer-fork 1.51× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.113662 ± 0.000896009 (W 0.00136927) | 0.125965 ± 0.00271652 (W 0.00286724) | 0.146002 ± 0.000523043 (W 0.00201509) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 0.481958 ± 0.00641833 (W 0.00388807) | 0.572808 ± 0.00489071 (W 0.00933028) | 0.315458 ± 0.0030734 (W 0.00205825) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.53× slower than `lapack-mkl` |  |
| `solve/n512/b1` | 3.59376 ± 0.0104125 (W 0.014306) | 2.74261 ± 0.0676476 (W 0.0995057) | 1.64182 ± 0.00744923 (W 0.00395691) | 🔴 faer-fork 1.31× slower than `faer-upstream` | 🔴 faer-fork 2.19× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 2.45656 ± 0.0124341 (W 0.00278) | 2.78576 ± 0.00973538 (W 0.0165519) | 2.48868 ± 0.0129646 (W 0.0068584) | 🔵 faer-fork 1.13× faster than `faer-upstream` | · |  |
| `svd_thin/n256/b1` | 10.1691 ± 0.0384795 (W 0.015329) | 13.0708 ± 0.133589 (W 0.017919) | 11.9632 ± 0.0448488 (W 0.015258) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 40.2866 ± 0.169171 (W 0.0621314) | 54.8792 ± 0.144133 (W 0.0649505) | 55.1341 ± 0.927609 (W 0.0552464) | 🔵 faer-fork 1.36× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.05896 ± 0.00437127 (W 0.00175036) | 2.10881 ± 0.00966244 (W 0.00589559) | 1.10127 ± 0.00386829 (W 0.0020664) | 🔵 faer-fork 1.99× faster than `faer-upstream` | · |  |
| `svd_values/n256/b1` | 4.98567 ± 0.0133062 (W 0.0103014) | 10.2521 ± 0.0398369 (W 0.0209656) | 6.03352 ± 0.0251382 (W 0.00513857) | 🔵 faer-fork 2.06× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 21.6464 ± 0.0303232 (W 0.0302414) | 40.9052 ± 0.0376039 (W 0.0400397) | 25.5588 ± 0.0262924 (W 0.0529703) | 🔵 faer-fork 1.89× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.00531 ± 0.000159478 (W 2.79875e-05) | 0.004348 ± 0.000111072 (W 1.87136e-05) | - | 🔴 faer-fork 1.22× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.015279 ± 0.000904423 (W 0.000283188) | 0.012743 ± 0.00125924 (W 6.10737e-05) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.039073 ± 0.000618437 (W 0.000412304) | 0.034504 ± 0.000205687 (W 0.00144817) | - | 🔴 faer-fork 1.13× slower than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-mid, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.055114 ± 0.000587949 (W 0.000511388) | 0.066285 ± 0.0038927 (W 0.000360039) | 0.091991 ± 0.000790825 (W 0.00227552) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.67× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n256/b1` | 0.204354 ± 0.00292992 (W 0.0022755) | 0.28222 ± 0.00523613 (W 0.0144526) | 0.27366 ± 0.0437875 (W 0.0462151) | 🔵 faer-fork 1.38× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `cholesky/n512/b1` | 0.796664 ± 0.0128826 (W 0.00337617) | 0.99575 ± 0.0141051 (W 0.0271099) | 0.952234 ± 0.00354621 (W 0.00886361) | 🔵 faer-fork 1.25× faster than `faer-upstream` | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.19365 ± 0.00504107 (W 0.00327079) | 2.165 ± 0.00658018 (W 0.00623471) | 0.978503 ± 0.00597197 (W 0.00559708) | · | 🔴 faer-fork 2.24× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 6.10741 ± 0.0154074 (W 0.0383511) | 6.70415 ± 0.00895281 (W 0.0148353) | 3.86859 ± 0.0142699 (W 0.00763756) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.58× slower than `lapack-mkl` |  |
| `eigh/n512/b1` | 21.0345 ± 0.0632984 (W 0.0150435) | 23.2227 ± 0.041432 (W 0.0691454) | 14.6482 ± 0.0385023 (W 0.0224937) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.44× slower than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.331137 ± 0.00467034 (W 0.00418101) | 0.289474 ± 0.000711549 (W 0.00244925) | - | 🔴 faer-fork 1.14× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 1.86038 ± 0.00411651 (W 0.00822636) | 2.60654 ± 0.00533575 (W 0.00803984) | - | 🔵 faer-fork 1.40× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 11.2433 ± 0.076758 (W 0.0405221) | 13.4209 ± 0.0502917 (W 0.0244049) | - | 🔵 faer-fork 1.19× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.056094 ± 0.000667186 (W 0.00156233) | 0.096731 ± 0.000684902 (W 0.00189357) | - | 🔵 faer-fork 1.72× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.056225 ± 0.000862473 (W 0.00057158) | 0.098603 ± 0.00132996 (W 0.00199422) | - | 🔵 faer-fork 1.75× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.284469 ± 0.00138755 (W 0.00130311) | 0.397841 ± 0.014462 (W 0.0119066) | - | 🔵 faer-fork 1.40× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.288508 ± 0.00122781 (W 0.0010577) | 0.393237 ± 0.0142226 (W 0.0136271) | - | 🔵 faer-fork 1.36× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 2.18421 ± 0.00567785 (W 0.00694769) | 2.81088 ± 0.32472 (W 0.323587) | - | 🔵 faer-fork 1.29× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 2.25022 ± 0.0136898 (W 0.0138518) | 2.89494 ± 0.00664863 (W 0.367388) | - | 🔵 faer-fork 1.29× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.143608 ± 0.0180349 (W 0.000780369) | 0.126426 ± 0.000796386 (W 0.00217453) | 0.148308 ± 0.000788945 (W 0.0020506) | 🔴 faer-fork 1.14× slower than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.498549 ± 0.122205 (W 0.00251191) | 0.668776 ± 0.00821091 (W 0.0216942) | 0.314991 ± 0.00175846 (W 0.00331484) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔴 faer-fork 1.58× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n512/b1` | 3.47011 ± 0.00401951 (W 0.00762808) | 2.89963 ± 0.0563466 (W 0.0611441) | 1.24394 ± 0.0143567 (W 0.0112474) | 🔴 faer-fork 1.20× slower than `faer-upstream` | 🔴 faer-fork 2.79× slower than `lapack-mkl` |  |
| `qr/n128/b1` | 0.297985 ± 0.00189492 (W 0.0023922) | 0.674646 ± 0.014043 (W 0.00435769) | 0.453591 ± 0.0236245 (W 0.0047196) | 🔵 faer-fork 2.26× faster than `faer-upstream` | 🔵 faer-fork 1.52× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n256/b1` | 0.895549 ± 0.00594452 (W 0.00256762) | 2.09844 ± 0.014914 (W 0.0125118) | 2.0587 ± 0.0177055 (W 0.0103876) | 🔵 faer-fork 2.34× faster than `faer-upstream` | 🔵 faer-fork 2.30× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 5.1681 ± 0.01044 (W 0.00704207) | 7.4034 ± 0.0433249 (W 0.0391719) | 10.409 ± 0.0177257 (W 0.0268402) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 2.01× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.197688 ± 0.00176631 (W 0.00447829) | 0.526921 ± 0.00937448 (W 0.00350691) | 0.14364 ± 0.000591787 (W 0.00245013) | 🔵 faer-fork 2.67× faster than `faer-upstream` | 🔴 faer-fork 1.38× slower than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 0.573849 ± 0.00460457 (W 0.00222565) | 1.58144 ± 0.035711 (W 0.01093) | 0.546678 ± 0.00478776 (W 0.00362484) | 🔵 faer-fork 2.76× faster than `faer-upstream` | · |  |
| `qr_factor/n512/b1` | 1.78468 ± 0.00745096 (W 0.00423104) | 4.75339 ± 0.0142976 (W 0.0265905) | 2.23894 ± 0.0025389 (W 0.00682994) | 🔵 faer-fork 2.66× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.113071 ± 0.000997969 (W 0.00041125) | 0.122398 ± 0.000716203 (W 0.00132278) | 0.147185 ± 0.000972126 (W 0.00199628) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 0.475786 ± 0.00511577 (W 0.00291281) | 0.555633 ± 0.00479956 (W 0.0199489) | 0.304227 ± 0.0038388 (W 0.00206534) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔴 faer-fork 1.56× slower than `lapack-mkl` |  |
| `solve/n512/b1` | 3.32371 ± 0.0244577 (W 0.00606452) | 2.5096 ± 0.0227978 (W 0.0654311) | 1.20783 ± 0.01446 (W 0.00610364) | 🔴 faer-fork 1.32× slower than `faer-upstream` | 🔴 faer-fork 2.75× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 2.45292 ± 0.0101999 (W 0.00361953) | 2.78885 ± 0.00891871 (W 0.0050547) | 2.36967 ± 0.00295806 (W 0.00926883) | 🔵 faer-fork 1.14× faster than `faer-upstream` | · |  |
| `svd_thin/n256/b1` | 9.66588 ± 0.027789 (W 0.0128157) | 13.161 ± 0.0359601 (W 0.0214859) | 10.9673 ± 0.0258528 (W 0.0148937) | 🔵 faer-fork 1.36× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 34.3942 ± 0.0637632 (W 0.0301532) | 51.3756 ± 0.136682 (W 0.0531593) | 47.9858 ± 1.06478 (W 0.0372897) | 🔵 faer-fork 1.49× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.10139 ± 0.00176214 (W 0.00193222) | 2.10888 ± 0.00168201 (W 0.00369224) | 1.08393 ± 0.00232557 (W 0.0032291) | 🔵 faer-fork 1.91× faster than `faer-upstream` | · |  |
| `svd_values/n256/b1` | 4.86163 ± 0.00878031 (W 0.0141086) | 10.342 ± 0.0431603 (W 0.00944373) | 5.91103 ± 0.0708819 (W 0.00821549) | 🔵 faer-fork 2.13× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 19.5845 ± 0.0644837 (W 0.0324625) | 39.0755 ± 0.0334022 (W 0.0415943) | 22.3706 ± 0.075517 (W 0.0477196) | 🔵 faer-fork 2.00× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.006221 ± 0.000274367 (W 2.74827e-05) | 0.004268 ± 0.000358535 (W 3.4135e-05) | - | 🔴 faer-fork 1.46× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.014067 ± 9.30609e-05 (W 0.000156009) | 0.010971 ± 0.000393303 (W 3.73805e-05) | - | 🔴 faer-fork 1.28× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.036768 ± 0.00114627 (W 0.000283567) | 0.033112 ± 0.0021558 (W 0.000282799) | - | 🔴 faer-fork 1.11× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.191517 ± 0.000126623 (W 0.00139083) | 0.185014 ± 0.000894727 (W 0.00227102) | 0.470367 ± 0.000236961 (W 0.00322384) | · | 🔵 faer-fork 2.46× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 1.23934 ± 0.0101465 (W 0.00389138) | 1.21263 ± 0.00587739 (W 0.00300603) | 1.84333 ± 0.0102426 (W 0.00446296) | · | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `cholesky/n512/b1` | 7.92568 ± 0.0294709 (W 0.0147654) | 7.9085 ± 0.0272225 (W 0.0163748) | 11.3716 ± 0.0746646 (W 0.0382779) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 3.34898 ± 0.0126168 (W 0.00952889) | 3.28007 ± 0.00448908 (W 0.00625395) | 4.38458 ± 0.0137263 (W 0.00769962) | · | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `eigh/n256/b1` | 17.6533 ± 0.0801443 (W 0.0238393) | 17.4319 ± 0.0637784 (W 0.025797) | 26.3556 ± 0.0706009 (W 0.0284895) | · | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `eigh/n512/b1` | 107.006 ± 0.334246 (W 0.158345) | 105.657 ± 0.180651 (W 0.164941) | 171.437 ± 0.443475 (W 0.159388) | · | 🔵 faer-fork 1.60× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.807024 ± 0.000992171 (W 0.0058986) | 0.779493 ± 0.00215229 (W 0.00368817) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 5.94558 ± 0.0263953 (W 0.0114383) | 6.04357 ± 0.039126 (W 0.00988051) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 40.6477 ± 0.192778 (W 0.0570561) | 40.9267 ± 0.126307 (W 0.0261787) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 1.05866 ± 0.00190427 (W 0.00364952) | 1.05151 ± 0.00750661 (W 0.0050393) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 1.05656 ± 0.00368928 (W 0.00183329) | 1.05044 ± 0.00483357 (W 0.00205449) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 7.51037 ± 0.0237438 (W 0.0096427) | 7.49484 ± 0.0638478 (W 0.0110415) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 7.57403 ± 0.0184941 (W 0.0156945) | 7.58122 ± 0.0507844 (W 0.0143754) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 56.9012 ± 0.169337 (W 0.0891662) | 56.8475 ± 0.0866803 (W 0.0497487) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 57.0069 ± 0.162429 (W 0.109564) | 56.8364 ± 0.0383215 (W 0.0548066) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.329635 ± 0.0020159 (W 0.00296482) | 0.328162 ± 0.000286194 (W 0.00282507) | 0.491686 ± 0.00341349 (W 0.00419047) | · | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `lu/n256/b1` | 2.13445 ± 0.00357454 (W 0.00483294) | 2.21388 ± 0.0125761 (W 0.0055602) | 3.25229 ± 0.014635 (W 0.0089523) | · | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `lu/n512/b1` | 14.6534 ± 0.110224 (W 0.0652554) | 14.8481 ± 0.0768393 (W 0.0245619) | 20.7599 ± 0.0528001 (W 0.0596477) | · | 🔵 faer-fork 1.42× faster than `lapack-mkl` |  |
| `qr/n128/b1` | 1.53285 ± 0.00310514 (W 0.00434534) | 1.5857 ± 0.00435264 (W 0.00301694) | 2.00486 ± 0.00658889 (W 0.00782561) | · | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 10.0582 ± 0.0347392 (W 0.00920423) | 10.3868 ± 0.0489387 (W 0.0209833) | 12.4604 ± 0.0383263 (W 0.0376488) | · | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 69.0735 ± 0.195709 (W 0.0733429) | 69.9609 ± 0.30262 (W 0.299595) | 81.2983 ± 0.222572 (W 0.0595613) | · | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.779683 ± 0.00383804 (W 0.00369167) | 1.07256 ± 0.00358822 (W 0.0042127) | 0.956713 ± 0.00683006 (W 0.00438244) | 🔵 faer-fork 1.38× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 4.65896 ± 0.0228578 (W 0.0109277) | 6.53572 ± 0.0839728 (W 0.0150799) | 5.72318 ± 0.0159286 (W 0.00985096) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 30.1064 ± 0.0748754 (W 0.0458651) | 37.8951 ± 0.188252 (W 0.0281074) | 39.1529 ± 0.135787 (W 0.103292) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.326679 ± 0.00176657 (W 0.0032918) | 0.328563 ± 0.00401357 (W 0.00287265) | 0.476368 ± 0.00080707 (W 0.0034229) | · | 🔵 faer-fork 1.46× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 2.066 ± 0.00871695 (W 0.0020781) | 2.14573 ± 0.0082913 (W 0.00379251) | 2.79275 ± 0.0213262 (W 0.0113387) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `solve/n512/b1` | 14.6746 ± 0.12471 (W 0.0690489) | 14.8288 ± 0.0524806 (W 0.0368291) | 18.4692 ± 0.105985 (W 0.0454554) | · | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 5.32123 ± 0.0182352 (W 0.00941437) | 5.83448 ± 0.0158908 (W 0.0107593) | 6.98247 ± 0.0205842 (W 0.0074295) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `svd_thin/n256/b1` | 32.058 ± 0.0711505 (W 0.0520346) | 34.741 ± 0.156329 (W 0.0435821) | 43.0635 ± 0.43113 (W 0.0392088) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 205.757 ± 0.50647 (W 0.479481) | 214.833 ± 0.698049 (W 0.644633) | 276.873 ± 1.85281 (W 1.23696) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.76642 ± 0.00823599 (W 0.00498538) | 3.54222 ± 0.00883034 (W 0.00829439) | 2.70989 ± 0.00832692 (W 0.00763506) | 🔵 faer-fork 2.01× faster than `faer-upstream` | 🔵 faer-fork 1.53× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 12.7671 ± 0.0934677 (W 0.0750527) | 20.0714 ± 0.191495 (W 0.389497) | 18.0526 ± 0.040269 (W 0.0146723) | 🔵 faer-fork 1.57× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 90.9481 ± 0.269105 (W 0.260952) | 114.757 ± 0.743176 (W 0.125424) | 122.324 ± 0.845601 (W 0.260331) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.007925 ± 2.51661e-05 (W 3.21916e-05) | 0.007564 ± 4.72582e-05 (W 3.80789e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.025037 ± 0.00020694 (W 0.000161245) | 0.023755 ± 0.000320052 (W 0.000126148) | - | 🔴 faer-fork 1.05× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.087853 ± 0.000277388 (W 0.00157997) | 0.08612 ± 0.00134493 (W 0.000537942) | - | · | - | `*` one row has no measurement here |

## linalg-mid, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.159367 ± 0.000796131 (W 0.00210384) | 0.178252 ± 0.00130758 (W 0.00373066) | 0.473382 ± 0.00263548 (W 0.0039834) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 2.97× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.744627 ± 0.00125182 (W 0.0026714) | 0.794861 ± 0.0124021 (W 0.00631647) | 0.79933 ± 0.0134841 (W 0.00904181) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |
| `cholesky/n512/b1` | 3.14833 ± 0.00982597 (W 0.00977975) | 3.37604 ± 0.018343 (W 0.0739362) | 3.63805 ± 0.008607 (W 0.0173148) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.16× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.59131 ± 0.00500813 (W 0.00353134) | 2.81724 ± 0.00451577 (W 0.00398184) | 1.98003 ± 0.00625026 (W 0.00558564) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.31× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 8.69364 ± 0.0414041 (W 0.0177734) | 11.3754 ± 0.00224285 (W 0.0170831) | 9.9781 ± 0.0142393 (W 0.0184914) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `eigh/n512/b1` | 39.4285 ± 0.0597996 (W 0.043449) | 45.1525 ± 0.137693 (W 0.0318246) | 52.4761 ± 0.180866 (W 0.0536202) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.610708 ± 0.00258001 (W 0.00446236) | 0.775595 ± 0.0109101 (W 0.00686812) | - | 🔵 faer-fork 1.27× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 3.47651 ± 0.02287 (W 0.00878775) | 6.00982 ± 0.0252731 (W 0.0147468) | - | 🔵 faer-fork 1.73× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 17.459 ± 0.0813231 (W 0.0305395) | 25.7477 ± 0.157579 (W 0.0360679) | - | 🔵 faer-fork 1.47× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.284731 ± 0.000492261 (W 0.00154731) | 0.282316 ± 0.00140906 (W 0.00173846) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.285362 ± 0.00128146 (W 0.00240814) | 0.283498 ± 0.001606 (W 0.00221683) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.92726 ± 0.0022351 (W 0.00481228) | 1.91992 ± 0.00611642 (W 0.00338278) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.94454 ± 0.0105327 (W 0.00113555) | 1.93298 ± 0.00774471 (W 0.00469639) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 14.6114 ± 0.0441225 (W 0.0168621) | 14.5931 ± 0.0665527 (W 0.029264) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 14.6023 ± 0.0395392 (W 0.0266022) | 14.6147 ± 0.039065 (W 0.0163602) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.291303 ± 0.000680427 (W 0.00237461) | 0.307933 ± 0.00134697 (W 0.00345908) | 0.470356 ± 0.000723941 (W 0.00276517) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.61× faster than `lapack-mkl` |  |
| `lu/n256/b1` | 1.30119 ± 0.00476314 (W 0.00460326) | 1.56177 ± 0.0257269 (W 0.0125251) | 1.01437 ± 0.00465101 (W 0.00302833) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔴 faer-fork 1.28× slower than `lapack-mkl` |  |
| `lu/n512/b1` | 6.52944 ± 0.0282611 (W 0.0287283) | 7.33929 ± 0.0873733 (W 0.101448) | 6.14575 ± 0.0579365 (W 0.0108991) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `qr/n128/b1` | 0.74563 ± 0.00218361 (W 0.00194342) | 1.03587 ± 0.00441157 (W 0.00313435) | 1.07145 ± 0.0008483 (W 0.00365756) | 🔵 faer-fork 1.39× faster than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 3.24417 ± 0.0108146 (W 0.0070552) | 4.35716 ± 0.0201855 (W 0.00578129) | 4.86212 ± 0.0317304 (W 0.00445714) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 20.6863 ± 0.0365002 (W 0.0202715) | 22.8107 ± 0.11586 (W 0.0254683) | 28.4481 ± 0.111627 (W 0.0444641) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.435742 ± 0.00277078 (W 0.00230006) | 0.997558 ± 0.00212768 (W 0.00373214) | 0.468434 ± 0.000775193 (W 0.00276131) | 🔵 faer-fork 2.29× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 1.61461 ± 0.00349268 (W 0.00404751) | 4.69188 ± 0.0486458 (W 0.0157364) | 1.62875 ± 0.00139278 (W 0.00422091) | 🔵 faer-fork 2.91× faster than `faer-upstream` | · |  |
| `qr_factor/n512/b1` | 9.44249 ± 0.0782914 (W 0.0167153) | 21.2585 ± 0.322165 (W 0.0321657) | 11.254 ± 0.0209613 (W 0.013304) | 🔵 faer-fork 2.25× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.286303 ± 0.00144035 (W 0.0019304) | 0.304527 ± 0.00519531 (W 0.00538183) | 0.457723 ± 0.00168555 (W 0.0030374) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.60× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 1.23604 ± 0.00592376 (W 0.00526412) | 1.45042 ± 0.00498422 (W 0.0141327) | 0.898625 ± 0.00293407 (W 0.00239147) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔴 faer-fork 1.38× slower than `lapack-mkl` |  |
| `solve/n512/b1` | 6.34647 ± 0.0401086 (W 0.0269045) | 7.107 ± 0.100848 (W 0.129869) | 5.65876 ± 0.0376052 (W 0.0155219) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.12× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 3.17084 ± 0.0142584 (W 0.00271713) | 4.13765 ± 0.00359291 (W 0.0190565) | 4.00082 ± 0.00705774 (W 0.00710141) | 🔵 faer-fork 1.30× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `svd_thin/n256/b1` | 15.2013 ± 0.00511404 (W 0.0321001) | 22.2464 ± 0.109536 (W 0.00772545) | 20.7581 ± 0.0940405 (W 0.0545985) | 🔵 faer-fork 1.46× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 73.6183 ± 0.169085 (W 0.110796) | 88.2598 ± 0.198137 (W 0.146531) | 112.263 ± 0.396852 (W 0.107814) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.41238 ± 0.0113971 (W 0.00637117) | 3.07302 ± 0.00128119 (W 0.00700884) | 1.97765 ± 0.014735 (W 0.00827141) | 🔵 faer-fork 2.18× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 7.53292 ± 0.11567 (W 0.0164372) | 16.929 ± 0.155435 (W 0.0217032) | 10.8578 ± 0.00752238 (W 0.00709089) | 🔵 faer-fork 2.25× faster than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 39.2312 ± 0.46757 (W 0.10314) | 58.8398 ± 0.168523 (W 0.0511035) | 55.2747 ± 0.098262 (W 0.0914072) | 🔵 faer-fork 1.50× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.009187 ± 3.51188e-05 (W 2.16795e-05) | 0.007404 ± 3.66106e-05 (W 2.20749e-05) | - | 🔴 faer-fork 1.24× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.021951 ± 3e-05 (W 0.000111937) | 0.023043 ± 6.4291e-05 (W 5.77062e-05) | - | · | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.057106 ± 0.000955886 (W 0.000294003) | 0.061915 ± 0.0014842 (W 0.000351405) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-mid, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.153135 ± 0.00172707 (W 0.00209962) | 0.16624 ± 0.000592141 (W 0.00178182) | 0.476227 ± 0.00203356 (W 0.0037812) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 3.11× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.69797 ± 0.0116633 (W 0.0029727) | 0.790151 ± 0.025313 (W 0.0166691) | 0.661142 ± 0.00313621 (W 0.00335865) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n512/b1` | 2.58708 ± 0.0671642 (W 0.00800326) | 2.73544 ± 0.024186 (W 0.0173217) | 2.27016 ± 0.0279041 (W 0.00943155) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.14× slower than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.47688 ± 0.0120164 (W 0.00603613) | 2.81746 ± 0.0148828 (W 0.00565833) | 1.65099 ± 0.00180818 (W 0.00429419) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.50× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 7.70486 ± 0.0502996 (W 0.0112353) | 11.1204 ± 0.0172768 (W 0.0278225) | 7.8912 ± 0.00890567 (W 0.0184952) | 🔵 faer-fork 1.44× faster than `faer-upstream` | · |  |
| `eigh/n512/b1` | 30.6763 ± 0.0389491 (W 0.035369) | 39.1704 ± 0.119764 (W 0.221122) | 36.625 ± 0.0339716 (W 0.0213369) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.592203 ± 0.00811069 (W 0.0054765) | 0.785954 ± 0.00507938 (W 0.00334597) | - | 🔵 faer-fork 1.33× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 3.12302 ± 0.0109597 (W 0.0096514) | 6.08229 ± 0.0258895 (W 0.0134541) | - | 🔵 faer-fork 1.95× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 13.9774 ± 0.0673713 (W 0.0349213) | 23.4136 ± 0.0706598 (W 0.0324848) | - | 🔵 faer-fork 1.68× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.176261 ± 0.000481623 (W 0.00146451) | 0.273241 ± 0.00431233 (W 0.00246016) | - | 🔵 faer-fork 1.55× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.177632 ± 0.000721149 (W 0.00142559) | 0.271379 ± 0.0013365 (W 0.00349201) | - | 🔵 faer-fork 1.53× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.998439 ± 0.00158333 (W 0.00120574) | 1.28072 ± 0.00233089 (W 0.0930247) | - | 🔵 faer-fork 1.28× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.01671 ± 0.0105865 (W 0.00281561) | 1.3034 ± 0.0164245 (W 0.0723462) | - | 🔵 faer-fork 1.28× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 7.99552 ± 0.0609695 (W 0.0375289) | 10.468 ± 0.249452 (W 1.1925) | - | 🔵 faer-fork 1.31× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 8.01356 ± 0.0467248 (W 0.0627723) | 9.8544 ± 1.34531 (W 1.10246) | - | 🔵 faer-fork 1.23× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/n128/b1` | 0.283739 ± 0.00285791 (W 0.00213111) | 0.294572 ± 0.00141185 (W 0.00356137) | 0.47259 ± 0.00204702 (W 0.00334257) | · | 🔵 faer-fork 1.67× faster than `lapack-mkl` |  |
| `lu/n256/b1` | 1.19082 ± 0.00184746 (W 0.00532212) | 1.45881 ± 0.0305058 (W 0.0145962) | 0.690977 ± 0.00459807 (W 0.00317766) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔴 faer-fork 1.72× slower than `lapack-mkl` |  |
| `lu/n512/b1` | 5.10894 ± 0.0218297 (W 0.00807422) | 5.84025 ± 0.0144071 (W 0.0209776) | 3.6044 ± 0.0201429 (W 0.0123101) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.42× slower than `lapack-mkl` |  |
| `qr/n128/b1` | 0.615383 ± 0.0049719 (W 0.00198876) | 1.14033 ± 0.0171304 (W 0.00420681) | 0.800862 ± 0.00255718 (W 0.00346869) | 🔵 faer-fork 1.85× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 2.34398 ± 0.00700194 (W 0.00558744) | 4.34334 ± 0.0670475 (W 0.0328557) | 3.96625 ± 0.0303691 (W 0.00741822) | 🔵 faer-fork 1.85× faster than `faer-upstream` | 🔵 faer-fork 1.69× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 11.7897 ± 0.0316021 (W 0.0136222) | 19.3047 ± 0.374123 (W 0.169529) | 16.3088 ± 0.0555404 (W 0.0545078) | 🔵 faer-fork 1.64× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.379316 ± 0.00363732 (W 0.00206798) | 1.08202 ± 0.00332629 (W 0.00788841) | 0.33313 ± 0.000901922 (W 0.00182286) | 🔵 faer-fork 2.85× faster than `faer-upstream` | 🔴 faer-fork 1.14× slower than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 1.30191 ± 0.00748623 (W 0.00280918) | 4.77402 ± 0.037522 (W 0.0213742) | 1.66244 ± 0.00609118 (W 0.00347612) | 🔵 faer-fork 3.67× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 5.04438 ± 0.010097 (W 0.0118273) | 19.8809 ± 0.337223 (W 0.18653) | 5.76928 ± 0.0124388 (W 0.0128461) | 🔵 faer-fork 3.94× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.279824 ± 0.00210445 (W 0.00200923) | 0.28469 ± 0.00256829 (W 0.00137339) | 0.459856 ± 0.0010199 (W 0.00435962) | · | 🔵 faer-fork 1.64× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 1.11624 ± 0.00925401 (W 0.0027854) | 1.33165 ± 0.0458119 (W 0.0136484) | 0.6713 ± 0.00548543 (W 0.00457226) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.66× slower than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n512/b1` | 4.97488 ± 0.0194816 (W 0.0115217) | 5.68204 ± 0.0267262 (W 0.0274122) | 3.4427 ± 0.0198408 (W 0.0112591) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.45× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 2.98793 ± 0.011057 (W 0.00344528) | 4.14196 ± 0.00558374 (W 0.00563179) | 3.53178 ± 0.00945596 (W 0.00495268) | 🔵 faer-fork 1.39× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `svd_thin/n256/b1` | 13.2814 ± 0.0302399 (W 0.0273793) | 21.9578 ± 0.303389 (W 0.0511004) | 16.8205 ± 0.0136492 (W 0.0297725) | 🔵 faer-fork 1.65× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 54.7969 ± 0.200413 (W 0.0791055) | 75.287 ± 0.574643 (W 0.213887) | 82.805 ± 0.0573055 (W 0.139663) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.42409 ± 0.0043486 (W 0.00340285) | 3.06643 ± 0.00275652 (W 0.00717212) | 1.86605 ± 0.00632244 (W 0.0105594) | 🔵 faer-fork 2.15× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 6.93258 ± 0.0254395 (W 0.0086706) | 16.843 ± 0.259581 (W 0.0309148) | 9.51016 ± 0.0399687 (W 0.0144966) | 🔵 faer-fork 2.43× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 31.271 ± 0.162849 (W 0.0507434) | 51.9314 ± 0.0908205 (W 0.0409863) | 42.6272 ± 0.0846338 (W 0.069665) | 🔵 faer-fork 1.66× faster than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.009227 ± 6e-05 (W 4.78884e-05) | 0.007444 ± 6.08276e-06 (W 3.30938e-05) | - | 🔴 faer-fork 1.24× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.02115 ± 0.000236432 (W 8.75625e-05) | 0.023473 ± 0.00036894 (W 0.000143073) | - | 🔵 faer-fork 1.11× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.050214 ± 0.000432421 (W 0.000279614) | 0.056977 ± 0.000997523 (W 0.00111963) | - | 🔵 faer-fork 1.13× faster than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-mid, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.177471 ± 0.000517523 (W 0.000382267) | 0.172451 ± 0.000799863 (W 0.00146891) | 0.40746 ± 0.00159689 (W 0.00338947) | · | 🔵 faer-fork 2.30× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 1.14159 ± 0.00525055 (W 0.0024124) | 1.12593 ± 0.00314565 (W 0.00242833) | 1.60148 ± 0.00552491 (W 0.00365385) | · | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `cholesky/n512/b1` | 7.55539 ± 0.0244621 (W 0.0063025) | 7.5224 ± 0.0217692 (W 0.00896717) | 10.6522 ± 0.800149 (W 0.0271165) | · | 🔵 faer-fork 1.41× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n128/b1` | 3.33923 ± 0.0034409 (W 0.00883685) | 3.26365 ± 0.012589 (W 0.00628744) | 4.32102 ± 0.0127915 (W 0.00736218) | · | 🔵 faer-fork 1.29× faster than `lapack-mkl` |  |
| `eigh/n256/b1` | 17.5785 ± 0.0789679 (W 0.0198173) | 17.3299 ± 0.084149 (W 0.0211271) | 26.1332 ± 0.0559257 (W 0.0419812) | · | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `eigh/n512/b1` | 106.818 ± 0.281902 (W 0.123674) | 105.233 ± 0.267773 (W 0.112398) | 170.155 ± 0.440774 (W 0.328967) | · | 🔵 faer-fork 1.59× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.774685 ± 0.00897104 (W 0.00460656) | 0.747333 ± 0.00471446 (W 0.00619906) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 5.80993 ± 0.0218773 (W 0.0105291) | 5.80384 ± 0.033509 (W 0.008575) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 40.0079 ± 0.146934 (W 0.0399215) | 39.877 ± 0.0454441 (W 0.0355916) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 1.03866 ± 0.00376324 (W 0.00212972) | 1.03429 ± 0.00644801 (W 0.00214444) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 1.04143 ± 0.00419474 (W 0.00162291) | 1.04379 ± 0.00371241 (W 0.0023761) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 7.43845 ± 0.0191463 (W 0.0143979) | 7.42003 ± 0.0368769 (W 0.00480112) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 7.49386 ± 0.0656492 (W 0.0232371) | 7.49537 ± 0.0601079 (W 0.0186222) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 56.5447 ± 0.283403 (W 0.115201) | 56.6093 ± 0.236185 (W 0.0721094) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 56.7804 ± 0.0825353 (W 0.0678089) | 56.8385 ± 0.0751241 (W 0.12866) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.300991 ± 0.00101743 (W 0.00264384) | 0.29531 ± 0.00107517 (W 0.00198475) | 0.44555 ± 0.00104519 (W 0.00353608) | · | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `lu/n256/b1` | 2.02607 ± 0.017381 (W 0.00371466) | 1.99912 ± 0.00450791 (W 0.00482981) | 3.07812 ± 0.0117395 (W 0.00603219) | · | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `lu/n512/b1` | 13.8346 ± 0.0444374 (W 0.0199444) | 13.8621 ± 0.0665055 (W 0.0305055) | 19.8447 ± 0.315244 (W 0.041161) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `qr/n128/b1` | 1.50895 ± 0.00517184 (W 0.00282546) | 1.55327 ± 0.00555129 (W 0.00528148) | 1.97802 ± 0.00369061 (W 0.00397363) | · | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 9.95843 ± 0.0411049 (W 0.0120369) | 10.1147 ± 0.0421924 (W 0.0165155) | 12.4548 ± 0.0759648 (W 0.0231949) | · | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 68.2673 ± 0.176909 (W 0.0677343) | 68.7735 ± 0.220472 (W 0.0561654) | 80.3296 ± 0.385621 (W 0.0502293) | · | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.699664 ± 0.00447247 (W 0.00172251) | 0.747954 ± 0.00366643 (W 0.00237854) | 0.908322 ± 0.00369681 (W 0.00462138) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 4.33551 ± 0.0361733 (W 0.00696528) | 4.50801 ± 0.0452393 (W 0.0107589) | 5.54435 ± 0.061181 (W 0.0117866) | · | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 28.3584 ± 0.107142 (W 0.0242803) | 29.0182 ± 0.155662 (W 0.0297285) | 38.211 ± 0.160211 (W 0.0683981) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.297043 ± 0.00159071 (W 0.00208828) | 0.292075 ± 0.00145665 (W 0.00251173) | 0.436624 ± 0.00554682 (W 0.00264782) | · | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 1.96024 ± 0.0139653 (W 0.00504428) | 1.94028 ± 0.00913131 (W 0.00297707) | 2.61302 ± 0.0227395 (W 0.0046018) | · | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `solve/n512/b1` | 13.9242 ± 0.0446466 (W 0.0146799) | 13.8633 ± 0.0248678 (W 0.0316654) | 17.2424 ± 0.209373 (W 0.033222) | · | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 5.28905 ± 0.0268235 (W 0.0254163) | 5.79196 ± 0.0220823 (W 0.00495617) | 6.89502 ± 0.00692072 (W 0.0156948) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `svd_thin/n256/b1` | 31.7645 ± 0.0197365 (W 0.0478036) | 34.5319 ± 0.0568243 (W 0.0507736) | 42.8992 ± 1.54539 (W 0.0603712) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/n512/b1` | 204.418 ± 0.466148 (W 0.642768) | 213.641 ± 0.369078 (W 0.442335) | 309.517 ± 5.10341 (W 0.563544) | · | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.72244 ± 0.019962 (W 0.00200782) | 3.53285 ± 0.0144257 (W 0.00371931) | 2.66405 ± 0.00878393 (W 0.00697267) | 🔵 faer-fork 2.05× faster than `faer-upstream` | 🔵 faer-fork 1.55× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 12.4758 ± 0.094725 (W 0.0317483) | 19.7186 ± 0.187153 (W 0.0511444) | 17.9125 ± 1.64109 (W 0.0215472) | 🔵 faer-fork 1.58× faster than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n512/b1` | 89.9386 ± 0.114516 (W 0.220199) | 113.608 ± 0.511068 (W 0.201335) | 153.818 ± 2.71164 (W 0.175939) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.007585 ± 0.000485553 (W 3.04171e-05) | 0.008145 ± 0.000175214 (W 3.28968e-05) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.024276 ± 0.00137483 (W 0.000168096) | 0.025378 ± 0.000282419 (W 6.96585e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n512/b1` | 0.083906 ± 0.00283565 (W 0.000387679) | 0.089747 ± 0.00194017 (W 0.0004707) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.149028 ± 0.00242053 (W 0.00255741) | 0.164807 ± 0.0032844 (W 0.00282625) | 0.405315 ± 0.00481103 (W 0.0030955) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 2.72× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.651755 ± 0.00481106 (W 0.00318444) | 0.714351 ± 0.00290888 (W 0.00493241) | 0.58527 ± 0.00577502 (W 0.00754995) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `cholesky/n512/b1` | 2.79076 ± 0.0108816 (W 0.00635455) | 3.02017 ± 0.0165069 (W 0.0736138) | 3.17281 ± 0.00833433 (W 0.0172339) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `eigh/n128/b1` | 2.58081 ± 0.00238218 (W 0.00638813) | 2.80599 ± 0.000351709 (W 0.00506932) | 1.94313 ± 0.00335147 (W 0.00522965) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.33× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 8.56376 ± 0.017293 (W 0.0104808) | 11.2751 ± 0.0115279 (W 0.0159899) | 9.82209 ± 0.0266222 (W 0.010551) | 🔵 faer-fork 1.32× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `eigh/n512/b1` | 39.0167 ± 0.027279 (W 0.0262595) | 44.7276 ± 0.0300765 (W 0.0310687) | 51.9762 ± 0.159709 (W 0.0420127) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.588908 ± 0.00852323 (W 0.00542254) | 0.747954 ± 0.00417403 (W 0.00358785) | - | 🔵 faer-fork 1.27× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 3.31315 ± 0.0131756 (W 0.00950119) | 5.74212 ± 0.0229751 (W 0.015274) | - | 🔵 faer-fork 1.73× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 16.7421 ± 0.0754358 (W 0.0300804) | 24.6026 ± 0.0767851 (W 0.0257481) | - | 🔵 faer-fork 1.47× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.285562 ± 0.00152531 (W 0.00204812) | 0.279205 ± 0.000823035 (W 0.00164668) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.287676 ± 0.000463023 (W 0.00261275) | 0.281018 ± 0.00100104 (W 0.00188524) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.92079 ± 0.00639801 (W 0.00280751) | 1.9081 ± 0.00277564 (W 0.00645351) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.92759 ± 0.00255359 (W 0.00419108) | 1.92647 ± 0.00411763 (W 0.00464679) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 14.6302 ± 0.0499738 (W 0.0223852) | 14.655 ± 0.0167395 (W 0.0231805) | - | · | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 14.6349 ± 0.0143285 (W 0.0312065) | 14.6847 ± 0.0452138 (W 0.0234499) | - | · | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.261849 ± 0.001314 (W 0.00282441) | 0.277707 ± 0.00293551 (W 0.0050874) | 0.444167 ± 0.00171142 (W 0.00324734) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.70× faster than `lapack-mkl` |  |
| `lu/n256/b1` | 1.19539 ± 0.0033021 (W 0.00295651) | 1.34149 ± 0.0175589 (W 0.0122626) | 0.967362 ± 0.00379401 (W 0.00440631) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.24× slower than `lapack-mkl` |  |
| `lu/n512/b1` | 5.7598 ± 0.0162614 (W 0.0096208) | 6.41587 ± 0.0652075 (W 0.0651974) | 5.78052 ± 0.0438208 (W 0.0122022) | 🔵 faer-fork 1.11× faster than `faer-upstream` | · |  |
| `qr/n128/b1` | 0.718609 ± 0.00278465 (W 0.0020763) | 1.0081 ± 0.00248231 (W 0.0106774) | 1.08317 ± 0.00389654 (W 0.00445889) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 3.12715 ± 0.0248914 (W 0.0100472) | 4.15694 ± 0.0134362 (W 0.00910343) | 5.10492 ± 0.010946 (W 0.0113339) | 🔵 faer-fork 1.33× faster than `faer-upstream` | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 19.7992 ± 0.0338795 (W 0.0154173) | 21.7146 ± 0.0349009 (W 0.0126405) | 29.0002 ± 0.274948 (W 0.0240847) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.46× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.406949 ± 0.00285766 (W 0.00278068) | 0.657927 ± 0.00218904 (W 0.00197152) | 0.451932 ± 0.00200961 (W 0.00202171) | 🔵 faer-fork 1.62× faster than `faer-upstream` | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 1.51618 ± 0.00292373 (W 0.00315771) | 2.55189 ± 0.00391924 (W 0.00471445) | 1.56953 ± 0.00387692 (W 0.00519774) | 🔵 faer-fork 1.68× faster than `faer-upstream` | · |  |
| `qr_factor/n512/b1` | 8.78221 ± 0.0504977 (W 0.0135186) | 10.7248 ± 0.0343434 (W 0.01906) | 10.8706 ± 0.0167359 (W 0.012561) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.258161 ± 0.00259845 (W 0.00299695) | 0.270084 ± 0.00444154 (W 0.00355985) | 0.433137 ± 0.0010969 (W 0.00338598) | · | 🔵 faer-fork 1.68× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 1.12218 ± 0.00211584 (W 0.00516881) | 1.24012 ± 0.0115461 (W 0.0166198) | 0.857919 ± 0.00105813 (W 0.00332822) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.31× slower than `lapack-mkl` |  |
| `solve/n512/b1` | 5.58919 ± 0.0206163 (W 0.00595229) | 6.27177 ± 0.0793099 (W 0.0801399) | 5.3636 ± 0.175389 (W 0.0197846) | 🔵 faer-fork 1.12× faster than `faer-upstream` | · | `!` between-start range over 5% |
| `svd_thin/n128/b1` | 3.15966 ± 0.00380181 (W 0.0102828) | 4.12823 ± 0.016643 (W 0.0136211) | 3.94718 ± 0.0155226 (W 0.00908333) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `svd_thin/n256/b1` | 14.9456 ± 0.0700095 (W 0.0322076) | 22.0425 ± 0.111547 (W 0.0371888) | 20.4905 ± 0.0191073 (W 0.0350465) | 🔵 faer-fork 1.47× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 72.7288 ± 0.187965 (W 0.0790046) | 87.4621 ± 0.0410896 (W 0.0682354) | 110.663 ± 1.16596 (W 0.0922731) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.3938 ± 0.0078697 (W 0.00302903) | 3.0315 ± 0.0046672 (W 0.00549358) | 1.9554 ± 0.00514873 (W 0.00875145) | 🔵 faer-fork 2.17× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 7.37138 ± 0.108761 (W 0.0100075) | 16.6548 ± 0.150925 (W 0.032833) | 10.8269 ± 0.0142438 (W 0.0220314) | 🔵 faer-fork 2.26× faster than `faer-upstream` | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 38.3356 ± 0.423594 (W 0.0565891) | 57.7669 ± 0.119129 (W 0.390381) | 54.9188 ± 0.201084 (W 0.0628823) | 🔵 faer-fork 1.51× faster than `faer-upstream` | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.008035 ± 5.2915e-05 (W 2.94143e-05) | 0.007995 ± 1.1547e-05 (W 3.57533e-05) | - | · | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.021781 ± 0.000166154 (W 0.000239915) | 0.025107 ± 0.000113725 (W 9.28127e-05) | - | 🔵 faer-fork 1.15× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.059721 ± 0.00294079 (W 0.000348347) | 0.066003 ± 0.00138853 (W 0.000469107) | - | 🔵 faer-fork 1.11× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n128/b1` | 0.141513 ± 0.00272916 (W 0.00293469) | 0.153388 ± 0.000369384 (W 0.00156373) | 0.409232 ± 0.00136813 (W 0.00310532) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 2.89× faster than `lapack-mkl` |  |
| `cholesky/n256/b1` | 0.590508 ± 0.00290778 (W 0.00566757) | 0.685287 ± 0.00512292 (W 0.0146822) | 0.462352 ± 0.00231437 (W 0.00262846) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔴 faer-fork 1.28× slower than `lapack-mkl` |  |
| `cholesky/n512/b1` | 2.23516 ± 0.0193364 (W 0.00412779) | 2.35818 ± 0.0117249 (W 0.0435821) | 1.87085 ± 0.101785 (W 0.0234713) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.19× slower than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n128/b1` | 2.46339 ± 0.00643704 (W 0.00268435) | 2.8052 ± 0.00970337 (W 0.00677469) | 1.60701 ± 0.00659107 (W 0.00530318) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.53× slower than `lapack-mkl` |  |
| `eigh/n256/b1` | 7.60432 ± 0.0258172 (W 0.00623135) | 11.052 ± 0.00275561 (W 0.02796) | 7.74852 ± 0.019404 (W 0.0182306) | 🔵 faer-fork 1.45× faster than `faer-upstream` | · |  |
| `eigh/n512/b1` | 30.3222 ± 0.0231745 (W 0.0235553) | 38.737 ± 0.101366 (W 0.222931) | 36.1641 ± 0.0708794 (W 0.0709137) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `full_piv_lu/n128/b1` | 0.567106 ± 0.00424438 (W 0.00520111) | 0.760176 ± 0.00345681 (W 0.00693858) | - | 🔵 faer-fork 1.34× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.986 ± 0.00687742 (W 0.0102048) | 5.79644 ± 0.0360659 (W 0.0124423) | - | 🔵 faer-fork 1.94× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 13.213 ± 0.0304115 (W 0.0153313) | 22.3659 ± 0.0278933 (W 0.0170713) | - | 🔵 faer-fork 1.69× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.178895 ± 0.000442267 (W 0.000996859) | 0.268803 ± 0.00165659 (W 0.00245385) | - | 🔵 faer-fork 1.50× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.179686 ± 0.000766722 (W 0.00181463) | 0.267328 ± 0.002683 (W 0.0024658) | - | 🔵 faer-fork 1.49× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.999773 ± 0.0022195 (W 0.00255246) | 1.30793 ± 0.0109799 (W 0.0808603) | - | 🔵 faer-fork 1.31× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.02553 ± 0.00940257 (W 0.00383582) | 1.3074 ± 0.0888531 (W 0.0962345) | - | 🔵 faer-fork 1.27× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 8.10866 ± 0.0633906 (W 0.119314) | 10.265 ± 1.45796 (W 1.24139) | - | 🔵 faer-fork 1.27× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 7.8342 ± 0.144015 (W 0.178126) | 10.1296 ± 1.3348 (W 1.15243) | - | 🔵 faer-fork 1.29× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/n128/b1` | 0.255907 ± 0.00440968 (W 0.00162786) | 0.264011 ± 0.00142411 (W 0.0021984) | 0.446167 ± 0.000680969 (W 0.00273289) | · | 🔵 faer-fork 1.74× faster than `lapack-mkl` |  |
| `lu/n256/b1` | 1.08053 ± 0.00598791 (W 0.00339449) | 1.25009 ± 0.00618791 (W 0.0067213) | 0.672223 ± 0.000743724 (W 0.00350443) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔴 faer-fork 1.61× slower than `lapack-mkl` |  |
| `lu/n512/b1` | 4.40915 ± 0.0228009 (W 0.0140973) | 4.9487 ± 0.0237847 (W 0.0246624) | 3.45973 ± 0.00720442 (W 0.00889534) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `qr/n128/b1` | 0.587946 ± 0.00101277 (W 0.00286857) | 1.11998 ± 0.00940763 (W 0.0040724) | 0.822473 ± 0.0012539 (W 0.00593447) | 🔵 faer-fork 1.90× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `qr/n256/b1` | 2.22698 ± 0.0112484 (W 0.00294802) | 4.16063 ± 0.0389342 (W 0.0330823) | 4.21284 ± 0.0201937 (W 0.0117533) | 🔵 faer-fork 1.87× faster than `faer-upstream` | 🔵 faer-fork 1.89× faster than `lapack-mkl` |  |
| `qr/n512/b1` | 10.941 ± 0.0189107 (W 0.00985036) | 18.1724 ± 0.189249 (W 0.300494) | 17.1997 ± 0.0581514 (W 0.0253282) | 🔵 faer-fork 1.66× faster than `faer-upstream` | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |
| `qr_factor/n128/b1` | 0.361052 ± 0.00212607 (W 0.00207197) | 0.751269 ± 0.00716816 (W 0.00505746) | 0.316363 ± 0.00148846 (W 0.00195847) | 🔵 faer-fork 2.08× faster than `faer-upstream` | 🔴 faer-fork 1.14× slower than `lapack-mkl` |  |
| `qr_factor/n256/b1` | 1.24503 ± 0.00322794 (W 0.0022732) | 2.67013 ± 0.0174809 (W 0.0145034) | 1.61752 ± 0.00355899 (W 0.00305039) | 🔵 faer-fork 2.14× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `qr_factor/n512/b1` | 4.73902 ± 0.00899211 (W 0.00853699) | 9.81527 ± 0.0428156 (W 0.134383) | 5.59939 ± 0.0272345 (W 0.00948603) | 🔵 faer-fork 2.07× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `solve/n128/b1` | 0.250557 ± 0.00175407 (W 0.00194197) | 0.252841 ± 0.0029534 (W 0.00290214) | 0.433493 ± 0.000894846 (W 0.00263656) | · | 🔵 faer-fork 1.73× faster than `lapack-mkl` |  |
| `solve/n256/b1` | 1.00684 ± 0.00662626 (W 0.00221477) | 1.1314 ± 0.00968643 (W 0.0123472) | 0.647384 ± 0.00523615 (W 0.00398796) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.56× slower than `lapack-mkl` |  |
| `solve/n512/b1` | 4.22623 ± 0.0202399 (W 0.00903439) | 4.75734 ± 0.0560363 (W 0.0282422) | 3.28874 ± 0.00821084 (W 0.00935352) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.29× slower than `lapack-mkl` |  |
| `svd_thin/n128/b1` | 2.97372 ± 0.00189577 (W 0.00858243) | 4.12266 ± 0.00314957 (W 0.00843834) | 3.47774 ± 0.0083241 (W 0.00684167) | 🔵 faer-fork 1.39× faster than `faer-upstream` | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |
| `svd_thin/n256/b1` | 12.912 ± 0.0571019 (W 0.0291655) | 21.7112 ± 0.138809 (W 0.0568843) | 16.6416 ± 0.0494202 (W 0.0135601) | 🔵 faer-fork 1.68× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` |  |
| `svd_thin/n512/b1` | 53.8017 ± 0.0593056 (W 0.0470658) | 74.2764 ± 0.149215 (W 0.280415) | 80.4819 ± 0.942811 (W 0.342177) | 🔵 faer-fork 1.38× faster than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `svd_values/n128/b1` | 1.40313 ± 0.00876679 (W 0.00415628) | 3.02346 ± 0.0122035 (W 0.0102358) | 1.86205 ± 0.0133436 (W 0.00422249) | 🔵 faer-fork 2.15× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `svd_values/n256/b1` | 6.76124 ± 0.0236363 (W 0.0164589) | 16.6051 ± 0.0563237 (W 0.0281214) | 9.50571 ± 0.0145028 (W 0.0181845) | 🔵 faer-fork 2.46× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `svd_values/n512/b1` | 30.3687 ± 0.13994 (W 0.0424933) | 50.9614 ± 0.0870564 (W 0.0478933) | 42.4584 ± 0.0997244 (W 0.30393) | 🔵 faer-fork 1.68× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `triangular_solve/n128/b1` | 0.008045 ± 0.000494975 (W 2.59673e-05) | 0.008035 ± 4.58258e-05 (W 2.04939e-05) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.020848 ± 0.000966433 (W 0.00014562) | 0.025097 ± 0.000352733 (W 0.00188756) | - | 🔵 faer-fork 1.20× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n512/b1` | 0.056055 ± 0.00180716 (W 0.000170154) | 0.063209 ± 0.000270785 (W 0.000364419) | - | 🔵 faer-fork 1.13× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

Not applicable to this population's shapes and reported as skipped: `eig/128`, `eig/256`, `eig/512`, `full_piv_lu/128`, `full_piv_lu/256`, `full_piv_lu/512`, `householder_apply/128`, `householder_apply/256`, `householder_apply/512`, `triangular_solve/128`, `triangular_solve/256`, `triangular_solve/512`, `upgrade_factor/128`, `upgrade_factor/256`, `upgrade_factor/512`.

## linalg-tall, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.816147 ± 0.000882461 (W 0.00475799) | 0.814747 ± 0.0112718 (W 0.00785802) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 49.1161 ± 0.22476 (W 0.127965) | 54.5813 ± 1.15753 (W 0.674601) | - | 🔵 faer-fork 1.11× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.551177 ± 0.00170899 (W 0.00256736) | 0.565193 ± 0.00787511 (W 0.00354075) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.551072 ± 0.00139571 (W 0.00331103) | 0.564832 ± 0.00238666 (W 0.00256283) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 35.0487 ± 0.180559 (W 0.0559299) | 35.0402 ± 0.224227 (W 0.0670984) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 35.0342 ± 0.142023 (W 0.026154) | 35.0796 ± 0.146263 (W 0.0452603) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.472544 ± 0.00359456 (W 0.00285431) | 0.473187 ± 0.00656712 (W 0.00512385) | 0.662089 ± 0.133739 (W 0.00513006) | · | 🔵 faer-fork 1.40× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/4096x256/b1` | 15.2769 ± 0.15778 (W 0.0516251) | 19.0011 ± 0.0463545 (W 0.0250147) | 18.5392 ± 2.6725 (W 0.0680772) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/1024x64/b1` | 1.42894 ± 0.00300531 (W 0.00445519) | 1.55155 ± 0.00369674 (W 0.00547864) | 1.87825 ± 0.0100555 (W 0.00510145) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 69.8586 ± 0.132286 (W 0.145193) | 74.4511 ± 0.0864756 (W 0.0943601) | 81.5868 ± 0.813804 (W 0.179486) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |
| `qr_factor/1024x64/b1` | 0.931195 ± 0.00309569 (W 0.00235692) | 1.86448 ± 0.0116721 (W 0.00602147) | 0.914432 ± 0.00529612 (W 0.00288198) | 🔵 faer-fork 2.00× faster than `faer-upstream` | · |  |
| `qr_factor/4096x256/b1` | 30.8101 ± 0.0296622 (W 0.0941427) | 77.9616 ± 0.0907949 (W 0.436335) | 34.9958 ± 0.033054 (W 0.106594) | 🔵 faer-fork 2.53× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 2.30501 ± 0.0106521 (W 0.0075669) | 2.49784 ± 0.0122327 (W 0.00628603) | 3.02761 ± 0.0183063 (W 0.00630639) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 85.7902 ± 0.30545 (W 0.18969) | 88.5125 ± 0.264724 (W 0.170071) | 120.072 ± 4.36427 (W 0.525586) | · | 🔵 faer-fork 1.40× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/1024x64/b1` | 1.04369 ± 0.00943933 (W 0.0039478) | 1.49185 ± 0.0041802 (W 0.006176) | 1.38347 ± 0.00567231 (W 0.00350821) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 38.452 ± 0.0741923 (W 0.0821793) | 44.903 ± 0.111001 (W 0.0632581) | 46.4997 ± 0.338449 (W 0.114566) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |

## linalg-tall, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.587979 ± 0.00548213 (W 0.00304979) | 0.816788 ± 0.000493135 (W 0.0071222) | - | 🔵 faer-fork 1.39× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 16.6704 ± 0.0590052 (W 0.102221) | 22.9259 ± 1.41405 (W 0.0656123) | - | 🔵 faer-fork 1.38× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.166472 ± 0.00270819 (W 0.00320155) | 0.156703 ± 0.00340094 (W 0.00102784) | - | 🔴 faer-fork 1.06× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.168375 ± 0.004093 (W 0.00182031) | 0.156994 ± 0.00367174 (W 0.00077257) | - | 🔴 faer-fork 1.07× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 9.48964 ± 0.0562103 (W 0.0284703) | 9.38841 ± 0.00161179 (W 0.046277) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 9.52904 ± 0.0138244 (W 0.0238307) | 9.43164 ± 0.0828791 (W 0.0562834) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.437047 ± 0.00292339 (W 0.00325572) | 0.43834 ± 0.00728147 (W 0.00183412) | 0.323896 ± 0.117092 (W 0.00260437) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/4096x256/b1` | 9.12326 ± 0.18827 (W 0.0280392) | 12.6876 ± 0.0312942 (W 0.0257902) | 16.9535 ± 2.02304 (W 0.0543521) | 🔵 faer-fork 1.39× faster than `faer-upstream` | 🔵 faer-fork 1.86× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/1024x64/b1` | 0.838889 ± 0.00234339 (W 0.00259157) | 1.20379 ± 0.00770492 (W 0.0317676) | 1.06107 ± 0.0111922 (W 0.010177) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 24.839 ± 2.82949 (W 0.18404) | 34.2626 ± 0.0675601 (W 0.0824572) | 30.1814 ± 0.243834 (W 0.119501) | 🔵 faer-fork 1.38× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 0.600513 ± 0.00612146 (W 0.00345519) | 3.17998 ± 0.171487 (W 0.144299) | 0.462344 ± 0.00531705 (W 0.00620572) | 🔵 faer-fork 5.30× faster than `faer-upstream` | 🔴 faer-fork 1.30× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 12.9222 ± 0.31903 (W 0.0284413) | 73.5787 ± 0.753325 (W 0.408534) | 12.7003 ± 0.139174 (W 0.0713806) | 🔵 faer-fork 5.69× faster than `faer-upstream` | · |  |
| `svd_thin/1024x64/b1` | 1.76626 ± 0.00903355 (W 0.00366456) | 2.1501 ± 0.00727295 (W 0.00446002) | 1.8777 ± 0.00362661 (W 0.0124799) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 39.9104 ± 0.109525 (W 0.0579142) | 47.4798 ± 0.297051 (W 0.236582) | 51.7116 ± 2.13395 (W 0.0510469) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/1024x64/b1` | 0.90933 ± 0.00612808 (W 0.00601497) | 1.54987 ± 0.00521167 (W 0.007865) | 0.946741 ± 0.00363132 (W 0.00666065) | 🔵 faer-fork 1.70× faster than `faer-upstream` | · |  |
| `svd_values/4096x256/b1` | 23.2166 ± 0.0465358 (W 0.0340999) | 32.7389 ± 0.0879921 (W 0.060246) | 22.5466 ± 0.102525 (W 0.120937) | 🔵 faer-fork 1.41× faster than `faer-upstream` | · |  |

## linalg-tall, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.583992 ± 0.00723806 (W 0.00957859) | 0.816395 ± 0.00487497 (W 0.00742451) | - | 🔵 faer-fork 1.40× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 11.8834 ± 0.0622109 (W 0.0426592) | 17.4868 ± 1.32129 (W 0.0911359) | - | 🔵 faer-fork 1.47× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.100097 ± 0.0015888 (W 0.00426403) | 0.141193 ± 0.00555956 (W 0.00686838) | - | 🔵 faer-fork 1.41× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.102761 ± 0.00123881 (W 0.00404284) | 0.131746 ± 0.00733595 (W 0.00676339) | - | 🔵 faer-fork 1.28× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 5.65158 ± 0.0577165 (W 0.0400121) | 5.06407 ± 0.867547 (W 0.877812) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 5.51928 ± 0.0981474 (W 0.115477) | 5.08099 ± 0.0209003 (W 0.710118) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.432128 ± 0.00448134 (W 0.00399603) | 0.439211 ± 0.00654091 (W 0.00398733) | 0.306593 ± 0.173064 (W 0.00196207) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/4096x256/b1` | 8.00162 ± 0.277136 (W 0.0142813) | 11.7561 ± 0.0204334 (W 0.0258162) | 7.27481 ± 1.89274 (W 0.0394699) | 🔵 faer-fork 1.47× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/1024x64/b1` | 0.742807 ± 0.00518407 (W 0.00352924) | 1.27661 ± 0.0357364 (W 0.0274679) | 0.886205 ± 0.00512722 (W 0.00444547) | 🔵 faer-fork 1.72× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 18.6591 ± 2.88687 (W 0.059062) | 32.9122 ± 0.677237 (W 0.544462) | 20.8523 ± 0.0981971 (W 0.0765829) | 🔵 faer-fork 1.76× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 0.561229 ± 0.017518 (W 0.00447805) | 3.09038 ± 0.182766 (W 0.183427) | 0.324837 ± 0.00168101 (W 0.00301579) | 🔵 faer-fork 5.51× faster than `faer-upstream` | 🔴 faer-fork 1.73× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 9.61648 ± 0.369592 (W 0.027515) | 71.4849 ± 0.181423 (W 0.254845) | 7.26173 ± 0.0530588 (W 0.0361632) | 🔵 faer-fork 7.43× faster than `faer-upstream` | 🔴 faer-fork 1.32× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 1.6708 ± 0.00721093 (W 0.00487771) | 2.24399 ± 0.00860326 (W 0.00848767) | 1.66084 ± 0.00404686 (W 0.00467319) | 🔵 faer-fork 1.34× faster than `faer-upstream` | · |  |
| `svd_thin/4096x256/b1` | 33.7091 ± 1.64531 (W 0.0407581) | 46.2148 ± 0.233889 (W 0.212363) | 39.7934 ± 2.14055 (W 0.0966965) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/1024x64/b1` | 0.900604 ± 0.0092728 (W 0.00274333) | 1.62043 ± 0.0106967 (W 0.00675541) | 0.804735 ± 0.00314224 (W 0.0038223) | 🔵 faer-fork 1.80× faster than `faer-upstream` | 🔴 faer-fork 1.12× slower than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 20.7114 ± 0.0182152 (W 0.0341538) | 33.5536 ± 0.137803 (W 0.117364) | 16.818 ± 0.0207125 (W 0.0643408) | 🔵 faer-fork 1.62× faster than `faer-upstream` | 🔴 faer-fork 1.23× slower than `lapack-mkl` |  |

## linalg-tall, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.734686 ± 0.00210694 (W 0.00335829) | 0.734168 ± 0.0107243 (W 0.0015567) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 46.9216 ± 0.233637 (W 0.200962) | 47.0288 ± 0.262161 (W 0.0577163) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.594664 ± 0.00579894 (W 0.00286757) | 0.59315 ± 0.00276656 (W 0.00223703) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.603324 ± 0.0203089 (W 0.00255679) | 0.588476 ± 0.0110183 (W 0.00174144) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 35.7567 ± 0.133131 (W 0.0488191) | 35.6074 ± 0.13184 (W 0.0418141) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 35.679 ± 0.0949717 (W 0.0612883) | 35.7061 ± 0.0755996 (W 0.408978) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.38429 ± 0.000542031 (W 0.00316375) | 0.388444 ± 0.00201311 (W 0.0035367) | 0.28274 ± 0.00316416 (W 0.00251771) | · | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |
| `lu/4096x256/b1` | 13.2781 ± 0.0100503 (W 0.0318982) | 13.3093 ± 0.0271956 (W 0.0455993) | 11.8779 ± 0.104682 (W 0.0117217) | · | 🔴 faer-fork 1.12× slower than `lapack-mkl` |  |
| `qr/1024x64/b1` | 1.3134 ± 0.00584473 (W 0.00537153) | 1.46363 ± 0.00787188 (W 0.00380997) | 1.58202 ± 0.00429873 (W 0.00459178) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 67.4115 ± 0.220176 (W 0.0656796) | 68.857 ± 0.0792476 (W 0.103945) | 70.0945 ± 0.0195293 (W 0.172498) | · | · |  |
| `qr_factor/1024x64/b1` | 0.625 ± 0.0236654 (W 0.00442974) | 0.781593 ± 0.0112494 (W 0.00310913) | 0.76938 ± 0.0021509 (W 0.0023514) | 🔵 faer-fork 1.25× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 24.7831 ± 0.139227 (W 0.0412939) | 25.9196 ± 0.186261 (W 0.0341783) | 29.1259 ± 0.0905113 (W 0.0850655) | · | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 2.25043 ± 0.0037358 (W 0.00557882) | 2.4529 ± 0.00738135 (W 0.00257528) | 2.81277 ± 0.0138495 (W 0.00630653) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 80.3888 ± 0.284163 (W 0.234561) | 83.0238 ± 0.097348 (W 0.259035) | 109.327 ± 0.546793 (W 0.0690326) | · | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 0.956241 ± 0.00697101 (W 0.00395037) | 1.39943 ± 0.00593798 (W 0.00460967) | 1.23554 ± 0.00140057 (W 0.00290215) | 🔵 faer-fork 1.46× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 32.5552 ± 0.0661673 (W 0.0679194) | 39.0782 ± 0.111849 (W 0.0267087) | 40.221 ± 0.197892 (W 0.0568902) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |

## linalg-tall, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.511837 ± 0.00460058 (W 0.0064893) | 0.731999 ± 0.00760985 (W 0.00869805) | - | 🔵 faer-fork 1.43× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 14.5639 ± 0.067211 (W 0.0293418) | 14.9764 ± 0.083637 (W 0.031605) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.203401 ± 0.00201836 (W 0.00105841) | 0.198271 ± 0.0036159 (W 0.00174262) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.204813 ± 0.000357823 (W 0.000967983) | 0.199022 ± 0.00220724 (W 0.00241347) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 10.8673 ± 0.211062 (W 0.0143211) | 10.8412 ± 0.182312 (W 0.0166962) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 11.1683 ± 0.170719 (W 0.00923694) | 11.1022 ± 0.133022 (W 0.0276821) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.352589 ± 0.00300597 (W 0.00242671) | 0.356186 ± 0.00109942 (W 0.00215875) | 0.284812 ± 0.003435 (W 0.00269315) | · | 🔴 faer-fork 1.24× slower than `lapack-mkl` |  |
| `lu/4096x256/b1` | 6.96176 ± 0.0436126 (W 0.0297181) | 7.03442 ± 0.024795 (W 0.0222453) | 11.6856 ± 0.0054722 (W 0.0193801) | · | 🔵 faer-fork 1.68× faster than `lapack-mkl` |  |
| `qr/1024x64/b1` | 0.728712 ± 0.00542299 (W 0.00256645) | 1.11385 ± 0.0351027 (W 0.0352205) | 0.98427 ± 0.00184248 (W 0.00787992) | 🔵 faer-fork 1.53× faster than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/4096x256/b1` | 22.1682 ± 2.86232 (W 0.0364718) | 28.121 ± 0.0182249 (W 0.0600617) | 26.825 ± 0.112222 (W 0.105328) | 🔵 faer-fork 1.27× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 0.490888 ± 0.0201637 (W 0.00233568) | 0.821386 ± 0.0143585 (W 0.00487636) | 0.414835 ± 0.00716633 (W 0.0048717) | 🔵 faer-fork 1.67× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 10.4064 ± 0.241643 (W 0.0159392) | 15.1213 ± 0.212118 (W 0.0278424) | 11.2795 ± 0.0294125 (W 0.0914088) | 🔵 faer-fork 1.45× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 1.71426 ± 0.00625363 (W 0.00454562) | 2.10242 ± 0.0058966 (W 0.00548513) | 1.79955 ± 0.00527575 (W 0.00577881) | 🔵 faer-fork 1.23× faster than `faer-upstream` | · |  |
| `svd_thin/4096x256/b1` | 34.3814 ± 0.166435 (W 0.0693638) | 42.2368 ± 0.297196 (W 0.0987079) | 45.079 ± 0.108347 (W 0.0469085) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 0.831515 ± 0.00343206 (W 0.0019374) | 1.45764 ± 0.00660832 (W 0.00451075) | 0.905804 ± 0.0072048 (W 0.00769479) | 🔵 faer-fork 1.75× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 17.4259 ± 0.0526715 (W 0.0279225) | 26.9645 ± 0.00631042 (W 0.0376637) | 20.692 ± 0.1104 (W 0.0904603) | 🔵 faer-fork 1.55× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |

## linalg-tall, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.491048 ± 0.00202117 (W 0.00324714) | 0.730996 ± 0.00192872 (W 0.00484765) | - | 🔵 faer-fork 1.49× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 9.85844 ± 0.0951069 (W 0.0253268) | 10.4021 ± 0.0562025 (W 0.0469573) | - | 🔵 faer-fork 1.06× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.127639 ± 0.00252108 (W 0.00113063) | 0.185547 ± 0.00330632 (W 0.00653271) | - | 🔵 faer-fork 1.45× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.131786 ± 0.00295355 (W 0.00169539) | 0.18195 ± 0.00740391 (W 0.00755117) | - | 🔵 faer-fork 1.38× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 8.60757 ± 0.100136 (W 0.0356359) | 6.96561 ± 0.749051 (W 0.631829) | - | 🔴 faer-fork 1.24× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 8.91695 ± 0.105941 (W 0.0201355) | 7.05441 ± 0.633899 (W 0.688848) | - | 🔴 faer-fork 1.26× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/1024x64/b1` | 0.346398 ± 0.00114544 (W 0.00312976) | 0.356457 ± 0.00236348 (W 0.00436227) | 0.279953 ± 0.00351327 (W 0.00231716) | · | 🔴 faer-fork 1.24× slower than `lapack-mkl` |  |
| `lu/4096x256/b1` | 6.03941 ± 0.0158613 (W 0.016028) | 6.14961 ± 0.0133476 (W 0.027097) | 3.12484 ± 0.0148616 (W 0.0168454) | · | 🔴 faer-fork 1.93× slower than `lapack-mkl` |  |
| `qr/1024x64/b1` | 0.637271 ± 0.00294821 (W 0.00471875) | 1.15517 ± 0.00785332 (W 0.0272644) | 0.848264 ± 0.00481127 (W 0.00591382) | 🔵 faer-fork 1.81× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 16.4546 ± 2.73231 (W 0.0578176) | 27.2037 ± 1.89301 (W 0.780037) | 19.2744 ± 0.0497353 (W 0.0498046) | 🔵 faer-fork 1.65× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 0.471011 ± 0.019505 (W 0.00339352) | 0.916833 ± 0.00750908 (W 0.0042297) | 0.301122 ± 0.000919708 (W 0.00295183) | 🔵 faer-fork 1.95× faster than `faer-upstream` | 🔴 faer-fork 1.56× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 8.1165 ± 0.267112 (W 0.0403179) | 16.047 ± 0.133921 (W 0.0714855) | 6.46683 ± 0.032265 (W 0.0431234) | 🔵 faer-fork 1.98× faster than `faer-upstream` | 🔴 faer-fork 1.26× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 1.62 ± 0.00232273 (W 0.00328006) | 2.1804 ± 0.00625775 (W 0.00630486) | 1.63333 ± 0.0141869 (W 0.0114586) | 🔵 faer-fork 1.35× faster than `faer-upstream` | · |  |
| `svd_thin/4096x256/b1` | 28.3733 ± 0.134094 (W 0.0509983) | 40.9179 ± 0.362291 (W 0.292913) | 34.2734 ± 0.0245771 (W 0.0814795) | 🔵 faer-fork 1.44× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 0.812609 ± 0.00411535 (W 0.00311896) | 1.53611 ± 0.00342714 (W 0.00518577) | 0.779987 ± 0.00327281 (W 0.00364559) | 🔵 faer-fork 1.89× faster than `faer-upstream` | · |  |
| `svd_values/4096x256/b1` | 15.0097 ± 0.0625027 (W 0.0215052) | 27.7157 ± 0.0371633 (W 0.0746061) | 15.8651 ± 0.137366 (W 0.043687) | 🔵 faer-fork 1.85× faster than `faer-upstream` | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |

## linalg-tall, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 1.78123 ± 0.00553782 (W 0.00701164) | 1.84499 ± 0.00492565 (W 0.00576135) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 149.453 ± 1.12065 (W 0.94679) | 156.906 ± 1.66746 (W 0.533675) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 2.198 ± 0.0316189 (W 0.00688883) | 2.23336 ± 0.00555481 (W 0.00496203) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 2.19596 ± 0.0016725 (W 0.00593794) | 2.19956 ± 0.0229224 (W 0.00437861) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 137.369 ± 0.0489359 (W 0.153602) | 137.31 ± 0.236001 (W 0.420422) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 137.559 ± 0.0602492 (W 0.333757) | 137.214 ± 0.193906 (W 0.119724) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.998558 ± 0.00339986 (W 0.00122566) | 1.01227 ± 0.00728221 (W 0.00658413) | 1.13115 ± 0.0125095 (W 0.00710839) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `lu/4096x256/b1` | 46.7214 ± 0.36374 (W 0.156992) | 53.8871 ± 0.109649 (W 0.0704035) | 55.1537 ± 5.47875 (W 0.347486) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/1024x64/b1` | 4.52429 ± 0.00520464 (W 0.00755806) | 4.73987 ± 0.0190635 (W 0.00929584) | 5.16996 ± 0.0475411 (W 0.0119441) | · | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 247.186 ± 0.51622 (W 0.298723) | 256.01 ± 0.240494 (W 0.450539) | 227.951 ± 5.65611 (W 0.579921) | · | 🔴 faer-fork 1.08× slower than `lapack-mkl` |  |
| `qr_factor/1024x64/b1` | 2.28748 ± 0.0146151 (W 0.00618001) | 4.07939 ± 0.0698572 (W 0.0148758) | 2.38688 ± 0.0119093 (W 0.0056123) | 🔵 faer-fork 1.78× faster than `faer-upstream` | · |  |
| `qr_factor/4096x256/b1` | 97.545 ± 0.543241 (W 0.120577) | 175.658 ± 0.574136 (W 0.409606) | 109.882 ± 0.171564 (W 0.29726) | 🔵 faer-fork 1.80× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 5.70477 ± 0.0453094 (W 0.0102891) | 5.97425 ± 0.0288921 (W 0.0105398) | 8.71896 ± 0.0345253 (W 0.0205622) | · | 🔵 faer-fork 1.53× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 275.638 ± 1.03717 (W 2.58134) | 281.711 ± 0.0853785 (W 0.499338) | 378.226 ± 0.887983 (W 0.445633) | · | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 2.55822 ± 0.00719839 (W 0.00620262) | 3.08444 ± 0.0222262 (W 0.00629516) | 3.86967 ± 0.0406976 (W 0.00991974) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 113.956 ± 0.55333 (W 0.424907) | 123.157 ± 0.78664 (W 0.450992) | 145.044 ± 6.46534 (W 0.250697) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` | `!` between-start range over 5% |

## linalg-tall, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.94078 ± 0.0071501 (W 0.00303313) | 1.83136 ± 0.0100585 (W 0.0067531) | - | 🔵 faer-fork 1.95× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 52.1459 ± 0.167157 (W 0.192925) | 64.3167 ± 0.201364 (W 0.887846) | - | 🔵 faer-fork 1.23× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.592827 ± 0.00317256 (W 0.00340344) | 0.589512 ± 0.00360495 (W 0.00256138) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.591576 ± 0.00317939 (W 0.00224496) | 0.584472 ± 0.00299767 (W 0.00318531) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 37.0031 ± 0.086312 (W 0.0689585) | 36.8677 ± 0.0431679 (W 0.0744367) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 37.0336 ± 0.211909 (W 0.0636369) | 36.9725 ± 0.0987184 (W 0.0451204) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.758107 ± 0.0021645 (W 0.00247376) | 0.751204 ± 0.0147982 (W 0.0028616) | 1.00702 ± 0.00853703 (W 0.00114673) | · | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `lu/4096x256/b1` | 22.7088 ± 0.0353008 (W 0.105528) | 29.4957 ± 0.139999 (W 0.0556096) | 58.1897 ± 0.818797 (W 0.163685) | 🔵 faer-fork 1.30× faster than `faer-upstream` | 🔵 faer-fork 2.56× faster than `lapack-mkl` |  |
| `qr/1024x64/b1` | 1.98591 ± 0.00447715 (W 0.00329913) | 2.45882 ± 0.0373904 (W 0.0428234) | 3.11822 ± 0.00208453 (W 0.00506713) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 89.0918 ± 0.165376 (W 0.427271) | 96.3804 ± 5.44702 (W 0.314995) | 86.6705 ± 0.57714 (W 0.868721) | 🔵 faer-fork 1.08× faster than `faer-upstream` | · | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 1.2635 ± 0.00811826 (W 0.00641071) | 4.22007 ± 0.0851332 (W 0.078281) | 1.40281 ± 0.00235763 (W 0.00408328) | 🔵 faer-fork 3.34× faster than `faer-upstream` | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `qr_factor/4096x256/b1` | 36.3684 ± 0.152994 (W 0.121939) | 127.334 ± 0.236564 (W 0.741276) | 33.8946 ± 0.116888 (W 0.224655) | 🔵 faer-fork 3.50× faster than `faer-upstream` | 🔴 faer-fork 1.07× slower than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 3.09208 ± 0.00540261 (W 0.0064842) | 3.6858 ± 0.0139872 (W 0.00520467) | 5.47195 ± 0.0174324 (W 0.0145281) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 1.77× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 102.319 ± 0.207072 (W 2.02358) | 118.891 ± 0.0666442 (W 0.0855259) | 140.224 ± 0.239626 (W 0.4033) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 1.70305 ± 0.00500316 (W 0.00384305) | 2.44573 ± 0.0262376 (W 0.00438479) | 2.845 ± 0.00348305 (W 0.0369695) | 🔵 faer-fork 1.44× faster than `faer-upstream` | 🔵 faer-fork 1.67× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 53.6926 ± 0.100044 (W 0.114573) | 72.3989 ± 1.28272 (W 0.0617804) | 59.9831 ± 5.0237 (W 0.261916) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.12× faster than `lapack-mkl` | `!` between-start range over 5% |

## linalg-tall, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.831052 ± 0.0148194 (W 0.00333562) | 1.83904 ± 0.0141893 (W 0.00542869) | - | 🔵 faer-fork 2.21× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 28.5519 ± 0.206656 (W 0.212392) | 39.9986 ± 0.609779 (W 0.879358) | - | 🔵 faer-fork 1.40× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.315278 ± 0.00358438 (W 0.00326763) | 0.471962 ± 0.0440414 (W 0.0348036) | - | 🔵 faer-fork 1.50× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.31593 ± 0.00503133 (W 0.00503036) | 0.469517 ± 0.0481602 (W 0.0418874) | - | 🔵 faer-fork 1.49× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 23.9718 ± 0.449741 (W 0.169042) | 18.9614 ± 3.51328 (W 3.48495) | - | 🔴 faer-fork 1.26× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 24.0351 ± 0.344116 (W 0.0739091) | 24.8934 ± 3.65452 (W 3.46455) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/1024x64/b1` | 0.709725 ± 0.00167907 (W 0.00260528) | 0.698353 ± 0.027864 (W 0.00622497) | 0.988166 ± 0.00576481 (W 0.00405829) | · | 🔵 faer-fork 1.39× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/4096x256/b1` | 18.2036 ± 0.124195 (W 0.137177) | 25.3979 ± 0.112568 (W 0.0721781) | 56.3087 ± 0.220237 (W 0.100496) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔵 faer-fork 3.09× faster than `lapack-mkl` |  |
| `qr/1024x64/b1` | 1.61389 ± 0.0117773 (W 0.00645675) | 2.42958 ± 0.0234705 (W 0.047823) | 2.32377 ± 0.00302371 (W 0.00428553) | 🔵 faer-fork 1.51× faster than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 66.1377 ± 0.379856 (W 0.0768573) | 84.5436 ± 2.29941 (W 2.14254) | 51.6651 ± 0.216255 (W 0.226073) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔴 faer-fork 1.28× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 1.11667 ± 0.0222424 (W 0.00496251) | 4.07093 ± 0.0212743 (W 0.0864605) | 0.880336 ± 0.000893179 (W 0.00346693) | 🔵 faer-fork 3.65× faster than `faer-upstream` | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `qr_factor/4096x256/b1` | 26.6712 ± 0.0367574 (W 0.0695511) | 123.55 ± 0.743357 (W 0.829132) | 19.582 ± 0.142826 (W 0.0729258) | 🔵 faer-fork 4.63× faster than `faer-upstream` | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 2.71501 ± 0.0157243 (W 0.00716966) | 3.66811 ± 0.0241464 (W 0.0197995) | 4.44797 ± 0.0029409 (W 0.00914357) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.64× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 77.5989 ± 0.158101 (W 0.103438) | 106.638 ± 0.427648 (W 0.999406) | 83.8977 ± 3.72228 (W 0.536935) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/1024x64/b1` | 1.58781 ± 0.00827986 (W 0.00623475) | 2.48928 ± 0.0175627 (W 0.0107199) | 2.34792 ± 0.00476275 (W 0.0114562) | 🔵 faer-fork 1.57× faster than `faer-upstream` | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 44.648 ± 0.0558443 (W 0.0566426) | 69.8264 ± 0.572741 (W 0.626218) | 42.1711 ± 4.72923 (W 0.144322) | 🔵 faer-fork 1.56× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |

## linalg-tall, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 1.66269 ± 0.000252703 (W 0.00454888) | 1.69119 ± 0.00299664 (W 0.00296408) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 143.621 ± 0.517293 (W 0.806363) | 145.446 ± 0.847561 (W 0.69867) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 2.25336 ± 0.0107894 (W 0.0039377) | 2.24848 ± 0.0256011 (W 0.00948713) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 2.27877 ± 0.0128916 (W 0.00380684) | 2.27661 ± 0.0118201 (W 0.00627163) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 137.882 ± 0.465876 (W 0.134871) | 138.113 ± 0.0640814 (W 0.135315) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 138.226 ± 0.177543 (W 0.196316) | 138.133 ± 0.172182 (W 0.0999306) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.883085 ± 0.00406906 (W 0.00188985) | 0.881091 ± 0.00329028 (W 0.00234714) | 0.995852 ± 0.0182191 (W 0.00233608) | · | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `lu/4096x256/b1` | 41.7184 ± 0.0933542 (W 0.0878668) | 41.6865 ± 0.0943181 (W 0.0461909) | 47.8481 ± 0.403849 (W 0.0839649) | · | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `qr/1024x64/b1` | 4.40201 ± 0.00856307 (W 0.0148616) | 4.61613 ± 0.0185068 (W 0.014899) | 4.86434 ± 0.00880932 (W 0.00786783) | · | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 240.598 ± 0.188598 (W 0.444465) | 244.315 ± 0.526445 (W 0.426627) | 215.953 ± 0.716543 (W 0.492608) | · | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `qr_factor/1024x64/b1` | 2.01354 ± 0.0393146 (W 0.00247447) | 2.25388 ± 0.017964 (W 0.00357379) | 2.24965 ± 0.0167213 (W 0.00749271) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 1.12× faster than `lapack-mkl` |  |
| `qr_factor/4096x256/b1` | 86.3005 ± 0.754679 (W 0.0660975) | 89.1765 ± 0.51503 (W 0.0708806) | 103.654 ± 0.0379199 (W 0.173866) | · | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 5.62424 ± 0.0275143 (W 0.0191353) | 5.88162 ± 0.0131581 (W 0.0129275) | 8.50143 ± 0.0562752 (W 0.0204274) | · | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 263.15 ± 0.175266 (W 0.212654) | 269.574 ± 0.129411 (W 0.474962) | 357.373 ± 6.44172 (W 0.708706) | · | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 2.42797 ± 0.0138141 (W 0.00658569) | 2.96801 ± 0.0189934 (W 0.00600557) | 3.67372 ± 0.027867 (W 0.0088567) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 101.712 ± 0.124367 (W 0.184213) | 110.657 ± 0.13079 (W 0.0864616) | 138.358 ± 2.59667 (W 0.358518) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |

## linalg-tall, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.832637 ± 0.00738351 (W 0.00309079) | 1.67908 ± 0.0053374 (W 0.00387633) | - | 🔵 faer-fork 2.02× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 46.6493 ± 0.356946 (W 0.213657) | 49.2951 ± 0.345012 (W 0.327703) | - | 🔵 faer-fork 1.06× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.64256 ± 0.00126208 (W 0.00308776) | 0.635738 ± 0.00722351 (W 0.00276264) | - | · | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.643893 ± 0.00812582 (W 0.00365725) | 0.624406 ± 0.0102188 (W 0.0030297) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 39.3543 ± 0.168964 (W 0.151463) | 39.5244 ± 0.0697743 (W 0.0405716) | - | · | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 39.5863 ± 0.224763 (W 0.0988355) | 39.5783 ± 0.130251 (W 0.103841) | - | · | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.646278 ± 0.00373178 (W 0.00306309) | 0.651788 ± 0.000322274 (W 0.00562594) | 0.982508 ± 0.00363791 (W 0.00177642) | · | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `lu/4096x256/b1` | 17.2399 ± 0.0369817 (W 0.0335837) | 17.3537 ± 0.0886232 (W 0.0353434) | 48.389 ± 0.590601 (W 0.200518) | · | 🔵 faer-fork 2.81× faster than `lapack-mkl` |  |
| `qr/1024x64/b1` | 1.86532 ± 0.00560143 (W 0.00510576) | 2.3723 ± 0.0511042 (W 0.0398359) | 3.04537 ± 0.00789799 (W 0.00765723) | 🔵 faer-fork 1.27× faster than `faer-upstream` | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 82.8775 ± 0.180217 (W 0.138506) | 83.861 ± 6.08166 (W 0.28456) | 74.5534 ± 0.151824 (W 0.403185) | · | 🔴 faer-fork 1.11× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 1.11144 ± 0.006584 (W 0.00370031) | 1.56507 ± 0.001376 (W 0.0070046) | 1.35922 ± 0.00540251 (W 0.00478239) | 🔵 faer-fork 1.41× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `qr_factor/4096x256/b1` | 31.4529 ± 0.210844 (W 0.075474) | 41.0478 ± 0.0830777 (W 0.0402593) | 31.2808 ± 0.25158 (W 0.025628) | 🔵 faer-fork 1.31× faster than `faer-upstream` | · |  |
| `svd_thin/1024x64/b1` | 2.98611 ± 0.0132921 (W 0.00948426) | 3.57256 ± 0.0116743 (W 0.00924368) | 5.39324 ± 0.0172761 (W 0.00761467) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.81× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 90.2377 ± 0.138241 (W 0.139338) | 106.996 ± 0.221011 (W 0.146072) | 129.004 ± 0.567308 (W 0.445553) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `svd_values/1024x64/b1` | 1.61387 ± 0.00266978 (W 0.00598516) | 2.36217 ± 0.00304083 (W 0.00534975) | 2.78725 ± 0.00764665 (W 0.00810234) | 🔵 faer-fork 1.46× faster than `faer-upstream` | 🔵 faer-fork 1.73× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 41.6245 ± 0.1961 (W 0.118013) | 60.1048 ± 0.125235 (W 0.0710256) | 49.1237 ± 0.495985 (W 0.265203) | 🔵 faer-fork 1.44× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |

## linalg-tall, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.711468 ± 0.00498077 (W 0.00247782) | 1.69187 ± 0.00537896 (W 0.0034574) | - | 🔵 faer-fork 2.38× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 23.7846 ± 0.102482 (W 0.0948797) | 27.2106 ± 0.162984 (W 0.18352) | - | 🔵 faer-fork 1.14× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.395388 ± 0.00551269 (W 0.00433764) | 0.526753 ± 0.0438965 (W 0.0443823) | - | 🔵 faer-fork 1.33× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.367997 ± 0.00825705 (W 0.00288722) | 0.453737 ± 0.0381911 (W 0.0410894) | - | 🔵 faer-fork 1.23× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 24.6336 ± 0.375697 (W 0.53567) | 26.3467 ± 0.0780158 (W 0.16506) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 25.1091 ± 0.922935 (W 1.08598) | 26.3939 ± 0.107023 (W 0.108063) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/1024x64/b1` | 0.602726 ± 0.00201664 (W 0.00290119) | 0.608766 ± 0.00395975 (W 0.00472926) | 0.982183 ± 0.0103456 (W 0.0023731) | · | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `lu/4096x256/b1` | 13.2567 ± 0.0167913 (W 0.0177077) | 13.3747 ± 0.0816261 (W 0.0317898) | 49.0075 ± 0.6623 (W 0.0730461) | · | 🔵 faer-fork 3.70× faster than `lapack-mkl` |  |
| `qr/1024x64/b1` | 1.48977 ± 0.00435895 (W 0.00603587) | 2.29907 ± 0.0234251 (W 0.0300541) | 2.29632 ± 0.00457973 (W 0.00486429) | 🔵 faer-fork 1.54× faster than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` |  |
| `qr/4096x256/b1` | 59.8612 ± 0.0928499 (W 0.0944535) | 75.9057 ± 2.53749 (W 2.21454) | 42.4345 ± 0.7314 (W 0.434192) | 🔵 faer-fork 1.27× faster than `faer-upstream` | 🔴 faer-fork 1.41× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 1.00295 ± 0.00733199 (W 0.00405919) | 1.60826 ± 0.00374998 (W 0.0056096) | 0.858455 ± 0.00479607 (W 0.00167934) | 🔵 faer-fork 1.60× faster than `faer-upstream` | 🔴 faer-fork 1.17× slower than `lapack-mkl` |  |
| `qr_factor/4096x256/b1` | 23.1739 ± 0.398254 (W 0.0590655) | 39.1675 ± 0.634124 (W 0.463628) | 17.7547 ± 0.192233 (W 0.153081) | 🔵 faer-fork 1.69× faster than `faer-upstream` | 🔴 faer-fork 1.31× slower than `lapack-mkl` |  |
| `svd_thin/1024x64/b1` | 2.61363 ± 0.00908656 (W 0.0209199) | 3.55383 ± 0.00516719 (W 0.0276672) | 4.40217 ± 0.00861195 (W 0.0101013) | 🔵 faer-fork 1.36× faster than `faer-upstream` | 🔵 faer-fork 1.68× faster than `lapack-mkl` |  |
| `svd_thin/4096x256/b1` | 65.2579 ± 0.111008 (W 0.0752685) | 94.1635 ± 1.27013 (W 1.31092) | 73.8289 ± 7.33106 (W 0.278708) | 🔵 faer-fork 1.44× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/1024x64/b1` | 1.51821 ± 0.00439358 (W 0.00364474) | 2.39926 ± 0.00629329 (W 0.0136538) | 2.31576 ± 0.00812159 (W 0.00470619) | 🔵 faer-fork 1.58× faster than `faer-upstream` | 🔵 faer-fork 1.53× faster than `lapack-mkl` |  |
| `svd_values/4096x256/b1` | 32.8643 ± 0.101357 (W 0.0815139) | 57.6664 ± 0.349763 (W 0.369917) | 32.4114 ± 0.347943 (W 0.147967) | 🔵 faer-fork 1.75× faster than `faer-upstream` | · |  |

Not applicable to this population's shapes and reported as skipped: `cholesky/1024x64`, `cholesky/4096x256`, `eigh/1024x64`, `eigh/4096x256`, `full_piv_lu/1024x64`, `full_piv_lu/4096x256`, `householder_apply/1024x64`, `householder_apply/4096x256`, `solve/1024x64`, `solve/4096x256`, `triangular_solve/1024x64`, `triangular_solve/4096x256`, `upgrade_factor/1024x64`, `upgrade_factor/4096x256`.

## linalg-wide, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 74.9533 ± 0.163802 (W 0.146188) | 76.9069 ± 0.827472 (W 0.216454) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.12047 ± 0.0118954 (W 0.00585805) | 1.25422 ± 0.0137325 (W 0.00659113) | - | 🔵 faer-fork 1.12× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 15.9396 ± 0.222726 (W 0.0399648) | 17.8123 ± 0.188151 (W 0.0430105) | 27.571 ± 3.10121 (W 0.167636) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 1.73× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/64x1024/b1` | 0.39592 ± 0.000796295 (W 0.00240504) | 0.511505 ± 0.000442119 (W 0.00379767) | 0.631369 ± 0.00117279 (W 0.0055305) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.59× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 30.5295 ± 0.0578696 (W 0.0927851) | 31.8544 ± 0.140751 (W 0.103636) | 67.2345 ± 0.690078 (W 1.48163) | · | 🔵 faer-fork 2.20× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 0.740522 ± 0.00463013 (W 0.00307025) | 0.840901 ± 0.00661993 (W 0.0025073) | 1.532 ± 0.0128182 (W 0.0155885) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔵 faer-fork 2.07× faster than `lapack-mkl` |  |
| `qr_factor/256x4096/b1` | 27.5541 ± 0.379738 (W 0.0390883) | 28.0116 ± 0.24465 (W 0.0664278) | 61.8716 ± 2.24582 (W 0.713078) | · | 🔵 faer-fork 2.25× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.998544 ± 0.0052778 (W 0.00650487) | 1.02128 ± 0.0090373 (W 0.00580909) | 1.35314 ± 0.0053355 (W 0.00455195) | · | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 80.3992 ± 0.152566 (W 0.10953) | 83.0131 ± 0.0399573 (W 0.170085) | 251.207 ± 3.47098 (W 2.44116) | · | 🔵 faer-fork 3.12× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 2.25324 ± 0.00669975 (W 0.0111532) | 2.44939 ± 0.00620343 (W 0.00521775) | 4.16912 ± 0.0307033 (W 0.0135434) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.85× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 32.5975 ± 0.0902029 (W 0.0318597) | 39.1261 ± 0.145127 (W 0.0517026) | 184.724 ± 5.87831 (W 1.57622) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 5.67× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 0.954862 ± 0.00767124 (W 0.00270436) | 1.41408 ± 0.00167727 (W 0.00617169) | 2.63634 ± 0.0232549 (W 0.00740983) | 🔵 faer-fork 1.48× faster than `faer-upstream` | 🔵 faer-fork 2.76× faster than `lapack-mkl` |  |

## linalg-wide, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 32.5965 ± 0.0391485 (W 0.0658226) | 36.8191 ± 0.535026 (W 0.0900121) | - | 🔵 faer-fork 1.13× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.721836 ± 0.00404694 (W 0.00296592) | 1.25851 ± 0.0196924 (W 0.00580618) | - | 🔵 faer-fork 1.74× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 6.63291 ± 0.263048 (W 0.0295559) | 9.99379 ± 0.459898 (W 0.50844) | 10.0079 ± 0.207078 (W 0.0600384) | 🔵 faer-fork 1.51× faster than `faer-upstream` | 🔵 faer-fork 1.51× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/64x1024/b1` | 0.204632 ± 0.00137255 (W 0.00171287) | 0.365923 ± 0.00836285 (W 0.0191973) | 0.288819 ± 0.00702739 (W 0.00280518) | 🔵 faer-fork 1.79× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 10.5709 ± 0.0762188 (W 0.0234317) | 12.7737 ± 0.274347 (W 0.0475756) | 16.6454 ± 1.84771 (W 0.143296) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.57× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/64x1024/b1` | 0.367296 ± 0.000553571 (W 0.00266899) | 0.548885 ± 0.00321756 (W 0.00407472) | 0.61649 ± 0.00295399 (W 0.0109298) | 🔵 faer-fork 1.49× faster than `faer-upstream` | 🔵 faer-fork 1.68× faster than `lapack-mkl` |  |
| `qr_factor/256x4096/b1` | 9.98486 ± 0.0136635 (W 0.0273145) | 10.4632 ± 0.166342 (W 0.0354289) | 13.2271 ± 0.185128 (W 0.0338424) | · | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.615759 ± 0.00418639 (W 0.00772568) | 0.693644 ± 0.00226728 (W 0.00483333) | 0.420765 ± 0.00168064 (W 0.00229293) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.46× slower than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 34.3532 ± 0.0675507 (W 0.0587898) | 42.1516 ± 0.0520525 (W 0.0804925) | 123.909 ± 3.27731 (W 0.391409) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 3.61× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/64x1024/b1` | 1.70149 ± 0.00635338 (W 0.00174486) | 2.10583 ± 0.00336066 (W 0.00609533) | 3.0395 ± 0.0256572 (W 0.00918064) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.79× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 17.4782 ± 0.00480023 (W 0.0309227) | 26.9977 ± 0.0642819 (W 0.0450749) | 98.9013 ± 2.49727 (W 0.268766) | 🔵 faer-fork 1.54× faster than `faer-upstream` | 🔵 faer-fork 5.66× faster than `lapack-mkl` |  |
| `svd_values/64x1024/b1` | 0.834026 ± 0.00154719 (W 0.00339959) | 1.46957 ± 0.00641734 (W 0.00513989) | 2.14103 ± 0.0276247 (W 0.0078762) | 🔵 faer-fork 1.76× faster than `faer-upstream` | 🔵 faer-fork 2.57× faster than `lapack-mkl` |  |

## linalg-wide, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 27.1835 ± 0.148464 (W 0.0764761) | 30.6363 ± 0.074899 (W 0.0569359) | - | 🔵 faer-fork 1.13× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.682805 ± 0.00267576 (W 0.00252189) | 1.26442 ± 0.0180204 (W 0.00326042) | - | 🔵 faer-fork 1.85× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 4.98372 ± 0.11784 (W 0.0401573) | 7.83169 ± 0.0279559 (W 0.11412) | 6.90149 ± 0.0324871 (W 0.0568701) | 🔵 faer-fork 1.57× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.177662 ± 0.00238966 (W 0.0020219) | 0.330387 ± 0.00876325 (W 0.00547529) | 0.167874 ± 0.00242446 (W 0.0016259) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr/256x4096/b1` | 7.26832 ± 0.152227 (W 0.0162408) | 11.2007 ± 0.12738 (W 0.222378) | 13.0493 ± 0.0929799 (W 0.0875216) | 🔵 faer-fork 1.54× faster than `faer-upstream` | 🔵 faer-fork 1.80× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 0.313385 ± 0.00097922 (W 0.0020815) | 0.584279 ± 0.015231 (W 0.00414324) | 0.469616 ± 0.00895788 (W 0.0122557) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `qr_factor/256x4096/b1` | 7.20078 ± 0.0881136 (W 0.0244891) | 8.86618 ± 0.238787 (W 0.223696) | 6.79185 ± 0.0467412 (W 0.0257371) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.551258 ± 0.0067736 (W 0.00425501) | 0.734611 ± 0.00887974 (W 0.00801081) | 0.252321 ± 0.000783378 (W 0.00263333) | 🔵 faer-fork 1.33× faster than `faer-upstream` | 🔴 faer-fork 2.18× slower than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 28.5235 ± 0.0404929 (W 0.0764993) | 40.7154 ± 0.226197 (W 0.240342) | 114.689 ± 1.64964 (W 0.503686) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 4.02× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 1.61593 ± 0.000131394 (W 0.00231107) | 2.18854 ± 0.00663595 (W 0.00822477) | 2.93722 ± 0.0427397 (W 0.00729872) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.82× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 15.0777 ± 0.0791059 (W 0.0302803) | 27.7926 ± 0.0707537 (W 0.0681361) | 86.625 ± 3.21751 (W 0.71637) | 🔵 faer-fork 1.84× faster than `faer-upstream` | 🔵 faer-fork 5.75× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 0.805211 ± 0.00515977 (W 0.00188642) | 1.55175 ± 0.00162138 (W 0.00997984) | 2.10332 ± 0.0135074 (W 0.00381758) | 🔵 faer-fork 1.93× faster than `faer-upstream` | 🔵 faer-fork 2.61× faster than `lapack-mkl` |  |

## linalg-wide, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 71.9694 ± 0.398421 (W 0.250426) | 72.2707 ± 0.710927 (W 0.338382) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.04967 ± 0.00597909 (W 0.0024301) | 1.05177 ± 0.00233978 (W 0.00523034) | - | · | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 13.3124 ± 0.0197697 (W 0.0244516) | 13.3464 ± 0.0421047 (W 0.024033) | 21.4451 ± 0.0694477 (W 0.0503171) | · | 🔵 faer-fork 1.61× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.312082 ± 0.0020748 (W 0.00307884) | 0.31085 ± 0.00092253 (W 0.00251395) | 0.458596 ± 0.00298732 (W 0.0026778) | · | 🔵 faer-fork 1.47× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 27.6263 ± 0.241353 (W 0.0646493) | 27.5124 ± 0.143057 (W 0.0674966) | 68.3743 ± 1.23853 (W 0.336841) | · | 🔵 faer-fork 2.47× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 0.628865 ± 0.00349668 (W 0.00342757) | 0.631641 ± 0.00322931 (W 0.00262175) | 1.49991 ± 0.0586641 (W 0.00524995) | · | 🔵 faer-fork 2.39× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/256x4096/b1` | 25.2568 ± 0.0989984 (W 0.0472381) | 25.273 ± 0.249987 (W 0.129194) | 53.5063 ± 1.0247 (W 0.892625) | · | 🔵 faer-fork 2.12× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.567741 ± 0.00226524 (W 0.00286953) | 0.566828 ± 0.00189581 (W 0.00247906) | 6.28149 ± 0.0138206 (W 0.00952237) | · | 🔵 faer-fork 11.06× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 85.6094 ± 0.184099 (W 0.172523) | 88.5311 ± 0.196639 (W 0.282531) | 233.646 ± 1.1886 (W 1.09697) | · | 🔵 faer-fork 2.73× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 2.31074 ± 0.0135401 (W 0.00624454) | 2.51166 ± 0.00700171 (W 0.00541585) | 3.91448 ± 0.0474297 (W 0.00524859) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.69× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 38.2298 ± 0.0451238 (W 0.428045) | 44.8526 ± 0.0789569 (W 0.07751) | 172.67 ± 2.02112 (W 0.732978) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 4.52× faster than `lapack-mkl` |  |
| `svd_values/64x1024/b1` | 1.03815 ± 0.00173464 (W 0.00515275) | 1.47381 ± 0.00406445 (W 0.00798999) | 2.50583 ± 0.0321257 (W 0.00855109) | 🔵 faer-fork 1.42× faster than `faer-upstream` | 🔵 faer-fork 2.41× faster than `lapack-mkl` |  |

## linalg-wide, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 29.9864 ± 0.0802035 (W 0.0827348) | 31.3803 ± 0.0431119 (W 0.0238887) | - | · | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.647979 ± 0.00176953 (W 0.00333871) | 1.05628 ± 0.000986071 (W 0.00449347) | - | 🔵 faer-fork 1.63× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 4.06254 ± 0.0165514 (W 0.0140091) | 4.859 ± 0.352888 (W 0.249694) | 5.30146 ± 0.0207285 (W 0.0157765) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/64x1024/b1` | 0.116788 ± 0.000214337 (W 0.000564743) | 0.158946 ± 0.00724489 (W 0.0118341) | 0.229538 ± 0.00856176 (W 0.00341637) | 🔵 faer-fork 1.36× faster than `faer-upstream` | 🔵 faer-fork 1.97× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/256x4096/b1` | 7.63703 ± 0.0371944 (W 0.0169594) | 8.05554 ± 0.0374389 (W 0.0362882) | 24.3287 ± 4.19671 (W 0.0600471) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔵 faer-fork 3.19× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/64x1024/b1` | 0.252371 ± 0.000949903 (W 0.00168082) | 0.32176 ± 0.00286645 (W 0.00223171) | 0.695778 ± 0.0605494 (W 0.0188513) | 🔵 faer-fork 1.27× faster than `faer-upstream` | 🔵 faer-fork 2.76× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/256x4096/b1` | 6.56546 ± 0.0364994 (W 0.00813651) | 6.96112 ± 0.0171702 (W 0.0115856) | 11.2157 ± 0.0696005 (W 0.0111172) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.199492 ± 0.000222442 (W 0.00157621) | 0.262831 ± 0.00219985 (W 0.00195426) | 0.363067 ± 0.00101718 (W 0.00370702) | 🔵 faer-fork 1.32× faster than `faer-upstream` | 🔵 faer-fork 1.82× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 39.6478 ± 0.106458 (W 0.0718928) | 47.6302 ± 0.0475819 (W 0.102551) | 119.152 ± 1.02224 (W 0.266555) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 3.01× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 1.77852 ± 0.00581901 (W 0.00321786) | 2.16509 ± 0.00478793 (W 0.00409384) | 3.048 ± 0.0772846 (W 0.0112593) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 23.1106 ± 0.0167369 (W 0.0302713) | 32.8308 ± 0.106913 (W 0.0554584) | 93.9856 ± 1.11388 (W 0.423612) | 🔵 faer-fork 1.42× faster than `faer-upstream` | 🔵 faer-fork 4.07× faster than `lapack-mkl` |  |
| `svd_values/64x1024/b1` | 0.902674 ± 0.0146478 (W 0.00383381) | 1.5294 ± 0.0088108 (W 0.00446932) | 2.08042 ± 0.0429877 (W 0.00476686) | 🔵 faer-fork 1.69× faster than `faer-upstream` | 🔵 faer-fork 2.30× faster than `lapack-mkl` |  |

## linalg-wide, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 24.7073 ± 0.135502 (W 0.0810433) | 25.9878 ± 0.116812 (W 0.0717946) | - | 🔵 faer-fork 1.05× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.609487 ± 0.00244883 (W 0.00160456) | 1.06097 ± 0.0138752 (W 0.00283079) | - | 🔵 faer-fork 1.74× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 2.5395 ± 0.0150417 (W 0.00672954) | 3.28097 ± 0.0327982 (W 0.0945268) | 3.15471 ± 0.0384052 (W 0.00631501) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.088716 ± 0.00110691 (W 0.000654992) | 0.137406 ± 0.000753632 (W 0.0049597) | 0.132628 ± 0.00238349 (W 0.00238269) | 🔵 faer-fork 1.55× faster than `faer-upstream` | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 4.37012 ± 0.0238473 (W 0.00978731) | 6.37262 ± 0.267767 (W 0.233609) | 25.7987 ± 0.133437 (W 0.058008) | 🔵 faer-fork 1.46× faster than `faer-upstream` | 🔵 faer-fork 5.90× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/64x1024/b1` | 0.201856 ± 0.00190108 (W 0.00195265) | 0.381222 ± 0.00278417 (W 0.00441852) | 0.467101 ± 0.00147536 (W 0.00394575) | 🔵 faer-fork 1.89× faster than `faer-upstream` | 🔵 faer-fork 2.31× faster than `lapack-mkl` |  |
| `qr_factor/256x4096/b1` | 3.58909 ± 0.0150702 (W 0.0157941) | 5.39528 ± 0.061019 (W 0.141052) | 5.84976 ± 0.00686134 (W 0.0100559) | 🔵 faer-fork 1.50× faster than `faer-upstream` | 🔵 faer-fork 1.63× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.153416 ± 0.00669487 (W 0.000474875) | 0.320738 ± 0.00491145 (W 0.00483409) | 0.212597 ± 0.00201203 (W 0.00208778) | 🔵 faer-fork 2.09× faster than `faer-upstream` | 🔵 faer-fork 1.39× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/256x4096/b1` | 33.6993 ± 1.59397 (W 0.0363074) | 46.2142 ± 1.62481 (W 0.315301) | 105.527 ± 1.17572 (W 0.630682) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 3.13× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/64x1024/b1` | 1.67881 ± 0.00355177 (W 0.00408175) | 2.2475 ± 0.00431828 (W 0.00864963) | 3.0402 ± 0.0163629 (W 0.0172404) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔵 faer-fork 1.81× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 20.724 ± 1.60604 (W 0.055263) | 33.4804 ± 0.123834 (W 0.120983) | 82.1622 ± 2.92894 (W 0.365324) | 🔵 faer-fork 1.62× faster than `faer-upstream` | 🔵 faer-fork 3.96× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 0.878348 ± 0.00459454 (W 0.0035661) | 1.61567 ± 0.006564 (W 0.0058751) | 2.0933 ± 0.0301323 (W 0.00419985) | 🔵 faer-fork 1.84× faster than `faer-upstream` | 🔵 faer-fork 2.38× faster than `lapack-mkl` |  |

## linalg-wide, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 232.455 ± 6.37436 (W 0.805878) | 234.391 ± 5.52837 (W 0.857718) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/64x1024/b1` | 2.44611 ± 0.013956 (W 0.00710181) | 2.54119 ± 0.0318436 (W 0.0217987) | - | · | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 45.9789 ± 0.262336 (W 0.120497) | 46.5648 ± 0.310799 (W 0.0629928) | 88.6254 ± 0.253866 (W 0.138045) | · | 🔵 faer-fork 1.93× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.998565 ± 0.00945019 (W 0.00319648) | 1.05211 ± 0.00677048 (W 0.00528411) | 2.32771 ± 0.0117104 (W 0.0060858) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔵 faer-fork 2.33× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 106.494 ± 0.879507 (W 0.1389) | 107.891 ± 0.367108 (W 0.464023) | 183.297 ± 1.75811 (W 0.997526) | · | 🔵 faer-fork 1.72× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 2.50032 ± 0.00465276 (W 0.00382259) | 2.56558 ± 0.0476682 (W 0.0119709) | 3.91488 ± 0.0461203 (W 0.0110876) | · | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |
| `qr_factor/256x4096/b1` | 97.1058 ± 0.132748 (W 0.309999) | 97.2331 ± 0.251554 (W 0.0734899) | 160.817 ± 1.07481 (W 0.755775) | · | 🔵 faer-fork 1.66× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 2.58134 ± 0.00319716 (W 0.0112809) | 2.61035 ± 0.0176439 (W 0.00462613) | 3.59023 ± 0.0386269 (W 0.0100674) | · | 🔵 faer-fork 1.39× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 264.149 ± 0.718309 (W 3.43804) | 269.856 ± 0.357376 (W 0.281197) | 543.243 ± 2.02749 (W 2.03763) | · | 🔵 faer-fork 2.06× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 5.61546 ± 0.418864 (W 0.00584757) | 5.90765 ± 0.0109406 (W 0.00777843) | 12.2816 ± 0.0965179 (W 0.0252881) | · | 🔵 faer-fork 2.19× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/256x4096/b1` | 101.723 ± 0.178127 (W 0.083559) | 110.553 ± 0.224089 (W 0.116225) | 201.562 ± 7.19223 (W 2.01459) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.98× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 2.41158 ± 0.00919811 (W 0.00620187) | 2.97424 ± 0.0249408 (W 0.00532604) | 5.50571 ± 0.0658588 (W 0.0167758) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 2.28× faster than `lapack-mkl` |  |

## linalg-wide, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 87.4168 ± 2.60788 (W 0.52495) | 88.2934 ± 2.41092 (W 0.223978) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/64x1024/b1` | 1.34071 ± 0.00441817 (W 0.00429974) | 2.4859 ± 0.0121641 (W 0.0138389) | - | 🔵 faer-fork 1.85× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 17.17 ± 0.0460297 (W 0.0482452) | 20.9758 ± 1.07762 (W 0.69155) | 29.638 ± 0.0983442 (W 0.0929248) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.73× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/64x1024/b1` | 0.489553 ± 0.0446612 (W 0.0377036) | 0.590682 ± 0.026676 (W 0.0484211) | 0.644393 ± 0.00166107 (W 0.00364321) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/256x4096/b1` | 31.9743 ± 0.437871 (W 0.0863357) | 33.3787 ± 0.20952 (W 0.0880286) | 50.7242 ± 0.120545 (W 0.226992) | · | 🔵 faer-fork 1.59× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 0.880124 ± 0.00368195 (W 0.00276205) | 1.04335 ± 0.029514 (W 0.00285843) | 1.60024 ± 0.00611728 (W 0.00420199) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 1.82× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/256x4096/b1` | 27.8985 ± 0.208173 (W 0.0359118) | 28.4279 ± 0.278917 (W 0.0454462) | 38.3515 ± 0.11217 (W 0.0571219) | · | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.973256 ± 0.00440046 (W 0.00327062) | 1.06462 ± 0.00439995 (W 0.00575661) | 1.29288 ± 0.00340353 (W 0.00503961) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 90.595 ± 0.285896 (W 0.0664467) | 107.53 ± 0.231331 (W 0.137294) | 192.401 ± 0.349001 (W 0.937137) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 2.12× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 3.03473 ± 0.0138457 (W 0.00666255) | 3.61873 ± 0.0122337 (W 0.00761604) | 7.43854 ± 0.106558 (W 0.0185715) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔵 faer-fork 2.45× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 41.6249 ± 0.359459 (W 0.0762915) | 60.2063 ± 0.0565112 (W 0.0614585) | 85.0644 ± 5.23992 (W 0.269151) | 🔵 faer-fork 1.45× faster than `faer-upstream` | 🔵 faer-fork 2.04× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 1.60339 ± 0.00325755 (W 0.00502799) | 2.35873 ± 0.0102087 (W 0.00951314) | 3.71879 ± 0.0408468 (W 0.00588879) | 🔵 faer-fork 1.47× faster than `faer-upstream` | 🔵 faer-fork 2.32× faster than `lapack-mkl` |  |

## linalg-wide, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 54.7517 ± 1.24235 (W 0.190115) | 59.8582 ± 0.479898 (W 0.197411) | - | 🔵 faer-fork 1.09× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.21068 ± 0.00750615 (W 0.00358681) | 2.50953 ± 0.019107 (W 0.01294) | - | 🔵 faer-fork 2.07× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 11.6018 ± 0.265559 (W 0.0772702) | 13.6428 ± 0.203359 (W 0.484101) | 19.0264 ± 0.120157 (W 0.119543) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔵 faer-fork 1.64× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.361033 ± 0.00126955 (W 0.00241248) | 0.43966 ± 0.00118105 (W 0.00650551) | 0.452955 ± 0.00316291 (W 0.00207893) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 19.6137 ± 0.0963419 (W 0.0975902) | 24.5816 ± 0.500328 (W 0.757427) | 31.4177 ± 0.0448221 (W 0.0746363) | 🔵 faer-fork 1.25× faster than `faer-upstream` | 🔵 faer-fork 1.60× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 0.617 ± 0.00221818 (W 0.00241047) | 1.0206 ± 0.0344492 (W 0.0132663) | 1.02524 ± 0.00183261 (W 0.003367) | 🔵 faer-fork 1.65× faster than `faer-upstream` | 🔵 faer-fork 1.66× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/256x4096/b1` | 16.3577 ± 0.0641501 (W 0.245912) | 20.2002 ± 0.51346 (W 1.00233) | 20.6093 ± 0.0862517 (W 0.0504443) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.729092 ± 0.0319973 (W 0.00627147) | 1.03423 ± 0.00453799 (W 0.0134826) | 0.730833 ± 0.00322124 (W 0.00241285) | 🔵 faer-fork 1.42× faster than `faer-upstream` | · | `!` between-start range over 5% |
| `svd_thin/256x4096/b1` | 65.8777 ± 0.11143 (W 0.0811766) | 95.0258 ± 0.593861 (W 1.39735) | 118.623 ± 0.346215 (W 0.316826) | 🔵 faer-fork 1.44× faster than `faer-upstream` | 🔵 faer-fork 1.80× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 2.6337 ± 0.01071 (W 0.00968713) | 3.60933 ± 0.00785036 (W 0.0201289) | 6.25868 ± 0.0578034 (W 0.00906946) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 2.38× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 32.784 ± 0.0971865 (W 0.0295185) | 57.9093 ± 0.315582 (W 0.531494) | 56.4297 ± 3.97064 (W 0.14328) | 🔵 faer-fork 1.77× faster than `faer-upstream` | 🔵 faer-fork 1.72× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 1.50098 ± 0.0121492 (W 0.00717021) | 2.39358 ± 0.0102189 (W 0.00918146) | 9.76569 ± 3.72156 (W 0.0154329) | 🔵 faer-fork 1.59× faster than `faer-upstream` | 🔵 faer-fork 6.51× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |

## linalg-wide, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 229.845 ± 7.50864 (W 1.26624) | 229.525 ± 5.33346 (W 0.717059) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/64x1024/b1` | 2.29504 ± 0.0216012 (W 0.0112031) | 2.30798 ± 0.0425762 (W 0.0138631) | - | · | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 41.8854 ± 0.133976 (W 0.0489211) | 41.8895 ± 0.594113 (W 0.0584849) | 72.2971 ± 0.299106 (W 0.0513782) | · | 🔵 faer-fork 1.73× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.899368 ± 0.00512614 (W 0.00313191) | 0.890883 ± 0.00337389 (W 0.00480567) | 2.12204 ± 0.00441601 (W 0.00171208) | · | 🔵 faer-fork 2.36× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 103.259 ± 0.274703 (W 0.500547) | 103.507 ± 0.50888 (W 0.334975) | 192.228 ± 5.63967 (W 0.593073) | · | 🔵 faer-fork 1.86× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/64x1024/b1` | 2.38911 ± 0.0113523 (W 0.0042585) | 2.38124 ± 0.0186723 (W 0.0077685) | 3.91093 ± 0.246114 (W 0.0137584) | · | 🔵 faer-fork 1.64× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/256x4096/b1` | 96.1223 ± 0.301735 (W 0.497844) | 96.5285 ± 0.297218 (W 0.339379) | 155.642 ± 6.32962 (W 0.613193) | · | 🔵 faer-fork 1.62× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 2.22882 ± 0.00992712 (W 0.00567946) | 2.2229 ± 0.0115231 (W 0.00884181) | 16.8127 ± 0.0371353 (W 0.0230067) | · | 🔵 faer-fork 7.54× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 275.873 ± 0.323336 (W 0.372105) | 282.061 ± 0.439248 (W 0.39556) | 526.789 ± 13.4279 (W 0.909215) | · | 🔵 faer-fork 1.91× faster than `lapack-mkl` |  |
| `svd_thin/64x1024/b1` | 5.72262 ± 0.00501467 (W 0.00669709) | 6.02665 ± 0.00354964 (W 0.0077216) | 11.7739 ± 0.101815 (W 0.0170881) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔵 faer-fork 2.06× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 113.722 ± 0.942471 (W 0.514467) | 123.178 ± 0.273524 (W 0.256691) | 191.886 ± 8.12271 (W 0.602281) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.69× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 2.53094 ± 0.00814704 (W 0.00765474) | 3.09644 ± 0.024855 (W 0.00614048) | 5.41556 ± 0.0725283 (W 0.0154662) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 2.14× faster than `lapack-mkl` |  |

## linalg-wide, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 82.672 ± 2.04506 (W 0.325124) | 84.0435 ± 2.72266 (W 0.348316) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/64x1024/b1` | 1.20162 ± 0.00994339 (W 0.00394803) | 2.24988 ± 0.0272025 (W 0.0120049) | - | 🔵 faer-fork 1.87× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 13.2874 ± 0.0215916 (W 0.0191782) | 17.9643 ± 1.31519 (W 1.49834) | 20.5621 ± 0.0567648 (W 0.0215287) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.55× faster than `lapack-mkl` | `!` between-start range over 5% |
| `lu/64x1024/b1` | 0.310539 ± 0.00281609 (W 0.0426649) | 0.333802 ± 0.0393593 (W 0.0342009) | 0.583901 ± 0.000941269 (W 0.00503833) | · | 🔵 faer-fork 1.88× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/256x4096/b1` | 28.0799 ± 0.20556 (W 0.0333132) | 28.4432 ± 0.192388 (W 0.0520843) | 69.827 ± 0.468634 (W 0.383642) | · | 🔵 faer-fork 2.49× faster than `lapack-mkl` |  |
| `qr/64x1024/b1` | 0.769475 ± 0.00170986 (W 0.00267677) | 0.869905 ± 0.00160056 (W 0.00323541) | 1.81578 ± 0.230155 (W 0.0127745) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔵 faer-fork 2.36× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/256x4096/b1` | 25.2321 ± 0.201907 (W 0.030597) | 25.7308 ± 0.342503 (W 0.0228746) | 35.2631 ± 0.0288409 (W 0.0280526) | · | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.649722 ± 0.00192278 (W 0.00166423) | 0.721227 ± 0.00353532 (W 0.00330765) | 1.21775 ± 0.00358676 (W 0.0036898) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔵 faer-fork 1.87× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 103.04 ± 0.0198928 (W 0.33175) | 119.574 ± 0.34075 (W 0.221977) | 190.24 ± 5.79975 (W 0.654466) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔵 faer-fork 1.85× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/64x1024/b1` | 3.1553 ± 0.0360335 (W 0.00847501) | 3.72984 ± 0.0139762 (W 0.0106553) | 7.28577 ± 0.13739 (W 0.0195331) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔵 faer-fork 2.31× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 53.5953 ± 0.0941281 (W 0.138046) | 72.3034 ± 0.151049 (W 0.0677623) | 82.7389 ± 0.193882 (W 0.306358) | 🔵 faer-fork 1.35× faster than `faer-upstream` | 🔵 faer-fork 1.54× faster than `lapack-mkl` |  |
| `svd_values/64x1024/b1` | 1.71111 ± 0.00641927 (W 0.00526685) | 2.44606 ± 0.0116881 (W 0.00760563) | 3.65285 ± 0.012555 (W 0.00797341) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 2.13× faster than `lapack-mkl` |  |

## linalg-wide, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 50.4954 ± 0.667732 (W 0.368936) | 55.9856 ± 0.383674 (W 0.296066) | - | 🔵 faer-fork 1.11× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.07708 ± 0.00497085 (W 0.00293664) | 2.24607 ± 0.0287888 (W 0.014445) | - | 🔵 faer-fork 2.09× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 7.66357 ± 0.0875913 (W 0.0157933) | 9.53978 ± 0.0675067 (W 0.316039) | 11.3155 ± 0.0200843 (W 0.0256437) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `lu/64x1024/b1` | 0.248885 ± 0.00105733 (W 0.00146144) | 0.278319 ± 0.00252611 (W 0.00203076) | 0.417029 ± 0.00211641 (W 0.00316848) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 1.68× faster than `lapack-mkl` |  |
| `qr/256x4096/b1` | 15.4333 ± 0.0961094 (W 0.0259594) | 20.6093 ± 0.692123 (W 1.02924) | 52.5634 ± 0.407444 (W 0.531944) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔵 faer-fork 3.41× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr/64x1024/b1` | 0.505502 ± 0.00151967 (W 0.00282252) | 0.851109 ± 0.00536581 (W 0.0157738) | 1.49576 ± 0.170809 (W 0.00716816) | 🔵 faer-fork 1.68× faster than `faer-upstream` | 🔵 faer-fork 2.96× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/256x4096/b1` | 13.3054 ± 0.0592396 (W 0.0423406) | 17.097 ± 0.372817 (W 1.04952) | 18.1237 ± 0.0261449 (W 0.0161008) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` |  |
| `qr_factor/64x1024/b1` | 0.394045 ± 0.00026963 (W 0.00222913) | 0.687833 ± 0.00866316 (W 0.0138115) | 0.675189 ± 0.000839831 (W 0.00356615) | 🔵 faer-fork 1.75× faster than `faer-upstream` | 🔵 faer-fork 1.71× faster than `lapack-mkl` |  |
| `svd_thin/256x4096/b1` | 78.2022 ± 0.179461 (W 0.23131) | 106.958 ± 0.765733 (W 2.05855) | 122.185 ± 6.4388 (W 0.224859) | 🔵 faer-fork 1.37× faster than `faer-upstream` | 🔵 faer-fork 1.56× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/64x1024/b1` | 2.80234 ± 0.0408109 (W 0.00553981) | 3.72007 ± 0.0149886 (W 0.0188623) | 6.2007 ± 0.026727 (W 0.0203833) | 🔵 faer-fork 1.33× faster than `faer-upstream` | 🔵 faer-fork 2.21× faster than `lapack-mkl` |  |
| `svd_values/256x4096/b1` | 44.8378 ± 0.0634722 (W 0.0698065) | 70.0438 ± 0.224727 (W 0.461417) | 54.7035 ± 0.18463 (W 0.232201) | 🔵 faer-fork 1.56× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `svd_values/64x1024/b1` | 1.60272 ± 0.024464 (W 0.00530008) | 2.50535 ± 0.0145398 (W 0.00670214) | 3.35634 ± 0.0922676 (W 0.0279185) | 🔵 faer-fork 1.56× faster than `faer-upstream` | 🔵 faer-fork 2.09× faster than `lapack-mkl` | `!` between-start range over 5% |

Not applicable to this population's shapes and reported as skipped: `cholesky/256x4096`, `cholesky/64x1024`, `eigh/256x4096`, `eigh/64x1024`, `full_piv_lu/256x4096`, `full_piv_lu/64x1024`, `solve/256x4096`, `solve/64x1024`, `triangular_solve/256x4096`, `triangular_solve/64x1024`.

Repeated process sets describe observed repeatability under the recorded order schedule; they are not a paired baseline/candidate experiment and do not establish equal performance between engines.

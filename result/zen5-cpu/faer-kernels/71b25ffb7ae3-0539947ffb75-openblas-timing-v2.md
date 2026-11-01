<!-- generated from data/results/zen5-cpu/faer-kernels/20261101T031016Z-pub-71b25ffb-20261031-openblas/report.md by scripts/publish_report.py; the report below is the source of truth -->

# `faer-kernels` on `zen5-cpu`

- t4a-faer (fork, measured) commit: `71b25ffb7ae3ce038ec25b35c91e526be41b9a63`
- t4a-faer version: `0.27.1`
- upstream faer commit: `0539947ffb757a739d7e703a7d2fa0c792a909c1`
- upstream faer ref/version: `faer-v0.24.4` / `0.24.4`
- features: `std, rayon`
- faer rows: `faer-fork` (the provider in the measured revision; see library and upstream above)
- harness commit: `eeeaa36388c515a992d5056f4211e4a6cb92ba54`
- toolkit commit: `74e50e8199cb2c2f07e810744a0943fc3a8c1170`
- measured binary SHA-256: `031d85f03c297a1d21ddd298f0192a7bbb88b1d0c4e807fe553207f01c8362a9`
- hardware profile: `zen5-cpu`
- host role: `development` — **provisional**: recorded on a development host, superseded by the measurement host's dataset
- timestamp: `2026-11-01T05:54:18.477502Z`
- timing policy: v2, median of 5 reps, priming 250 ms (time-based, identical on every row)
- guards: idle window 3 s, max busy 5.0% including SMT siblings, 3 attempts
- command: `scripts/record_run.py zen5-cpu faer-kernels --checkout /home/shinaoka/.local/state/faer-measurement-checkouts/71b25ffb7ae3ce038ec25b35c91e526be41b9a63/t4a-faer --upstream extern/upstream-faer --vendor openblas --engines faer-fork,lapack-openblas --threads 1,4,8 --dtypes f64,c64 --reps 5 --aa 6 --prime-ms 250 --label pub-71b25ffb-20261031-openblas --no-publish`
- raw data: `data/results/zen5-cpu/faer-kernels/20261101T031016Z-pub-71b25ffb-20261031-openblas/`

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
  Known blind spot: Known limitation (71b25ffb recording): multi-thread figures include threadteam 0.2.0 and are not final for the 0.3.0 runtime.
- **Rows** — one row per engine in every table below:
  - `faer-fork` — The measured library: the tensor4all fork (`t4a-faer`, `[lib] name = "faer"`) at the checkout the harness linked by path. This is the row the campaign exists for; the fork's three perf experiments and the two correctness changes land here.
    Identity: the fork revision in this run's manifest (`library.commit`), pinned by `pins/t4a-faer.rev`
    Caveat: Both faer crates declare `[lib] name = "faer"`. They are distinct dependency keys (`faer_fork = { package = "t4a-faer" }`, `faer_upstream = { package = "faer" }`) and therefore distinct Rust crate identities, but their `Mat`, `Par` and trait types are not interchangeable: every adapter is written per arm, and shared transitive dependencies can unify Cargo features, so both arms declare equivalent feature sets and the resolved lock is recorded. For the 71b25ffb recording: measured at 71b25ffb, the commit immediately before the 0.28.0 release commit 325e482; the only difference is Cargo.lock and faer/Cargo.toml (threadteam 0.2.0 in the measured build, 0.3.0 as shipped, plus the version string). Single-thread numbers apply to 0.28.0 as released; multi-thread numbers carry that threadteam difference and will be re-measured in the next campaign.
    As measured: `faer-fork` (the provider in the measured revision; see library and upstream above)
  - `lapack-openblas` — CBLAS `?gemm` plus LAPACK drivers linked against OpenBLAS: vendor calls and their marshalling, vendor-owned threading. The vendor's own thread budget is set by the harness before the row and read back, and the vendor identity and the dispatched kernel are recorded in the manifest.
    Identity: the OpenBLAS build recorded in this run's manifest (`providers[openblas]`)
    Caveat: LAPACK and BLAS own their threading, so this row's thread budget is the vendor's, not the harness pool's. Where a family has no LAPACK route the row is absent and the CSV says the case was skipped for it.
    As measured: linked static; openblas 0.3.32; kernel dispatched to `Cooperlake`; pthread threading; config `OpenBLAS 0.3.32 DYNAMIC_ARCH NO_AFFINITY Cooperlake MAX_THREADS=24`

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
Each process retains 5 chronological calls; 6 complete process sets are recorded.
Spread guide (computed from this run's own rows): per-engine between-start range median 1.56%, worst 30537.56% among cells of 1 us or more (a sub-microsecond row is timer and scheduler jitter, not kernel time); 204 of 2328 engine cells exceed 5% and carry `!`; median within-process relative SD 0.38%. A cell whose `±`, `!` or `p` is as large as the difference you are reading is not evidence of a regression.
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

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002359 ± 2.11699e-05 (W 1.54568e-05) | 0.0022145 ± 1.49722e-05 (W 1.91584e-05) | 🔴 faer-fork 1.07× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0171825 ± 6.25089e-05 (W 3.09456e-05) | 0.0168275 ± 2.82235e-05 (W 1.17879e-05) | · | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.0568065 ± 4.93778e-05 (W 0.000579358) | 0.056338 ± 0.000183914 (W 2.88781e-05) | · |  |

## gemm-small, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.0023995 ± 1.15873e-05 (W 2.64895e-05) | 0.002214 ± 2.58199e-05 (W 2.66624e-05) | 🔴 faer-fork 1.08× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.011337 ± 0.000164274 (W 0.000199995) | 0.0168215 ± 2.00366e-05 (W 2.78553e-05) | 🔵 faer-fork 1.48× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.0232305 ± 0.000326879 (W 0.000283509) | 0.0564025 ± 0.000211264 (W 3.94372e-05) | 🔵 faer-fork 2.43× faster than `lapack-openblas` |  |

## gemm-small, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.0024095 ± 2.07244e-05 (W 2.50326e-05) | 0.002214 ± 1.16905e-05 (W 2.93732e-05) | 🔴 faer-fork 1.09× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0098885 ± 8.1496e-05 (W 0.000116553) | 0.016831 ± 5.65072e-05 (W 2.00926e-05) | 🔵 faer-fork 1.70× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.020263 ± 8.76236e-05 (W 8.022e-05) | 0.056315 ± 0.000211306 (W 2.88384e-05) | 🔵 faer-fork 2.78× faster than `lapack-openblas` |  |

## gemm-small, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002354 ± 1.00797e-05 (W 1.51689e-05) | 0.0022095 ± 1.96367e-05 (W 1.46901e-05) | 🔴 faer-fork 1.07× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.017183 ± 0.000175569 (W 3.04318e-05) | 0.016827 ± 5.07385e-05 (W 1.86659e-05) | · | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.056789 ± 9.52794e-05 (W 5.7498e-05) | 0.0564125 ± 5.60669e-05 (W 0.000867691) | · |  |

## gemm-small, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.0024045 ± 1.52403e-05 (W 2.10557e-05) | 0.002214 ± 2.35266e-05 (W 2.05698e-05) | 🔴 faer-fork 1.09× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0113765 ± 0.000127194 (W 0.000243038) | 0.016826 ± 7.42224e-05 (W 1.94841e-05) | 🔵 faer-fork 1.48× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.0232935 ± 0.000308025 (W 0.000195185) | 0.056383 ± 6.32266e-05 (W 0.000801459) | 🔵 faer-fork 2.42× faster than `lapack-openblas` |  |

## gemm-small, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.002404 ± 1.59875e-05 (W 1.25266e-05) | 0.002214 ± 2.42212e-05 (W 2.0106e-05) | 🔴 faer-fork 1.09× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0097885 ± 1.2203 (W 7.78436e-05) | 0.0168315 ± 4.62663e-05 (W 1.45147e-05) | · | `!` between-start range over 5%; `p` position effect over 5%; dispatch-dominated (row under 20 us) |
| `gemm/96x96x96/b1` | 0.020209 ± 9.17664e-05 (W 5.40187e-05) | 0.0562905 ± 0.000153007 (W 0.000880631) | 🔵 faer-fork 2.79× faster than `lapack-openblas` |  |

## gemm-small, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.008857 ± 3.16228e-05 (W 1.48324e-05) | 0.0115815 ± 2.09897e-05 (W 3.59009e-05) | 🔵 faer-fork 1.31× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0677975 ± 0.000214784 (W 0.00141333) | 0.086136 ± 0.00013168 (W 0.00143736) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `gemm/96x96x96/b1` | 0.226828 ± 0.000802046 (W 0.00174933) | 0.276618 ± 0.000440838 (W 0.00222731) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |

## gemm-small, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.009583 ± 0.000243826 (W 0.000159968) | 0.011632 ± 3.09106e-05 (W 3.57316e-05) | 🔵 faer-fork 1.21× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.02911 ± 0.000195809 (W 0.000200336) | 0.025633 ± 0.000385272 (W 0.000665371) | 🔴 faer-fork 1.14× slower than `lapack-openblas` |  |
| `gemm/96x96x96/b1` | 0.0786055 ± 0.000446684 (W 0.000423694) | 0.0794165 ± 0.000221438 (W 0.00144422) | · |  |

## gemm-small, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.009878 ± 9.69153e-05 (W 7.34492e-05) | 0.0116175 ± 6.0889e-05 (W 4.37887e-05) | 🔵 faer-fork 1.18× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.02689 ± 0.000127301 (W 8.39595e-05) | 0.0259345 ± 0.000227779 (W 0.000348097) | · |  |
| `gemm/96x96x96/b1` | 0.039861 ± 0.000255454 (W 0.000116181) | 0.055366 ± 0.000225565 (W 0.000312976) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |

## gemm-small, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.0088715 ± 1.44591e-05 (W 1.79843e-05) | 0.011587 ± 2.07236e-05 (W 3.05483e-05) | 🔵 faer-fork 1.31× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0676865 ± 0.000224118 (W 3.97803e-05) | 0.0861395 ± 9.99368e-05 (W 0.000319171) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `gemm/96x96x96/b1` | 0.226739 ± 0.000611055 (W 0.00178942) | 0.276489 ± 0.00068425 (W 0.0016828) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |

## gemm-small, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.0096235 ± 0.000256384 (W 0.000152293) | 0.011632 ± 1.52807e-05 (W 2.1927e-05) | 🔵 faer-fork 1.21× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.028919 ± 0.000284997 (W 0.000234277) | 0.0257895 ± 0.000394121 (W 0.000166684) | 🔴 faer-fork 1.12× slower than `lapack-openblas` |  |
| `gemm/96x96x96/b1` | 0.078335 ± 0.000322588 (W 0.000410508) | 0.078209 ± 0.000585271 (W 0.000267396) | · |  |

## gemm-small, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/32x32x32/b1` | 0.0098935 ± 6.95893e-05 (W 7.74988e-05) | 0.0115465 ± 6.77161e-05 (W 3.5492e-05) | 🔵 faer-fork 1.17× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `gemm/64x64x64/b1` | 0.0269355 ± 6.85877e-05 (W 9.35468e-05) | 0.026025 ± 0.000152685 (W 0.00020645) | · |  |
| `gemm/96x96x96/b1` | 0.039569 ± 0.000309231 (W 0.000129961) | 0.0552855 ± 0.000267107 (W 0.000300446) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |

## gemm-mid, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.133004 ± 0.0009712 (W 0.000810018) | 0.162319 ± 0.000782981 (W 0.00154557) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.452178 ± 0.00324822 (W 0.0022064) | 0.53756 ± 0.00199591 (W 0.00248788) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 1.07433 ± 0.00524406 (W 0.00146217) | 1.2647 ± 0.00828126 (W 0.00193346) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 3.59474 ± 0.0172123 (W 0.00672772) | 4.2218 ± 0.0262539 (W 0.0133811) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 8.57599 ± 0.0263489 (W 0.0165817) | 10.0294 ± 0.0305868 (W 0.0122611) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 29.3712 ± 0.0819886 (W 0.0484444) | 33.7158 ± 0.138497 (W 0.0309305) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |

## gemm-mid, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.045309 ± 0.000189906 (W 0.000323181) | 0.050143 ± 0.000657066 (W 0.000752802) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.120199 ± 0.00152351 (W 0.00126459) | 0.148733 ± 0.000588119 (W 0.0017585) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 0.290616 ± 0.00125239 (W 0.00193964) | 0.343778 ± 0.00153969 (W 0.00272794) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 0.916686 ± 0.00444362 (W 0.00252752) | 1.10289 ± 0.00353903 (W 0.00460772) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 2.20832 ± 0.00739375 (W 0.00516685) | 2.59222 ± 0.02797 (W 0.00553217) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 7.5189 ± 0.0263426 (W 0.00969382) | 8.72061 ± 0.0240548 (W 0.0185903) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |

## gemm-mid, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.033309 ± 1.53003 (W 0.000713719) | 0.029984 ± 0.000492486 (W 0.000552131) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `gemm/192x192x192/b1` | 0.085877 ± 0.000475143 (W 0.000657132) | 0.084544 ± 0.00113018 (W 0.000692959) | · |  |
| `gemm/256x256x256/b1` | 0.164758 ± 0.000385589 (W 0.00175554) | 0.184801 ± 0.00191722 (W 0.00226153) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 0.47973 ± 0.0029851 (W 0.00277431) | 0.55934 ± 0.00312046 (W 0.00315929) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 1.14168 ± 0.00318879 (W 0.00344146) | 1.31953 ± 0.00387565 (W 0.00298469) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 3.90908 ± 0.00598213 (W 0.00806843) | 4.55948 ± 0.0232587 (W 0.00821362) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |

## gemm-mid, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.132888 ± 0.00096067 (W 0.00134333) | 0.16192 ± 0.000760829 (W 0.00167445) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.451422 ± 0.00277054 (W 0.00247872) | 0.53794 ± 0.00164359 (W 0.00327142) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 1.0719 ± 0.0048323 (W 0.00145397) | 1.26107 ± 0.00852888 (W 0.00322083) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 3.59434 ± 0.0153358 (W 0.00626238) | 4.22625 ± 0.0113994 (W 0.00767596) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 8.53914 ± 0.0381601 (W 0.00884105) | 10.0531 ± 0.0309191 (W 0.0135926) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 29.3136 ± 0.0580483 (W 0.0546066) | 33.7118 ± 0.118934 (W 0.0398965) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |

## gemm-mid, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.045361 ± 0.000335545 (W 0.000229316) | 0.0508515 ± 0.00046456 (W 0.00137355) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.12045 ± 0.000776008 (W 0.00125278) | 0.148878 ± 0.000792729 (W 0.00177071) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 0.290441 ± 0.000613905 (W 0.00139064) | 0.341434 ± 0.00386631 (W 0.00203682) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 0.916626 ± 0.00301345 (W 0.00309326) | 1.0993 ± 0.00556351 (W 0.00336551) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 2.20787 ± 0.00680935 (W 0.00409574) | 2.58148 ± 0.00843507 (W 0.00500358) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 7.52221 ± 0.0274897 (W 0.00753221) | 8.71743 ± 0.0278841 (W 0.00856253) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |

## gemm-mid, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.0325085 ± 0.00055065 (W 0.00104777) | 0.029673 ± 0.000471095 (W 0.00027712) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.0864275 ± 0.000354168 (W 0.00105981) | 0.0843855 ± 0.000685416 (W 0.00132085) | · |  |
| `gemm/256x256x256/b1` | 0.165326 ± 0.00159892 (W 0.000987455) | 0.184702 ± 0.00122857 (W 0.00165879) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 0.478826 ± 0.00194389 (W 0.00317149) | 0.556261 ± 0.00215096 (W 0.00337143) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 1.14187 ± 0.00303346 (W 0.00288615) | 1.32334 ± 0.00698836 (W 0.0042974) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 3.91546 ± 0.0144138 (W 0.00853203) | 4.55394 ± 0.00825336 (W 0.00745621) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |

## gemm-mid, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.537829 ± 0.00225704 (W 0.00271558) | 0.656096 ± 0.00358284 (W 0.00266186) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 1.81002 ± 0.00766828 (W 0.00303682) | 2.17341 ± 0.00699668 (W 0.0031243) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 4.26452 ± 0.0167913 (W 0.00563729) | 5.16635 ± 0.0110118 (W 0.00842242) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 14.378 ± 0.0667784 (W 0.0208069) | 17.3057 ± 0.053946 (W 0.0196326) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 34.1874 ± 0.0961976 (W 0.0398427) | 40.9857 ± 0.121182 (W 0.0440944) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 116.052 ± 0.4018 (W 0.073922) | 137.459 ± 0.283213 (W 0.210407) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |

## gemm-mid, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.153404 ± 0.000710819 (W 0.000508496) | 0.17755 ± 0.000610243 (W 0.00149033) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.457765 ± 0.00218252 (W 0.00245497) | 0.560674 ± 0.00307462 (W 0.0021234) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 1.11155 ± 0.00418319 (W 0.00244904) | 1.33171 ± 0.00521871 (W 0.00404396) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 3.63251 ± 0.0138376 (W 0.00559401) | 4.40688 ± 0.0170425 (W 0.00717352) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 8.6644 ± 0.027728 (W 0.0139379) | 10.4508 ± 0.0359053 (W 0.0103758) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 29.4225 ± 0.120534 (W 0.0257215) | 34.9137 ± 0.0811343 (W 0.0350261) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |

## gemm-mid, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.102671 ± 0.000282003 (W 0.000502552) | 0.0945215 ± 0.000698406 (W 0.00180808) | 🔴 faer-fork 1.09× slower than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.236762 ± 0.002048 (W 0.0016868) | 0.295848 ± 0.000352565 (W 0.00220161) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 0.583331 ± 0.000961871 (W 0.00186339) | 0.685885 ± 0.00225901 (W 0.00331075) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 1.83837 ± 0.0039352 (W 0.00382267) | 2.20788 ± 0.00364174 (W 0.00376577) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 4.45683 ± 0.00642013 (W 0.0110839) | 5.27925 ± 0.00924759 (W 0.00826985) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 14.9827 ± 0.0889047 (W 0.0184139) | 17.7862 ± 0.0210714 (W 0.0318238) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |

## gemm-mid, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.53811 ± 0.00283668 (W 0.00230045) | 0.65759 ± 0.00315275 (W 0.00237356) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 1.80642 ± 0.00945544 (W 0.00306199) | 2.17021 ± 0.00532908 (W 0.00520213) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 4.27737 ± 0.0215094 (W 0.00676603) | 5.15902 ± 0.0122859 (W 0.00860368) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 14.393 ± 0.0631729 (W 0.0176631) | 17.2779 ± 0.0409029 (W 0.0238397) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 34.137 ± 0.101318 (W 0.0370394) | 40.9765 ± 0.106571 (W 0.0410419) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 115.828 ± 0.404008 (W 0.138689) | 137.444 ± 0.331319 (W 0.106258) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |

## gemm-mid, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.153832 ± 0.00076615 (W 0.00059461) | 0.178507 ± 0.00107135 (W 0.00182772) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.458963 ± 0.00289333 (W 0.00231144) | 0.558827 ± 0.00154591 (W 0.00273658) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 1.11313 ± 0.00512693 (W 0.00315364) | 1.33195 ± 0.00443512 (W 0.00402253) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 3.62781 ± 0.0113584 (W 0.00525415) | 4.40729 ± 0.0171445 (W 0.00379542) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 8.65385 ± 0.0326678 (W 0.0111595) | 10.4454 ± 0.0413736 (W 0.00948014) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 29.4485 ± 0.102691 (W 0.0177035) | 34.8354 ± 0.107739 (W 0.0261212) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |

## gemm-mid, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/128x128x128/b1` | 0.103577 ± 0.000704135 (W 0.000599415) | 0.09469 ± 0.000274866 (W 0.00127263) | 🔴 faer-fork 1.09× slower than `lapack-openblas` |  |
| `gemm/192x192x192/b1` | 0.236863 ± 0.00171081 (W 0.00188697) | 0.296679 ± 0.000955429 (W 0.00317653) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `gemm/256x256x256/b1` | 0.583011 ± 0.00116989 (W 0.00241993) | 0.687153 ± 0.00225147 (W 0.00320429) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `gemm/384x384x384/b1` | 1.83372 ± 0.00431073 (W 0.00390834) | 2.20446 ± 0.00167712 (W 0.0023516) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/512x512x512/b1` | 4.46028 ± 0.0100496 (W 0.0104638) | 5.295 ± 0.0106349 (W 0.0109473) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `gemm/768x768x768/b1` | 15.008 ± 0.0255988 (W 0.0143249) | 17.8024 ± 0.144575 (W 0.0140154) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |

## gemm-tall, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.25596 ± 0.0145658 (W 0.00793935) | 1.64013 ± 0.00827154 (W 0.00591399) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 1.08505 ± 0.0295084 (W 0.00769889) | 1.44299 ± 0.00872799 (W 0.00976063) | 🔵 faer-fork 1.33× faster than `lapack-openblas` | `!` between-start range over 5% |
| `gemm/4096x64x64/b1` | 1.08216 ± 0.0372595 (W 0.00341485) | 1.36286 ± 0.00888399 (W 0.00428437) | 🔵 faer-fork 1.26× faster than `lapack-openblas` | `!` between-start range over 5% |

## gemm-tall, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.422601 ± 0.00363293 (W 0.0047421) | 0.50805 ± 0.00257456 (W 0.00447548) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 0.310038 ± 0.00238138 (W 0.00313494) | 0.472744 ± 0.00217699 (W 0.00664222) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 0.278555 ± 0.00111847 (W 0.00177107) | 0.347342 ± 0.00168353 (W 0.00246929) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |

## gemm-tall, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.424032 ± 0.00252201 (W 0.00311732) | 0.275747 ± 0.0073957 (W 0.00364737) | 🔴 faer-fork 1.54× slower than `lapack-openblas` | `!` between-start range over 5% |
| `gemm/4096x16x240/b1` | 0.186087 ± 0.00176506 (W 0.00242505) | 0.312565 ± 0.00173625 (W 0.00199258) | 🔵 faer-fork 1.68× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 0.14228 ± 2.4225 (W 0.00186102) | 0.17914 ± 1.1356 (W 0.00165873) | · | `!` between-start range over 5%; `p` position effect over 5% |

## gemm-tall, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.0416 ± 0.00651706 (W 0.00295486) | 1.68995 ± 0.01268 (W 0.00586597) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 1.11431 ± 0.0167889 (W 0.00594382) | 1.42932 ± 0.00563774 (W 0.00826421) | 🔵 faer-fork 1.28× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 1.1302 ± 0.00486328 (W 0.0031008) | 1.37633 ± 0.00524463 (W 0.00301896) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |

## gemm-tall, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.328541 ± 0.00157686 (W 0.00338946) | 0.424793 ± 0.00331904 (W 0.00296466) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 0.294162 ± 0.00106479 (W 0.00249158) | 0.47832 ± 0.00456535 (W 0.00305855) | 🔵 faer-fork 1.63× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 0.295766 ± 0.00142651 (W 0.0018392) | 0.363077 ± 0.00130594 (W 0.00252114) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |

## gemm-tall, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.198916 ± 0.00283715 (W 0.00396167) | 0.224129 ± 0.001176 (W 0.00238834) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 0.180612 ± 0.00237969 (W 0.00248961) | 0.323051 ± 0.00345854 (W 0.00197171) | 🔵 faer-fork 1.79× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 0.156262 ± 0.00105032 (W 0.00123275) | 0.195375 ± 0.00254104 (W 0.00202671) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |

## gemm-tall, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 4.14053 ± 0.00792244 (W 0.00954674) | 5.96714 ± 0.0268208 (W 0.0119933) | 🔵 faer-fork 1.44× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 4.41096 ± 0.0542419 (W 0.0151784) | 5.75156 ± 0.0159362 (W 0.0171932) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 4.39837 ± 0.0261353 (W 0.008913) | 5.41073 ± 0.326404 (W 0.00803882) | 🔵 faer-fork 1.23× faster than `lapack-openblas` | `!` between-start range over 5% |

## gemm-tall, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.65207 ± 0.0051844 (W 0.00413374) | 1.74641 ± 0.0270347 (W 0.00680133) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 1.15397 ± 0.00726117 (W 0.00549046) | 1.67554 ± 0.00337966 (W 0.00752232) | 🔵 faer-fork 1.45× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 1.11857 ± 0.00432769 (W 0.00357974) | 1.38928 ± 0.0055721 (W 0.00362706) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |

## gemm-tall, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.890749 ± 0.0141099 (W 0.016067) | 0.944441 ± 0.00634588 (W 0.010085) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 0.593649 ± 0.00947859 (W 0.00273585) | 1.00106 ± 0.00439987 (W 0.0100172) | 🔵 faer-fork 1.69× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 0.572237 ± 0.00349794 (W 0.00307751) | 0.702155 ± 0.00305924 (W 0.00356793) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |

## gemm-tall, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 4.07123 ± 0.0271082 (W 0.008001) | 5.77704 ± 0.0240042 (W 0.0138863) | 🔵 faer-fork 1.42× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 4.38648 ± 0.0319686 (W 0.0126446) | 5.74978 ± 0.0336683 (W 0.0178875) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 4.43969 ± 0.0167652 (W 0.0170818) | 5.53231 ± 0.0111274 (W 0.00847649) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |

## gemm-tall, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 1.18949 ± 0.00306926 (W 0.00441576) | 1.50626 ± 0.00311233 (W 0.00739226) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 1.15655 ± 0.00635541 (W 0.00281495) | 1.74429 ± 0.0111178 (W 0.00488142) | 🔵 faer-fork 1.51× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 1.17435 ± 0.0101203 (W 0.00724448) | 1.45433 ± 0.00640339 (W 0.00332459) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |

## gemm-tall, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/16x4096x240/b1` | 0.660546 ± 0.00410756 (W 0.004325) | 0.824714 ± 0.00501701 (W 0.00792359) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `gemm/4096x16x240/b1` | 0.596129 ± 0.00782654 (W 0.00334706) | 1.00556 ± 0.00153555 (W 0.00453691) | 🔵 faer-fork 1.69× faster than `lapack-openblas` |  |
| `gemm/4096x64x64/b1` | 0.580639 ± 0.00533748 (W 0.00443736) | 0.771915 ± 0.00459779 (W 0.00417088) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |

## gemm-wide, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.11874 ± 0.00902068 (W 0.00269244) | 1.36999 ± 0.00791924 (W 0.00380974) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |

## gemm-wide, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.295654 ± 0.00115574 (W 0.00206327) | 0.36313 ± 0.00149354 (W 0.00199908) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |

## gemm-wide, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.155338 ± 2.36897 (W 0.00166234) | 0.195796 ± 0.001177 (W 0.00142478) | · | `!` between-start range over 5%; `p` position effect over 5% |

## gemm-wide, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.08625 ± 0.0060309 (W 0.00235989) | 1.36056 ± 0.00516724 (W 0.0038932) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |

## gemm-wide, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.277438 ± 0.00163541 (W 0.00155631) | 0.345309 ± 0.00155173 (W 0.00241394) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |

## gemm-wide, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.141928 ± 0.000707295 (W 0.00156621) | 0.179381 ± 0.00161886 (W 0.00201195) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |

## gemm-wide, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 4.4235 ± 0.0150453 (W 0.0109812) | 5.53721 ± 0.0170668 (W 0.00865196) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |

## gemm-wide, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.15738 ± 0.0032257 (W 0.00262384) | 1.4474 ± 0.0531505 (W 0.00371445) | 🔵 faer-fork 1.25× faster than `lapack-openblas` | `!` between-start range over 5% |

## gemm-wide, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.573746 ± 0.00192316 (W 0.00371482) | 0.768713 ± 0.00448705 (W 0.00391546) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |

## gemm-wide, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 4.37538 ± 0.0204815 (W 0.00907847) | 5.41051 ± 0.0177982 (W 0.0139876) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |

## gemm-wide, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 1.11497 ± 0.00510414 (W 0.00379464) | 1.39023 ± 0.00854724 (W 0.00328806) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |

## gemm-wide, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/64x64x4096/b1` | 0.569186 ± 0.00313349 (W 0.00268593) | 0.699172 ± 0.00294191 (W 0.0032879) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |

## linalg-small, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.0031765 ± 1.88724e-05 (W 2.44872e-05) | 0.0043285 ± 6.44994e-05 (W 2.75784e-05) | 🔵 faer-fork 1.36× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.0145875 ± 0.0014047 (W 7.80908e-05) | 0.0191545 ± 0.000126462 (W 8.51745e-05) | 🔵 faer-fork 1.31× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.0308425 ± 0.00148562 (W 7.11645e-05) | 0.044745 ± 0.000305157 (W 0.000136174) | 🔵 faer-fork 1.45× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.111946 ± 0.000520286 (W 0.00141777) | 0.122864 ± 0.000829224 (W 0.00156694) | 🔵 faer-fork 1.10× faster than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.494557 ± 0.00336101 (W 0.00250703) | 0.435005 ± 0.00193095 (W 0.0021) | 🔴 faer-fork 1.14× slower than `lapack-openblas` |  |
| `eigh/n96/b1` | 1.2008 ± 0.00384999 (W 0.00264523) | 0.968679 ± 0.00387185 (W 0.00273103) | 🔴 faer-fork 1.24× slower than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.012934 ± 0.000128173 (W 7.35869e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.05399 ± 0.000148966 (W 0.000242016) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.149563 ± 0.00089496 (W 0.0023945) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.008311 ± 5.21562e-05 (W 7.53883e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.008366 ± 4.77092e-05 (W 7.60011e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.041054 ± 0.000116496 (W 8.70634e-05) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0411545 ± 0.000504564 (W 0.00010531) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.122397 ± 0.000399711 (W 0.00183895) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.121983 ± 0.000499179 (W 0.000183183) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.0090375 ± 6.70564e-05 (W 7.76424e-05) | 0.0102895 ± 0.000376295 (W 0.000105189) | 🔵 faer-fork 1.14× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.032406 ± 0.000195855 (W 0.000116866) | 0.0395005 ± 0.000591974 (W 0.00011471) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.078706 ± 0.000363532 (W 0.00221129) | 0.0986745 ± 0.00108574 (W 0.00134543) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.0319205 ± 0.00043978 (W 0.00018034) | 0.032554 ± 0.000612764 (W 0.00014996) | · |  |
| `qr/n64/b1` | 0.114872 ± 0.00103033 (W 0.00166371) | 0.12875 ± 0.00286497 (W 0.00106089) | 🔵 faer-fork 1.12× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n96/b1` | 0.276928 ± 0.0108092 (W 0.00301373) | 0.372505 ± 0.00373089 (W 0.00222663) | 🔵 faer-fork 1.35× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n32/b1` | 0.023074 ± 0.000218408 (W 6.1418e-05) | 0.017503 ± 0.000441852 (W 0.000112232) | 🔴 faer-fork 1.32× slower than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n64/b1` | 0.0823155 ± 0.00081849 (W 0.000235915) | 0.0666245 ± 0.000827566 (W 0.000252289) | 🔴 faer-fork 1.24× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.178671 ± 0.00144449 (W 0.00199148) | 0.185248 ± 0.00214617 (W 0.00200568) | · |  |
| `solve/n32/b1` | 0.0103195 ± 0.000109283 (W 5.40098e-05) | 0.0101935 ± 0.000184866 (W 3.80968e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.033686 ± 0.000137309 (W 0.000119091) | 0.038983 ± 0.000738546 (W 9.61656e-05) | 🔵 faer-fork 1.16× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.0831415 ± 0.000178926 (W 0.00255376) | 0.0908435 ± 0.00172343 (W 0.000921054) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.168264 ± 0.00135814 (W 0.00179126) | 0.185051 ± 0.00161296 (W 0.00198565) | 🔵 faer-fork 1.10× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 0.861984 ± 0.00393192 (W 0.00236516) | 0.674683 ± 0.00329327 (W 0.00447141) | 🔴 faer-fork 1.28× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.05908 ± 0.0323231 (W 0.00575954) | 1.62587 ± 0.0107467 (W 0.00432733) | 🔴 faer-fork 1.27× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.0672475 ± 0.000697489 (W 0.000246106) | 0.0774815 ± 0.000426378 (W 0.000944652) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.238681 ± 0.00422083 (W 0.00185242) | 0.273492 ± 0.00299334 (W 0.0021368) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.54442 ± 0.00420732 (W 0.00256202) | 0.666409 ± 0.00223884 (W 0.00201407) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.000716 ± 8.16497e-06 (W 1.63932e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.001613 ± 8.94427e-06 (W 2.36634e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.002785 ± 9.69407e-05 (W 2.13818e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003186 ± 2.33809e-05 (W 3.22234e-05) | 0.004318 ± 2.4988e-05 (W 4.60824e-05) | 🔵 faer-fork 1.36× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014763 ± 7.08569e-05 (W 2.80469e-05) | 0.01904 ± 0.000107949 (W 0.000674109) | 🔵 faer-fork 1.29× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.0312435 ± 0.00115068 (W 7.06078e-05) | 0.044444 ± 0.000287354 (W 0.000159766) | 🔵 faer-fork 1.42× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.113659 ± 0.000547665 (W 0.000200885) | 0.106743 ± 0.000645728 (W 0.00145217) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.487698 ± 0.00162592 (W 0.00195509) | 0.359901 ± 0.00212143 (W 0.00232479) | 🔴 faer-fork 1.36× slower than `lapack-openblas` |  |
| `eigh/n96/b1` | 1.16587 ± 0.00141434 (W 0.002788) | 0.784055 ± 0.00177319 (W 0.00163861) | 🔴 faer-fork 1.49× slower than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.0141865 ± 0.000156138 (W 0.000113907) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.056091 ± 0.000699567 (W 0.000226047) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.166109 ± 0.00317294 (W 0.00273486) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.006161 ± 0.000393145 (W 0.000139121) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.0067625 ± 0.000402583 (W 0.000269033) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.0192005 ± 0.000208928 (W 0.000230643) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0208035 ± 0.000294446 (W 0.000359145) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.044142 ± 0.000325565 (W 0.000318313) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.046048 ± 0.000396961 (W 0.000530317) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.0091065 ± 7.81563e-05 (W 9.91481e-05) | 0.0101545 ± 0.000209238 (W 0.000145376) | 🔵 faer-fork 1.12× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0324215 ± 0.000269083 (W 0.000188644) | 0.039038 ± 0.000413395 (W 0.000118289) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.0786785 ± 0.000985549 (W 0.001017) | 0.099252 ± 0.00236281 (W 0.00248146) | 🔵 faer-fork 1.26× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n32/b1` | 0.033232 ± 0.000162731 (W 0.000186424) | 0.032917 ± 0.000663276 (W 0.000121889) | · |  |
| `qr/n64/b1` | 0.109103 ± 0.000857121 (W 0.00181653) | 0.128086 ± 0.00228615 (W 0.00186884) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.23731 ± 0.00145507 (W 0.00323185) | 0.374876 ± 0.00264906 (W 0.00256636) | 🔵 faer-fork 1.58× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.023718 ± 0.000171618 (W 9.70144e-05) | 0.017573 ± 0.000441391 (W 0.000114178) | 🔴 faer-fork 1.35× slower than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n64/b1` | 0.0735935 ± 0.000472531 (W 0.00103684) | 0.0668105 ± 0.000954633 (W 0.000851767) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.146257 ± 0.00151051 (W 0.00105979) | 0.183742 ± 0.00171244 (W 0.00197154) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.0108555 ± 8.75551e-05 (W 9.06748e-05) | 0.0102995 ± 0.000290596 (W 5.05725e-05) | 🔴 faer-fork 1.05× slower than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.034299 ± 0.000198777 (W 0.000210768) | 0.0389325 ± 0.00118043 (W 7.47573e-05) | 🔵 faer-fork 1.14× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.088202 ± 0.00202679 (W 0.00254426) | 0.0908495 ± 0.00153871 (W 0.000235709) | · | `!` between-start range over 5% |
| `svd_thin/n32/b1` | 0.171389 ± 0.000896645 (W 0.000891212) | 0.184319 ± 0.00132788 (W 0.00184518) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 0.850958 ± 0.00345341 (W 0.00227158) | 0.641211 ± 0.00812133 (W 0.00344758) | 🔴 faer-fork 1.33× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.05147 ± 0.0101728 (W 0.00589455) | 1.61382 ± 0.0105224 (W 0.00422276) | 🔴 faer-fork 1.27× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.068604 ± 0.000571859 (W 0.000162502) | 0.0776915 ± 0.000294324 (W 0.00014221) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.242513 ± 0.00175028 (W 0.00173501) | 0.273176 ± 0.00180392 (W 0.00252189) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.579473 ± 0.00199986 (W 0.00257477) | 0.654952 ± 0.00618225 (W 0.00265443) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.000942 ± 2.46367e-05 (W 1.76638e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002059 ± 3.01662e-05 (W 1.53643e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003752 ± 5.64506e-05 (W 2.62508e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003181 ± 2.74056e-05 (W 3.965e-05) | 0.0043485 ± 6.56526e-05 (W 5.04845e-05) | 🔵 faer-fork 1.37× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014752 ± 0.00113014 (W 3.03597e-05) | 0.0189205 ± 0.00022467 (W 7.96048e-05) | 🔵 faer-fork 1.28× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.031278 ± 0.0012401 (W 5.68461e-05) | 0.0444305 ± 0.000244794 (W 0.00017911) | 🔵 faer-fork 1.42× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.113315 ± 0.000577848 (W 0.000230363) | 0.104532 ± 0.000161981 (W 0.00150654) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.48744 ± 0.000846433 (W 0.00219082) | 0.351024 ± 0.00271752 (W 0.00191593) | 🔴 faer-fork 1.39× slower than `lapack-openblas` |  |
| `eigh/n96/b1` | 1.16579 ± 0.00325573 (W 0.00248064) | 0.764459 ± 0.00195118 (W 0.00202729) | 🔴 faer-fork 1.52× slower than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.0140655 ± 0.000169696 (W 0.000110749) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.0562365 ± 0.000532424 (W 0.000722527) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.17254 ± 0.00130141 (W 0.00253605) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.0061065 ± 0.00064909 (W 0.000154638) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.0062265 ± 0.000342801 (W 0.000181585) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.014813 ± 0.000255524 (W 0.000196655) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0163765 ± 0.000228371 (W 0.000376886) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.031729 ± 0.000325216 (W 0.000538134) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.0322555 ± 0.000288629 (W 0.000459087) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.0091875 ± 8.34036e-05 (W 6.74706e-05) | 0.0100185 ± 0.000113878 (W 0.0001238) | 🔵 faer-fork 1.09× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.032169 ± 0.00014083 (W 0.000148261) | 0.0391965 ± 0.00116399 (W 0.000117822) | 🔵 faer-fork 1.22× faster than `lapack-openblas` | `!` between-start range over 5% |
| `lu/n96/b1` | 0.080292 ± 0.00277426 (W 0.00232576) | 0.0972135 ± 0.00240615 (W 0.00258374) | 🔵 faer-fork 1.21× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n32/b1` | 0.033188 ± 0.000439884 (W 0.000161111) | 0.0321305 ± 0.000490302 (W 0.0010258) | · |  |
| `qr/n64/b1` | 0.106897 ± 0.000719865 (W 0.00203061) | 0.127628 ± 0.00125299 (W 0.00102392) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.233595 ± 0.00329704 (W 0.00323714) | 0.375312 ± 0.00599529 (W 0.00358666) | 🔵 faer-fork 1.61× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.023868 ± 0.000189021 (W 9.70533e-05) | 0.017428 ± 0.000241245 (W 8.45372e-05) | 🔴 faer-fork 1.37× slower than `lapack-openblas` |  |
| `qr_factor/n64/b1` | 0.0739015 ± 0.0007725 (W 0.000540909) | 0.065576 ± 0.000932837 (W 0.000644766) | 🔴 faer-fork 1.13× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.138635 ± 0.000916978 (W 0.00113133) | 0.184041 ± 0.00261014 (W 0.00172824) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.0108255 ± 8.25486e-05 (W 7.62523e-05) | 0.0102895 ± 0.000391937 (W 5.00447e-05) | 🔴 faer-fork 1.05× slower than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0345335 ± 0.000295632 (W 8.11052e-05) | 0.0378515 ± 0.000919062 (W 8.85981e-05) | 🔵 faer-fork 1.10× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.0910165 ± 0.00162034 (W 0.00254337) | 0.0877005 ± 0.00118157 (W 0.000302176) | · |  |
| `svd_thin/n32/b1` | 0.170868 ± 0.000942606 (W 0.000970144) | 0.183051 ± 0.00129357 (W 0.0021673) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 0.845531 ± 0.00454985 (W 0.00201353) | 0.652413 ± 0.00235707 (W 0.00317449) | 🔴 faer-fork 1.30× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.06275 ± 0.00829172 (W 0.00359652) | 1.61637 ± 0.0120341 (W 0.00370812) | 🔴 faer-fork 1.28× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.068321 ± 0.000257449 (W 0.000139741) | 0.077753 ± 0.000367087 (W 0.000181554) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.242093 ± 0.00111184 (W 0.00155243) | 0.271674 ± 0.00195923 (W 0.00234228) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.602893 ± 0.0054978 (W 0.00220093) | 0.667944 ± 0.00576968 (W 0.00278131) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.000952 ± 4.44597e-05 (W 2.24605e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002068 ± 3.01822e-05 (W 2.37307e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003422 ± 0.000127068 (W 2.29226e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003071 ± 6.9964e-05 (W 3.18644e-05) | 0.003411 ± 4.96655e-05 (W 3.88948e-05) | 🔵 faer-fork 1.11× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.014347 ± 0.00135001 (W 2.70463e-05) | 0.0157295 ± 0.000111328 (W 7.06043e-05) | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.030131 ± 0.0011989 (W 3.69386e-05) | 0.037842 ± 0.000181067 (W 0.000185734) | 🔵 faer-fork 1.26× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.111804 ± 0.00049533 (W 0.00178965) | 0.121526 ± 0.000648314 (W 0.000176834) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.494168 ± 0.00277978 (W 0.00257202) | 0.43077 ± 0.00196277 (W 0.00202048) | 🔴 faer-fork 1.15× slower than `lapack-openblas` |  |
| `eigh/n96/b1` | 1.20211 ± 0.00275025 (W 0.00264432) | 0.961472 ± 0.00502679 (W 0.00266901) | 🔴 faer-fork 1.25× slower than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.010936 ± 0.00011325 (W 6.23673e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.0471925 ± 0.00048485 (W 0.000717435) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.134205 ± 0.000947893 (W 0.00271624) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.0085265 ± 8.35498e-05 (W 4.50166e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.0085255 ± 3.95002e-05 (W 4.98184e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.0407375 ± 0.000158765 (W 0.000612814) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0407995 ± 0.000414481 (W 8.31293e-05) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.125041 ± 0.000892173 (W 0.000956007) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.124084 ± 0.000439991 (W 0.00211122) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.007254 ± 3.42389e-05 (W 5.81996e-05) | 0.0084965 ± 0.000121789 (W 0.000121137) | 🔵 faer-fork 1.17× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0260525 ± 0.000222042 (W 0.000111598) | 0.0329775 ± 0.000406189 (W 0.000136221) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.0639 ± 0.000467104 (W 0.00262856) | 0.0771035 ± 0.000471323 (W 0.00124815) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.030047 ± 0.000501808 (W 0.000190044) | 0.0293555 ± 0.000315431 (W 0.000115475) | · |  |
| `qr/n64/b1` | 0.106879 ± 0.000914498 (W 0.000376106) | 0.118777 ± 0.00128673 (W 0.000967509) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.260101 ± 0.00986758 (W 0.00272051) | 0.339001 ± 0.00200108 (W 0.00243734) | 🔵 faer-fork 1.30× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n32/b1` | 0.0163345 ± 0.000256776 (W 0.000105146) | 0.0160545 ± 0.000298103 (W 8.89384e-05) | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `qr_factor/n64/b1` | 0.066236 ± 0.000429715 (W 0.000270129) | 0.0610115 ± 0.000898997 (W 0.000881238) | 🔴 faer-fork 1.09× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.143361 ± 0.00186448 (W 0.0021661) | 0.170227 ± 0.00112877 (W 0.00168506) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.008206 ± 0.000101498 (W 5.95298e-05) | 0.0085055 ± 0.000144876 (W 4.09593e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0264305 ± 0.000204006 (W 0.000153723) | 0.032836 ± 0.00024375 (W 0.000141183) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.067633 ± 0.000349232 (W 0.00254638) | 0.0767725 ± 0.000392856 (W 0.000131385) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.170457 ± 0.000968052 (W 0.00176159) | 0.178086 ± 0.000992515 (W 0.00171483) | · |  |
| `svd_thin/n64/b1` | 0.904992 ± 0.00331487 (W 0.00210661) | 0.637199 ± 0.00268356 (W 0.00261655) | 🔴 faer-fork 1.42× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.03651 ± 0.00939554 (W 0.00600489) | 1.49244 ± 0.00513952 (W 0.00414125) | 🔴 faer-fork 1.36× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.066648 ± 0.00053282 (W 0.000187265) | 0.073512 ± 0.000232948 (W 0.0014624) | 🔵 faer-fork 1.10× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.243105 ± 0.00419822 (W 0.00185114) | 0.269176 ± 0.00122221 (W 0.0023779) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.551516 ± 0.00400281 (W 0.00264806) | 0.663009 ± 0.00311197 (W 0.00217058) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.000762 ± 1.58198e-05 (W 1.45592e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.001783 ± 1.79713e-05 (W 1.91809e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003146 ± 3.47203e-05 (W 3.84772e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003106 ± 2.87518e-05 (W 3.25909e-05) | 0.003332 ± 3.65276e-05 (W 3.2051e-05) | 🔵 faer-fork 1.07× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.0144065 ± 0.001078 (W 4.25591e-05) | 0.015484 ± 0.000124667 (W 5.15407e-05) | · | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.0303465 ± 0.00122644 (W 6.06914e-05) | 0.037453 ± 0.000202355 (W 8.73605e-05) | 🔵 faer-fork 1.23× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.113678 ± 0.000751133 (W 0.000314468) | 0.105256 ± 0.000501069 (W 0.00168886) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.4872 ± 0.00190979 (W 0.00241654) | 0.35458 ± 0.00111784 (W 0.00198087) | 🔴 faer-fork 1.37× slower than `lapack-openblas` |  |
| `eigh/n96/b1` | 1.16602 ± 0.00327806 (W 0.00359696) | 0.774697 ± 0.00264699 (W 0.00215668) | 🔴 faer-fork 1.51× slower than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.0122975 ± 9.94393e-05 (W 0.000107202) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.0496535 ± 0.000429538 (W 0.000290468) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.149925 ± 0.00170744 (W 0.00194445) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.006362 ± 0.000104387 (W 0.000148936) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.006492 ± 5.43706e-05 (W 0.000156405) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.019542 ± 0.000288024 (W 0.000267258) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0197005 ± 0.0001612 (W 0.00030288) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.044428 ± 0.000118417 (W 0.000431847) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.0446295 ± 0.000245091 (W 0.000277348) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.0073385 ± 6.63345e-05 (W 6.5262e-05) | 0.0084505 ± 0.000123479 (W 9.79505e-05) | 🔵 faer-fork 1.15× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0261475 ± 0.000143451 (W 0.000144921) | 0.033013 ± 0.000364933 (W 0.000144491) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.0648865 ± 0.000593531 (W 0.00194428) | 0.076777 ± 0.000317075 (W 0.00172662) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.031219 ± 0.000406527 (W 0.000124708) | 0.0297245 ± 0.000199224 (W 0.000122148) | · |  |
| `qr/n64/b1` | 0.100558 ± 0.00102796 (W 0.000457631) | 0.117211 ± 0.000691341 (W 0.000410265) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.219025 ± 0.00147097 (W 0.00354046) | 0.341089 ± 0.00222085 (W 0.00214757) | 🔵 faer-fork 1.56× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.017021 ± 0.000124277 (W 8.79472e-05) | 0.015939 ± 0.000121971 (W 8.22948e-05) | 🔴 faer-fork 1.07× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `qr_factor/n64/b1` | 0.06632 ± 0.000626638 (W 0.000323259) | 0.0601025 ± 0.00101783 (W 0.000903592) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.129172 ± 0.00130275 (W 0.000497881) | 0.17151 ± 0.0015943 (W 0.00171242) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.0086655 ± 6.31432e-05 (W 5.44221e-05) | 0.008556 ± 5.96344e-05 (W 2.86941e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0274615 ± 0.00017945 (W 0.000112443) | 0.0324915 ± 0.00029879 (W 8.42349e-05) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.0731745 ± 0.00144877 (W 0.00207606) | 0.0758285 ± 0.00033385 (W 0.000123754) | · | `!` between-start range over 5% |
| `svd_thin/n32/b1` | 0.17236 ± 0.00101549 (W 0.00132586) | 0.176758 ± 0.00105144 (W 0.00161244) | · |  |
| `svd_thin/n64/b1` | 0.894703 ± 0.00462754 (W 0.00197705) | 0.619355 ± 0.00215568 (W 0.00278726) | 🔴 faer-fork 1.44× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.02144 ± 0.0359446 (W 0.00381958) | 1.48148 ± 0.00777243 (W 0.00354642) | 🔴 faer-fork 1.36× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.067337 ± 0.000576608 (W 0.000231543) | 0.0736295 ± 0.000311802 (W 0.000110026) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.245982 ± 0.001294 (W 0.00155715) | 0.265261 ± 0.00177065 (W 0.00205005) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.589306 ± 0.001535 (W 0.00230712) | 0.654968 ± 0.00370466 (W 0.00265324) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.000957 ± 9.83192e-06 (W 2.41225e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.002169 ± 1.18771e-05 (W 4.17559e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.003777 ± 4.08542e-05 (W 6.32284e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.003111 ± 0.000127641 (W 3.0321e-05) | 0.0034165 ± 4.88156e-05 (W 3.13814e-05) | 🔵 faer-fork 1.10× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.0144165 ± 0.00119364 (W 2.87119e-05) | 0.0157595 ± 0.000159496 (W 0.000110075) | 🔵 faer-fork 1.09× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n96/b1` | 0.0303065 ± 0.00166948 (W 7.38819e-05) | 0.037429 ± 0.000321898 (W 0.000179687) | 🔵 faer-fork 1.24× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.112897 ± 0.000390564 (W 0.000154052) | 0.103276 ± 0.000387159 (W 0.00170408) | 🔴 faer-fork 1.09× slower than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.487526 ± 0.000893975 (W 0.0020416) | 0.347904 ± 0.0017725 (W 0.00176438) | 🔴 faer-fork 1.40× slower than `lapack-openblas` |  |
| `eigh/n96/b1` | 1.16726 ± 0.0029812 (W 0.00193691) | 0.754628 ± 0.00229998 (W 0.0019849) | 🔴 faer-fork 1.55× slower than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.0121575 ± 0.000261499 (W 8.11064e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.0496785 ± 0.000387584 (W 0.000347946) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.158455 ± 0.00242807 (W 0.00226696) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.005761 ± 7.23298e-05 (W 0.000127386) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.0057705 ± 7.18259e-05 (W 0.000103814) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.0147575 ± 0.000177875 (W 0.000219223) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0147575 ± 9.69297e-05 (W 0.00028921) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.0304225 ± 0.00035755 (W 0.000434593) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.0304525 ± 0.000152898 (W 0.000368961) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.007324 ± 9.28238e-05 (W 9.13967e-05) | 0.008326 ± 0.000151422 (W 9.75666e-05) | 🔵 faer-fork 1.14× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.025839 ± 0.000290066 (W 0.000154104) | 0.0331975 ± 0.00024399 (W 0.000112994) | 🔵 faer-fork 1.28× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.065418 ± 0.425246 (W 0.00237626) | 0.0766815 ± 0.000296833 (W 0.00151061) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n32/b1` | 0.031152 ± 0.000311228 (W 0.000171318) | 0.0293235 ± 0.000206122 (W 0.000149322) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.0999235 ± 0.000388202 (W 0.00041582) | 0.117569 ± 0.00123449 (W 0.00034239) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.215057 ± 0.00167283 (W 0.00377721) | 0.342594 ± 0.00262663 (W 0.00238922) | 🔵 faer-fork 1.59× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.016991 ± 0.000145255 (W 8.91802e-05) | 0.015925 ± 0.000164286 (W 8.26411e-05) | 🔴 faer-fork 1.07× slower than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `qr_factor/n64/b1` | 0.0665825 ± 0.000593562 (W 0.000345987) | 0.060358 ± 0.000553125 (W 0.00184068) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.128493 ± 0.0011959 (W 0.000381131) | 0.173669 ± 0.00169285 (W 0.00140389) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.008756 ± 7.94743e-05 (W 6.5105e-05) | 0.0085315 ± 6.82781e-05 (W 3.45698e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0274445 ± 0.00038783 (W 9.59142e-05) | 0.0324565 ± 0.000312588 (W 9.40076e-05) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.0758325 ± 0.00196885 (W 0.00250958) | 0.0756195 ± 0.000459115 (W 0.000177288) | · | `!` between-start range over 5% |
| `svd_thin/n32/b1` | 0.172482 ± 0.000602475 (W 0.00114032) | 0.177795 ± 0.00132729 (W 0.0017836) | · |  |
| `svd_thin/n64/b1` | 0.889389 ± 0.00470851 (W 0.00190276) | 0.630359 ± 0.00963121 (W 0.00237866) | 🔴 faer-fork 1.41× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.03399 ± 0.03944 (W 0.00154144) | 1.47949 ± 0.00329138 (W 0.00331529) | 🔴 faer-fork 1.37× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.067355 ± 0.000346231 (W 0.000112973) | 0.0736095 ± 0.000434833 (W 0.000947058) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.24645 ± 0.00147203 (W 0.00167447) | 0.265109 ± 0.00198654 (W 0.00242572) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.608742 ± 0.00575193 (W 0.00194714) | 0.665536 ± 0.00658511 (W 0.00216469) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.000952 ± 2.31661e-05 (W 2.23772e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.0021785 ± 2.30687e-05 (W 2.19436e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.0035865 ± 5.95441e-05 (W 2.31177e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.0052995 ± 4.30368e-05 (W 2.71218e-05) | 0.006943 ± 5.60015e-05 (W 4.88187e-05) | 🔵 faer-fork 1.31× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030828 ± 0.00019949 (W 0.000118736) | 0.0397795 ± 0.000109343 (W 0.00026851) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `cholesky/n96/b1` | 0.086498 ± 0.000428852 (W 0.000231607) | 0.0960775 ± 0.000356305 (W 0.00170004) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `eigh/n32/b1` | 0.142064 ± 0.000817785 (W 0.000900873) | 0.153782 ± 0.00081686 (W 0.00164251) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.66369 ± 0.00217313 (W 0.00311895) | 0.660249 ± 0.00233493 (W 0.00291989) | · |  |
| `eigh/n96/b1` | 1.65706 ± 0.00482375 (W 0.00370405) | 1.66024 ± 0.00346662 (W 0.00344549) | · |  |
| `full_piv_lu/n32/b1` | 0.019006 ± 0.000235526 (W 0.000105348) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.100811 ± 0.000396062 (W 0.000984709) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.286079 ± 0.00117328 (W 0.00182371) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.028554 ± 0.000177592 (W 0.000116889) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.028534 ± 0.000217355 (W 9.46623e-05) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.159859 ± 0.000513512 (W 0.00178963) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.160587 ± 0.000522002 (W 0.00197611) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.471003 ± 0.0035283 (W 0.000844309) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.47232 ± 0.00355673 (W 0.000935732) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.013415 ± 7.26021e-05 (W 0.00011072) | 0.014055 ± 0.000123179 (W 9.19206e-05) | · | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0589445 ± 0.000351111 (W 0.000126126) | 0.067743 ± 0.000125844 (W 0.00194383) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.153645 ± 0.000718987 (W 0.00136123) | 0.179819 ± 0.00113827 (W 0.00191854) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.0692215 ± 0.000416391 (W 0.000457833) | 0.05457 ± 0.000330533 (W 0.00174856) | 🔴 faer-fork 1.27× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.311984 ± 0.00115416 (W 0.0019117) | 0.264339 ± 0.00283229 (W 0.00223488) | 🔴 faer-fork 1.18× slower than `lapack-openblas` |  |
| `qr/n96/b1` | 0.759745 ± 0.00257488 (W 0.00241282) | 0.726504 ± 0.00327446 (W 0.00248604) | · |  |
| `qr_factor/n32/b1` | 0.040052 ± 0.000254296 (W 0.00177885) | 0.0302205 ± 0.000246746 (W 5.84164e-05) | 🔴 faer-fork 1.33× slower than `lapack-openblas` |  |
| `qr_factor/n64/b1` | 0.170372 ± 0.000338738 (W 0.00181803) | 0.138742 ± 0.00136443 (W 0.00107657) | 🔴 faer-fork 1.23× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.409618 ± 0.00237392 (W 0.00257404) | 0.370981 ± 0.00191157 (W 0.00255997) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `solve/n32/b1` | 0.014581 ± 0.000136847 (W 5.33453e-05) | 0.0154635 ± 4.74275e-05 (W 5.63982e-05) | 🔵 faer-fork 1.06× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.060233 ± 0.000204541 (W 9.64242e-05) | 0.0723255 ± 0.000582262 (W 0.00156713) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.156585 ± 0.00117736 (W 0.00190115) | 0.187523 ± 0.00068033 (W 0.0024454) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.220974 ± 0.000935715 (W 0.00231642) | 0.229889 ± 0.00176491 (W 0.00172366) | · |  |
| `svd_thin/n64/b1` | 1.16832 ± 0.00486017 (W 0.00381389) | 0.966245 ± 0.00751369 (W 0.00328541) | 🔴 faer-fork 1.21× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 3.01097 ± 0.00780591 (W 0.006419) | 2.65106 ± 0.095563 (W 0.00553088) | 🔴 faer-fork 1.14× slower than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/n32/b1` | 0.0842135 ± 0.000872884 (W 0.000319802) | 0.103153 ± 0.00039505 (W 0.000274968) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.346907 ± 0.00174615 (W 0.00254647) | 0.408871 ± 0.00239039 (W 0.00236769) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.866408 ± 0.00253307 (W 0.00311164) | 1.02845 ± 0.00748912 (W 0.00308118) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.0011675 ± 8.01041e-06 (W 1.5021e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.0029 ± 2.62329e-05 (W 2.33115e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.005225 ± 5.25119e-05 (W 3.8847e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.0052945 ± 0.000160836 (W 3.59684e-05) | 0.006898 ± 4.40927e-05 (W 6.69063e-05) | 🔵 faer-fork 1.30× faster than `lapack-openblas` | `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030716 ± 0.000305601 (W 0.000112269) | 0.0442445 ± 0.00328004 (W 0.000502809) | 🔵 faer-fork 1.44× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `cholesky/n96/b1` | 0.080328 ± 0.000296567 (W 0.000394459) | 0.09294 ± 0.000532039 (W 0.000859628) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `eigh/n32/b1` | 0.138863 ± 0.000475445 (W 0.000214848) | 0.139361 ± 0.000619606 (W 0.000769984) | · |  |
| `eigh/n64/b1` | 0.574837 ± 0.00199813 (W 0.00216222) | 0.577419 ± 0.00345321 (W 0.00211603) | · |  |
| `eigh/n96/b1` | 1.36501 ± 0.00457882 (W 0.00271108) | 1.64632 ± 0.00498021 (W 0.00445284) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.0200485 ± 0.000234591 (W 0.000103292) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n64/b1` | 0.105935 ± 0.0011449 (W 0.00144001) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.250544 ± 0.00466811 (W 0.00248594) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.014682 ± 0.000163917 (W 0.000199174) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.014793 ± 0.000358487 (W 0.00025487) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.0619945 ± 0.000394824 (W 0.000564895) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.062024 ± 0.000588491 (W 0.000423435) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.152649 ± 0.000563168 (W 0.00133081) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.152574 ± 0.000814274 (W 0.000356422) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.013365 ± 9.85008e-05 (W 0.000111426) | 0.0138655 ± 9.62725e-05 (W 9.35551e-05) | · | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.060314 ± 0.00202008 (W 0.000244344) | 0.0681075 ± 0.00030742 (W 0.000337427) | 🔵 faer-fork 1.13× faster than `lapack-openblas` | `!` between-start range over 5% |
| `lu/n96/b1` | 0.152303 ± 0.00215821 (W 0.00252728) | 0.178176 ± 0.00037565 (W 0.00192807) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.06397 ± 0.000337327 (W 0.000356434) | 0.054103 ± 0.000202702 (W 0.000953856) | 🔴 faer-fork 1.18× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.197888 ± 0.00143271 (W 0.00179124) | 0.264132 ± 0.00182185 (W 0.00235808) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.424148 ± 0.002647 (W 0.00242353) | 0.927071 ± 0.00304897 (W 0.00238228) | 🔵 faer-fork 2.19× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.039757 ± 0.000287894 (W 0.000255922) | 0.0303925 ± 0.00020141 (W 6.25041e-05) | 🔴 faer-fork 1.31× slower than `lapack-openblas` |  |
| `qr_factor/n64/b1` | 0.126168 ± 0.000547375 (W 0.000543022) | 0.137179 ± 0.00100615 (W 0.00121527) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.267396 ± 0.000887332 (W 0.00217045) | 0.471357 ± 0.00276296 (W 0.00281667) | 🔵 faer-fork 1.76× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.015143 ± 0.000144025 (W 5.7245e-05) | 0.015504 ± 9.80865e-05 (W 5.73049e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.064496 ± 0.00164298 (W 0.00140072) | 0.0719705 ± 0.000327117 (W 0.000533828) | 🔵 faer-fork 1.12× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.156737 ± 0.0172889 (W 0.00171488) | 0.187493 ± 0.0011312 (W 0.00206651) | 🔵 faer-fork 1.20× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n32/b1` | 0.215556 ± 0.00057174 (W 0.00173998) | 0.228599 ± 0.000626254 (W 0.00198628) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 1.0108 ± 0.00221162 (W 0.00196192) | 0.976258 ± 0.0021327 (W 0.00185205) | · |  |
| `svd_thin/n96/b1` | 2.51979 ± 0.00812223 (W 0.00385929) | 2.59831 ± 0.117972 (W 0.00402944) | · | `!` between-start range over 5% |
| `svd_values/n32/b1` | 0.085024 ± 0.000299096 (W 0.000164705) | 0.103353 ± 0.000406316 (W 0.000864798) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.353209 ± 0.00153519 (W 0.00207997) | 0.409938 ± 0.00177604 (W 0.00251938) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.803241 ± 0.00297827 (W 0.00225709) | 1.28327 ± 0.00443515 (W 0.00302984) | 🔵 faer-fork 1.60× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.001423 ± 2.65361e-05 (W 2.02634e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.0034515 ± 2.90218e-05 (W 2.23554e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.006001 ± 5.19833e-05 (W 2.67832e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.00534 ± 7.77972e-05 (W 6.20985e-05) | 0.006898 ± 0.000108776 (W 6.85793e-05) | 🔵 faer-fork 1.29× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.0306225 ± 0.000222231 (W 0.000141683) | 0.0423145 ± 0.000415535 (W 0.000723132) | 🔵 faer-fork 1.38× faster than `lapack-openblas` |  |
| `cholesky/n96/b1` | 0.0805985 ± 0.000398823 (W 0.000304424) | 0.098803 ± 0.00193015 (W 0.000976583) | 🔵 faer-fork 1.23× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n32/b1` | 0.139531 ± 0.000457592 (W 0.000224206) | 0.139182 ± 0.00038936 (W 0.000840081) | · |  |
| `eigh/n64/b1` | 0.567561 ± 0.00249103 (W 0.00221607) | 0.566663 ± 0.0023239 (W 0.00240716) | · |  |
| `eigh/n96/b1` | 1.33135 ± 0.00565416 (W 0.00333154) | 1.66727 ± 0.0101307 (W 0.00393369) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.020028 ± 0.000164047 (W 9.90215e-05) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n64/b1` | 0.108907 ± 0.0015603 (W 0.0013683) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.252921 ± 0.00439335 (W 0.00230921) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.010866 ± 0.000157355 (W 0.000168154) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.0113055 ± 0.00030355 (W 0.000386062) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.03715 ± 0.000283831 (W 0.000295895) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.0381825 ± 0.000268387 (W 0.000332966) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.0860675 ± 0.000928492 (W 0.000697047) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.086749 ± 0.000963781 (W 0.00128833) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.0134045 ± 0.000137567 (W 8.5502e-05) | 0.0139415 ± 9.99335e-05 (W 8.50957e-05) | · | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0636505 ± 0.000272695 (W 0.000247586) | 0.0679315 ± 0.000407444 (W 0.000392087) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.154303 ± 0.000407509 (W 0.00124803) | 0.178233 ± 0.000592074 (W 0.00152213) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.06387 ± 0.000111342 (W 0.000247979) | 0.0539365 ± 9.23849e-05 (W 0.000758382) | 🔴 faer-fork 1.18× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.184452 ± 0.00149023 (W 0.00188665) | 0.2643 ± 0.00148771 (W 0.00192863) | 🔵 faer-fork 1.43× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.36963 ± 0.00243246 (W 0.00248332) | 0.988834 ± 0.00416794 (W 0.00283239) | 🔵 faer-fork 2.68× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.0391185 ± 0.0014492 (W 0.000688393) | 0.02989 ± 0.000297957 (W 9.63183e-05) | 🔴 faer-fork 1.31× slower than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n64/b1` | 0.123075 ± 0.000652266 (W 0.00106426) | 0.137574 ± 0.00131705 (W 0.00178018) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.24408 ± 0.00182124 (W 0.00200372) | 0.504118 ± 0.0022649 (W 0.00258083) | 🔵 faer-fork 2.07× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.0151285 ± 0.000121873 (W 6.44561e-05) | 0.0153795 ± 5.06425e-05 (W 8.90144e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.066953 ± 0.000590569 (W 0.000467466) | 0.0715115 ± 0.000176996 (W 0.000279541) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.154131 ± 0.00111719 (W 0.00175716) | 0.187295 ± 0.00165968 (W 0.00205285) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.217033 ± 0.0033661 (W 0.00193453) | 0.229274 ± 0.00101581 (W 0.0019527) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 1.00138 ± 0.00672824 (W 0.00175617) | 0.971753 ± 0.0101741 (W 0.00234355) | · |  |
| `svd_thin/n96/b1` | 2.46782 ± 0.00938396 (W 0.00354027) | 2.61909 ± 0.0709261 (W 0.00418003) | 🔵 faer-fork 1.06× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/n32/b1` | 0.085491 ± 0.000385188 (W 0.00016791) | 0.102792 ± 0.000360005 (W 0.00142879) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.361465 ± 0.00115295 (W 0.00177692) | 0.407876 ± 0.00283124 (W 0.00208966) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.826169 ± 0.00263561 (W 0.00250894) | 1.37839 ± 0.00529041 (W 0.00418466) | 🔵 faer-fork 1.67× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.001433 ± 8.3666e-06 (W 1.89106e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003421 ± 3.62073e-05 (W 1.49827e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.0060315 ± 5.97852e-05 (W 4.05228e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |

## linalg-small, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.0052795 ± 0.000100566 (W 3.64517e-05) | 0.005881 ± 3.64074e-05 (W 5.81592e-05) | 🔵 faer-fork 1.11× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.0306275 ± 0.00018153 (W 8.22297e-05) | 0.0320505 ± 0.000126063 (W 0.000111325) | · |  |
| `cholesky/n96/b1` | 0.085605 ± 0.000251555 (W 0.00145274) | 0.0864085 ± 0.000375152 (W 0.00141289) | · |  |
| `eigh/n32/b1` | 0.141609 ± 0.000671614 (W 0.00151046) | 0.153591 ± 0.000696001 (W 0.00150656) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `eigh/n64/b1` | 0.65926 ± 0.00219151 (W 0.00213052) | 0.652106 ± 0.00223001 (W 0.00228637) | · |  |
| `eigh/n96/b1` | 1.65541 ± 0.00546696 (W 0.0022445) | 1.63864 ± 0.0058216 (W 0.00391092) | · |  |
| `full_piv_lu/n32/b1` | 0.017156 ± 0.000231841 (W 9.55194e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.094314 ± 0.000645764 (W 0.00180522) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.272806 ± 0.00183361 (W 0.00232508) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.0284535 ± 0.00018019 (W 9.73951e-05) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.028493 ± 0.000104718 (W 8.05792e-05) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.158315 ± 0.0010141 (W 0.00223646) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.158951 ± 0.000528103 (W 0.00191041) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.466515 ± 0.00204216 (W 0.00135625) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.464867 ± 0.00282156 (W 0.00119159) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.011892 ± 0.000145592 (W 6.61862e-05) | 0.0128195 ± 7.4435e-05 (W 0.000100099) | 🔵 faer-fork 1.08× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0523095 ± 0.000262347 (W 0.000196564) | 0.0603145 ± 0.000203287 (W 0.000139536) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `lu/n96/b1` | 0.139223 ± 0.000627655 (W 0.00153735) | 0.16411 ± 0.000728841 (W 0.00147918) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.0674675 ± 0.000443481 (W 0.000451257) | 0.0515975 ± 0.000432544 (W 0.000133093) | 🔴 faer-fork 1.31× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.306181 ± 0.00124435 (W 0.00201768) | 0.2518 ± 0.00267464 (W 0.00216451) | 🔴 faer-fork 1.22× slower than `lapack-openblas` |  |
| `qr/n96/b1` | 0.747389 ± 0.00137494 (W 0.00256221) | 0.697734 ± 0.0030934 (W 0.00224662) | 🔴 faer-fork 1.07× slower than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.0323185 ± 0.000145899 (W 0.000239825) | 0.0288575 ± 0.000247775 (W 6.56418e-05) | 🔴 faer-fork 1.12× slower than `lapack-openblas` |  |
| `qr_factor/n64/b1` | 0.154506 ± 0.00064939 (W 0.00145454) | 0.131736 ± 0.00117251 (W 0.00147921) | 🔴 faer-fork 1.17× slower than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.373541 ± 0.00466568 (W 0.00209699) | 0.355892 ± 0.00242288 (W 0.00234657) | · |  |
| `solve/n32/b1` | 0.012824 ± 0.000188523 (W 3.62903e-05) | 0.014122 ± 8.80401e-05 (W 3.78676e-05) | 🔵 faer-fork 1.10× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0538755 ± 0.000105863 (W 7.55626e-05) | 0.0642955 ± 0.000343471 (W 0.00155829) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.142159 ± 0.000352039 (W 0.00110551) | 0.17242 ± 0.000734968 (W 0.00186225) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.21808 ± 0.00106449 (W 0.00185952) | 0.229295 ± 0.00172572 (W 0.00187793) | 🔵 faer-fork 1.05× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 1.19446 ± 0.00470669 (W 0.00329111) | 0.948513 ± 0.00718372 (W 0.00225797) | 🔴 faer-fork 1.26× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.96497 ± 0.0080416 (W 0.00785236) | 2.5327 ± 0.0164469 (W 0.00513225) | 🔴 faer-fork 1.17× slower than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.08463 ± 0.000613827 (W 0.000675871) | 0.103249 ± 0.000642431 (W 0.000795366) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.344287 ± 0.00227137 (W 0.00247913) | 0.402178 ± 0.000953779 (W 0.00254811) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.862777 ± 0.00355924 (W 0.00215113) | 1.01051 ± 0.00794214 (W 0.00159667) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.001132 ± 8.72735e-06 (W 1.07742e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.00271 ± 2.30275e-05 (W 1.3302e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.0050495 ± 0.0004586 (W 2.20765e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.005285 ± 6.22896e-05 (W 4.42326e-05) | 0.0058215 ± 5.94096e-05 (W 4.79641e-05) | 🔵 faer-fork 1.10× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.030331 ± 0.000234647 (W 0.000139298) | 0.032621 ± 0.00042577 (W 0.00140718) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `cholesky/n96/b1` | 0.0793245 ± 0.000320816 (W 0.000408745) | 0.0874955 ± 0.000613986 (W 0.000444792) | 🔵 faer-fork 1.10× faster than `lapack-openblas` |  |
| `eigh/n32/b1` | 0.139314 ± 0.000383812 (W 0.000339938) | 0.13797 ± 0.000459976 (W 0.000137599) | · |  |
| `eigh/n64/b1` | 0.57557 ± 0.00275752 (W 0.00216815) | 0.568712 ± 0.00144035 (W 0.00292744) | · |  |
| `eigh/n96/b1` | 1.36735 ± 0.00369042 (W 0.00215029) | 1.63327 ± 0.00685856 (W 0.00320394) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.0182 ± 0.00022142 (W 0.000108373) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.0985755 ± 0.00130775 (W 0.001429) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.234597 ± 0.00321115 (W 0.00195742) | - | - | `*` one row has no measurement here |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.015214 ± 6.44621e-05 (W 0.000347534) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.0150385 ± 8.74338e-05 (W 0.000158741) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.061942 ± 0.000265989 (W 0.000469695) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.062326 ± 0.000149307 (W 0.000266875) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.152322 ± 0.000530946 (W 0.00142634) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.152377 ± 0.000669933 (W 0.00110285) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.011747 ± 7.4312e-05 (W 6.07309e-05) | 0.012749 ± 0.000108088 (W 9.00906e-05) | 🔵 faer-fork 1.09× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0571725 ± 0.000201319 (W 0.00144338) | 0.059828 ± 0.000341009 (W 0.000151325) | · |  |
| `lu/n96/b1` | 0.140161 ± 0.00210787 (W 0.00184963) | 0.163085 ± 0.000594567 (W 0.00157173) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.062132 ± 0.000486469 (W 0.000209962) | 0.0515405 ± 0.000386531 (W 0.000174737) | 🔴 faer-fork 1.21× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.191602 ± 0.00123444 (W 0.00225353) | 0.247748 ± 0.0015784 (W 0.00186167) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.409483 ± 0.00144159 (W 0.00228691) | 0.894094 ± 0.0039705 (W 0.000847257) | 🔵 faer-fork 2.18× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.0310335 ± 0.000276611 (W 0.00024548) | 0.028808 ± 0.000360811 (W 9.13686e-05) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `qr_factor/n64/b1` | 0.116862 ± 0.000611678 (W 0.000491005) | 0.129327 ± 0.000861109 (W 0.00138914) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.247571 ± 0.001967 (W 0.00134758) | 0.455991 ± 0.00201599 (W 0.00212723) | 🔵 faer-fork 1.84× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.0134095 ± 0.000144715 (W 4.96942e-05) | 0.0141065 ± 8.0697e-05 (W 6.75659e-05) | 🔵 faer-fork 1.05× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0593365 ± 0.00144044 (W 0.000348346) | 0.0640575 ± 0.000199069 (W 0.000109555) | 🔵 faer-fork 1.08× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n96/b1` | 0.141857 ± 0.00113967 (W 0.00153326) | 0.171693 ± 0.00109266 (W 0.00221468) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.213334 ± 0.000445989 (W 0.00176889) | 0.227588 ± 0.00111942 (W 0.00156812) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 1.04078 ± 0.00432846 (W 0.00136986) | 0.940756 ± 0.00546981 (W 0.00138347) | 🔴 faer-fork 1.11× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.47048 ± 0.00582343 (W 0.00538893) | 2.47339 ± 0.00726806 (W 0.00502245) | · |  |
| `svd_values/n32/b1` | 0.085656 ± 0.000526957 (W 9.12115e-05) | 0.102962 ± 0.000532584 (W 0.000860991) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.351886 ± 0.00108661 (W 0.00205894) | 0.401627 ± 0.00188453 (W 0.00263312) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.79982 ± 0.0032081 (W 0.00247412) | 1.26922 ± 0.00520344 (W 0.00242355) | 🔵 faer-fork 1.59× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.001392 ± 7.84857e-06 (W 1.75362e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003296 ± 1.4148e-05 (W 2.29581e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.00576 ± 0.000215444 (W 2.07659e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

## linalg-small, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n32/b1` | 0.0052195 ± 7.48262e-05 (W 4.10381e-05) | 0.0058515 ± 6.27102e-05 (W 5.64286e-05) | 🔵 faer-fork 1.12× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `cholesky/n64/b1` | 0.0302465 ± 0.000293474 (W 0.000107973) | 0.0370345 ± 0.00243456 (W 0.00164076) | 🔵 faer-fork 1.22× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n96/b1` | 0.0797215 ± 0.000303726 (W 0.00030702) | 0.095377 ± 0.000802575 (W 0.00107736) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `eigh/n32/b1` | 0.139555 ± 0.000398947 (W 0.000270129) | 0.13763 ± 0.000458341 (W 0.000193117) | · |  |
| `eigh/n64/b1` | 0.568103 ± 0.00303629 (W 0.00210991) | 0.559627 ± 0.00224297 (W 0.00199499) | · |  |
| `eigh/n96/b1` | 1.33406 ± 0.00527204 (W 0.00416827) | 1.65567 ± 0.0121486 (W 0.00335809) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `full_piv_lu/n32/b1` | 0.018239 ± 0.000194091 (W 8.7944e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `full_piv_lu/n64/b1` | 0.102261 ± 0.00137519 (W 0.000958354) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n96/b1` | 0.238544 ± 0.00541989 (W 0.00228728) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n32/b1 [block(basis=32,target=32)]` | 0.0110405 ± 7.37222e-05 (W 0.000143362) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n32/b1 [sequence(basis=32,target=32)]` | 0.011176 ± 0.00015363 (W 0.000170164) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `householder_apply/n64/b1 [block(basis=64,target=64)]` | 0.038621 ± 0.00030091 (W 0.000541505) | - | - | `*` one row has no measurement here |
| `householder_apply/n64/b1 [sequence(basis=64,target=64)]` | 0.038843 ± 0.000435028 (W 0.000358225) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [block(basis=96,target=96)]` | 0.0882865 ± 0.000730566 (W 0.00122515) | - | - | `*` one row has no measurement here |
| `householder_apply/n96/b1 [sequence(basis=96,target=96)]` | 0.0878965 ± 0.000346827 (W 0.000705915) | - | - | `*` one row has no measurement here |
| `lu/n32/b1` | 0.0118365 ± 0.000201466 (W 7.38662e-05) | 0.012739 ± 5.63019e-05 (W 6.76145e-05) | 🔵 faer-fork 1.08× faster than `lapack-openblas` | dispatch-dominated (row under 20 us) |
| `lu/n64/b1` | 0.0575395 ± 0.000310096 (W 0.000247794) | 0.0600665 ± 0.0004358 (W 0.00085051) | · |  |
| `lu/n96/b1` | 0.139602 ± 0.000784984 (W 0.0018173) | 0.163229 ± 0.000989636 (W 0.00230165) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `qr/n32/b1` | 0.0618975 ± 0.000239719 (W 0.000274894) | 0.051399 ± 0.00022201 (W 6.45043e-05) | 🔴 faer-fork 1.20× slower than `lapack-openblas` |  |
| `qr/n64/b1` | 0.178121 ± 0.00126888 (W 0.00212873) | 0.248413 ± 0.00306278 (W 0.00207252) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `qr/n96/b1` | 0.355633 ± 0.00191956 (W 0.00244878) | 0.954614 ± 0.00126273 (W 0.00186892) | 🔵 faer-fork 2.68× faster than `lapack-openblas` |  |
| `qr_factor/n32/b1` | 0.0308085 ± 0.000109177 (W 0.000202387) | 0.028758 ± 0.000171517 (W 6.73716e-05) | 🔴 faer-fork 1.07× slower than `lapack-openblas` |  |
| `qr_factor/n64/b1` | 0.11378 ± 0.000430256 (W 0.00161893) | 0.12922 ± 0.000982815 (W 0.00150257) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `qr_factor/n96/b1` | 0.231791 ± 0.00167192 (W 0.0020432) | 0.486354 ± 0.00182995 (W 0.00312454) | 🔵 faer-fork 2.10× faster than `lapack-openblas` |  |
| `solve/n32/b1` | 0.0133045 ± 0.000109328 (W 8.10362e-05) | 0.0139865 ± 8.33851e-05 (W 5.96386e-05) | · | dispatch-dominated (row under 20 us) |
| `solve/n64/b1` | 0.0604735 ± 0.000691949 (W 0.000239395) | 0.06387 ± 0.000409291 (W 0.00015841) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `solve/n96/b1` | 0.140464 ± 0.000560872 (W 0.00141164) | 0.171194 ± 0.000425371 (W 0.00186104) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_thin/n32/b1` | 0.214342 ± 0.0037084 (W 0.00176386) | 0.227614 ± 0.000618979 (W 0.0016222) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `svd_thin/n64/b1` | 1.03279 ± 0.00464797 (W 0.00285424) | 0.949255 ± 0.00598589 (W 0.000772235) | 🔴 faer-fork 1.09× slower than `lapack-openblas` |  |
| `svd_thin/n96/b1` | 2.41932 ± 0.0110865 (W 0.00475103) | 2.55414 ± 0.0166795 (W 0.00616949) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `svd_values/n32/b1` | 0.0854875 ± 0.000454654 (W 0.000112127) | 0.102828 ± 0.000189089 (W 0.00195903) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_values/n64/b1` | 0.361389 ± 0.00168296 (W 0.00205862) | 0.400854 ± 0.00394848 (W 0.00257402) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `svd_values/n96/b1` | 0.826782 ± 0.00445194 (W 0.00198414) | 1.36116 ± 0.00499373 (W 0.00293296) | 🔵 faer-fork 1.65× faster than `lapack-openblas` |  |
| `triangular_solve/n32/b1` | 0.0013925 ± 2.14072e-05 (W 2.11449e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n64/b1` | 0.003271 ± 4.55796e-05 (W 2.14024e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n96/b1` | 0.0057255 ± 0.000234014 (W 2.60046e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |

Not applicable to this population's shapes and reported as skipped: `eig/32`, `eig/64`, `eig/96`, `full_piv_lu/32`, `full_piv_lu/64`, `full_piv_lu/96`, `householder_apply/32`, `householder_apply/64`, `householder_apply/96`, `triangular_solve/32`, `triangular_solve/64`, `triangular_solve/96`, `upgrade_factor/32`, `upgrade_factor/64`, `upgrade_factor/96`.

## linalg-mid, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.0667965 ± 0.000191353 (W 0.000959235) | 0.158011 ± 0.000833324 (W 0.00244241) | 🔵 faer-fork 2.37× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.387775 ± 0.00427162 (W 0.00220264) | 0.991481 ± 0.00369872 (W 0.00313182) | 🔵 faer-fork 2.56× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 2.50803 ± 0.0330737 (W 0.00539721) | 5.87396 ± 0.012617 (W 0.0116402) | 🔵 faer-fork 2.34× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.32492 ± 0.00997762 (W 0.00542264) | 1.86952 ± 0.00713471 (W 0.0106382) | 🔴 faer-fork 1.24× slower than `lapack-openblas` |  |
| `eigh/n256/b1` | 10.068 ± 0.0418841 (W 0.0157927) | 9.11331 ± 0.016739 (W 0.00933813) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `eigh/n512/b1` | 49.9474 ± 0.190765 (W 0.0638828) | 51.8966 ± 0.11841 (W 0.0623075) | · |  |
| `full_piv_lu/n128/b1` | 0.317043 ± 0.00191261 (W 0.00243754) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.71715 ± 0.0129487 (W 0.010559) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 21.8735 ± 0.194481 (W 0.0526302) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.259168 ± 0.00215472 (W 0.00218356) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.26042 ± 0.00116073 (W 0.00265296) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.91035 ± 0.0117986 (W 0.00369325) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.9014 ± 0.00556826 (W 0.00552633) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 15.8789 ± 0.054419 (W 0.0338162) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 15.8338 ± 0.0478848 (W 0.0314922) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.167323 ± 0.00129186 (W 0.00191522) | 0.205308 ± 0.00356933 (W 0.00505211) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `lu/n256/b1` | 0.994157 ± 0.00216435 (W 0.00407016) | 1.37668 ± 0.0151923 (W 0.00663233) | 🔵 faer-fork 1.38× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 6.66441 ± 0.0425233 (W 0.0177141) | 8.23865 ± 0.0692926 (W 0.0180576) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `qr/n128/b1` | 0.487164 ± 0.00287183 (W 0.00220829) | 0.862731 ± 0.00609334 (W 0.0061129) | 🔵 faer-fork 1.77× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 2.79045 ± 0.00775473 (W 0.00819976) | 4.37166 ± 0.0471646 (W 0.0121705) | 🔵 faer-fork 1.57× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 19.81 ± 0.0246335 (W 0.0860458) | 30.7569 ± 0.170659 (W 0.0401028) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.30799 ± 0.00101928 (W 0.00329665) | 0.433164 ± 0.00249033 (W 0.00482924) | 🔵 faer-fork 1.41× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 1.52067 ± 0.00531275 (W 0.00329981) | 2.19526 ± 0.0116634 (W 0.00935933) | 🔵 faer-fork 1.44× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 8.58279 ± 0.0553508 (W 0.0156731) | 14.4583 ± 0.0530923 (W 0.0209849) | 🔵 faer-fork 1.68× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.137496 ± 0.000848177 (W 0.00151658) | 0.208087 ± 0.00391606 (W 0.00492374) | 🔵 faer-fork 1.51× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 0.770591 ± 0.00261215 (W 0.002981) | 1.14509 ± 0.0171149 (W 0.00373589) | 🔵 faer-fork 1.49× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 6.57026 ± 0.0345407 (W 0.0114081) | 7.16967 ± 0.0230407 (W 0.0131184) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 3.37333 ± 0.0132259 (W 0.00638915) | 3.13575 ± 0.00501251 (W 0.00603739) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 16.7681 ± 0.0574488 (W 0.0215765) | 17.5075 ± 0.0488692 (W 0.0268199) | · |  |
| `svd_thin/n512/b1` | 94.7995 ± 0.261539 (W 0.129721) | 120.442 ± 1.78679 (W 0.619293) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.03374 ± 0.00504639 (W 0.00383281) | 1.34987 ± 0.00696994 (W 0.00644001) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 6.35238 ± 0.021489 (W 0.00794775) | 7.90113 ± 0.0124568 (W 0.0213622) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 41.439 ± 0.16954 (W 0.243366) | 55.4567 ± 1.16119 (W 0.0856314) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.004333 ± 0.000136547 (W 6.91265e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.012673 ± 0.000471439 (W 0.000122726) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.0431325 ± 0.00152816 (W 0.000308798) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.062392 ± 0.000472516 (W 0.000841139) | 0.167871 ± 0.00161016 (W 0.00223299) | 🔵 faer-fork 2.69× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.278519 ± 0.00125716 (W 0.00183275) | 0.879816 ± 0.0105614 (W 0.00356655) | 🔵 faer-fork 3.16× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 1.39379 ± 0.0149643 (W 0.00464251) | 4.61877 ± 0.0368471 (W 0.00862553) | 🔵 faer-fork 3.31× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.21631 ± 0.00520912 (W 0.00508222) | 1.50376 ± 0.00494488 (W 0.00368272) | 🔴 faer-fork 1.47× slower than `lapack-openblas` |  |
| `eigh/n256/b1` | 6.38648 ± 0.0292155 (W 0.00728512) | 6.10079 ± 0.0239076 (W 0.00780576) | · |  |
| `eigh/n512/b1` | 24.1105 ± 0.0429156 (W 0.0399464) | 28.9995 ± 0.199929 (W 0.0314086) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.346029 ± 0.00511675 (W 0.00520806) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.03085 ± 0.00675507 (W 0.00917357) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 12.9587 ± 0.0722815 (W 0.0237645) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.083338 ± 0.00187573 (W 0.00106531) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.083396 ± 0.00123475 (W 0.000880751) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.520545 ± 0.00440166 (W 0.00236328) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.521607 ± 0.00182085 (W 0.00243121) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 4.0978 ± 0.0200641 (W 0.0121443) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 4.1457 ± 0.012526 (W 0.00824128) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.168826 ± 0.00222871 (W 0.00198341) | 0.206589 ± 0.00148971 (W 0.00657095) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `lu/n256/b1` | 0.815469 ± 0.00601369 (W 0.00513833) | 1.04881 ± 0.0117559 (W 0.00364346) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 4.30424 ± 0.0349374 (W 0.0121258) | 5.70279 ± 0.0551339 (W 0.0180441) | 🔵 faer-fork 1.32× faster than `lapack-openblas` |  |
| `qr/n128/b1` | 0.346525 ± 0.00248719 (W 0.00193445) | 0.904523 ± 0.00805088 (W 0.00523595) | 🔵 faer-fork 2.61× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 1.17135 ± 0.00754458 (W 0.00352096) | 3.60231 ± 0.0444792 (W 0.00619285) | 🔵 faer-fork 3.08× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 8.04504 ± 0.0345425 (W 0.0147222) | 19.4762 ± 0.129354 (W 0.0297942) | 🔵 faer-fork 2.42× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.219692 ± 0.003708 (W 0.00189602) | 0.452956 ± 0.00715839 (W 0.00487146) | 🔵 faer-fork 2.06× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 0.646433 ± 0.00486793 (W 0.00317031) | 1.80645 ± 0.0222693 (W 0.00293507) | 🔵 faer-fork 2.79× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 3.16373 ± 0.0392731 (W 0.00904443) | 9.5197 ± 0.161269 (W 0.0165981) | 🔵 faer-fork 3.01× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.138683 ± 0.00144615 (W 0.000980916) | 0.17388 ± 0.00258902 (W 0.00358383) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 0.585958 ± 0.00300256 (W 0.00258833) | 0.817554 ± 0.00979034 (W 0.00415208) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 4.15619 ± 0.0274844 (W 0.00883392) | 4.6085 ± 0.120576 (W 0.00749977) | 🔵 faer-fork 1.11× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n128/b1` | 2.46804 ± 0.00805163 (W 0.00534592) | 3.11348 ± 0.0132908 (W 0.00500429) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 10.296 ± 0.0323725 (W 0.0234574) | 15.0287 ± 0.0645348 (W 0.0192504) | 🔵 faer-fork 1.46× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 41.0035 ± 0.12349 (W 0.0310016) | 94.0952 ± 2.10682 (W 0.341366) | 🔵 faer-fork 2.29× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/n128/b1` | 1.07938 ± 0.000810353 (W 0.00387445) | 1.40532 ± 0.00588998 (W 0.00388528) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 5.1165 ± 0.0389677 (W 0.0106986) | 7.70561 ± 0.0570182 (W 0.0129766) | 🔵 faer-fork 1.51× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 22.7318 ± 0.0973798 (W 0.030014) | 49.6508 ± 0.522869 (W 0.0981863) | 🔵 faer-fork 2.18× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.0050245 ± 0.000216547 (W 3.83807e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.0121275 ± 0.000308428 (W 0.000120382) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.030287 ± 0.00135359 (W 0.000239485) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.0625615 ± 2.42401 (W 0.00076364) | 0.166459 ± 0.00164324 (W 0.00274988) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `cholesky/n256/b1` | 0.274859 ± 0.00301344 (W 0.00187115) | 0.886084 ± 0.0060357 (W 0.00344761) | 🔵 faer-fork 3.22× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 1.26058 ± 0.0241276 (W 0.00645913) | 4.43064 ± 0.0171649 (W 0.0168657) | 🔵 faer-fork 3.51× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.1994 ± 0.00741327 (W 0.00412202) | 1.43529 ± 0.00500373 (W 0.00708514) | 🔴 faer-fork 1.53× slower than `lapack-openblas` |  |
| `eigh/n256/b1` | 6.16718 ± 0.0150417 (W 0.00583849) | 5.71035 ± 0.0179541 (W 0.0133181) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `eigh/n512/b1` | 21.4711 ± 0.0728828 (W 0.0178589) | 25.2848 ± 0.108003 (W 0.0476169) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.351895 ± 0.00379399 (W 0.00374703) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 1.97123 ± 0.0104337 (W 0.00739845) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 11.7148 ± 0.0418844 (W 0.015917) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.0548325 ± 0.000539212 (W 0.00064161) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.0584885 ± 0.000844514 (W 0.00088916) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.279145 ± 0.00257507 (W 0.00179315) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.286567 ± 0.00195405 (W 0.00271296) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 2.22574 ± 0.0266119 (W 0.00857962) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 2.26274 ± 0.0173335 (W 0.0137859) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.169619 ± 4.8348 (W 0.000607026) | 0.210593 ± 0.0036114 (W 0.0043504) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.803783 ± 0.00579168 (W 0.00434099) | 1.00643 ± 0.0140566 (W 0.00576085) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 4.02573 ± 0.0275223 (W 0.0120358) | 4.833 ± 0.0996545 (W 0.0147658) | 🔵 faer-fork 1.20× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n128/b1` | 0.320912 ± 0.00180488 (W 0.00193368) | 0.905472 ± 0.0075367 (W 0.00534775) | 🔵 faer-fork 2.82× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 1.00562 ± 0.00600595 (W 0.00356898) | 3.54983 ± 0.0395169 (W 0.0074728) | 🔵 faer-fork 3.53× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 5.78623 ± 0.0223366 (W 0.0112838) | 17.7354 ± 0.13463 (W 0.0275638) | 🔵 faer-fork 3.07× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.201576 ± 0.00131069 (W 0.00259806) | 0.45443 ± 0.00276812 (W 0.00573368) | 🔵 faer-fork 2.25× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 0.603984 ± 0.00510141 (W 0.00322652) | 1.76677 ± 0.0135664 (W 0.00536631) | 🔵 faer-fork 2.93× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 1.8724 ± 0.0227906 (W 0.00420879) | 8.79375 ± 0.159272 (W 0.0140837) | 🔵 faer-fork 4.70× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n128/b1` | 0.138799 ± 0.000481095 (W 0.000398776) | 0.21018 ± 0.00276877 (W 0.00539951) | 🔵 faer-fork 1.51× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 0.577635 ± 0.00631029 (W 0.00254624) | 0.774741 ± 0.0105193 (W 0.00331087) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 3.86722 ± 0.0263139 (W 0.0114713) | 3.7569 ± 0.0707768 (W 0.0112283) | · | `!` between-start range over 5% |
| `svd_thin/n128/b1` | 2.46579 ± 0.00935051 (W 0.0043708) | 3.09951 ± 0.0107461 (W 0.00858503) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 9.74319 ± 0.0262475 (W 0.0123821) | 14.6543 ± 0.0425749 (W 0.0210297) | 🔵 faer-fork 1.50× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 35.3314 ± 0.0628398 (W 0.10232) | 89.7942 ± 1.74022 (W 0.141927) | 🔵 faer-fork 2.54× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.12732 ± 0.00770419 (W 0.00311265) | 1.40184 ± 0.0112428 (W 0.00689671) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 4.98503 ± 0.0140843 (W 0.00656776) | 7.62163 ± 0.0496712 (W 0.0103889) | 🔵 faer-fork 1.53× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 20.567 ± 0.0575646 (W 0.0283802) | 48.6423 ± 0.409708 (W 0.0543764) | 🔵 faer-fork 2.37× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.004954 ± 0.000148707 (W 2.61934e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.011792 ± 0.000288396 (W 0.000130613) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.0286235 ± 0.00121084 (W 9.98933e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.059777 ± 0.00030922 (W 8.36711e-05) | 0.0731055 ± 0.00033671 (W 0.000149337) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.315819 ± 0.00263042 (W 0.00235971) | 0.41043 ± 0.00142003 (W 0.00230401) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 2.06189 ± 0.0177113 (W 0.00553632) | 2.69548 ± 0.00474676 (W 0.00425347) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.32348 ± 0.00735299 (W 0.0073966) | 1.79664 ± 0.00216977 (W 0.00786032) | 🔴 faer-fork 1.29× slower than `lapack-openblas` |  |
| `eigh/n256/b1` | 10.0061 ± 0.0430613 (W 0.0125739) | 8.70065 ± 0.0164924 (W 0.012708) | 🔴 faer-fork 1.15× slower than `lapack-openblas` |  |
| `eigh/n512/b1` | 49.5603 ± 0.227027 (W 0.0859306) | 49.446 ± 0.346194 (W 0.0652003) | · |  |
| `full_piv_lu/n128/b1` | 0.291025 ± 0.00147222 (W 0.0024329) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.62622 ± 0.0150334 (W 0.0114012) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 21.2437 ± 0.186899 (W 0.0329572) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.254414 ± 0.00150667 (W 0.00222143) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.254904 ± 0.00141924 (W 0.00214779) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.86978 ± 0.00885833 (W 0.00650683) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.87093 ± 0.00534492 (W 0.00503299) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 15.6206 ± 0.132886 (W 0.0198611) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 15.6478 ± 0.0514661 (W 0.0319107) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.128541 ± 0.0168225 (W 0.00181196) | 0.151797 ± 0.000768521 (W 0.00176591) | 🔵 faer-fork 1.18× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.891591 ± 0.00427813 (W 0.00338002) | 0.832027 ± 0.00246909 (W 0.00320167) | 🔴 faer-fork 1.07× slower than `lapack-openblas` |  |
| `lu/n512/b1` | 6.10182 ± 0.0230497 (W 0.0157805) | 5.12491 ± 0.00496344 (W 0.00916554) | 🔴 faer-fork 1.19× slower than `lapack-openblas` |  |
| `qr/n128/b1` | 0.457914 ± 0.00249746 (W 0.00268032) | 0.752199 ± 0.00338485 (W 0.00903986) | 🔵 faer-fork 1.64× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 2.66395 ± 0.00791911 (W 0.00432462) | 4.09725 ± 0.017634 (W 0.0121624) | 🔵 faer-fork 1.54× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 19.1699 ± 0.0419612 (W 0.0211961) | 26.8778 ± 0.0621719 (W 0.0570442) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.244285 ± 0.000764524 (W 0.00195944) | 0.371677 ± 0.00106817 (W 0.00286421) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 1.27027 ± 0.0048165 (W 0.00426013) | 1.86863 ± 0.00788804 (W 0.00314515) | 🔵 faer-fork 1.47× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 7.67337 ± 0.0465268 (W 0.0167358) | 12.3945 ± 0.026633 (W 0.0217156) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.110979 ± 0.000353683 (W 0.000763419) | 0.14746 ± 0.000825705 (W 0.00144571) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 0.662864 ± 0.00357224 (W 0.0042025) | 0.820402 ± 0.00280215 (W 0.003136) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 6.00718 ± 0.0172346 (W 0.0090259) | 5.08296 ± 0.0160875 (W 0.00942928) | 🔴 faer-fork 1.18× slower than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 3.35926 ± 0.012696 (W 0.00544345) | 3.00635 ± 0.00480374 (W 0.0116404) | 🔴 faer-fork 1.12× slower than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 16.6855 ± 0.0319178 (W 0.028174) | 16.8869 ± 0.0473407 (W 0.0202903) | · |  |
| `svd_thin/n512/b1` | 93.6714 ± 0.22063 (W 0.284813) | 116.966 ± 0.453657 (W 0.101991) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.01151 ± 0.00507536 (W 0.00109852) | 1.27878 ± 0.00356285 (W 0.00309109) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 6.19239 ± 0.0137045 (W 0.00769146) | 7.63449 ± 0.0311887 (W 0.0159421) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 40.1573 ± 0.184292 (W 0.0458067) | 52.8468 ± 0.289938 (W 0.0607744) | 🔵 faer-fork 1.32× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.0046485 ± 4.06813e-05 (W 5.8732e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.0142215 ± 0.000789784 (W 6.35905e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.0469765 ± 0.00223544 (W 0.00024828) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.0567355 ± 0.00199852 (W 0.000532709) | 0.077556 ± 0.00217281 (W 0.00129839) | 🔵 faer-fork 1.37× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n256/b1` | 0.213917 ± 0.00214862 (W 0.00176398) | 0.276299 ± 0.00233532 (W 0.00224414) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 0.930616 ± 0.00524003 (W 0.00408514) | 1.31647 ± 0.00791682 (W 0.00442887) | 🔵 faer-fork 1.41× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.21334 ± 0.00486716 (W 0.00272888) | 1.43259 ± 0.0059987 (W 0.00455148) | 🔴 faer-fork 1.54× slower than `lapack-openblas` |  |
| `eigh/n256/b1` | 6.34979 ± 0.0215706 (W 0.013023) | 5.67905 ± 0.038519 (W 0.00798092) | 🔴 faer-fork 1.12× slower than `lapack-openblas` |  |
| `eigh/n512/b1` | 23.7209 ± 0.0321012 (W 0.0284584) | 26.2231 ± 0.0980777 (W 0.0247793) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.325006 ± 0.00548276 (W 0.00285318) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 1.92857 ± 0.0074933 (W 0.00954409) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 12.4828 ± 0.0549141 (W 0.023583) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.082566 ± 0.00109735 (W 0.000864461) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.0846385 ± 0.000636677 (W 0.000500483) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.517622 ± 0.00243794 (W 0.0035656) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.526001 ± 0.00368552 (W 0.00339404) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 4.06909 ± 0.0155409 (W 0.0106224) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 4.12925 ± 0.00744758 (W 0.00705086) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.128713 ± 0.0175889 (W 0.00166197) | 0.150799 ± 0.000527001 (W 0.00133743) | 🔵 faer-fork 1.17× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.711364 ± 0.00499041 (W 0.00471305) | 0.50165 ± 0.000993138 (W 0.00300907) | 🔴 faer-fork 1.42× slower than `lapack-openblas` |  |
| `lu/n512/b1` | 3.74565 ± 0.0116093 (W 0.0110669) | 2.63112 ± 0.0148312 (W 0.00593304) | 🔴 faer-fork 1.42× slower than `lapack-openblas` |  |
| `qr/n128/b1` | 0.315038 ± 0.00199772 (W 0.00209255) | 0.803849 ± 0.0234438 (W 0.00253932) | 🔵 faer-fork 2.55× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n256/b1` | 1.05068 ± 0.00449298 (W 0.00181248) | 3.22783 ± 0.00553636 (W 0.00754101) | 🔵 faer-fork 3.07× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 7.39495 ± 0.0201489 (W 0.00766297) | 17.1601 ± 0.136429 (W 0.0234189) | 🔵 faer-fork 2.32× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.197829 ± 0.00159116 (W 0.0017057) | 0.390158 ± 0.00350121 (W 0.00198623) | 🔵 faer-fork 1.97× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 0.562984 ± 0.00345586 (W 0.00214973) | 1.4467 ± 0.0115584 (W 0.00632116) | 🔵 faer-fork 2.57× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 2.92476 ± 0.0108126 (W 0.00710918) | 7.64413 ± 0.0756252 (W 0.0159795) | 🔵 faer-fork 2.61× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.113523 ± 0.00156451 (W 0.000918584) | 0.114456 ± 0.00152234 (W 0.00139825) | · |  |
| `solve/n256/b1` | 0.481131 ± 0.00356779 (W 0.00252951) | 0.483073 ± 0.00288485 (W 0.00344237) | · |  |
| `solve/n512/b1` | 3.57872 ± 0.013756 (W 0.00539962) | 2.56358 ± 0.0200878 (W 0.00469961) | 🔴 faer-fork 1.40× slower than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 2.44916 ± 0.00587518 (W 0.00400202) | 2.98634 ± 0.0192548 (W 0.00678975) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 10.1273 ± 0.0419858 (W 0.0149886) | 14.3217 ± 0.0692532 (W 0.0192019) | 🔵 faer-fork 1.41× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 40.1141 ± 0.0391822 (W 0.0421388) | 86.787 ± 0.512505 (W 0.120337) | 🔵 faer-fork 2.16× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.05684 ± 0.00571713 (W 0.00201589) | 1.34728 ± 0.00523526 (W 0.00294442) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 4.96703 ± 0.0237028 (W 0.0115374) | 7.31709 ± 0.0657449 (W 0.0101816) | 🔵 faer-fork 1.47× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 21.7055 ± 0.0601994 (W 0.0269707) | 48.648 ± 0.421957 (W 0.0466571) | 🔵 faer-fork 2.24× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.005436 ± 0.000273383 (W 4.42911e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.014166 ± 0.000205126 (W 0.000200635) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.038602 ± 0.00143382 (W 0.000482282) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.0552135 ± 0.00240062 (W 0.000365866) | 0.0782115 ± 0.00171525 (W 0.00296273) | 🔵 faer-fork 1.42× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n256/b1` | 0.206103 ± 0.00345605 (W 0.0020378) | 0.278929 ± 0.00151957 (W 0.00245918) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 0.801295 ± 0.00582054 (W 0.0023527) | 1.20592 ± 0.00939423 (W 0.00461239) | 🔵 faer-fork 1.50× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.19674 ± 0.00872045 (W 0.00556026) | 1.36295 ± 0.0032223 (W 0.00485901) | 🔴 faer-fork 1.61× slower than `lapack-openblas` |  |
| `eigh/n256/b1` | 6.10908 ± 0.0654177 (W 0.00881906) | 5.29037 ± 0.0275598 (W 0.00753776) | 🔴 faer-fork 1.15× slower than `lapack-openblas` |  |
| `eigh/n512/b1` | 21.0944 ± 0.0647941 (W 0.0223516) | 22.5653 ± 0.0856852 (W 0.0517681) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.33012 ± 0.0033662 (W 0.00375918) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 1.86027 ± 0.0188734 (W 0.00654547) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 11.1724 ± 0.0395319 (W 0.0156274) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.056121 ± 0.000493147 (W 0.000581546) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.0565665 ± 0.000332668 (W 0.000664383) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.287491 ± 0.00297163 (W 0.00207342) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 0.291166 ± 0.00302413 (W 0.00238833) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 2.19236 ± 0.0565096 (W 0.00814527) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 2.25353 ± 0.0160867 (W 0.00699981) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.129754 ± 6.0675 (W 0.00107208) | 0.151004 ± 0.00130094 (W 0.00159808) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n256/b1` | 0.699532 ± 0.00286256 (W 0.00404862) | 0.435775 ± 0.00260667 (W 0.00265393) | 🔴 faer-fork 1.61× slower than `lapack-openblas` |  |
| `lu/n512/b1` | 3.46107 ± 0.0187206 (W 0.010912) | 1.75362 ± 0.0102391 (W 0.00913383) | 🔴 faer-fork 1.97× slower than `lapack-openblas` |  |
| `qr/n128/b1` | 0.290507 ± 0.0018319 (W 0.00206962) | 0.787625 ± 0.00505156 (W 0.00357482) | 🔵 faer-fork 2.71× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 0.883991 ± 0.00261133 (W 0.00304896) | 3.19514 ± 0.0235761 (W 0.00706554) | 🔵 faer-fork 3.61× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 5.12297 ± 0.00967809 (W 0.011298) | 15.3531 ± 0.138113 (W 0.0260644) | 🔵 faer-fork 3.00× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.189581 ± 0.00132566 (W 0.00234115) | 0.391914 ± 0.00183238 (W 0.00189004) | 🔵 faer-fork 2.07× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 0.557172 ± 0.00716603 (W 0.00322423) | 1.42545 ± 0.0175461 (W 0.00401007) | 🔵 faer-fork 2.56× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 1.7508 ± 0.00979587 (W 0.0038619) | 6.78302 ± 0.0469049 (W 0.0170817) | 🔵 faer-fork 3.87× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.113409 ± 0.000872635 (W 0.000304045) | 0.148295 ± 0.00161902 (W 0.00208108) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 0.47029 ± 0.00580815 (W 0.00248952) | 0.442868 ± 0.00126269 (W 0.00296351) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `solve/n512/b1` | 3.29602 ± 0.00661868 (W 0.00996506) | 1.73751 ± 0.00806014 (W 0.0067257) | 🔴 faer-fork 1.90× slower than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 2.43033 ± 0.00687287 (W 0.00503103) | 2.96467 ± 0.00948487 (W 0.00380866) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 9.63789 ± 0.0180894 (W 0.0135256) | 13.9402 ± 0.0703624 (W 0.0221517) | 🔵 faer-fork 1.45× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 34.4046 ± 0.0750968 (W 0.0414682) | 81.3007 ± 1.63398 (W 0.214269) | 🔵 faer-fork 2.36× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/n128/b1` | 1.10752 ± 0.00712777 (W 0.00326157) | 1.3462 ± 0.00909613 (W 0.00303421) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 4.86053 ± 0.0152875 (W 0.0131179) | 7.32 ± 0.0622715 (W 0.00971482) | 🔵 faer-fork 1.51× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 19.56 ± 0.0361418 (W 0.0298664) | 47.1619 ± 0.258252 (W 0.071331) | 🔵 faer-fork 2.41× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.0052145 ± 4.7437e-05 (W 4.91174e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.0141965 ± 0.000468799 (W 0.000202127) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n512/b1` | 0.0353815 ± 0.00138008 (W 0.000422286) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.190183 ± 0.000484028 (W 0.00178881) | 0.325786 ± 0.00469212 (W 0.00350634) | 🔵 faer-fork 1.71× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 1.23729 ± 0.0129075 (W 0.00254595) | 2.10562 ± 0.0128292 (W 0.00494492) | 🔵 faer-fork 1.70× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 7.90719 ± 0.0135702 (W 0.0112976) | 12.498 ± 0.059705 (W 0.0279694) | 🔵 faer-fork 1.58× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 3.32737 ± 0.0103623 (W 0.00544608) | 3.36183 ± 0.005048 (W 0.00568454) | · |  |
| `eigh/n256/b1` | 17.659 ± 0.0278944 (W 0.0238768) | 20.2189 ± 0.0632324 (W 0.0309956) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `eigh/n512/b1` | 106.265 ± 0.159594 (W 0.100595) | 140.589 ± 0.294458 (W 0.130308) | 🔵 faer-fork 1.32× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.78953 ± 0.00750206 (W 0.00490487) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 5.92605 ± 0.0570323 (W 0.00707854) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 40.2246 ± 0.141901 (W 0.0372874) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 1.04722 ± 0.00717665 (W 0.00177835) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 1.05076 ± 0.00436352 (W 0.00172635) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 7.48132 ± 0.026961 (W 0.015116) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 7.50714 ± 0.0204694 (W 0.0162816) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 56.7362 ± 0.0843408 (W 0.184086) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 56.7565 ± 0.0795408 (W 0.0727532) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.325468 ± 0.00202346 (W 0.0025333) | 0.423289 ± 0.00334805 (W 0.00375397) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `lu/n256/b1` | 2.10766 ± 0.0100452 (W 0.00317236) | 2.77623 ± 0.0303754 (W 0.00485389) | 🔵 faer-fork 1.32× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 14.6471 ± 0.057901 (W 0.0243358) | 18.357 ± 0.0485048 (W 0.0353921) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `qr/n128/b1` | 1.53583 ± 0.00498875 (W 0.00527757) | 1.61927 ± 0.00926138 (W 0.00575539) | 🔵 faer-fork 1.05× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 10.0601 ± 0.0245189 (W 0.0197539) | 11.2919 ± 0.0432314 (W 0.0226829) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 69.047 ± 0.16593 (W 0.105722) | 75.097 ± 0.205877 (W 0.0906945) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.777768 ± 0.00412061 (W 0.00189586) | 0.819381 ± 0.00442812 (W 0.00394672) | 🔵 faer-fork 1.05× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 4.65121 ± 0.0305839 (W 0.00961896) | 5.64115 ± 0.0180754 (W 0.0112681) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 30.1374 ± 0.0932175 (W 0.0622017) | 37.1735 ± 0.110689 (W 0.0416639) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.321242 ± 0.00255956 (W 0.002812) | 0.449214 ± 0.00255751 (W 0.00362658) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 2.05766 ± 0.00464994 (W 0.00793302) | 2.85117 ± 0.0174575 (W 0.00581776) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 14.6338 ± 0.0502059 (W 0.038717) | 18.4973 ± 0.0802501 (W 0.0343799) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 5.27723 ± 0.0107127 (W 0.0101756) | 5.66809 ± 0.032821 (W 0.0123161) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 31.9447 ± 0.0978039 (W 0.393755) | 36.8758 ± 0.297388 (W 0.0521595) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 203.473 ± 0.662144 (W 0.610061) | 234.93 ± 0.964497 (W 0.318992) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.76195 ± 0.00721031 (W 0.00445211) | 2.28702 ± 0.0112811 (W 0.00613856) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 12.7674 ± 0.0475769 (W 0.0402578) | 16.215 ± 0.0600581 (W 0.0149328) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 89.2991 ± 0.648135 (W 0.645972) | 100.765 ± 1.07402 (W 0.317176) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.00794 ± 0.000104602 (W 4.09016e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.0242755 ± 0.000188253 (W 0.000709267) | - | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.0869435 ± 0.000547361 (W 0.00186902) | - | - | `*` one row has no measurement here |

## linalg-mid, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.161236 ± 0.00208863 (W 0.00148756) | 0.263242 ± 0.00227176 (W 0.00236409) | 🔵 faer-fork 1.63× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.743854 ± 0.00277683 (W 0.00270275) | 1.40097 ± 0.0102613 (W 0.00603961) | 🔵 faer-fork 1.88× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 3.15157 ± 0.0632913 (W 0.0127724) | 6.84339 ± 0.017862 (W 0.0134072) | 🔵 faer-fork 2.17× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.58542 ± 0.0121096 (W 0.00410727) | 2.65372 ± 0.0182191 (W 0.00498903) | · |  |
| `eigh/n256/b1` | 8.66285 ± 0.033139 (W 0.0174674) | 12.0012 ± 0.0406177 (W 0.0162124) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `eigh/n512/b1` | 39.4893 ± 0.0339665 (W 0.0381262) | 55.648 ± 0.0980197 (W 0.051475) | 🔵 faer-fork 1.41× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.605954 ± 0.00589737 (W 0.00600387) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 3.471 ± 0.0356719 (W 0.0095403) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 17.4361 ± 0.0432111 (W 0.0444782) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.283745 ± 0.00105026 (W 0.00207782) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.284237 ± 0.00163109 (W 0.00168984) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.92293 ± 0.00644949 (W 0.00245454) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.94571 ± 0.0066211 (W 0.00350813) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 14.6076 ± 0.0449528 (W 0.0155037) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 14.6519 ± 0.0336586 (W 0.0191082) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.287947 ± 0.00255696 (W 0.00225083) | 0.309156 ± 0.00107542 (W 0.00254732) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `lu/n256/b1` | 1.29765 ± 0.00196421 (W 0.00471655) | 1.69048 ± 0.0429345 (W 0.00416039) | 🔵 faer-fork 1.30× faster than `lapack-openblas` | `!` between-start range over 5% |
| `lu/n512/b1` | 6.54816 ± 0.0448773 (W 0.0142473) | 7.42512 ± 0.0494076 (W 0.0211665) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `qr/n128/b1` | 0.74996 ± 0.00187721 (W 0.00249232) | 1.45911 ± 0.00709048 (W 0.00493833) | 🔵 faer-fork 1.95× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 3.27194 ± 0.0101804 (W 0.00574988) | 7.10543 ± 0.091873 (W 0.0181106) | 🔵 faer-fork 2.17× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 20.7664 ± 0.0604929 (W 0.0442576) | 34.8232 ± 0.241221 (W 0.054911) | 🔵 faer-fork 1.68× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.437299 ± 0.00156821 (W 0.00322258) | 0.728234 ± 0.00285844 (W 0.00407666) | 🔵 faer-fork 1.67× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 1.61944 ± 0.0193649 (W 0.00343035) | 3.51335 ± 0.0559725 (W 0.00745995) | 🔵 faer-fork 2.17× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 9.41873 ± 0.104009 (W 0.0188393) | 17.115 ± 0.134423 (W 0.0214345) | 🔵 faer-fork 1.82× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.281863 ± 0.00378289 (W 0.00259037) | 0.303905 ± 0.00171835 (W 0.00222869) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 1.22653 ± 0.007421 (W 0.0063389) | 1.69252 ± 0.0304482 (W 0.00953108) | 🔵 faer-fork 1.38× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 6.38288 ± 0.0196208 (W 0.01255) | 7.39489 ± 0.137315 (W 0.0218992) | 🔵 faer-fork 1.16× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n128/b1` | 3.16855 ± 0.0136097 (W 0.00647198) | 4.81905 ± 0.0177888 (W 0.00858076) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 15.1336 ± 0.0576224 (W 0.0281331) | 23.4616 ± 0.172601 (W 0.0332925) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 73.1242 ± 0.147975 (W 0.0865886) | 118.521 ± 0.293077 (W 0.161412) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.40978 ± 0.00652026 (W 0.00358312) | 2.45093 ± 0.00527052 (W 0.00543321) | 🔵 faer-fork 1.74× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 7.47651 ± 0.0506376 (W 0.0167973) | 12.0313 ± 0.0313055 (W 0.0301862) | 🔵 faer-fork 1.61× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 38.7199 ± 0.102534 (W 0.0704197) | 54.032 ± 0.154062 (W 0.0478674) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.009037 ± 9.36385e-05 (W 4.4937e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.02162 ± 0.000221203 (W 6.7658e-05) | - | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.0559385 ± 0.000905629 (W 0.000642551) | - | - | `*` one row has no measurement here |

## linalg-mid, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.15339 ± 0.00145963 (W 0.00173257) | 0.295327 ± 0.00263209 (W 0.00344897) | 🔵 faer-fork 1.93× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.699476 ± 0.00636131 (W 0.00443449) | 1.35022 ± 0.0180705 (W 0.0078286) | 🔵 faer-fork 1.93× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 2.56365 ± 0.0444625 (W 0.00976196) | 5.79665 ± 0.0591673 (W 0.0182575) | 🔵 faer-fork 2.26× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.47703 ± 71.7258 (W 0.00721205) | 2.56628 ± 0.0173781 (W 0.00601868) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `eigh/n256/b1` | 7.69916 ± 0.0258127 (W 0.0112415) | 10.8665 ± 0.0313582 (W 0.0233042) | 🔵 faer-fork 1.41× faster than `lapack-openblas` |  |
| `eigh/n512/b1` | 30.6628 ± 0.521998 (W 0.0278852) | 43.3247 ± 0.140683 (W 0.0613489) | 🔵 faer-fork 1.41× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.589891 ± 0.00638668 (W 0.00416217) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 3.11477 ± 0.0165335 (W 0.00750709) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 14.018 ± 0.0585319 (W 0.0320443) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.177922 ± 0.00146947 (W 0.00106725) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.179718 ± 0.00156749 (W 0.00136456) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 0.994968 ± 0.00376668 (W 0.00291968) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.01104 ± 0.00721747 (W 0.00281252) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 7.98539 ± 0.120755 (W 0.0580656) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 7.99961 ± 0.0205868 (W 0.0383275) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.282782 ± 0.0015048 (W 0.00159452) | 0.296855 ± 0.00135882 (W 0.00266263) | · |  |
| `lu/n256/b1` | 1.18219 ± 0.00601426 (W 0.00299081) | 1.31251 ± 0.0215106 (W 0.00452046) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 5.14879 ± 0.0414492 (W 0.0191051) | 5.16148 ± 0.0555286 (W 0.0132272) | · |  |
| `qr/n128/b1` | 0.621101 ± 0.00403365 (W 0.00234013) | 1.45053 ± 0.00922874 (W 0.00627243) | 🔵 faer-fork 2.34× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 2.34652 ± 0.00631931 (W 0.00632801) | 6.52158 ± 0.0237456 (W 0.0147709) | 🔵 faer-fork 2.78× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 11.8545 ± 0.0612876 (W 0.0411218) | 28.4044 ± 0.417483 (W 0.0415339) | 🔵 faer-fork 2.40× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.386193 ± 0.00268347 (W 0.00244634) | 0.724961 ± 0.00467562 (W 0.00370245) | 🔵 faer-fork 1.88× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 1.31627 ± 0.0113778 (W 0.00398117) | 3.21919 ± 0.0069527 (W 0.0083285) | 🔵 faer-fork 2.45× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 5.1202 ± 0.0614882 (W 0.0138498) | 13.9533 ± 0.214636 (W 0.0186266) | 🔵 faer-fork 2.73× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.276154 ± 0.00121977 (W 0.00201245) | 0.296349 ± 0.00187742 (W 0.00239909) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 1.10267 ± 0.00851464 (W 0.00294935) | 1.32549 ± 0.0300534 (W 0.00708713) | 🔵 faer-fork 1.20× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n512/b1` | 5.02051 ± 0.0397735 (W 0.0158576) | 5.31895 ± 0.182528 (W 0.0261209) | 🔵 faer-fork 1.06× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n128/b1` | 2.98969 ± 0.00588306 (W 0.00575619) | 4.80407 ± 0.0275271 (W 0.0130776) | 🔵 faer-fork 1.61× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 13.2319 ± 0.0613664 (W 0.0222943) | 21.8151 ± 0.0856883 (W 0.0352326) | 🔵 faer-fork 1.65× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 54.5871 ± 0.0438403 (W 0.356284) | 100.035 ± 0.593748 (W 0.195471) | 🔵 faer-fork 1.83× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.42511 ± 0.00394041 (W 0.00419128) | 2.55211 ± 0.0136724 (W 0.00731476) | 🔵 faer-fork 1.79× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 6.95791 ± 0.0362812 (W 0.0166144) | 11.8782 ± 0.0391325 (W 0.0250158) | 🔵 faer-fork 1.71× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 31.1947 ± 0.0918628 (W 0.0457003) | 48.3908 ± 0.274622 (W 0.0691006) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.009132 ± 4.82925e-05 (W 3.4174e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.0208945 ± 0.000156029 (W 8.10962e-05) | - | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.049848 ± 0.000525519 (W 0.000273803) | - | - | `*` one row has no measurement here |

## linalg-mid, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.177582 ± 0.000765259 (W 0.00155254) | 0.182969 ± 0.000532273 (W 0.00161081) | · |  |
| `cholesky/n256/b1` | 1.13904 ± 0.00284272 (W 0.00338233) | 1.28802 ± 0.00427533 (W 0.00288644) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `cholesky/n512/b1` | 7.5213 ± 0.0136301 (W 0.0127759) | 8.98783 ± 0.0209445 (W 0.0151164) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 3.31493 ± 0.00473568 (W 0.00423437) | 3.23805 ± 0.00499789 (W 0.00287359) | · |  |
| `eigh/n256/b1` | 17.5859 ± 0.0445827 (W 0.0223012) | 19.4905 ± 0.0287668 (W 0.0255737) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `eigh/n512/b1` | 105.861 ± 0.167325 (W 0.0700981) | 139.107 ± 1.93383 (W 0.255583) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.761702 ± 0.00842483 (W 0.00576349) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 5.79488 ± 0.0566038 (W 0.0128444) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 39.5755 ± 0.108506 (W 0.0502822) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 1.0312 ± 0.00411022 (W 0.00195459) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 1.03885 ± 0.00305 (W 0.00221489) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 7.39034 ± 0.0249783 (W 0.00948397) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 7.41831 ± 0.0324339 (W 0.0105695) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 56.7345 ± 0.120233 (W 0.0652059) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 56.4645 ± 0.0981311 (W 0.0623264) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.297373 ± 0.00206285 (W 0.00311168) | 0.346274 ± 0.00143133 (W 0.00239178) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `lu/n256/b1` | 2.00424 ± 0.00961815 (W 0.00342279) | 2.33646 ± 0.0255649 (W 0.00654556) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 13.8352 ± 0.0704911 (W 0.0226282) | 16.2414 ± 0.0694654 (W 0.0207758) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `qr/n128/b1` | 1.51099 ± 0.00445059 (W 0.00407195) | 1.5397 ± 0.00951824 (W 0.00515965) | · |  |
| `qr/n256/b1` | 9.95348 ± 0.0362721 (W 0.0151388) | 10.7915 ± 0.10364 (W 0.0160539) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 68.1478 ± 0.16409 (W 0.0740745) | 72.4781 ± 0.3741 (W 0.0772161) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.709812 ± 0.00756475 (W 0.00278844) | 0.744522 ± 0.00310954 (W 0.00287998) | · |  |
| `qr_factor/n256/b1` | 4.35952 ± 0.0277563 (W 0.00816561) | 5.19462 ± 0.0205182 (W 0.00945426) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 28.1115 ± 0.22733 (W 0.216675) | 35.3046 ± 0.0876746 (W 0.0514762) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.294814 ± 0.00172141 (W 0.00203735) | 0.362837 ± 0.00261748 (W 0.00291748) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `solve/n256/b1` | 1.94495 ± 0.00609079 (W 0.00457276) | 2.39043 ± 0.015621 (W 0.00626299) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 13.8423 ± 0.0412199 (W 0.016643) | 16.4605 ± 0.0248941 (W 0.024701) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 5.24566 ± 0.0158812 (W 0.00810401) | 5.50265 ± 0.0202973 (W 0.00967256) | · |  |
| `svd_thin/n256/b1` | 31.5724 ± 0.102495 (W 0.0437202) | 35.6561 ± 0.156966 (W 0.0609973) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 202.04 ± 0.5993 (W 0.525834) | 230.216 ± 3.18416 (W 0.625956) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.7368 ± 0.00476186 (W 0.00287325) | 2.21111 ± 0.0057985 (W 0.0077455) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 12.4812 ± 0.0626637 (W 0.0237645) | 15.6521 ± 0.09488 (W 0.0247239) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 88.7292 ± 0.732503 (W 0.504979) | 96.7436 ± 1.89617 (W 0.433946) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.007419 ± 0.000437045 (W 3.86306e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.022402 ± 0.000296507 (W 0.000108364) | - | - | `*` one row has no measurement here |
| `triangular_solve/n512/b1` | 0.084521 ± 0.00219813 (W 0.000697671) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.149828 ± 0.00240652 (W 0.00203286) | 0.124789 ± 0.00162741 (W 0.0015405) | 🔴 faer-fork 1.20× slower than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.652141 ± 0.00289478 (W 0.00338897) | 0.591758 ± 0.00207595 (W 0.00315695) | 🔴 faer-fork 1.10× slower than `lapack-openblas` |  |
| `cholesky/n512/b1` | 2.78717 ± 0.00339813 (W 0.00713286) | 3.49134 ± 0.015761 (W 0.00737384) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.56835 ± 0.0105771 (W 0.00452129) | 2.54696 ± 0.0137045 (W 0.00509903) | · |  |
| `eigh/n256/b1` | 8.56259 ± 0.0173782 (W 0.0113862) | 11.3459 ± 0.0309741 (W 0.0149511) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `eigh/n512/b1` | 39.1358 ± 0.0253737 (W 0.0216573) | 52.937 ± 0.431679 (W 0.045604) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.578884 ± 0.00913034 (W 0.00419831) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 3.31548 ± 0.0339924 (W 0.0106736) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 16.7457 ± 0.0395655 (W 0.0288444) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.285154 ± 0.00126236 (W 0.00174322) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.285804 ± 0.00160469 (W 0.0017907) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.91538 ± 0.00670893 (W 0.00550767) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.93323 ± 0.00495274 (W 0.00499687) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 14.6722 ± 0.0381912 (W 0.0261772) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 14.6626 ± 0.0934992 (W 0.0245656) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.264649 ± 0.00204021 (W 0.00215269) | 0.237992 ± 0.00150471 (W 0.00178384) | 🔴 faer-fork 1.11× slower than `lapack-openblas` |  |
| `lu/n256/b1` | 1.19506 ± 0.00395216 (W 0.00340277) | 1.25942 ± 0.00339625 (W 0.00325073) | 🔵 faer-fork 1.05× faster than `lapack-openblas` |  |
| `lu/n512/b1` | 5.73011 ± 0.0206195 (W 0.0149998) | 5.45845 ± 0.00979921 (W 0.00753374) | · |  |
| `qr/n128/b1` | 0.725773 ± 0.00226554 (W 0.00205757) | 1.36367 ± 0.0082391 (W 0.00464163) | 🔵 faer-fork 1.88× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 3.15152 ± 0.0164769 (W 0.00909084) | 6.55033 ± 0.0555273 (W 0.0129448) | 🔵 faer-fork 2.08× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 19.8501 ± 0.0514226 (W 0.0185535) | 32.2173 ± 0.175354 (W 0.0318923) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.411116 ± 0.0015002 (W 0.0026203) | 0.655614 ± 0.00365558 (W 0.00299723) | 🔵 faer-fork 1.59× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 1.52756 ± 0.0638898 (W 0.00664378) | 3.09207 ± 0.0277068 (W 0.00817268) | 🔵 faer-fork 2.02× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n512/b1` | 8.80457 ± 0.0313168 (W 0.0125764) | 15.2178 ± 0.0599885 (W 0.0216614) | 🔵 faer-fork 1.73× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.256498 ± 0.00288686 (W 0.00338064) | 0.236533 ± 0.00123508 (W 0.00224713) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `solve/n256/b1` | 1.12111 ± 0.00548272 (W 0.00311226) | 1.25535 ± 0.00364715 (W 0.00339756) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `solve/n512/b1` | 5.60074 ± 0.114508 (W 0.0147277) | 5.54768 ± 0.0304412 (W 0.00907358) | · | `!` between-start range over 5% |
| `svd_thin/n128/b1` | 3.15308 ± 0.0108976 (W 0.00499061) | 4.65455 ± 0.0123624 (W 0.0104162) | 🔵 faer-fork 1.48× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 14.803 ± 0.0529455 (W 0.0200633) | 22.4395 ± 0.133264 (W 0.0520472) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 72.1652 ± 0.183501 (W 0.0990041) | 113.494 ± 0.422956 (W 0.129582) | 🔵 faer-fork 1.57× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.39115 ± 0.00942004 (W 0.00358585) | 2.37899 ± 0.00641669 (W 0.00521956) | 🔵 faer-fork 1.71× faster than `lapack-openblas` |  |
| `svd_values/n256/b1` | 7.28795 ± 0.0207093 (W 0.0136404) | 11.684 ± 0.0998438 (W 0.0182175) | 🔵 faer-fork 1.60× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 37.9302 ± 0.151866 (W 0.0578676) | 51.7079 ± 0.177263 (W 0.0552798) | 🔵 faer-fork 1.36× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.008711 ± 0.000414054 (W 2.99808e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.021605 ± 0.000905978 (W 0.000153607) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n512/b1` | 0.058237 ± 0.00264687 (W 0.000583302) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-mid, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n128/b1` | 0.139636 ± 0.00141221 (W 0.00156703) | 0.156669 ± 0.00125617 (W 0.0016702) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `cholesky/n256/b1` | 0.584619 ± 0.00286433 (W 0.00319851) | 0.554194 ± 0.00327771 (W 0.0028344) | 🔴 faer-fork 1.05× slower than `lapack-openblas` |  |
| `cholesky/n512/b1` | 2.21774 ± 0.0156794 (W 0.00491398) | 2.42403 ± 0.0392905 (W 0.00631846) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `eigh/n128/b1` | 2.46994 ± 0.0105503 (W 0.00642842) | 2.45658 ± 0.00942224 (W 0.00561016) | · |  |
| `eigh/n256/b1` | 7.621 ± 0.180363 (W 0.0150795) | 10.2315 ± 0.102352 (W 0.0122443) | 🔵 faer-fork 1.34× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n512/b1` | 30.3037 ± 0.0417602 (W 0.0236789) | 40.5495 ± 0.040786 (W 0.0394309) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `full_piv_lu/n128/b1` | 0.566097 ± 0.00399178 (W 0.00375649) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n256/b1` | 2.99338 ± 0.0168119 (W 0.00806565) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n512/b1` | 13.2053 ± 0.0607833 (W 0.0168054) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [block(basis=128,target=128)]` | 0.180414 ± 0.0014568 (W 0.00176021) | - | - | `*` one row has no measurement here |
| `householder_apply/n128/b1 [sequence(basis=128,target=128)]` | 0.181284 ± 0.000737784 (W 0.00163135) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [block(basis=256,target=256)]` | 1.00194 ± 0.00400731 (W 0.00311868) | - | - | `*` one row has no measurement here |
| `householder_apply/n256/b1 [sequence(basis=256,target=256)]` | 1.00809 ± 0.0089579 (W 0.00249237) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [block(basis=512,target=512)]` | 8.01051 ± 0.11439 (W 0.12294) | - | - | `*` one row has no measurement here |
| `householder_apply/n512/b1 [sequence(basis=512,target=512)]` | 7.9959 ± 0.0780061 (W 0.0604282) | - | - | `*` one row has no measurement here |
| `lu/n128/b1` | 0.257548 ± 0.000209625 (W 0.00195166) | 0.224782 ± 0.00155485 (W 0.00181464) | 🔴 faer-fork 1.15× slower than `lapack-openblas` |  |
| `lu/n256/b1` | 1.0779 ± 0.00372871 (W 0.00219234) | 0.892533 ± 0.00345646 (W 0.00406923) | 🔴 faer-fork 1.21× slower than `lapack-openblas` |  |
| `lu/n512/b1` | 4.38233 ± 0.0266815 (W 0.013872) | 3.25981 ± 0.0229285 (W 0.00733633) | 🔴 faer-fork 1.34× slower than `lapack-openblas` |  |
| `qr/n128/b1` | 0.596334 ± 0.00328806 (W 0.00242381) | 1.35297 ± 0.00608411 (W 0.00555761) | 🔵 faer-fork 2.27× faster than `lapack-openblas` |  |
| `qr/n256/b1` | 2.23586 ± 0.0132989 (W 0.0037592) | 5.9962 ± 0.0326641 (W 0.0119779) | 🔵 faer-fork 2.68× faster than `lapack-openblas` |  |
| `qr/n512/b1` | 10.9486 ± 0.0396075 (W 0.0130192) | 25.993 ± 0.248694 (W 0.0445425) | 🔵 faer-fork 2.37× faster than `lapack-openblas` |  |
| `qr_factor/n128/b1` | 0.368829 ± 0.00377843 (W 0.00235451) | 0.654934 ± 0.00386475 (W 0.00229843) | 🔵 faer-fork 1.78× faster than `lapack-openblas` |  |
| `qr_factor/n256/b1` | 1.25456 ± 0.00338462 (W 0.00285702) | 2.79815 ± 0.0185384 (W 0.00794449) | 🔵 faer-fork 2.23× faster than `lapack-openblas` |  |
| `qr_factor/n512/b1` | 4.73569 ± 0.00995295 (W 0.00799313) | 12.0184 ± 0.0908107 (W 0.0216155) | 🔵 faer-fork 2.54× faster than `lapack-openblas` |  |
| `solve/n128/b1` | 0.249436 ± 0.0012829 (W 0.00180272) | 0.228085 ± 0.00184727 (W 0.00238878) | 🔴 faer-fork 1.09× slower than `lapack-openblas` |  |
| `solve/n256/b1` | 1.00047 ± 0.00391894 (W 0.00297099) | 0.903522 ± 0.00273844 (W 0.00419775) | 🔴 faer-fork 1.11× slower than `lapack-openblas` |  |
| `solve/n512/b1` | 4.2023 ± 0.0186708 (W 0.0105988) | 3.34973 ± 0.0272282 (W 0.0114912) | 🔴 faer-fork 1.25× slower than `lapack-openblas` |  |
| `svd_thin/n128/b1` | 2.97094 ± 0.00933235 (W 0.00543988) | 4.60934 ± 0.0239172 (W 0.0110887) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `svd_thin/n256/b1` | 12.9592 ± 0.0548566 (W 0.0129275) | 20.8095 ± 0.0604857 (W 0.0314302) | 🔵 faer-fork 1.61× faster than `lapack-openblas` |  |
| `svd_thin/n512/b1` | 53.5907 ± 0.105825 (W 0.0459801) | 95.0012 ± 0.627021 (W 0.0909658) | 🔵 faer-fork 1.77× faster than `lapack-openblas` |  |
| `svd_values/n128/b1` | 1.39821 ± 0.0307876 (W 0.00541152) | 2.48982 ± 0.00449128 (W 0.008295) | 🔵 faer-fork 1.78× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/n256/b1` | 6.78744 ± 0.0306574 (W 0.00933518) | 11.4876 ± 0.0417351 (W 0.0184479) | 🔵 faer-fork 1.69× faster than `lapack-openblas` |  |
| `svd_values/n512/b1` | 30.299 ± 0.0715522 (W 0.0369923) | 46.0355 ± 0.354259 (W 0.0545) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `triangular_solve/n128/b1` | 0.00803 ± 0.000476513 (W 4.1087e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n256/b1` | 0.021926 ± 0.000782709 (W 0.000193883) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n512/b1` | 0.0548955 ± 0.000540968 (W 0.000477654) | - | - | `*` one row has no measurement here |

Not applicable to this population's shapes and reported as skipped: `eig/128`, `eig/256`, `eig/512`, `full_piv_lu/128`, `full_piv_lu/256`, `full_piv_lu/512`, `householder_apply/128`, `householder_apply/256`, `householder_apply/512`, `triangular_solve/128`, `triangular_solve/256`, `triangular_solve/512`, `upgrade_factor/128`, `upgrade_factor/256`, `upgrade_factor/512`.

## linalg-tall, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.833053 ± 0.00233599 (W 0.00834898) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 49.1784 ± 0.403904 (W 0.135815) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.554756 ± 0.00245207 (W 0.00256105) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.55478 ± 0.00168425 (W 0.00254816) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 35.2066 ± 0.0394507 (W 0.0833259) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 35.2394 ± 0.218752 (W 0.370061) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.48807 ± 0.00269606 (W 0.00287256) | 0.76499 ± 0.121944 (W 0.00367562) | 🔵 faer-fork 1.57× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/4096x256/b1` | 15.6176 ± 0.107697 (W 0.0511974) | 28.6242 ± 0.225767 (W 0.07478) | 🔵 faer-fork 1.83× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 1.43935 ± 0.00674322 (W 0.00432771) | 2.54762 ± 0.0281673 (W 0.0146124) | 🔵 faer-fork 1.77× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 70.2117 ± 0.15612 (W 0.131656) | 107.259 ± 1.78166 (W 1.10275) | 🔵 faer-fork 1.53× faster than `lapack-openblas` |  |
| `qr_factor/1024x64/b1` | 0.937818 ± 0.00381696 (W 0.002441) | 1.30337 ± 0.00556001 (W 0.00568872) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 30.7987 ± 0.272855 (W 0.151097) | 50.9037 ± 1.18127 (W 0.853851) | 🔵 faer-fork 1.65× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 2.29919 ± 0.0118081 (W 0.00447381) | 3.78722 ± 0.0201233 (W 0.0112314) | 🔵 faer-fork 1.65× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 85.9255 ± 0.142221 (W 0.150575) | 147.664 ± 1.14759 (W 1.36979) | 🔵 faer-fork 1.72× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 1.04274 ± 0.00448477 (W 0.00674585) | 1.95532 ± 0.0163749 (W 0.00609771) | 🔵 faer-fork 1.88× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 38.3753 ± 0.0444253 (W 0.0625449) | 69.7292 ± 3.6569 (W 0.89063) | 🔵 faer-fork 1.82× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-tall, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.608123 ± 0.00864393 (W 0.0073319) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 17.0564 ± 0.0760964 (W 0.041426) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.159611 ± 0.00235976 (W 0.00332778) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.164916 ± 0.00286167 (W 0.00225455) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 9.44703 ± 0.0596881 (W 0.0352197) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 9.46371 ± 0.0329659 (W 0.0597495) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.452627 ± 0.00276146 (W 0.0029129) | 0.702368 ± 0.128154 (W 0.00503145) | 🔵 faer-fork 1.55× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/4096x256/b1` | 9.26456 ± 0.172929 (W 0.0334189) | 22.5091 ± 0.361599 (W 0.0459338) | 🔵 faer-fork 2.43× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 0.847435 ± 0.00401767 (W 0.00317304) | 2.5969 ± 0.0448749 (W 0.00793696) | 🔵 faer-fork 3.06× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 29.6064 ± 0.0621478 (W 0.0364694) | 66.6139 ± 3.28712 (W 0.559967) | 🔵 faer-fork 2.25× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 0.602987 ± 0.00202612 (W 0.00339303) | 1.35684 ± 0.00953003 (W 0.0061251) | 🔵 faer-fork 2.25× faster than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 13.2554 ± 0.116736 (W 0.0314619) | 32.6903 ± 0.685636 (W 0.225644) | 🔵 faer-fork 2.47× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 1.7606 ± 0.00887702 (W 0.00433837) | 3.63704 ± 0.0198166 (W 0.0102912) | 🔵 faer-fork 2.07× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 39.7033 ± 0.058716 (W 0.059309) | 90.9709 ± 1.29235 (W 0.714166) | 🔵 faer-fork 2.29× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 0.909348 ± 0.00912352 (W 0.00344331) | 2.0126 ± 0.0250664 (W 0.0055349) | 🔵 faer-fork 2.21× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 23.0979 ± 0.0868512 (W 0.0455312) | 47.8555 ± 0.441158 (W 0.618759) | 🔵 faer-fork 2.07× faster than `lapack-openblas` |  |

## linalg-tall, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.588059 ± 0.00282643 (W 0.00712931) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 12.3369 ± 0.115349 (W 0.11768) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.104219 ± 0.00348219 (W 0.00338768) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.108424 ± 0.00223119 (W 0.00329587) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 5.61313 ± 0.0888539 (W 0.0607279) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 5.69188 ± 0.0348392 (W 0.0420578) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.448202 ± 3.49154 (W 0.00357025) | 0.683412 ± 0.129261 (W 0.00473171) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/4096x256/b1` | 8.49992 ± 0.173685 (W 0.0313755) | 20.1644 ± 0.251051 (W 0.044161) | 🔵 faer-fork 2.37× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 0.754559 ± 0.00246784 (W 0.00316386) | 2.63732 ± 0.038042 (W 0.0066117) | 🔵 faer-fork 3.50× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 23.9854 ± 0.0630544 (W 0.0457384) | 65.2138 ± 2.09663 (W 0.798438) | 🔵 faer-fork 2.72× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 0.564132 ± 0.00212612 (W 0.00335452) | 1.3472 ± 0.0124434 (W 0.00387407) | 🔵 faer-fork 2.39× faster than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 9.64816 ± 0.278422 (W 0.0310716) | 31.0507 ± 0.894411 (W 0.362844) | 🔵 faer-fork 3.22× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 1.66939 ± 0.00709386 (W 0.00346941) | 3.62211 ± 0.0310827 (W 0.01103) | 🔵 faer-fork 2.17× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 33.7217 ± 1.19652 (W 0.255346) | 82.6907 ± 1.23013 (W 0.62236) | 🔵 faer-fork 2.45× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/1024x64/b1` | 0.88579 ± 0.00771403 (W 0.0033431) | 2.01704 ± 0.029339 (W 0.00529631) | 🔵 faer-fork 2.28× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 20.7216 ± 1.13461 (W 0.0514111) | 46.2823 ± 1.10642 (W 0.119082) | 🔵 faer-fork 2.23× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-tall, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.735785 ± 0.00651049 (W 0.00662438) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 46.7332 ± 1.44935 (W 0.261976) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.593282 ± 0.00487692 (W 0.00320189) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.597891 ± 0.0034513 (W 0.0029849) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 35.8588 ± 0.113123 (W 0.0353289) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 35.8298 ± 0.0827731 (W 0.0439419) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.385744 ± 0.00146294 (W 0.00275784) | 0.304584 ± 0.000845468 (W 0.00294557) | 🔴 faer-fork 1.27× slower than `lapack-openblas` |  |
| `lu/4096x256/b1` | 13.2459 ± 0.0305983 (W 0.0278153) | 13.0673 ± 0.0841749 (W 0.0225699) | · |  |
| `qr/1024x64/b1` | 1.31782 ± 0.00728265 (W 0.00300816) | 1.87828 ± 0.0035163 (W 0.00207584) | 🔵 faer-fork 1.43× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 67.7132 ± 0.128262 (W 0.111314) | 77.8363 ± 0.447024 (W 0.0547054) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `qr_factor/1024x64/b1` | 0.641878 ± 0.0226193 (W 0.00304406) | 0.961785 ± 0.004773 (W 0.0015123) | 🔵 faer-fork 1.50× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 24.74 ± 0.0415103 (W 0.0453514) | 39.0935 ± 0.193827 (W 0.0367407) | 🔵 faer-fork 1.58× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 2.24706 ± 0.0101909 (W 0.00511821) | 3.2524 ± 0.00803768 (W 0.00472214) | 🔵 faer-fork 1.45× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 80.5849 ± 0.281364 (W 0.145949) | 121.76 ± 1.02562 (W 0.108963) | 🔵 faer-fork 1.51× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 0.963187 ± 0.00250023 (W 0.0024276) | 1.6085 ± 0.00380809 (W 0.00351624) | 🔵 faer-fork 1.67× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 32.5494 ± 0.0726867 (W 0.0469522) | 55.1054 ± 0.12709 (W 0.0867828) | 🔵 faer-fork 1.69× faster than `lapack-openblas` |  |

## linalg-tall, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.510424 ± 0.0103028 (W 0.00905799) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/4096x256/b1` | 14.6156 ± 0.0639539 (W 0.0373241) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.190472 ± 0.0101762 (W 0.000805974) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.201899 ± 0.00163739 (W 0.000864061) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 10.9751 ± 0.0133717 (W 0.0217303) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 11.0451 ± 0.165303 (W 0.0310239) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.351145 ± 0.00161465 (W 0.00252171) | 0.251597 ± 0.00124821 (W 0.00212204) | 🔴 faer-fork 1.40× slower than `lapack-openblas` |  |
| `lu/4096x256/b1` | 6.93332 ± 0.0251636 (W 0.0159683) | 7.20359 ± 0.0249265 (W 0.0226616) | · |  |
| `qr/1024x64/b1` | 0.728304 ± 0.00267378 (W 0.00373813) | 1.97499 ± 0.0127145 (W 0.00387312) | 🔵 faer-fork 2.71× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 27.1134 ± 0.0895581 (W 0.105045) | 41.0782 ± 0.445045 (W 0.0448912) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `qr_factor/1024x64/b1` | 0.483075 ± 0.00186718 (W 0.00268307) | 1.0293 ± 0.00816173 (W 0.00356377) | 🔵 faer-fork 2.13× faster than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 10.6295 ± 0.205949 (W 0.02062) | 20.5945 ± 0.16644 (W 0.0426055) | 🔵 faer-fork 1.94× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 1.70563 ± 0.00208133 (W 0.00452173) | 3.09608 ± 0.0173949 (W 0.00798071) | 🔵 faer-fork 1.82× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 34.2994 ± 0.0423813 (W 0.0905568) | 66.4409 ± 0.383742 (W 0.0907555) | 🔵 faer-fork 1.94× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 0.831925 ± 0.00340944 (W 0.00314485) | 1.67575 ± 0.00898206 (W 0.00295279) | 🔵 faer-fork 2.01× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 17.3112 ± 0.0427884 (W 0.0339987) | 35.6416 ± 0.468432 (W 0.0307488) | 🔵 faer-fork 2.06× faster than `lapack-openblas` |  |

## linalg-tall, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.491755 ± 0.00511239 (W 0.00866714) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 9.81884 ± 0.0903475 (W 0.0426623) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.124793 ± 0.00571734 (W 0.00185703) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.130659 ± 0.00213043 (W 0.00183321) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 8.84767 ± 0.155409 (W 0.0719326) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 8.8168 ± 0.123122 (W 0.0612754) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.345572 ± 0.00294747 (W 0.00320231) | 0.234013 ± 0.00141902 (W 0.00203053) | 🔴 faer-fork 1.48× slower than `lapack-openblas` |  |
| `lu/4096x256/b1` | 5.99973 ± 0.0308864 (W 0.00988189) | 4.76135 ± 0.0225255 (W 0.00856477) | 🔴 faer-fork 1.26× slower than `lapack-openblas` |  |
| `qr/1024x64/b1` | 0.634769 ± 0.00359888 (W 0.00393033) | 1.9878 ± 0.0139604 (W 0.00478484) | 🔵 faer-fork 3.13× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 21.2968 ± 0.059173 (W 0.0436176) | 36.4656 ± 0.345865 (W 0.0324935) | 🔵 faer-fork 1.71× faster than `lapack-openblas` |  |
| `qr_factor/1024x64/b1` | 0.461367 ± 0.00149431 (W 0.00292485) | 1.02923 ± 0.0081072 (W 0.00173393) | 🔵 faer-fork 2.23× faster than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 8.30059 ± 0.248184 (W 0.0209708) | 18.1657 ± 0.130636 (W 0.0273317) | 🔵 faer-fork 2.19× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 1.61291 ± 0.00479975 (W 0.00728198) | 3.07983 ± 0.0197961 (W 0.00752756) | 🔵 faer-fork 1.91× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 28.4531 ± 0.118273 (W 0.0600735) | 59.3065 ± 0.341145 (W 0.0719729) | 🔵 faer-fork 2.08× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 0.809359 ± 0.00233261 (W 0.00437484) | 1.68306 ± 0.014002 (W 0.00327599) | 🔵 faer-fork 2.08× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 14.9606 ± 0.0976967 (W 0.0470661) | 33.6672 ± 0.237417 (W 0.0593363) | 🔵 faer-fork 2.25× faster than `lapack-openblas` |  |

## linalg-tall, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 1.78638 ± 0.00989214 (W 0.00464346) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 149.039 ± 1.27937 (W 0.701779) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 2.20254 ± 0.00429656 (W 0.0052036) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 2.20265 ± 0.00839538 (W 0.00573155) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 137.763 ± 0.361204 (W 0.108426) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 137.723 ± 0.258663 (W 0.115777) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.993916 ± 0.00513594 (W 0.00585997) | 1.30318 ± 0.00479723 (W 0.00394893) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `lu/4096x256/b1` | 47.1817 ± 0.0639913 (W 0.0699964) | 64.2965 ± 0.297049 (W 0.252759) | 🔵 faer-fork 1.36× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 4.511 ± 0.0187799 (W 0.0103059) | 4.30474 ± 0.0466244 (W 0.00970471) | · |  |
| `qr/4096x256/b1` | 237.276 ± 0.455368 (W 0.459701) | 265.997 ± 1.09442 (W 0.926193) | 🔵 faer-fork 1.12× faster than `lapack-openblas` |  |
| `qr_factor/1024x64/b1` | 2.33098 ± 0.0195696 (W 0.0055267) | 2.20701 ± 0.0141375 (W 0.00439384) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 98.0757 ± 0.261956 (W 0.115243) | 133.922 ± 0.611945 (W 0.857435) | 🔵 faer-fork 1.37× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 5.7127 ± 0.0162682 (W 0.00876382) | 6.87725 ± 0.0470568 (W 0.0102063) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 276.283 ± 0.58554 (W 0.228186) | 382.818 ± 3.53176 (W 1.35858) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 2.54824 ± 0.0164157 (W 0.00552727) | 3.1193 ± 0.0328286 (W 0.00626213) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 114.842 ± 0.79196 (W 0.324808) | 158.854 ± 0.563859 (W 0.555162) | 🔵 faer-fork 1.38× faster than `lapack-openblas` |  |

## linalg-tall, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.946638 ± 0.00784513 (W 0.00427826) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 52.2309 ± 0.113878 (W 0.156506) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.589346 ± 0.00263984 (W 0.00228032) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.591084 ± 0.0016919 (W 0.00281093) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 37.3239 ± 0.135028 (W 0.206472) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 37.1675 ± 0.10911 (W 0.0343458) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.743847 ± 0.00439113 (W 0.00316095) | 1.04475 ± 0.0220877 (W 0.00192359) | 🔵 faer-fork 1.40× faster than `lapack-openblas` | `!` between-start range over 5% |
| `lu/4096x256/b1` | 22.3514 ± 0.302229 (W 0.0580027) | 45.8347 ± 6.53601 (W 0.0928627) | 🔵 faer-fork 2.05× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/1024x64/b1` | 1.9807 ± 0.00727596 (W 0.00375333) | 2.26461 ± 0.0460227 (W 0.0054146) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `qr/4096x256/b1` | 83.8652 ± 5.85921 (W 0.150975) | 116.039 ± 3.60436 (W 0.256288) | 🔵 faer-fork 1.38× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 1.23641 ± 0.024271 (W 0.00397765) | 1.15539 ± 0.0240879 (W 0.00426789) | 🔴 faer-fork 1.07× slower than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/4096x256/b1` | 36.2572 ± 0.434669 (W 0.0951009) | 53.4721 ± 1.82193 (W 0.230792) | 🔵 faer-fork 1.47× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/1024x64/b1` | 3.10074 ± 0.0162591 (W 0.00574366) | 3.75742 ± 0.0662133 (W 0.00876509) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 102.346 ± 0.124003 (W 0.405006) | 159.318 ± 2.16919 (W 0.814023) | 🔵 faer-fork 1.56× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 1.70076 ± 0.00695799 (W 0.00436662) | 2.09601 ± 0.0252537 (W 0.00448385) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 53.5268 ± 0.15417 (W 0.0715741) | 74.1075 ± 2.36877 (W 0.577715) | 🔵 faer-fork 1.38× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-tall, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.832549 ± 0.0120849 (W 0.0035067) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 28.9718 ± 0.189672 (W 0.106946) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.312252 ± 0.0047335 (W 0.00305609) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.313765 ± 0.00431437 (W 0.0064884) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 24.0202 ± 0.314423 (W 0.214606) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 23.831 ± 0.32374 (W 0.103777) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.695698 ± 0.00320217 (W 0.00398459) | 0.893795 ± 0.018435 (W 0.00339592) | 🔵 faer-fork 1.28× faster than `lapack-openblas` |  |
| `lu/4096x256/b1` | 18.4712 ± 0.151131 (W 0.0781593) | 39.9088 ± 4.60093 (W 0.0765953) | 🔵 faer-fork 2.16× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/1024x64/b1` | 1.59577 ± 0.0105344 (W 0.00685327) | 1.99196 ± 0.0390432 (W 0.0060401) | 🔵 faer-fork 1.25× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/4096x256/b1` | 65.9689 ± 5.68245 (W 0.208799) | 93.2597 ± 4.93733 (W 0.190807) | 🔵 faer-fork 1.41× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/1024x64/b1` | 1.10922 ± 0.017064 (W 0.004629) | 1.00191 ± 0.0147397 (W 0.0020034) | 🔴 faer-fork 1.11× slower than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 26.7998 ± 0.0259151 (W 0.0546161) | 41.8207 ± 0.0896511 (W 0.0824991) | 🔵 faer-fork 1.56× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 2.73939 ± 0.0305521 (W 0.003951) | 3.27829 ± 0.0493723 (W 0.00585838) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 77.6012 ± 0.413309 (W 0.114711) | 119.708 ± 2.48914 (W 0.520084) | 🔵 faer-fork 1.54× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 1.61187 ± 0.0163942 (W 0.0046949) | 1.95902 ± 0.0145266 (W 0.00667492) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 44.7052 ± 0.0951696 (W 0.0623527) | 62.3944 ± 4.73178 (W 0.131259) | 🔵 faer-fork 1.40× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-tall, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 1.67169 ± 0.00610735 (W 0.00311847) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 143.052 ± 1.29938 (W 0.402379) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 2.27568 ± 0.011591 (W 0.00495933) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 2.27567 ± 0.0113079 (W 0.0062957) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 138.335 ± 0.262728 (W 0.160333) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 138.471 ± 0.270878 (W 0.150283) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.875477 ± 0.00740468 (W 0.00617955) | 0.953269 ± 0.00551136 (W 0.00294166) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `lu/4096x256/b1` | 41.6474 ± 0.0661862 (W 0.0365398) | 47.3342 ± 0.149543 (W 0.0754844) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 4.39712 ± 0.0223225 (W 0.00768275) | 3.55611 ± 0.0369174 (W 0.0048355) | 🔴 faer-fork 1.24× slower than `lapack-openblas` |  |
| `qr/4096x256/b1` | 231.588 ± 0.495786 (W 0.211369) | 224.629 ± 1.05245 (W 0.503773) | · |  |
| `qr_factor/1024x64/b1` | 2.04144 ± 0.0232786 (W 0.00493659) | 1.82243 ± 0.0146341 (W 0.00307201) | 🔴 faer-fork 1.12× slower than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 87.4899 ± 0.141411 (W 0.101921) | 112.668 ± 0.690924 (W 0.263131) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 5.61501 ± 0.01902 (W 0.0102641) | 6.25971 ± 0.0396816 (W 0.00908815) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `svd_thin/4096x256/b1` | 264.17 ± 0.424987 (W 0.291209) | 350.159 ± 1.53356 (W 0.707159) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 2.43809 ± 0.0165717 (W 0.00648805) | 2.74739 ± 0.0171958 (W 0.00598168) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 101.845 ± 0.249697 (W 0.129849) | 137.741 ± 0.762834 (W 0.17381) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |

## linalg-tall, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.827489 ± 0.0080818 (W 0.00391618) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 46.7046 ± 0.199383 (W 0.206513) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.646936 ± 0.00980605 (W 0.00230863) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.650418 ± 0.00559954 (W 0.00385099) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 39.5768 ± 0.0613167 (W 0.090007) | - | - | `*` one row has no measurement here |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 39.4587 ± 0.263908 (W 0.134225) | - | - | `*` one row has no measurement here |
| `lu/1024x64/b1` | 0.636246 ± 0.00321995 (W 0.0032412) | 0.682845 ± 0.00515781 (W 0.00388651) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `lu/4096x256/b1` | 17.1041 ± 0.0444817 (W 0.0569007) | 24.0016 ± 0.0480692 (W 0.0229609) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 1.8695 ± 0.0152583 (W 0.00479516) | 1.47049 ± 0.00359967 (W 0.00373221) | 🔴 faer-fork 1.27× slower than `lapack-openblas` |  |
| `qr/4096x256/b1` | 77.9222 ± 5.41419 (W 0.184296) | 73.5372 ± 0.279714 (W 0.272504) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 1.11665 ± 0.00277838 (W 0.00363108) | 0.785485 ± 0.00140056 (W 0.00431032) | 🔴 faer-fork 1.42× slower than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 31.4959 ± 0.0802608 (W 0.0487765) | 36.5114 ± 0.105908 (W 0.0372413) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 2.98595 ± 0.00740394 (W 0.00748432) | 3.13847 ± 0.0139901 (W 0.00573345) | · |  |
| `svd_thin/4096x256/b1` | 90.0539 ± 0.112644 (W 0.240152) | 123.605 ± 0.321682 (W 0.420267) | 🔵 faer-fork 1.37× faster than `lapack-openblas` |  |
| `svd_values/1024x64/b1` | 1.61287 ± 0.000770164 (W 0.00497982) | 1.72601 ± 0.00558709 (W 0.00471039) | 🔵 faer-fork 1.07× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 41.4883 ± 0.086062 (W 0.0549595) | 57.0066 ± 0.419239 (W 0.0699509) | 🔵 faer-fork 1.37× faster than `lapack-openblas` |  |

## linalg-tall, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/1024x64/b1` | 0.722838 ± 0.00682413 (W 0.0028074) | - | - | `*` one row has no measurement here |
| `full_piv_lu/4096x256/b1` | 23.7552 ± 0.144484 (W 0.0807751) | - | - | `*` one row has no measurement here |
| `householder_apply/1024x64/b1 [block(basis=64,target=64)]` | 0.381005 ± 0.00907411 (W 0.00362582) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/1024x64/b1 [sequence(basis=64,target=64)]` | 0.382263 ± 0.00957443 (W 0.00482401) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [block(basis=256,target=256)]` | 25.6039 ± 1.34819 (W 0.975911) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `householder_apply/4096x256/b1 [sequence(basis=256,target=256)]` | 24.7143 ± 0.79084 (W 1.14883) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/1024x64/b1` | 0.588695 ± 0.00333018 (W 0.00379832) | 0.57045 ± 0.00260317 (W 0.00319002) | · |  |
| `lu/4096x256/b1` | 13.0638 ± 0.0449693 (W 0.0360107) | 14.515 ± 0.0293005 (W 0.0191167) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `qr/1024x64/b1` | 1.477 ± 0.00816988 (W 0.00488922) | 1.17349 ± 0.00653148 (W 0.00169021) | 🔴 faer-fork 1.26× slower than `lapack-openblas` |  |
| `qr/4096x256/b1` | 59.8926 ± 5.20015 (W 0.0850236) | 50.381 ± 0.0408706 (W 0.0570796) | 🔴 faer-fork 1.19× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/1024x64/b1` | 1.00052 ± 0.00554055 (W 0.00422396) | 0.64408 ± 0.00314391 (W 0.00348527) | 🔴 faer-fork 1.55× slower than `lapack-openblas` |  |
| `qr_factor/4096x256/b1` | 23.1074 ± 0.103426 (W 0.0690763) | 25.0295 ± 0.0268909 (W 0.0593075) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `svd_thin/1024x64/b1` | 2.60595 ± 0.0171357 (W 0.00607243) | 2.71506 ± 0.0053772 (W 0.00403001) | · |  |
| `svd_thin/4096x256/b1` | 65.1855 ± 0.0842101 (W 0.0498742) | 88.9247 ± 4.57924 (W 0.0791409) | 🔵 faer-fork 1.36× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/1024x64/b1` | 1.512 ± 0.00847873 (W 0.00679344) | 1.59358 ± 0.00907043 (W 0.00511637) | 🔵 faer-fork 1.05× faster than `lapack-openblas` |  |
| `svd_values/4096x256/b1` | 32.7776 ± 0.101632 (W 0.0420883) | 45.2823 ± 0.207148 (W 0.055611) | 🔵 faer-fork 1.38× faster than `lapack-openblas` |  |

Not applicable to this population's shapes and reported as skipped: `cholesky/1024x64`, `cholesky/4096x256`, `eigh/1024x64`, `eigh/4096x256`, `full_piv_lu/1024x64`, `full_piv_lu/4096x256`, `householder_apply/1024x64`, `householder_apply/4096x256`, `solve/1024x64`, `solve/4096x256`, `triangular_solve/1024x64`, `triangular_solve/4096x256`, `upgrade_factor/1024x64`, `upgrade_factor/4096x256`.

## linalg-wide, f64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 74.8006 ± 0.648405 (W 0.435609) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.14622 ± 0.00487815 (W 0.00482902) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 16.2415 ± 0.144041 (W 0.0387219) | 35.9513 ± 0.582488 (W 0.0832303) | 🔵 faer-fork 2.21× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.417359 ± 0.00292013 (W 0.00304986) | 1.179 ± 0.139437 (W 0.00791679) | 🔵 faer-fork 2.82× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/256x4096/b1` | 30.957 ± 0.101968 (W 0.0902784) | 72.4523 ± 1.02898 (W 0.730352) | 🔵 faer-fork 2.34× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.754062 ± 0.0021993 (W 0.00240708) | 1.89025 ± 0.0234113 (W 0.0124396) | 🔵 faer-fork 2.51× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 27.3062 ± 0.341481 (W 0.0359911) | 65.2248 ± 2.17775 (W 0.354063) | 🔵 faer-fork 2.39× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.999548 ± 0.00784622 (W 0.00545434) | 1.75237 ± 0.0211745 (W 0.0115842) | 🔵 faer-fork 1.75× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 80.8704 ± 0.216853 (W 0.244499) | 224.136 ± 1.23721 (W 0.71838) | 🔵 faer-fork 2.77× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 2.25308 ± 0.00269766 (W 0.00348547) | 5.04605 ± 0.0307398 (W 0.0136328) | 🔵 faer-fork 2.24× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 32.6642 ± 0.0577102 (W 0.0581397) | 107.271 ± 1.65974 (W 0.372719) | 🔵 faer-fork 3.28× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 0.961155 ± 0.0051051 (W 0.00311128) | 2.61556 ± 0.0578417 (W 0.0157641) | 🔵 faer-fork 2.72× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-wide, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 33.0184 ± 0.221657 (W 0.088391) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.735205 ± 0.00628186 (W 0.00308109) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 6.77094 ± 0.0850621 (W 0.0731244) | 27.1244 ± 0.494261 (W 0.0555037) | 🔵 faer-fork 4.01× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.221813 ± 0.000604314 (W 0.00164765) | 0.955852 ± 0.143902 (W 0.00381462) | 🔵 faer-fork 4.31× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/256x4096/b1` | 10.6519 ± 0.0672223 (W 0.0334041) | 43.4196 ± 0.533783 (W 0.268364) | 🔵 faer-fork 4.08× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.375947 ± 0.000669262 (W 0.00168556) | 1.85052 ± 0.00724552 (W 0.00648426) | 🔵 faer-fork 4.92× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 9.79771 ± 0.12766 (W 0.030264) | 39.4096 ± 0.501394 (W 0.167895) | 🔵 faer-fork 4.02× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 0.614918 ± 0.00367903 (W 0.0034205) | 1.66849 ± 0.0163661 (W 0.0089625) | 🔵 faer-fork 2.71× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 34.3606 ± 0.127909 (W 0.0683864) | 148.042 ± 2.7534 (W 1.33428) | 🔵 faer-fork 4.31× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 1.70459 ± 0.0040499 (W 0.00591888) | 4.60767 ± 0.0333994 (W 0.0155952) | 🔵 faer-fork 2.70× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 17.4646 ± 0.0673582 (W 0.0233329) | 76.0793 ± 0.616868 (W 0.164893) | 🔵 faer-fork 4.36× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 0.833046 ± 0.0047483 (W 0.00342588) | 2.59143 ± 0.0208245 (W 0.00969718) | 🔵 faer-fork 3.11× faster than `lapack-openblas` |  |

## linalg-wide, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 27.3819 ± 0.0372721 (W 0.0639674) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.703916 ± 0.0144082 (W 0.00435485) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/256x4096/b1` | 5.19983 ± 0.0941818 (W 0.0233399) | 24.9593 ± 0.203197 (W 0.0430783) | 🔵 faer-fork 4.80× faster than `lapack-openblas` | `!` between-start range over 5% |
| `lu/64x1024/b1` | 0.195404 ± 0.357912 (W 0.00289365) | 0.918813 ± 0.13682 (W 0.00379919) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/256x4096/b1` | 7.33493 ± 0.0282808 (W 0.0228242) | 39.4423 ± 0.472133 (W 0.0724563) | 🔵 faer-fork 5.38× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.323287 ± 0.00326935 (W 0.00214446) | 1.85643 ± 0.00658544 (W 0.0114035) | 🔵 faer-fork 5.74× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 7.24491 ± 0.118372 (W 0.0293701) | 37.8133 ± 1.40771 (W 0.812395) | 🔵 faer-fork 5.22× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.554345 ± 0.00343449 (W 0.00647364) | 1.6854 ± 0.00843847 (W 0.00831895) | 🔵 faer-fork 3.04× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 28.5304 ± 0.078028 (W 0.0551738) | 138.058 ± 3.51623 (W 0.475907) | 🔵 faer-fork 4.84× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/64x1024/b1` | 1.60911 ± 0.00375097 (W 0.00450182) | 4.57935 ± 0.0311138 (W 0.0125988) | 🔵 faer-fork 2.85× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 15.0462 ± 0.0776011 (W 0.0320054) | 74.3725 ± 2.05142 (W 1.24325) | 🔵 faer-fork 4.94× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 0.808381 ± 0.00299219 (W 0.00287489) | 2.56986 ± 0.0130518 (W 0.0109197) | 🔵 faer-fork 3.18× faster than `lapack-openblas` |  |

## linalg-wide, f64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 71.5487 ± 0.910043 (W 0.22696) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.04195 ± 0.00455671 (W 0.00356996) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 13.3849 ± 0.0421291 (W 0.0169642) | 20.4132 ± 0.059265 (W 0.028824) | 🔵 faer-fork 1.53× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.314067 ± 0.00184587 (W 0.00219541) | 0.708179 ± 0.0050259 (W 0.00272685) | 🔵 faer-fork 2.25× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 27.8001 ± 0.173181 (W 0.0793747) | 69.8338 ± 4.4774 (W 0.637348) | 🔵 faer-fork 2.51× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/64x1024/b1` | 0.628034 ± 0.00204622 (W 0.00306094) | 1.69398 ± 0.016773 (W 0.0099726) | 🔵 faer-fork 2.70× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 25.3881 ± 0.214179 (W 0.0568574) | 53.65 ± 0.989888 (W 0.620267) | 🔵 faer-fork 2.11× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 0.56479 ± 0.0049613 (W 0.00300496) | 1.39575 ± 0.00946997 (W 0.00308296) | 🔵 faer-fork 2.47× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 86.0406 ± 0.284878 (W 0.106872) | 195.844 ± 0.689712 (W 0.919429) | 🔵 faer-fork 2.28× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 2.32036 ± 0.131709 (W 0.00597875) | 4.58905 ± 0.0316825 (W 0.0104105) | 🔵 faer-fork 1.98× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/256x4096/b1` | 38.3938 ± 0.123288 (W 0.0672789) | 90.9847 ± 0.90783 (W 0.352356) | 🔵 faer-fork 2.37× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 1.03969 ± 0.00761117 (W 0.00481025) | 2.255 ± 0.0716646 (W 0.00741415) | 🔵 faer-fork 2.17× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-wide, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 30.356 ± 0.208052 (W 0.0441553) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.648086 ± 0.00515973 (W 0.00263966) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 4.05965 ± 0.016369 (W 0.0100022) | 12.1143 ± 0.0476831 (W 0.0240942) | 🔵 faer-fork 2.98× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.116342 ± 0.000599555 (W 0.000460732) | 0.489572 ± 0.00385369 (W 0.00272895) | 🔵 faer-fork 4.21× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 7.62434 ± 0.0366204 (W 0.0229086) | 42.0969 ± 0.224687 (W 0.242208) | 🔵 faer-fork 5.52× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.249155 ± 0.00100641 (W 0.00180016) | 1.56689 ± 0.0345748 (W 0.0205855) | 🔵 faer-fork 6.29× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/256x4096/b1` | 6.64509 ± 0.0307409 (W 0.0157765) | 28.5363 ± 0.326513 (W 0.255276) | 🔵 faer-fork 4.29× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 0.195117 ± 0.00123871 (W 0.00166027) | 1.26678 ± 0.0190403 (W 0.00467196) | 🔵 faer-fork 6.49× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 39.7141 ± 0.109746 (W 0.0988754) | 126.499 ± 2.54175 (W 0.390605) | 🔵 faer-fork 3.19× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 1.76359 ± 0.00941009 (W 0.00307944) | 4.09683 ± 0.0434429 (W 0.0124485) | 🔵 faer-fork 2.32× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 23.0271 ± 0.0310599 (W 0.033267) | 64.4427 ± 0.439964 (W 0.30917) | 🔵 faer-fork 2.80× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 0.907313 ± 0.00603233 (W 0.00680398) | 2.18051 ± 0.0238101 (W 0.00862116) | 🔵 faer-fork 2.40× faster than `lapack-openblas` |  |

## linalg-wide, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 24.73 ± 0.108394 (W 0.0470799) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 0.608143 ± 0.0133191 (W 0.00291077) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/256x4096/b1` | 2.54688 ± 0.00722715 (W 0.00747351) | 9.85318 ± 0.0415786 (W 0.0201055) | 🔵 faer-fork 3.87× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.088726 ± 0.000536208 (W 0.000335355) | 0.451856 ± 0.00264492 (W 0.00247977) | 🔵 faer-fork 5.09× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 4.34755 ± 0.0113235 (W 0.0104498) | 38.5274 ± 0.613268 (W 0.252996) | 🔵 faer-fork 8.86× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.196612 ± 0.00169984 (W 0.00222324) | 1.56959 ± 0.0210659 (W 0.0153649) | 🔵 faer-fork 7.98× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 3.57844 ± 0.00375138 (W 0.00615471) | 25.3159 ± 0.740431 (W 0.125473) | 🔵 faer-fork 7.07× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.146428 ± 0.00602453 (W 0.000583814) | 1.28183 ± 0.0223241 (W 0.00502964) | 🔵 faer-fork 8.75× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/256x4096/b1` | 33.8667 ± 0.619201 (W 0.364214) | 118.85 ± 1.13179 (W 0.328649) | 🔵 faer-fork 3.51× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 1.68087 ± 0.11853 (W 0.00567676) | 4.0621 ± 0.0391482 (W 0.0115201) | 🔵 faer-fork 2.42× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/256x4096/b1` | 20.6487 ± 0.23908 (W 0.0308452) | 61.839 ± 0.776498 (W 0.267645) | 🔵 faer-fork 2.99× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 0.878189 ± 0.0108993 (W 0.00442849) | 2.16473 ± 0.0168226 (W 0.00753314) | 🔵 faer-fork 2.46× faster than `lapack-openblas` |  |

## linalg-wide, c64, c order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 227.109 ± 5.85032 (W 0.661927) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/64x1024/b1` | 2.4768 ± 0.0378554 (W 0.00964522) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 46.3715 ± 0.215504 (W 0.0940362) | 82.5983 ± 0.254817 (W 0.0916608) | 🔵 faer-fork 1.78× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 1.00066 ± 0.00844754 (W 0.00317449) | 1.66014 ± 0.0208686 (W 0.00410082) | 🔵 faer-fork 1.66× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 107.547 ± 0.272233 (W 0.226541) | 180.426 ± 1.53635 (W 1.86848) | 🔵 faer-fork 1.68× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 2.51066 ± 0.0139732 (W 0.00502034) | 3.60457 ± 0.0339953 (W 0.00957454) | 🔵 faer-fork 1.44× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 97.2052 ± 0.121703 (W 0.321045) | 161.652 ± 1.96681 (W 1.91325) | 🔵 faer-fork 1.66× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 2.5874 ± 0.0140493 (W 0.00502039) | 3.35471 ± 0.0314981 (W 0.00373288) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 265.22 ± 0.470855 (W 3.25405) | 682.278 ± 1.96081 (W 2.59491) | 🔵 faer-fork 2.57× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 5.62888 ± 0.0244629 (W 0.00661741) | 11.8785 ± 0.13604 (W 0.0281208) | 🔵 faer-fork 2.11× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 102.051 ± 0.254489 (W 0.28179) | 306.786 ± 7.03978 (W 1.46875) | 🔵 faer-fork 3.01× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 2.41541 ± 0.0170974 (W 0.00461647) | 5.65993 ± 0.112758 (W 0.0232143) | 🔵 faer-fork 2.34× faster than `lapack-openblas` | `!` between-start range over 5% |

## linalg-wide, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 82.962 ± 0.802885 (W 0.447856) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.33716 ± 0.0077223 (W 0.00485888) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 17.4965 ± 0.141366 (W 0.0567027) | 56.7203 ± 0.143849 (W 0.0908649) | 🔵 faer-fork 3.24× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.48859 ± 0.0313832 (W 0.0370483) | 1.19389 ± 0.0205881 (W 0.00458186) | 🔵 faer-fork 2.44× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/256x4096/b1` | 31.8469 ± 0.0856926 (W 0.0634891) | 90.3945 ± 2.14088 (W 1.67952) | 🔵 faer-fork 2.84× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/64x1024/b1` | 0.876848 ± 0.0026802 (W 0.003341) | 1.68242 ± 0.0110961 (W 0.00349414) | 🔵 faer-fork 1.92× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 27.7525 ± 0.0865294 (W 0.0315965) | 73.1467 ± 2.2435 (W 0.892197) | 🔵 faer-fork 2.64× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.981921 ± 0.00428493 (W 0.00515271) | 1.40845 ± 0.0191309 (W 0.00392614) | 🔵 faer-fork 1.43× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 90.5472 ± 0.14289 (W 0.0673372) | 446.543 ± 1.48496 (W 3.20839) | 🔵 faer-fork 4.93× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 3.02091 ± 0.0100832 (W 0.0100312) | 9.83407 ± 0.0825175 (W 0.0295582) | 🔵 faer-fork 3.26× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 41.6123 ± 0.0761517 (W 0.0825905) | 222.542 ± 6.06185 (W 0.399337) | 🔵 faer-fork 5.35× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 1.59975 ± 0.00375005 (W 0.00629642) | 5.01408 ± 0.0752059 (W 0.0107841) | 🔵 faer-fork 3.13× faster than `lapack-openblas` |  |

## linalg-wide, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 55.2535 ± 0.586309 (W 0.167853) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.2097 ± 0.0106584 (W 0.00621629) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 11.7562 ± 0.149584 (W 0.0475206) | 49.952 ± 1.72148 (W 0.0735511) | 🔵 faer-fork 4.25× faster than `lapack-openblas` | `!` between-start range over 5% |
| `lu/64x1024/b1` | 0.357078 ± 0.0039151 (W 0.00205789) | 1.05943 ± 0.010125 (W 0.00313208) | 🔵 faer-fork 2.97× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 19.6 ± 0.121969 (W 0.0833148) | 73.336 ± 2.57386 (W 0.755008) | 🔵 faer-fork 3.74× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/64x1024/b1` | 0.612054 ± 0.001815 (W 0.00305537) | 1.41019 ± 0.0291882 (W 0.00407839) | 🔵 faer-fork 2.30× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/256x4096/b1` | 16.2519 ± 0.187298 (W 0.0374937) | 56.4913 ± 1.30587 (W 0.897412) | 🔵 faer-fork 3.48× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/64x1024/b1` | 0.720832 ± 0.00265753 (W 0.00452208) | 1.13766 ± 0.0134918 (W 0.00547999) | 🔵 faer-fork 1.58× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 65.8853 ± 0.0454307 (W 0.165639) | 399.987 ± 4.52182 (W 2.74423) | 🔵 faer-fork 6.07× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 2.63465 ± 0.0149765 (W 0.00667414) | 9.79125 ± 0.0962508 (W 0.0288231) | 🔵 faer-fork 3.72× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 32.7803 ± 0.0672982 (W 0.0403388) | 209.426 ± 6.93105 (W 1.18526) | 🔵 faer-fork 6.39× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/64x1024/b1` | 1.50518 ± 0.00596384 (W 0.00604932) | 5.10005 ± 0.043194 (W 0.0152656) | 🔵 faer-fork 3.39× faster than `lapack-openblas` |  |

## linalg-wide, c64, f order, 1T (CPU 4)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 224.446 ± 5.75234 (W 0.614267) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/64x1024/b1` | 2.32838 ± 0.0325344 (W 0.00899731) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 42.1073 ± 0.0858091 (W 0.0557615) | 55.8715 ± 0.252893 (W 0.0532755) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.899232 ± 0.00324475 (W 0.0036865) | 1.27577 ± 0.00362914 (W 0.00254426) | 🔵 faer-fork 1.42× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 103.122 ± 0.396944 (W 0.352411) | 183.824 ± 1.41195 (W 0.739327) | 🔵 faer-fork 1.78× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 2.41743 ± 0.00537768 (W 0.00668418) | 3.79688 ± 0.0325238 (W 0.0141684) | 🔵 faer-fork 1.57× faster than `lapack-openblas` |  |
| `qr_factor/256x4096/b1` | 96.0057 ± 0.220282 (W 0.185051) | 146.198 ± 2.79376 (W 1.12068) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 2.23113 ± 0.00384415 (W 0.0026286) | 2.98543 ± 0.0357339 (W 0.00559025) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 277.251 ± 0.328576 (W 0.544094) | 648.406 ± 2.55336 (W 1.56791) | 🔵 faer-fork 2.34× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 5.74611 ± 0.0281084 (W 0.0095892) | 11.3099 ± 0.132807 (W 0.0178915) | 🔵 faer-fork 1.97× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 114.948 ± 0.860552 (W 0.63008) | 284.422 ± 1.27158 (W 1.09079) | 🔵 faer-fork 2.47× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 2.54715 ± 0.0226455 (W 0.00498434) | 5.27774 ± 0.0769882 (W 0.0152556) | 🔵 faer-fork 2.07× faster than `lapack-openblas` |  |

## linalg-wide, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 79.2368 ± 0.637395 (W 0.326874) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.2085 ± 0.0049973 (W 0.004367) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 13.4025 ± 0.0636342 (W 0.016549) | 30.4972 ± 0.0718875 (W 0.0268247) | 🔵 faer-fork 2.28× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.384669 ± 0.0342674 (W 0.00289863) | 0.791759 ± 0.00292082 (W 0.0025451) | 🔵 faer-fork 2.06× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/256x4096/b1` | 27.8053 ± 0.17732 (W 0.0482234) | 88.5913 ± 0.398772 (W 0.407143) | 🔵 faer-fork 3.19× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.772774 ± 0.0030844 (W 0.00353296) | 1.67725 ± 0.230936 (W 0.0110792) | 🔵 faer-fork 2.17× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/256x4096/b1` | 24.9465 ± 0.121706 (W 0.0330388) | 54.5215 ± 0.474562 (W 0.134044) | 🔵 faer-fork 2.19× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 0.649759 ± 0.0013616 (W 0.00223132) | 1.00642 ± 0.00538367 (W 0.00199404) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 102.903 ± 0.167952 (W 0.107305) | 395.088 ± 4.90923 (W 0.507481) | 🔵 faer-fork 3.84× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 3.13632 ± 0.0235481 (W 0.00730172) | 9.2097 ± 0.0337713 (W 0.0266024) | 🔵 faer-fork 2.94× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 53.6448 ± 0.137107 (W 0.0902884) | 197.843 ± 0.574019 (W 0.298462) | 🔵 faer-fork 3.69× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 1.70984 ± 0.00818886 (W 0.00572335) | 4.64595 ± 0.0194194 (W 0.0210706) | 🔵 faer-fork 2.72× faster than `lapack-openblas` |  |

## linalg-wide, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `full_piv_lu/256x4096/b1` | 50.9975 ± 0.595674 (W 0.1354) | - | - | `*` one row has no measurement here |
| `full_piv_lu/64x1024/b1` | 1.07166 ± 0.0056696 (W 0.00457658) | - | - | `*` one row has no measurement here |
| `lu/256x4096/b1` | 7.70762 ± 0.0658295 (W 0.0241536) | 23.6478 ± 0.0743903 (W 0.0244921) | 🔵 faer-fork 3.07× faster than `lapack-openblas` |  |
| `lu/64x1024/b1` | 0.248785 ± 0.000692102 (W 0.0016962) | 0.672938 ± 0.0054516 (W 0.00252157) | 🔵 faer-fork 2.70× faster than `lapack-openblas` |  |
| `qr/256x4096/b1` | 15.3831 ± 0.0675152 (W 0.0277605) | 72.1719 ± 1.05509 (W 0.284738) | 🔵 faer-fork 4.69× faster than `lapack-openblas` |  |
| `qr/64x1024/b1` | 0.504128 ± 0.00238089 (W 0.00241283) | 1.4329 ± 0.181272 (W 0.015203) | 🔵 faer-fork 2.84× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/256x4096/b1` | 13.229 ± 0.0742087 (W 0.0250952) | 38.1115 ± 0.447839 (W 0.0756595) | 🔵 faer-fork 2.88× faster than `lapack-openblas` |  |
| `qr_factor/64x1024/b1` | 0.393262 ± 0.0011874 (W 0.00253787) | 0.723974 ± 0.00342033 (W 0.00305106) | 🔵 faer-fork 1.84× faster than `lapack-openblas` |  |
| `svd_thin/256x4096/b1` | 78.2735 ± 0.0973671 (W 0.0931468) | 361.849 ± 7.56545 (W 0.798881) | 🔵 faer-fork 4.62× faster than `lapack-openblas` |  |
| `svd_thin/64x1024/b1` | 2.74192 ± 0.0299152 (W 0.00725855) | 9.12865 ± 0.0921142 (W 0.0205835) | 🔵 faer-fork 3.33× faster than `lapack-openblas` |  |
| `svd_values/256x4096/b1` | 44.7572 ± 0.4107 (W 0.0759868) | 183.685 ± 0.342628 (W 0.366917) | 🔵 faer-fork 4.10× faster than `lapack-openblas` |  |
| `svd_values/64x1024/b1` | 1.5943 ± 0.00889819 (W 0.00656449) | 4.66763 ± 0.0500007 (W 0.0152266) | 🔵 faer-fork 2.93× faster than `lapack-openblas` |  |

Not applicable to this population's shapes and reported as skipped: `cholesky/256x4096`, `cholesky/64x1024`, `eigh/256x4096`, `eigh/64x1024`, `full_piv_lu/256x4096`, `full_piv_lu/64x1024`, `solve/256x4096`, `solve/64x1024`, `triangular_solve/256x4096`, `triangular_solve/64x1024`.

Repeated process sets describe observed repeatability under the recorded order schedule; they are not a paired baseline/candidate experiment and do not establish equal performance between engines.

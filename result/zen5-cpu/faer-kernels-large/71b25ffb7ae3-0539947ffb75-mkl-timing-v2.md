<!-- generated from data/results/zen5-cpu/faer-kernels-large/20261101T005110Z-pub-71b25ffb-20261031-large1024-mkl/report.md by scripts/publish_report.py; the report below is the source of truth -->

# `faer-kernels-large` on `zen5-cpu`

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
- timestamp: `2026-11-01T03:10:10.179560Z`
- timing policy: v2, median of 5 reps, priming 250 ms (time-based, identical on every row)
- guards: idle window 3 s, max busy 5.0% including SMT siblings, 3 attempts
- command: `scripts/record_run.py zen5-cpu faer-kernels-large --checkout /home/shinaoka/.local/state/faer-measurement-checkouts/71b25ffb7ae3ce038ec25b35c91e526be41b9a63/t4a-faer --upstream extern/upstream-faer --vendor mkl --engines faer-fork,faer-upstream,lapack-mkl --threads 4,8 --regimes linalg-large,gemm-large,linalg-boundary --shapes 1024,1024x1024x1024,255,257,511,513 --dtypes f64,c64 --reps 5 --aa 3 --prime-ms 250 --label pub-71b25ffb-20261031-large1024-mkl --no-publish`
- raw data: `data/results/zen5-cpu/faer-kernels-large/20261101T005110Z-pub-71b25ffb-20261031-large1024-mkl/`

## What was measured

- **Workload** — Direct calls into one faer revision: square and rectangular dense matrices, C (row-major) and F (column-major) order, `f64` and `c64`. A shape is `N` for square, `MxN` for rectangular, or `MxKxN` for `gemm`, which is a three-index operation and cannot be written as two. Sizes are the matrix dimensions, not a memory budget, so a case name says exactly what was factored. `gemm` measures `linalg::matmul::matmul` into a caller-prepared destination with `Accum::Replace`; there is no operator path, so one shape is one work.
  Source: The fork's own public API (`faer/src/linalg`): `matmul`, the QR factor and composite, `upgrade_householder_factor`, the block/sequence Householder apply, LU and full-pivot LU, Cholesky, triangular solve, solve, thin SVD, singular values and the symmetric/nonsymmetric eigensolvers. Inputs are seeded from the case, so `verify` and `run` measure the same matrices and a rerun is reproducible.
  Known blind spot: Only the faer entry points are measured. tlinalg's packing, batch loop and lane policy, tenferro's tensor construction and dtype dispatch, and the small-`m` decode-projection shapes are other repositories' rows (tlinalg-benchmark, tenferro-benchmark).
  Known blind spot: Vendor C-order cells use CBLAS/LAPACKE row-major entry points. Workspace allocation or layout conversion internal to those APIs remains timed; these are not prepared-column-major or transpose measurements.
  Known blind spot: `gemm` covers the tall class's two Householder legs (a 16-wide basis and a 240-column target over 4096 rows: the reduction and the write-back) beside a vendor `?gemm` on the same leg. A single leg beside a vendor gemm is a diagnostic reference, not the equivalent implementation of the whole update, and the row is labelled accordingly.
  Known blind spot: `householder_apply` measures block apply and the one-block sequence form as two distinct rows, labelled with basis width min(m,n) and target width n. QR fixture preparation is outside timing. Independently varied basis/target widths and multi-panel sequences are not covered.
  Known blind spot: Allocation performed inside the measured call stays inside the clock. The fork's two row splits allocate their partial buffers inside the public call, and the public scratch function does not expose them; the campaign reports that as it is instead of changing faer's API to make the boundary look cleaner.
  Known blind spot: `cholesky`, `eigh`, `solve` and `triangular_solve` are measured on square shapes only: the matrix they factor or solve with is square by definition (self-adjoint for the first two, a triangular factor for the last). `lu` and `full_piv_lu` are not gated that way -- they take the declared rectangular shapes too, with `min(m, n)` pivots and a trapezoidal `L` or `U`, which is what `dgetrf` does as well -- so a rectangular LU cell is measured in both orders beside its square one.
  Known blind spot: `f32`/`c32`, the large regime's 1024 shapes, BLIS, sparse, iterative and GPU arms are later declarations, not machinery built now.
  Known blind spot: A vendor arm records the library it linked. Only OpenBLAS reports the kernel its runtime dispatched to; MKL names no kernel and no processor count, so its manifest leaves both empty rather than inferring them.
  Known blind spot: Known limitation (71b25ffb recording): multi-thread figures include threadteam 0.2.0 and are not final for the 0.3.0 runtime.
- **Rows** — one row per engine in every table below:
  - `faer-fork` — The measured library: the tensor4all fork (`t4a-faer`, `[lib] name = "faer"`) at the checkout the harness linked by path. This is the row the campaign exists for; the fork's three perf experiments and the two correctness changes land here.
    Identity: the fork revision in this run's manifest (`library.commit`), pinned by `pins/t4a-faer.rev`
    Caveat: Both faer crates declare `[lib] name = "faer"`. They are distinct dependency keys (`faer_fork = { package = "t4a-faer" }`, `faer_upstream = { package = "faer" }`) and therefore distinct Rust crate identities, but their `Mat`, `Par` and trait types are not interchangeable: every adapter is written per arm, and shared transitive dependencies can unify Cargo features, so both arms declare equivalent feature sets and the resolved lock is recorded. For the 71b25ffb recording: measured at 71b25ffb, the commit immediately before the 0.28.0 release commit 325e482; the only difference is Cargo.lock and faer/Cargo.toml (threadteam 0.2.0 in the measured build, 0.3.0 as shipped, plus the version string). Single-thread numbers apply to 0.28.0 as released; multi-thread numbers carry that threadteam difference and will be re-measured in the next campaign.
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
- CPU sets: 4T -> `4-7`, 8T -> `4-11`

Every timed cell matches a successful verification census, including operation variants.
Each cell is median of process medians ± sample SD of those medians; W is the median
within-process sample SD. All values are milliseconds. These are descriptive spreads,
not confidence intervals. The between-process spread includes the rotating-order schedule.
Each process retains 5 chronological calls; 3 complete process sets are recorded.
Spread guide (computed from this run's own rows): per-engine between-start range median 0.76%, worst 54.88% among cells of 1 us or more (a sub-microsecond row is timer and scheduler jitter, not kernel time); 94 of 1144 engine cells exceed 5% and carry `!`; median within-process relative SD 0.29%. A cell whose `±`, `!` or `p` is as large as the difference you are reading is not evidence of a regression.
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

## linalg-large, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 7.77327 ± 0.114583 (W 0.0167459) | 7.64989 ± 0.143131 (W 0.085303) | 8.32398 ± 0.0294811 (W 0.036899) | · | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |
| `eigh/n1024/b1` | 114.847 ± 1.06906 (W 0.747124) | 116.815 ± 3.8464 (W 0.153368) | 123.434 ± 0.827326 (W 0.154483) | · | 🔵 faer-fork 1.07× faster than `lapack-mkl` | `!` between-start range over 5% |
| `full_piv_lu/n1024/b1` | 60.409 ± 0.0373774 (W 0.092244) | 70.4047 ± 0.556005 (W 0.162396) | - | 🔵 faer-fork 1.17× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 15.0847 ± 3.22688 (W 0.0937436) | 21.3968 ± 0.318531 (W 0.125984) | 11.303 ± 1.96019 (W 0.0379406) | 🔵 faer-fork 1.42× faster than `faer-upstream` | 🔴 faer-fork 1.33× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 48.9699 ± 3.93367 (W 0.134802) | 57.5367 ± 0.956206 (W 0.117256) | 60.7512 ± 0.367386 (W 0.183077) | 🔵 faer-fork 1.17× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n1024/b1` | 19.3709 ± 0.118661 (W 0.0944845) | 74.3184 ± 0.39795 (W 0.114405) | 21.0289 ± 0.203018 (W 0.0571875) | 🔵 faer-fork 3.84× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 20.9355 ± 0.154381 (W 0.0646935) | 21.0299 ± 0.0635187 (W 0.172236) | 11.4284 ± 0.174643 (W 0.0441698) | · | 🔴 faer-fork 1.83× slower than `lapack-mkl` |  |
| `svd_thin/n1024/b1` | 236.264 ± 0.556915 (W 1.25679) | 292.66 ± 0.389285 (W 1.39049) | 294.34 ± 1.37652 (W 3.25165) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 123.784 ± 0.530765 (W 0.558973) | 189.832 ± 0.820168 (W 0.435318) | 124.393 ± 1.55024 (W 1.71165) | 🔵 faer-fork 1.53× faster than `faer-upstream` | · |  |
| `triangular_solve/n1024/b1` | 0.083425 ± 0.00467883 (W 0.000647479) | 0.077615 ± 0.00708098 (W 0.00177166) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-large, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 6.30333 ± 0.0479268 (W 0.0253734) | 6.41411 ± 0.196059 (W 0.0402417) | 5.2783 ± 0.00944455 (W 0.0319151) | · | 🔴 faer-fork 1.19× slower than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n1024/b1` | 90.5157 ± 0.106689 (W 0.403431) | 97.3859 ± 4.04284 (W 0.315878) | 84.2342 ± 0.374548 (W 0.35432) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.07× slower than `lapack-mkl` | `!` between-start range over 5% |
| `full_piv_lu/n1024/b1` | 48.035 ± 0.256192 (W 0.110057) | 56.5101 ± 0.341414 (W 0.109142) | - | 🔵 faer-fork 1.18× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 11.8128 ± 3.35043 (W 0.0333092) | 19.1082 ± 0.72481 (W 0.0966093) | 7.0345 ± 1.75286 (W 0.0360515) | 🔵 faer-fork 1.62× faster than `faer-upstream` | 🔴 faer-fork 1.68× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 31.2813 ± 4.27437 (W 0.0695404) | 43.4046 ± 0.29593 (W 1.38208) | 44.6357 ± 0.375703 (W 0.0853212) | 🔵 faer-fork 1.39× faster than `faer-upstream` | 🔵 faer-fork 1.43× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n1024/b1` | 10.4114 ± 0.178917 (W 0.0808454) | 71.7089 ± 0.48922 (W 0.30748) | 14.4861 ± 0.0452868 (W 0.0402402) | 🔵 faer-fork 6.89× faster than `faer-upstream` | 🔵 faer-fork 1.39× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 17.8816 ± 0.13385 (W 0.0575084) | 18.2066 ± 0.174011 (W 0.0819016) | 7.04534 ± 0.0344814 (W 0.0328391) | · | 🔴 faer-fork 2.54× slower than `lapack-mkl` |  |
| `svd_thin/n1024/b1` | 173.95 ± 0.171173 (W 0.360694) | 243.734 ± 1.50749 (W 0.696714) | 228.979 ± 0.370073 (W 0.800777) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 97.0136 ± 0.330767 (W 0.206721) | 163.045 ± 1.46887 (W 0.231586) | 94.2279 ± 0.887221 (W 0.508223) | 🔵 faer-fork 1.68× faster than `faer-upstream` | · |  |
| `triangular_solve/n1024/b1` | 0.068147 ± 0.0011398 (W 0.000348469) | 0.068117 ± 0.00158385 (W 0.000493826) | - | · | - | `*` one row has no measurement here |

## linalg-large, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 5.18202 ± 0.0146671 (W 0.00524331) | 5.64047 ± 0.0605969 (W 0.0988483) | 6.69755 ± 0.187224 (W 0.0345945) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n1024/b1` | 112.625 ± 0.647374 (W 0.456113) | 114.304 ± 3.90546 (W 0.476568) | 121.29 ± 0.365658 (W 0.132562) | · | 🔵 faer-fork 1.08× faster than `lapack-mkl` | `!` between-start range over 5% |
| `full_piv_lu/n1024/b1` | 58.2088 ± 0.0929757 (W 0.0484422) | 61.1812 ± 0.320539 (W 0.0566336) | - | · | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 12.8778 ± 0.0557191 (W 0.0179093) | 14.1401 ± 0.151248 (W 0.136497) | 9.53173 ± 0.0423968 (W 0.0142167) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.35× slower than `lapack-mkl` |  |
| `qr/n1024/b1` | 46.5381 ± 4.23609 (W 0.059551) | 49.968 ± 1.14729 (W 0.0485746) | 62.7121 ± 0.150461 (W 0.105291) | · | 🔵 faer-fork 1.35× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n1024/b1` | 17.238 ± 0.048803 (W 0.0169922) | 20.6288 ± 0.164888 (W 0.0215232) | 19.1197 ± 0.0920602 (W 0.0151211) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 18.5967 ± 0.0359477 (W 0.0880186) | 13.487 ± 0.0810593 (W 0.18365) | 9.55915 ± 0.062651 (W 0.0249013) | 🔴 faer-fork 1.38× slower than `faer-upstream` | 🔴 faer-fork 1.95× slower than `lapack-mkl` |  |
| `svd_thin/n1024/b1` | 228.242 ± 0.822022 (W 0.487873) | 283.646 ± 0.890089 (W 0.654011) | 273.028 ± 1.07128 (W 0.693511) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 115.279 ± 0.607425 (W 0.145547) | 180.429 ± 0.606685 (W 0.389217) | 125.382 ± 0.978392 (W 0.995055) | 🔵 faer-fork 1.57× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `triangular_solve/n1024/b1` | 0.110014 ± 0.00356516 (W 0.00115065) | 0.101178 ± 0.00698582 (W 0.000937055) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-large, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 3.74491 ± 0.0378697 (W 0.00723193) | 4.12953 ± 0.0605552 (W 0.0565229) | 4.01302 ± 0.170238 (W 0.0339304) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.07× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n1024/b1` | 88.3412 ± 0.106575 (W 0.0489174) | 95.1438 ± 4.16963 (W 0.316185) | 82.9512 ± 0.36391 (W 0.133657) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` | `!` between-start range over 5% |
| `full_piv_lu/n1024/b1` | 45.8876 ± 0.26739 (W 0.0460669) | 49.0867 ± 0.269622 (W 0.0721578) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 9.81516 ± 0.0815034 (W 0.025938) | 11.6309 ± 0.113004 (W 0.107227) | 5.98897 ± 0.0191743 (W 0.0121031) | 🔵 faer-fork 1.18× faster than `faer-upstream` | 🔴 faer-fork 1.64× slower than `lapack-mkl` |  |
| `qr/n1024/b1` | 28.8363 ± 4.2417 (W 0.0317628) | 36.3079 ± 1.33982 (W 0.372589) | 48.478 ± 0.222183 (W 0.119153) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔵 faer-fork 1.68× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n1024/b1` | 9.11079 ± 0.145241 (W 0.0135743) | 18.799 ± 0.168165 (W 0.205548) | 13.458 ± 0.103367 (W 0.0150991) | 🔵 faer-fork 2.06× faster than `faer-upstream` | 🔵 faer-fork 1.48× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 15.4376 ± 0.0491181 (W 0.0301688) | 10.8692 ± 0.125145 (W 0.125511) | 5.97523 ± 0.0915889 (W 0.0150982) | 🔴 faer-fork 1.42× slower than `faer-upstream` | 🔴 faer-fork 2.58× slower than `lapack-mkl` |  |
| `svd_thin/n1024/b1` | 167.263 ± 0.356852 (W 0.23539) | 237.129 ± 1.19541 (W 0.694742) | 209.996 ± 0.618243 (W 1.38371) | 🔵 faer-fork 1.42× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 88.3377 ± 0.254147 (W 0.0622824) | 154.498 ± 0.532172 (W 0.232002) | 94.9728 ± 1.15152 (W 0.643541) | 🔵 faer-fork 1.75× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `triangular_solve/n1024/b1` | 0.09109 ± 0.00377288 (W 0.000773534) | 0.084317 ± 0.00320908 (W 0.000495917) | - | 🔴 faer-fork 1.08× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-large, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 19.6558 ± 0.114871 (W 0.195577) | 20.4771 ± 2.88025 (W 0.355643) | 21.6206 ± 0.107976 (W 0.0710683) | · | 🔵 faer-fork 1.10× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `eigh/n1024/b1` | 244.77 ± 0.413454 (W 0.488231) | 251.138 ± 0.65942 (W 0.55968) | 346.265 ± 0.565362 (W 0.489878) | · | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `full_piv_lu/n1024/b1` | 140.334 ± 0.410617 (W 0.414504) | 154.711 ± 6.05032 (W 0.981517) | - | 🔵 faer-fork 1.10× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/n1024/b1` | 38.9427 ± 0.118308 (W 0.202486) | 44.9521 ± 5.45974 (W 0.54592) | 40.796 ± 0.168505 (W 0.110261) | 🔵 faer-fork 1.15× faster than `faer-upstream` | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 148.162 ± 0.440265 (W 0.269738) | 161.641 ± 7.37307 (W 0.422355) | 183.862 ± 0.708429 (W 0.355569) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.24× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n1024/b1` | 64.2206 ± 0.22829 (W 0.258575) | 117.533 ± 0.744897 (W 0.221114) | 74.1459 ± 0.35419 (W 0.0950577) | 🔵 faer-fork 1.83× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 39.3575 ± 0.30067 (W 0.141494) | 45.379 ± 6.98952 (W 0.39093) | 39.1487 ± 0.271262 (W 0.144469) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n1024/b1` | 565.659 ± 0.949015 (W 0.890843) | 605.186 ± 3.75276 (W 1.1727) | 731.583 ± 7.33583 (W 3.33395) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 316.621 ± 0.498963 (W 0.544446) | 367.738 ± 5.73058 (W 1.25158) | 368.326 ± 14.2583 (W 0.938651) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔵 faer-fork 1.16× faster than `lapack-mkl` | `!` between-start range over 5% |
| `triangular_solve/n1024/b1` | 0.20937 ± 0.00711026 (W 0.00393939) | 0.225269 ± 0.0107011 (W 0.00320114) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-large, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 13.7603 ± 0.165603 (W 0.110532) | 14.086 ± 0.0549489 (W 0.123403) | 12.941 ± 0.00663007 (W 0.0314354) | · | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `eigh/n1024/b1` | 165.77 ± 0.464233 (W 0.4106) | 190.352 ± 1.7454 (W 1.71037) | 215.545 ± 0.731613 (W 0.439269) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `full_piv_lu/n1024/b1` | 81.4817 ± 0.289759 (W 0.246763) | 97.1601 ± 3.32548 (W 0.412925) | - | 🔵 faer-fork 1.19× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/n1024/b1` | 27.1715 ± 0.0922381 (W 0.129349) | 32.4918 ± 3.36598 (W 0.346068) | 23.652 ± 0.0364321 (W 0.111108) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔴 faer-fork 1.15× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 81.5069 ± 0.298181 (W 0.146338) | 121.563 ± 0.201308 (W 4.79638) | 104.691 ± 0.192044 (W 0.123346) | 🔵 faer-fork 1.49× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `qr_factor/n1024/b1` | 35.1011 ± 0.117233 (W 0.0213665) | 98.5171 ± 1.25831 (W 1.13019) | 42.4939 ± 0.065464 (W 0.0390198) | 🔵 faer-fork 2.81× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 27.2175 ± 0.187854 (W 0.154911) | 32.2597 ± 4.10815 (W 0.47649) | 23.0276 ± 0.0467974 (W 0.0186377) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n1024/b1` | 351.285 ± 1.45621 (W 1.09711) | 431.139 ± 3.51569 (W 2.20233) | 481.974 ± 1.98193 (W 1.57177) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.37× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 195.029 ± 2.61872 (W 0.460101) | 252.029 ± 5.01369 (W 0.652124) | 229.764 ± 0.682299 (W 0.36965) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `triangular_solve/n1024/b1` | 0.132647 ± 0.00195642 (W 0.000963898) | 0.147575 ± 0.00477399 (W 0.00101863) | - | 🔵 faer-fork 1.11× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-large, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 16.8349 ± 0.103025 (W 0.0187917) | 17.5104 ± 3.03716 (W 0.309026) | 19.6813 ± 0.209177 (W 0.0434968) | · | 🔵 faer-fork 1.17× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `eigh/n1024/b1` | 241.283 ± 0.565691 (W 0.482518) | 248.886 ± 1.02403 (W 0.499035) | 344.254 ± 0.472532 (W 0.583028) | · | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `full_piv_lu/n1024/b1` | 135.818 ± 0.317067 (W 0.30455) | 145.96 ± 5.33138 (W 0.698716) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `lu/n1024/b1` | 34.394 ± 0.0832343 (W 0.0334866) | 36.5968 ± 6.05212 (W 0.371345) | 37.5568 ± 0.0753716 (W 0.0567544) | · | 🔵 faer-fork 1.09× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 142.885 ± 0.133785 (W 0.312969) | 153.748 ± 7.48122 (W 0.203522) | 184.935 ± 1.33841 (W 0.167602) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n1024/b1` | 60.0584 ± 0.147974 (W 0.0451474) | 65.5885 ± 0.183938 (W 0.179856) | 70.8454 ± 0.022209 (W 0.0565981) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 34.5166 ± 0.187463 (W 0.0279305) | 37.2714 ± 6.95101 (W 0.347963) | 36.02 ± 1.19638 (W 0.0602263) | · | · | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n1024/b1` | 557.432 ± 1.27745 (W 1.11117) | 598.819 ± 2.59583 (W 1.16009) | 715.191 ± 3.44008 (W 2.38297) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 309.622 ± 0.860551 (W 0.788447) | 359.244 ± 6.17331 (W 0.715248) | 366.117 ± 1.54655 (W 0.868462) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `triangular_solve/n1024/b1` | 0.222384 ± 0.000826275 (W 0.00324871) | 0.239295 ± 0.000419696 (W 0.00352691) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-large, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n1024/b1` | 10.9311 ± 0.00791714 (W 0.0190257) | 11.1515 ± 0.0579052 (W 0.125005) | 11.4952 ± 0.215346 (W 0.0261409) | · | 🔵 faer-fork 1.05× faster than `lapack-mkl` |  |
| `eigh/n1024/b1` | 163.276 ± 0.511286 (W 0.303022) | 188.913 ± 2.21923 (W 1.52615) | 213.97 ± 0.0563901 (W 0.383722) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `full_piv_lu/n1024/b1` | 76.5014 ± 0.143488 (W 0.244414) | 88.2719 ± 0.10521 (W 0.372871) | - | 🔵 faer-fork 1.15× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 22.5768 ± 0.0183561 (W 0.0194263) | 24.5588 ± 3.35727 (W 0.136749) | 21.1821 ± 0.140044 (W 0.106354) | · | 🔴 faer-fork 1.07× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 76.6927 ± 0.142762 (W 0.0411795) | 115.14 ± 3.07693 (W 2.22661) | 108.5 ± 0.0721882 (W 0.0993662) | 🔵 faer-fork 1.50× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` | `!` between-start range over 5% |
| `qr_factor/n1024/b1` | 31.8362 ± 0.0531424 (W 0.030088) | 51.7852 ± 1.0888 (W 0.953646) | 40.1651 ± 0.0440835 (W 0.0671231) | 🔵 faer-fork 1.63× faster than `faer-upstream` | 🔵 faer-fork 1.26× faster than `lapack-mkl` |  |
| `solve/n1024/b1` | 22.3931 ± 0.0375784 (W 0.0271332) | 24.6338 ± 4.03942 (W 0.150557) | 20.6419 ± 1.00762 (W 0.0507485) | · | 🔴 faer-fork 1.08× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n1024/b1` | 345.275 ± 1.23103 (W 1.02708) | 423.497 ± 3.49814 (W 2.93494) | 462.53 ± 1.62617 (W 1.46004) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `svd_values/n1024/b1` | 186.2 ± 0.531378 (W 0.64756) | 238.793 ± 5.07042 (W 0.662092) | 228.352 ± 1.94027 (W 0.190675) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.23× faster than `lapack-mkl` |  |
| `triangular_solve/n1024/b1` | 0.150971 ± 0.00126234 (W 0.00103934) | 0.166491 ± 0.0040491 (W 0.0016433) | - | 🔵 faer-fork 1.10× faster than `faer-upstream` | - | `*` one row has no measurement here |

Not applicable to this population's shapes and reported as skipped: `full_piv_lu/1024`, `triangular_solve/1024`.

## gemm-large, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 17.6203 ± 0.0183003 (W 0.0167194) | 17.5613 ± 0.0022049 (W 0.0093706) | 20.6899 ± 0.131319 (W 0.0289049) | · | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |

## gemm-large, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 9.01659 ± 0.0186083 (W 0.00650892) | 9.01651 ± 0.00871416 (W 0.0127312) | 11.5619 ± 0.0279017 (W 0.0231923) | · | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |

## gemm-large, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 17.6141 ± 0.0239334 (W 0.0119523) | 17.5453 ± 0.0319053 (W 0.011403) | 20.6315 ± 0.0712674 (W 0.0316918) | · | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |

## gemm-large, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 9.01711 ± 0.00832242 (W 0.00630015) | 9.00943 ± 0.00816322 (W 0.0086703) | 11.4127 ± 0.135062 (W 0.0423255) | · | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |

## gemm-large, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 69.9923 ± 0.0551949 (W 0.0744065) | 70.0556 ± 0.114116 (W 0.033483) | 109.615 ± 1.24218 (W 0.0978162) | · | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |

## gemm-large, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 35.3114 ± 0.0165728 (W 0.0103219) | 35.2783 ± 0.0169926 (W 0.0139657) | 45.283 ± 0.0890472 (W 0.250263) | · | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |

## gemm-large, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 69.9139 ± 0.0801908 (W 0.0858559) | 70.025 ± 0.0650382 (W 0.038572) | 109.47 ± 0.539231 (W 0.149516) | · | 🔵 faer-fork 1.57× faster than `lapack-mkl` |  |

## gemm-large, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 35.2868 ± 0.0173556 (W 0.0202983) | 35.2844 ± 0.0127377 (W 0.0198736) | 45.3075 ± 1.08403 (W 0.108388) | · | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |

## linalg-boundary, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.228617 ± 0.00100296 (W 0.00221922) | 0.327768 ± 0.00262808 (W 0.00958171) | 0.309143 ± 0.00190547 (W 0.010024) | 🔵 faer-fork 1.43× faster than `faer-upstream` | 🔵 faer-fork 1.35× faster than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.209098 ± 0.0158137 (W 0.00154912) | 0.303896 ± 0.0145959 (W 0.00999382) | 0.335973 ± 0.00470499 (W 0.0137156) | 🔵 faer-fork 1.45× faster than `faer-upstream` | 🔵 faer-fork 1.61× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `cholesky/n511/b1` | 0.94552 ± 0.00180945 (W 0.004667) | 1.14694 ± 0.0382593 (W 0.0228021) | 1.50576 ± 0.000563746 (W 0.0109391) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.59× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n513/b1` | 0.881756 ± 0.0175555 (W 0.00360885) | 1.08459 ± 0.0192278 (W 0.0336045) | 1.56507 ± 0.0169578 (W 0.0121969) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.77× faster than `lapack-mkl` |  |
| `eigh/n255/b1` | 6.43702 ± 0.0328298 (W 0.00752364) | 6.90567 ± 0.0333294 (W 0.0147245) | 4.46362 ± 0.0161855 (W 0.0053924) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.44× slower than `lapack-mkl` |  |
| `eigh/n257/b1` | 6.43399 ± 0.0238319 (W 0.00862562) | 7.01429 ± 0.0584 (W 0.00940621) | 4.56129 ± 0.00890375 (W 0.00874799) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.41× slower than `lapack-mkl` |  |
| `eigh/n511/b1` | 23.9187 ± 0.158713 (W 0.0251408) | 25.1565 ± 0.0444632 (W 0.0373895) | 19.5301 ± 0.063471 (W 0.0245087) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔴 faer-fork 1.22× slower than `lapack-mkl` |  |
| `eigh/n513/b1` | 24.1288 ± 0.138918 (W 0.0430939) | 25.6336 ± 0.0224275 (W 0.0516364) | 19.8085 ± 0.0427104 (W 0.0177451) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.22× slower than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 1.99627 ± 0.0145394 (W 0.00480985) | 2.64716 ± 0.014203 (W 0.00939772) | - | 🔵 faer-fork 1.33× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.25252 ± 0.00669024 (W 0.00597306) | 1.90183 ± 0.014928 (W 0.00199252) | - | 🔵 faer-fork 1.52× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 11.7416 ± 0.712515 (W 0.0245705) | 14.4918 ± 0.045652 (W 0.0291048) | - | 🔵 faer-fork 1.23× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/n513/b1` | 7.15163 ± 0.0144613 (W 0.0136485) | 8.65661 ± 0.079493 (W 0.0113562) | - | 🔵 faer-fork 1.21× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.793818 ± 0.00457701 (W 0.00320265) | 0.638869 ± 0.00231676 (W 0.0131615) | 0.386951 ± 0.0025681 (W 0.00257531) | 🔴 faer-fork 1.24× slower than `faer-upstream` | 🔴 faer-fork 2.05× slower than `lapack-mkl` |  |
| `lu/n257/b1` | 0.787215 ± 0.00339284 (W 0.00364314) | 0.57389 ± 0.0132356 (W 0.00994999) | 0.556723 ± 0.007774 (W 0.00506739) | 🔴 faer-fork 1.37× slower than `faer-upstream` | 🔴 faer-fork 1.41× slower than `lapack-mkl` |  |
| `lu/n511/b1` | 4.23131 ± 0.00113004 (W 0.0137579) | 3.16089 ± 0.0535285 (W 0.0959617) | 2.45016 ± 0.0168492 (W 0.012518) | 🔴 faer-fork 1.34× slower than `faer-upstream` | 🔴 faer-fork 1.73× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 3.58104 ± 0.0310821 (W 0.0192914) | 2.47934 ± 0.023743 (W 0.0509758) | 2.5191 ± 0.0177655 (W 0.0123436) | 🔴 faer-fork 1.44× slower than `faer-upstream` | 🔴 faer-fork 1.42× slower than `lapack-mkl` |  |
| `qr/n255/b1` | 1.16675 ± 0.0123518 (W 0.00371065) | 1.81898 ± 0.00746124 (W 0.00616181) | 1.63162 ± 0.00227165 (W 0.00517665) | 🔵 faer-fork 1.56× faster than `faer-upstream` | 🔵 faer-fork 1.40× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 1.19075 ± 0.0111338 (W 0.00256611) | 1.8724 ± 0.0127319 (W 0.0040398) | 1.67867 ± 0.00333523 (W 0.00753469) | 🔵 faer-fork 1.57× faster than `faer-upstream` | 🔵 faer-fork 1.41× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 6.37261 ± 0.00657774 (W 0.0153608) | 7.67473 ± 0.894138 (W 0.0231285) | 8.49726 ± 0.0269426 (W 0.0251524) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔵 faer-fork 1.33× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n513/b1` | 8.18787 ± 0.980957 (W 0.0142853) | 7.59755 ± 0.984223 (W 0.0202647) | 8.54654 ± 0.0582852 (W 0.0208707) | · | · | `!` between-start range over 5% |
| `qr_factor/n255/b1` | 0.66082 ± 0.004814 (W 0.00310249) | 2.30957 ± 0.0159559 (W 0.0106025) | 0.687842 ± 0.00184502 (W 0.00259846) | 🔵 faer-fork 3.50× faster than `faer-upstream` | · |  |
| `qr_factor/n257/b1` | 0.707382 ± 0.00962379 (W 0.00308255) | 2.39438 ± 0.0169343 (W 0.0159755) | 0.701006 ± 0.0017286 (W 0.00167664) | 🔵 faer-fork 3.38× faster than `faer-upstream` | · |  |
| `qr_factor/n511/b1` | 3.22622 ± 0.00590212 (W 0.0180939) | 9.58778 ± 0.0548096 (W 0.0309843) | 3.83835 ± 0.010124 (W 0.00269924) | 🔵 faer-fork 2.97× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 3.24477 ± 0.00512808 (W 0.00562651) | 9.35817 ± 0.0715919 (W 0.0458806) | 3.92362 ± 0.0181298 (W 0.00653852) | 🔵 faer-fork 2.88× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `solve/n255/b1` | 0.566576 ± 0.00418668 (W 0.00278061) | 0.5826 ± 0.00228712 (W 0.00884897) | 0.378852 ± 0.00113935 (W 0.00360782) | · | 🔴 faer-fork 1.50× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 0.532583 ± 0.00171537 (W 0.00422156) | 0.55771 ± 0.00987296 (W 0.00753162) | 0.38795 ± 0.0013283 (W 0.00231641) | · | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |
| `solve/n511/b1` | 2.75861 ± 0.769347 (W 0.00629956) | 2.88787 ± 0.0309924 (W 0.0368115) | 1.76264 ± 0.0184526 (W 0.00425627) | · | 🔴 faer-fork 1.57× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 3.66722 ± 0.00161895 (W 0.00915537) | 2.37025 ± 0.0175703 (W 0.0285501) | 1.80493 ± 0.00214786 (W 0.00353959) | 🔴 faer-fork 1.55× slower than `faer-upstream` | 🔴 faer-fork 2.03× slower than `lapack-mkl` |  |
| `svd_thin/n255/b1` | 11.2703 ± 0.0258271 (W 0.0141636) | 13.5666 ± 0.061473 (W 0.0123738) | 9.98392 ± 0.0711712 (W 0.027747) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔴 faer-fork 1.13× slower than `lapack-mkl` |  |
| `svd_thin/n257/b1` | 8.96214 ± 0.00291469 (W 0.018947) | 10.0717 ± 0.059088 (W 0.0175802) | 10.239 ± 0.0478917 (W 0.0190761) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 44.6313 ± 0.149253 (W 0.0542563) | 54.5678 ± 0.118168 (W 0.0750593) | 41.2349 ± 2.41026 (W 0.0298098) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔴 faer-fork 1.08× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/n513/b1` | 41.0232 ± 0.0435233 (W 0.0480077) | 41.699 ± 0.0969903 (W 0.0492443) | 41.9423 ± 0.102306 (W 0.0429801) | · | · |  |
| `svd_values/n255/b1` | 5.32349 ± 0.00983723 (W 0.00704936) | 10.7443 ± 0.0266604 (W 0.0131301) | 5.25816 ± 0.00888963 (W 0.00652578) | 🔵 faer-fork 2.02× faster than `faer-upstream` | · |  |
| `svd_values/n257/b1` | 5.10223 ± 0.0178414 (W 0.0113338) | 8.22754 ± 0.00632848 (W 0.00782793) | 5.29903 ± 0.00817152 (W 0.00793276) | 🔵 faer-fork 1.61× faster than `faer-upstream` | · |  |
| `svd_values/n511/b1` | 24.7815 ± 0.0210135 (W 0.033029) | 40.9012 ± 0.0568065 (W 0.0430738) | 19.5108 ± 0.0468723 (W 0.0178709) | 🔵 faer-fork 1.65× faster than `faer-upstream` | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `svd_values/n513/b1` | 22.154 ± 0.111477 (W 0.0295528) | 29.7636 ± 0.0193424 (W 0.0380054) | 19.6722 ± 0.0781844 (W 0.0238429) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔴 faer-fork 1.13× slower than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.012393 ± 0.000141067 (W 7.27338e-05) | 0.011351 ± 1.52753e-05 (W 0.000111898) | - | 🔴 faer-fork 1.09× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.012634 ± 2.36714e-05 (W 8.09765e-05) | 0.011532 ± 0.0001006 (W 5.02623e-05) | - | 🔴 faer-fork 1.10× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.030196 ± 0.00120131 (W 9.9158e-05) | 0.040966 ± 0.0012162 (W 0.0026547) | - | 🔵 faer-fork 1.36× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.030126 ± 0.00126278 (W 0.0001461) | 0.029374 ± 0.00082163 (W 0.000274586) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.222715 ± 0.00110376 (W 0.00145894) | 0.308796 ± 0.00378222 (W 0.0239826) | 0.297794 ± 0.00661622 (W 0.00340756) | 🔵 faer-fork 1.39× faster than `faer-upstream` | 🔵 faer-fork 1.34× faster than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.202327 ± 0.0086809 (W 0.00175247) | 0.312022 ± 0.00308443 (W 0.0151167) | 0.294397 ± 0.00271442 (W 0.00335177) | 🔵 faer-fork 1.54× faster than `faer-upstream` | 🔵 faer-fork 1.46× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 0.809363 ± 0.00293951 (W 0.00285736) | 1.06176 ± 0.0196562 (W 0.0296539) | 1.06375 ± 0.0118025 (W 0.0107193) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `cholesky/n513/b1` | 0.73484 ± 0.0121315 (W 0.00419649) | 0.948788 ± 0.022285 (W 0.0296934) | 1.09559 ± 0.0207949 (W 0.0103874) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `eigh/n255/b1` | 6.12571 ± 0.0060654 (W 0.0130176) | 6.94662 ± 0.0297018 (W 0.0243486) | 3.82627 ± 0.0104177 (W 0.0050441) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.60× slower than `lapack-mkl` |  |
| `eigh/n257/b1` | 6.13235 ± 0.019977 (W 0.00922334) | 7.00298 ± 0.086623 (W 0.018554) | 3.91195 ± 0.00843321 (W 0.00971914) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.57× slower than `lapack-mkl` |  |
| `eigh/n511/b1` | 21.3013 ± 0.0349152 (W 0.0196644) | 23.6334 ± 0.0975443 (W 0.0469228) | 13.7214 ± 0.0218971 (W 0.0215484) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.55× slower than `lapack-mkl` |  |
| `eigh/n513/b1` | 21.7109 ± 0.0211279 (W 0.021847) | 24.0518 ± 0.0202434 (W 0.0715623) | 13.8509 ± 0.0520632 (W 0.046232) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.57× slower than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 1.96064 ± 0.0133146 (W 0.00511252) | 2.65581 ± 0.00278011 (W 0.0117358) | - | 🔵 faer-fork 1.35× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.22427 ± 0.0107951 (W 0.00509723) | 1.90732 ± 0.000795804 (W 0.00279037) | - | 🔵 faer-fork 1.56× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 10.499 ± 0.0306724 (W 0.0137574) | 13.5805 ± 0.102487 (W 0.0220744) | - | 🔵 faer-fork 1.29× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 5.92516 ± 0.0529205 (W 0.0133192) | 7.70472 ± 0.0145348 (W 0.0211543) | - | 🔵 faer-fork 1.30× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.777968 ± 0.00414404 (W 0.00395792) | 0.628319 ± 0.0260247 (W 0.022846) | 0.351505 ± 0.00284499 (W 0.00386424) | 🔴 faer-fork 1.24× slower than `faer-upstream` | 🔴 faer-fork 2.21× slower than `lapack-mkl` | `!` between-start range over 5% |
| `lu/n257/b1` | 0.771178 ± 0.00659839 (W 0.00347732) | 0.602492 ± 0.0240861 (W 0.0277701) | 0.534294 ± 0.00455144 (W 0.00693656) | 🔴 faer-fork 1.28× slower than `faer-upstream` | 🔴 faer-fork 1.44× slower than `lapack-mkl` | `!` between-start range over 5% |
| `lu/n511/b1` | 3.919 ± 0.00559374 (W 0.00774131) | 3.02638 ± 0.0405015 (W 0.0626988) | 1.95713 ± 0.0449959 (W 0.00694805) | 🔴 faer-fork 1.29× slower than `faer-upstream` | 🔴 faer-fork 2.00× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 3.2692 ± 0.00125901 (W 0.0110445) | 2.36493 ± 0.0319943 (W 0.0398556) | 2.0222 ± 0.0598653 (W 0.010198) | 🔴 faer-fork 1.38× slower than `faer-upstream` | 🔴 faer-fork 1.62× slower than `lapack-mkl` | `!` between-start range over 5% |
| `qr/n255/b1` | 1.0012 ± 0.00464361 (W 0.00201599) | 2.11905 ± 0.018307 (W 0.0119636) | 1.48846 ± 0.00583292 (W 0.00870177) | 🔵 faer-fork 2.12× faster than `faer-upstream` | 🔵 faer-fork 1.49× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 1.01673 ± 0.0105663 (W 0.00285916) | 2.1816 ± 0.00100556 (W 0.0100355) | 1.54545 ± 0.00884626 (W 0.00973092) | 🔵 faer-fork 2.15× faster than `faer-upstream` | 🔵 faer-fork 1.52× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 4.06807 ± 0.0377973 (W 0.012649) | 7.58628 ± 0.0474332 (W 0.0757959) | 5.61496 ± 0.0135585 (W 0.0216084) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.38× faster than `lapack-mkl` |  |
| `qr/n513/b1` | 4.43575 ± 0.0186335 (W 0.0148418) | 7.4763 ± 0.0303158 (W 0.084012) | 5.61704 ± 0.0708304 (W 0.019811) | 🔵 faer-fork 1.69× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |
| `qr_factor/n255/b1` | 0.622378 ± 0.00590809 (W 0.0030226) | 2.52707 ± 0.0150831 (W 0.0164014) | 0.588833 ± 0.00430274 (W 0.00398038) | 🔵 faer-fork 4.06× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `qr_factor/n257/b1` | 0.663827 ± 0.00272302 (W 0.0029538) | 2.62361 ± 0.0150838 (W 0.0204028) | 0.602902 ± 0.00196953 (W 0.00297789) | 🔵 faer-fork 3.95× faster than `faer-upstream` | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `qr_factor/n511/b1` | 1.9136 ± 0.00939821 (W 0.00452239) | 9.73595 ± 0.0347332 (W 0.0570546) | 2.32481 ± 0.0109933 (W 0.00582197) | 🔵 faer-fork 5.09× faster than `faer-upstream` | 🔵 faer-fork 1.21× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 2.28764 ± 0.00713661 (W 0.00709215) | 9.13041 ± 0.0380631 (W 0.0391645) | 2.38733 ± 0.00576138 (W 0.00633619) | 🔵 faer-fork 3.99× faster than `faer-upstream` | · |  |
| `solve/n255/b1` | 0.555946 ± 0.00152565 (W 0.00303304) | 0.559571 ± 0.00195637 (W 0.0202868) | 0.347766 ± 0.00277818 (W 0.00282022) | · | 🔴 faer-fork 1.60× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 0.520881 ± 0.00859229 (W 0.00260639) | 0.544584 ± 0.0244899 (W 0.026869) | 0.35463 ± 0.00147191 (W 0.00308029) | · | 🔴 faer-fork 1.47× slower than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n511/b1` | 2.51773 ± 0.7414 (W 0.00864135) | 2.70608 ± 0.0434205 (W 0.0590394) | 1.24579 ± 0.0204139 (W 0.00541813) | · | 🔴 faer-fork 2.02× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 3.3573 ± 0.769592 (W 0.00856167) | 2.27422 ± 0.0484672 (W 0.0540937) | 1.29493 ± 0.0168707 (W 0.0067317) | 🔴 faer-fork 1.48× slower than `faer-upstream` | 🔴 faer-fork 2.59× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n255/b1` | 10.8187 ± 0.0192868 (W 0.0124745) | 13.6554 ± 0.0427657 (W 0.0204864) | 9.14933 ± 0.0495512 (W 0.0293228) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` |  |
| `svd_thin/n257/b1` | 8.42327 ± 0.034574 (W 0.00826643) | 10.1575 ± 0.0416977 (W 0.0159352) | 9.40551 ± 0.0208572 (W 0.011802) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.12× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 39.1979 ± 0.018241 (W 0.047479) | 51.5051 ± 0.166778 (W 0.053379) | 33.2911 ± 2.29624 (W 0.0421828) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/n513/b1` | 35.2168 ± 0.0610287 (W 0.0394683) | 38.1817 ± 0.0128914 (W 0.381082) | 33.7791 ± 0.19347 (W 0.0570137) | 🔵 faer-fork 1.08× faster than `faer-upstream` | · |  |
| `svd_values/n255/b1` | 5.27169 ± 0.015594 (W 0.00998632) | 10.7565 ± 0.0351459 (W 0.0287933) | 5.11292 ± 0.0180003 (W 0.00799544) | 🔵 faer-fork 2.04× faster than `faer-upstream` | · |  |
| `svd_values/n257/b1` | 4.99987 ± 0.0117744 (W 0.00585358) | 8.25987 ± 0.00665663 (W 0.0078663) | 5.16706 ± 0.0108831 (W 0.0137208) | 🔵 faer-fork 1.65× faster than `faer-upstream` | · |  |
| `svd_values/n511/b1` | 22.821 ± 0.027218 (W 0.0325118) | 39.4382 ± 0.228824 (W 0.0436429) | 16.7439 ± 0.0422467 (W 0.0305507) | 🔵 faer-fork 1.73× faster than `faer-upstream` | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |
| `svd_values/n513/b1` | 20.1037 ± 0.017427 (W 0.016641) | 28.0487 ± 0.0629823 (W 0.0352346) | 16.8247 ± 0.0325144 (W 0.0369524) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔴 faer-fork 1.19× slower than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.012553 ± 0.000245941 (W 0.000106875) | 0.011381 ± 1.1547e-05 (W 8.7116e-05) | - | 🔴 faer-fork 1.10× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.012704 ± 8.16721e-05 (W 5.6181e-05) | 0.011571 ± 5.89661e-05 (W 3.99662e-05) | - | 🔴 faer-fork 1.10× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.028533 ± 0.000166103 (W 0.000189104) | 0.039824 ± 0.000323074 (W 0.0017986) | - | 🔵 faer-fork 1.40× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.029004 ± 0.000685061 (W 0.000203954) | 0.027831 ± 0.000917198 (W 0.0002992) | - | · | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.228406 ± 0.00114759 (W 0.00173871) | 0.323111 ± 0.00722602 (W 0.00853561) | 0.261627 ± 0.00270546 (W 0.0109023) | 🔵 faer-fork 1.41× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.211602 ± 0.0134562 (W 0.00188336) | 0.296783 ± 0.00225763 (W 0.00996981) | 0.272557 ± 0.0038518 (W 0.0112926) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `cholesky/n511/b1` | 0.93923 ± 0.00260894 (W 0.00402559) | 1.13189 ± 0.0174074 (W 0.0432096) | 1.3406 ± 0.00953735 (W 0.00572999) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `cholesky/n513/b1` | 0.868589 ± 0.0127413 (W 0.003651) | 1.06156 ± 0.0257254 (W 0.0329519) | 1.40107 ± 0.0114126 (W 0.00556156) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.61× faster than `lapack-mkl` |  |
| `eigh/n255/b1` | 6.41981 ± 0.0328106 (W 0.00646146) | 6.88105 ± 0.0189032 (W 0.00879215) | 4.40996 ± 0.00164248 (W 0.00981784) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.46× slower than `lapack-mkl` |  |
| `eigh/n257/b1` | 6.44464 ± 0.0160296 (W 0.00776713) | 6.97517 ± 0.0400847 (W 0.00667533) | 4.50274 ± 0.00283871 (W 0.00753433) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.43× slower than `lapack-mkl` |  |
| `eigh/n511/b1` | 23.72 ± 0.136795 (W 0.0374831) | 25.0631 ± 0.0340541 (W 0.0276454) | 19.1571 ± 0.0400467 (W 0.0156424) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.24× slower than `lapack-mkl` |  |
| `eigh/n513/b1` | 24.1283 ± 0.115428 (W 0.0215295) | 25.5355 ± 0.0320754 (W 0.0500984) | 19.4171 ± 0.028391 (W 0.014375) | 🔵 faer-fork 1.06× faster than `faer-upstream` | 🔴 faer-fork 1.24× slower than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 1.9329 ± 0.00599991 (W 0.00528356) | 2.62742 ± 0.00659839 (W 0.00782659) | - | 🔵 faer-fork 1.36× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.16681 ± 0.0115888 (W 0.00765738) | 1.8961 ± 0.00702187 (W 0.00661737) | - | 🔵 faer-fork 1.63× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 11.3107 ± 0.643138 (W 0.0159835) | 14.2922 ± 0.0133741 (W 0.0256076) | - | 🔵 faer-fork 1.26× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/n513/b1` | 6.64072 ± 0.0428118 (W 0.00794841) | 8.44362 ± 0.0232876 (W 0.0107988) | - | 🔵 faer-fork 1.27× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.705684 ± 0.119976 (W 0.00539546) | 0.623661 ± 0.00145242 (W 0.0131165) | 0.330346 ± 0.00178019 (W 0.00335007) | · | 🔴 faer-fork 2.14× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n257/b1` | 0.684145 ± 0.00469556 (W 0.00367575) | 0.568404 ± 0.00187283 (W 0.0100852) | 0.336033 ± 0.00459086 (W 0.00235962) | 🔴 faer-fork 1.20× slower than `faer-upstream` | 🔴 faer-fork 2.04× slower than `lapack-mkl` |  |
| `lu/n511/b1` | 3.71823 ± 0.0206853 (W 0.0119139) | 2.98667 ± 0.0682034 (W 0.10837) | 1.57759 ± 0.0048189 (W 0.00774633) | 🔴 faer-fork 1.24× slower than `faer-upstream` | 🔴 faer-fork 2.36× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 3.07537 ± 0.0126598 (W 0.00936913) | 2.3127 ± 0.00838293 (W 0.0320425) | 1.60959 ± 0.00803735 (W 0.00437895) | 🔴 faer-fork 1.33× slower than `faer-upstream` | 🔴 faer-fork 1.91× slower than `lapack-mkl` |  |
| `qr/n255/b1` | 1.05929 ± 0.0136708 (W 0.00201386) | 1.78307 ± 0.00127061 (W 0.00257966) | 1.52195 ± 0.00671506 (W 0.00257187) | 🔵 faer-fork 1.68× faster than `faer-upstream` | 🔵 faer-fork 1.44× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 1.0877 ± 0.00865735 (W 0.00385752) | 1.83422 ± 0.000659927 (W 0.00497417) | 1.555 ± 0.00374919 (W 0.00721975) | 🔵 faer-fork 1.69× faster than `faer-upstream` | 🔵 faer-fork 1.43× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 5.83281 ± 0.00989197 (W 0.0190464) | 7.34596 ± 0.919752 (W 0.0174187) | 7.94016 ± 0.013411 (W 0.0101957) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔵 faer-fork 1.36× faster than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n513/b1` | 7.59917 ± 0.952825 (W 0.0122765) | 7.32473 ± 0.940911 (W 0.00959563) | 8.03075 ± 0.0279982 (W 0.0128177) | · | · | `!` between-start range over 5% |
| `qr_factor/n255/b1` | 0.578447 ± 0.00924207 (W 0.00280039) | 1.30826 ± 0.00363845 (W 0.0060866) | 0.631541 ± 0.00204054 (W 0.00325475) | 🔵 faer-fork 2.26× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `qr_factor/n257/b1` | 0.593701 ± 0.00676351 (W 0.00281868) | 1.33917 ± 0.00693201 (W 0.00367306) | 0.643879 ± 0.00258055 (W 0.00178354) | 🔵 faer-fork 2.26× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `qr_factor/n511/b1` | 2.90681 ± 0.00415746 (W 0.00718355) | 4.3851 ± 0.0141757 (W 0.00775424) | 3.62528 ± 0.00413029 (W 0.00573686) | 🔵 faer-fork 1.51× faster than `faer-upstream` | 🔵 faer-fork 1.25× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 2.9065 ± 0.02028 (W 0.00693929) | 4.23526 ± 0.000632947 (W 0.00821712) | 3.69844 ± 0.0108768 (W 0.00543847) | 🔵 faer-fork 1.46× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |
| `solve/n255/b1` | 0.480064 ± 0.00135926 (W 0.00297999) | 0.571564 ± 0.00857991 (W 0.00653431) | 0.321529 ± 0.00338787 (W 0.00195686) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.49× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 0.447953 ± 0.00103606 (W 0.00301234) | 0.534531 ± 0.00978928 (W 0.00865375) | 0.326528 ± 0.00239918 (W 0.00362591) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |
| `solve/n511/b1` | 2.37085 ± 0.693767 (W 0.00666797) | 2.72254 ± 0.0322555 (W 0.0587554) | 1.56456 ± 0.0102588 (W 0.00525819) | · | 🔴 faer-fork 1.52× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 3.18765 ± 0.0126393 (W 0.0100941) | 2.26029 ± 0.0231162 (W 0.0181845) | 1.60396 ± 0.0162392 (W 0.00524582) | 🔴 faer-fork 1.41× slower than `faer-upstream` | 🔴 faer-fork 1.99× slower than `lapack-mkl` |  |
| `svd_thin/n255/b1` | 11.3336 ± 0.0507035 (W 0.0152804) | 13.6584 ± 0.0449536 (W 0.0281392) | 9.8271 ± 0.0314106 (W 0.0129211) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `svd_thin/n257/b1` | 8.93506 ± 0.00613753 (W 0.00910155) | 10.1112 ± 0.0384176 (W 0.0199792) | 10.0775 ± 0.0330317 (W 0.0145563) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔵 faer-fork 1.13× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 44.291 ± 0.109006 (W 0.0610204) | 54.4386 ± 0.0633336 (W 0.0622413) | 40.3989 ± 0.0814343 (W 0.0446251) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `svd_thin/n513/b1` | 40.8542 ± 0.0643963 (W 0.0323078) | 41.4625 ± 0.102541 (W 0.0426439) | 41.2704 ± 0.161147 (W 0.0420286) | · | · |  |
| `svd_values/n255/b1` | 5.2856 ± 0.0167864 (W 0.0113501) | 10.7955 ± 0.0217596 (W 0.0197869) | 5.18292 ± 0.0117162 (W 0.00748838) | 🔵 faer-fork 2.04× faster than `faer-upstream` | · |  |
| `svd_values/n257/b1` | 5.15725 ± 0.0177021 (W 0.0111313) | 8.20949 ± 0.00359865 (W 0.0132997) | 5.2669 ± 0.0122605 (W 0.0103798) | 🔵 faer-fork 1.59× faster than `faer-upstream` | · |  |
| `svd_values/n511/b1` | 24.6916 ± 0.0733078 (W 0.0255233) | 40.7853 ± 0.031433 (W 0.0339023) | 19.3777 ± 0.0742158 (W 0.0187512) | 🔵 faer-fork 1.65× faster than `faer-upstream` | 🔴 faer-fork 1.27× slower than `lapack-mkl` |  |
| `svd_values/n513/b1` | 22.0565 ± 0.0672234 (W 0.0249636) | 29.5246 ± 0.0175538 (W 0.0248621) | 19.4455 ± 0.0189685 (W 0.0232578) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔴 faer-fork 1.13× slower than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.014557 ± 0.000316871 (W 0.000264746) | 0.012112 ± 0.000142479 (W 7.91473e-05) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.014988 ± 7.2111e-05 (W 0.000236453) | 0.012403 ± 0.000176721 (W 5.12835e-05) | - | 🔴 faer-fork 1.21× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.039003 ± 0.000874356 (W 0.000524156) | 0.043862 ± 0.00188191 (W 0.000375695) | - | 🔵 faer-fork 1.12× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.038021 ± 0.00174706 (W 0.000370623) | 0.033753 ± 0.00161419 (W 0.000385214) | - | 🔴 faer-fork 1.13× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.221762 ± 0.000595416 (W 0.00260022) | 0.309895 ± 0.00187983 (W 0.0191279) | 0.255275 ± 0.00944054 (W 0.00410619) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n257/b1` | 0.198741 ± 0.007219 (W 0.00193682) | 0.280121 ± 0.00578158 (W 0.0262705) | 0.252921 ± 0.00384804 (W 0.00484292) | 🔵 faer-fork 1.41× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 0.800927 ± 0.00369988 (W 0.00375018) | 1.02175 ± 0.0158584 (W 0.0251204) | 0.924027 ± 0.00313466 (W 0.00816195) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `cholesky/n513/b1` | 0.732951 ± 0.0185836 (W 0.00323718) | 0.946628 ± 0.0212581 (W 0.0404967) | 0.965387 ± 0.00668827 (W 0.0110368) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `eigh/n255/b1` | 6.13321 ± 0.00424568 (W 0.00744133) | 6.95895 ± 0.0413737 (W 0.0237178) | 3.77572 ± 0.00654231 (W 0.009895) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.62× slower than `lapack-mkl` |  |
| `eigh/n257/b1` | 6.12354 ± 0.0812717 (W 0.0134965) | 6.94894 ± 0.0558795 (W 0.0203582) | 3.85831 ± 0.00292753 (W 0.010038) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.59× slower than `lapack-mkl` |  |
| `eigh/n511/b1` | 21.2173 ± 0.0168019 (W 0.0563748) | 23.5456 ± 0.00666874 (W 0.0723634) | 13.4508 ± 0.035182 (W 0.0284663) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.58× slower than `lapack-mkl` |  |
| `eigh/n513/b1` | 21.6169 ± 0.0375418 (W 0.0318999) | 23.8714 ± 0.0568076 (W 0.0770505) | 13.5658 ± 0.0717437 (W 0.0207281) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.59× slower than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 1.86261 ± 0.0154098 (W 0.00783659) | 2.64871 ± 0.00429725 (W 0.00736741) | - | 🔵 faer-fork 1.42× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.12637 ± 0.0113761 (W 0.00566388) | 1.89284 ± 0.00326366 (W 0.00701386) | - | 🔵 faer-fork 1.68× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 10.1232 ± 0.0141509 (W 0.0196451) | 13.3978 ± 0.112982 (W 0.0206839) | - | 🔵 faer-fork 1.32× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 5.44366 ± 0.0498745 (W 0.00967341) | 7.5235 ± 0.0199717 (W 0.015337) | - | 🔵 faer-fork 1.38× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.687296 ± 0.115122 (W 0.00398555) | 0.624814 ± 0.00534035 (W 0.0276846) | 0.311601 ± 0.00296686 (W 0.0034083) | · | 🔴 faer-fork 2.21× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n257/b1` | 0.667233 ± 0.00294199 (W 0.00417483) | 0.555273 ± 0.0311947 (W 0.0211927) | 0.317311 ± 0.0024401 (W 0.00201151) | 🔴 faer-fork 1.20× slower than `faer-upstream` | 🔴 faer-fork 2.10× slower than `lapack-mkl` | `!` between-start range over 5% |
| `lu/n511/b1` | 3.44545 ± 0.0122817 (W 0.00957896) | 2.86102 ± 0.00779667 (W 0.0312887) | 1.16308 ± 0.00448947 (W 0.00183302) | 🔴 faer-fork 1.20× slower than `faer-upstream` | 🔴 faer-fork 2.96× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 2.79156 ± 0.00127934 (W 0.00770218) | 2.21925 ± 0.180909 (W 0.0594268) | 1.21522 ± 0.0134067 (W 0.00621425) | 🔴 faer-fork 1.26× slower than `faer-upstream` | 🔴 faer-fork 2.30× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n255/b1` | 0.890985 ± 0.00533453 (W 0.00167203) | 2.08837 ± 0.00279949 (W 0.0104404) | 1.41077 ± 0.0039336 (W 0.0074095) | 🔵 faer-fork 2.34× faster than `faer-upstream` | 🔵 faer-fork 1.58× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 0.911717 ± 0.010455 (W 0.00270023) | 2.15516 ± 0.0225694 (W 0.0103298) | 1.47436 ± 0.00623187 (W 0.00496984) | 🔵 faer-fork 2.36× faster than `faer-upstream` | 🔵 faer-fork 1.62× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 3.55373 ± 0.0157923 (W 0.0107487) | 7.37535 ± 0.047681 (W 0.0489217) | 5.34141 ± 0.00534413 (W 0.00751236) | 🔵 faer-fork 2.08× faster than `faer-upstream` | 🔵 faer-fork 1.50× faster than `lapack-mkl` |  |
| `qr/n513/b1` | 3.88986 ± 0.0101368 (W 0.00889869) | 7.22948 ± 0.0314355 (W 0.0593998) | 5.42211 ± 0.0124722 (W 0.0187583) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.39× faster than `lapack-mkl` |  |
| `qr_factor/n255/b1` | 0.570049 ± 0.00376164 (W 0.00190576) | 1.55777 ± 0.0203403 (W 0.00856429) | 0.551404 ± 0.00244385 (W 0.00483532) | 🔵 faer-fork 2.73× faster than `faer-upstream` | · |  |
| `qr_factor/n257/b1` | 0.582962 ± 0.00283496 (W 0.00198774) | 1.60162 ± 0.0032009 (W 0.00911894) | 0.5631 ± 0.0032143 (W 0.00173941) | 🔵 faer-fork 2.75× faster than `faer-upstream` | · |  |
| `qr_factor/n511/b1` | 1.73737 ± 0.00258535 (W 0.00357638) | 4.69483 ± 0.0234916 (W 0.0256968) | 2.20256 ± 0.00748955 (W 0.0038198) | 🔵 faer-fork 2.70× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 2.06758 ± 0.0133164 (W 0.00377275) | 4.45219 ± 0.0459573 (W 0.027374) | 2.25144 ± 0.00518906 (W 0.00468564) | 🔵 faer-fork 2.15× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `solve/n255/b1` | 0.471147 ± 0.00409308 (W 0.00275376) | 0.566584 ± 0.00942758 (W 0.0244166) | 0.304247 ± 0.000692501 (W 0.00142019) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔴 faer-fork 1.55× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 0.434678 ± 0.00219804 (W 0.00214765) | 0.547166 ± 0.025508 (W 0.0315179) | 0.314866 ± 0.00110869 (W 0.00254004) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔴 faer-fork 1.38× slower than `lapack-mkl` | `!` between-start range over 5% |
| `solve/n511/b1` | 2.13018 ± 0.672207 (W 0.00948242) | 2.51615 ± 0.0362547 (W 0.0627241) | 1.13173 ± 0.0173882 (W 0.00601157) | · | 🔴 faer-fork 1.88× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 2.89217 ± 0.708915 (W 0.00614677) | 2.10627 ± 0.0329658 (W 0.0428685) | 1.19612 ± 0.000930268 (W 0.00716682) | 🔴 faer-fork 1.37× slower than `faer-upstream` | 🔴 faer-fork 2.42× slower than `lapack-mkl` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n255/b1` | 10.8783 ± 0.0181696 (W 0.0206046) | 13.6884 ± 0.024368 (W 0.0169814) | 9.02728 ± 0.0210445 (W 0.00962227) | 🔵 faer-fork 1.26× faster than `faer-upstream` | 🔴 faer-fork 1.21× slower than `lapack-mkl` |  |
| `svd_thin/n257/b1` | 8.41085 ± 0.0318411 (W 0.0187864) | 10.1633 ± 0.010827 (W 0.0190395) | 9.29095 ± 0.00636746 (W 0.0117952) | 🔵 faer-fork 1.21× faster than `faer-upstream` | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 39.0213 ± 0.0713132 (W 0.0239044) | 51.2642 ± 0.276002 (W 0.0906466) | 32.7374 ± 0.0296389 (W 0.0305354) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔴 faer-fork 1.19× slower than `lapack-mkl` |  |
| `svd_thin/n513/b1` | 35.0655 ± 0.0547905 (W 0.0372046) | 37.9978 ± 0.0746366 (W 0.0774924) | 33.5888 ± 0.0634743 (W 0.0360893) | 🔵 faer-fork 1.08× faster than `faer-upstream` | · |  |
| `svd_values/n255/b1` | 5.2248 ± 0.00329566 (W 0.010929) | 10.8156 ± 0.0248297 (W 0.0198321) | 5.06793 ± 0.00820394 (W 0.00559708) | 🔵 faer-fork 2.07× faster than `faer-upstream` | · |  |
| `svd_values/n257/b1` | 5.04086 ± 0.00800335 (W 0.0080719) | 8.18323 ± 0.0719947 (W 0.0170527) | 5.16754 ± 0.0132889 (W 0.00560339) | 🔵 faer-fork 1.62× faster than `faer-upstream` | · |  |
| `svd_values/n511/b1` | 22.7271 ± 0.0587899 (W 0.0206289) | 39.2015 ± 0.200785 (W 0.0490528) | 16.6419 ± 0.0607014 (W 0.0221274) | 🔵 faer-fork 1.72× faster than `faer-upstream` | 🔴 faer-fork 1.37× slower than `lapack-mkl` |  |
| `svd_values/n513/b1` | 19.94 ± 0.0359914 (W 0.0278733) | 27.8342 ± 0.0140724 (W 0.0356758) | 16.6559 ± 0.0571452 (W 0.0306573) | 🔵 faer-fork 1.40× faster than `faer-upstream` | 🔴 faer-fork 1.20× slower than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.014847 ± 0.000127189 (W 0.000188829) | 0.012393 ± 8.99463e-05 (W 4.86744e-05) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.014928 ± 0.00021997 (W 0.000264236) | 0.012413 ± 8.02081e-05 (W 3.28634e-05) | - | 🔴 faer-fork 1.20× slower than `faer-upstream` | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.036428 ± 0.000648324 (W 0.000515403) | 0.042599 ± 0.000200575 (W 0.00026084) | - | 🔵 faer-fork 1.17× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.03739 ± 0.000777214 (W 0.00150488) | 0.03228 ± 0.00205711 (W 0.000247357) | - | 🔴 faer-fork 1.16× slower than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.661427 ± 0.00578121 (W 0.00264684) | 0.728215 ± 0.0025186 (W 0.00616253) | 0.568575 ± 0.00843775 (W 0.00541179) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔴 faer-fork 1.16× slower than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.637236 ± 0.00962442 (W 0.00303443) | 0.683252 ± 0.0172967 (W 0.0137592) | 0.575853 ± 0.0125442 (W 0.00749268) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `cholesky/n511/b1` | 2.88022 ± 0.0140857 (W 0.00932217) | 3.14229 ± 0.0935616 (W 0.14704) | 2.94645 ± 0.0147724 (W 0.0118455) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · | `!` between-start range over 5% |
| `cholesky/n513/b1` | 2.81523 ± 0.00435524 (W 0.00947685) | 2.9477 ± 0.0316334 (W 0.0688943) | 3.02476 ± 0.00330688 (W 0.00579073) | · | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |
| `eigh/n255/b1` | 8.70252 ± 0.0167337 (W 0.0165864) | 11.3427 ± 0.0367154 (W 0.0131861) | 9.5712 ± 0.0256593 (W 0.0159432) | 🔵 faer-fork 1.30× faster than `faer-upstream` | 🔵 faer-fork 1.10× faster than `lapack-mkl` |  |
| `eigh/n257/b1` | 8.67767 ± 0.0106243 (W 0.0092761) | 11.3835 ± 0.0193039 (W 0.0160251) | 9.69809 ± 0.00166509 (W 0.00884558) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔵 faer-fork 1.12× faster than `lapack-mkl` |  |
| `eigh/n511/b1` | 39.2998 ± 0.0921565 (W 0.0293443) | 44.9082 ± 0.0627463 (W 0.037503) | 50.505 ± 0.0700766 (W 0.031327) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔵 faer-fork 1.29× faster than `lapack-mkl` |  |
| `eigh/n513/b1` | 39.8176 ± 0.508452 (W 0.438181) | 45.7127 ± 0.163479 (W 0.0286976) | 50.9259 ± 0.0843856 (W 0.0437528) | 🔵 faer-fork 1.15× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 3.45136 ± 0.0419548 (W 0.00970994) | 5.77102 ± 0.0211394 (W 0.00796743) | - | 🔵 faer-fork 1.67× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 2.0799 ± 0.0177371 (W 0.00364364) | 4.40838 ± 0.025848 (W 0.00990378) | - | 🔵 faer-fork 2.12× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 17.3602 ± 0.0254508 (W 0.0133576) | 25.0021 ± 0.0841948 (W 0.0206227) | - | 🔵 faer-fork 1.44× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 11.624 ± 0.0280073 (W 0.0240985) | 19.1231 ± 0.101449 (W 0.0661516) | - | 🔵 faer-fork 1.65× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.28726 ± 0.00692476 (W 0.0046384) | 1.34356 ± 0.00457207 (W 0.0212075) | 0.934023 ± 0.00149778 (W 0.00392243) | · | 🔴 faer-fork 1.38× slower than `lapack-mkl` |  |
| `lu/n257/b1` | 1.19251 ± 0.00216566 (W 0.00337742) | 1.22778 ± 0.0136983 (W 0.0203269) | 0.98605 ± 0.00332131 (W 0.00187159) | · | 🔴 faer-fork 1.21× slower than `lapack-mkl` |  |
| `lu/n511/b1` | 6.45044 ± 0.0316389 (W 0.0198465) | 6.6157 ± 0.0591427 (W 0.102024) | 5.51231 ± 0.0116452 (W 0.00964841) | · | 🔴 faer-fork 1.17× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 6.26045 ± 0.0210013 (W 0.0184776) | 6.45876 ± 0.0321637 (W 0.0955547) | 5.63499 ± 0.00773131 (W 0.00959139) | · | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `qr/n255/b1` | 3.25385 ± 0.00494778 (W 0.00468162) | 4.18933 ± 0.0128404 (W 0.0107341) | 3.85885 ± 0.0105374 (W 0.00521581) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 3.33086 ± 0.000738719 (W 0.00221202) | 4.26166 ± 0.0275306 (W 0.0169657) | 3.96145 ± 0.0207605 (W 0.00903858) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 20.675 ± 0.052807 (W 0.0328671) | 22.053 ± 0.0432212 (W 0.0233286) | 24.7392 ± 0.0100263 (W 0.0175732) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `qr/n513/b1` | 21.0578 ± 0.0493336 (W 0.0265666) | 22.5686 ± 0.0723066 (W 0.0151815) | 24.887 ± 0.0826002 (W 0.0367218) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `qr_factor/n255/b1` | 1.6178 ± 0.0028622 (W 0.00366305) | 3.4338 ± 0.0128702 (W 0.00996569) | 1.64206 ± 0.00122479 (W 0.00601513) | 🔵 faer-fork 2.12× faster than `faer-upstream` | · |  |
| `qr_factor/n257/b1` | 1.68722 ± 0.00161922 (W 0.00204473) | 3.53449 ± 0.0166204 (W 0.0103335) | 1.70354 ± 0.00685665 (W 0.00431672) | 🔵 faer-fork 2.09× faster than `faer-upstream` | · |  |
| `qr_factor/n511/b1` | 9.43141 ± 0.013683 (W 0.0123337) | 15.6771 ± 0.0596605 (W 0.0368587) | 11.2077 ± 0.027204 (W 0.025008) | 🔵 faer-fork 1.66× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 9.62993 ± 0.0102134 (W 0.0124077) | 16.8005 ± 0.09079 (W 0.0382174) | 11.385 ± 0.00439467 (W 0.0137479) | 🔵 faer-fork 1.74× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `solve/n255/b1` | 1.23173 ± 0.00825172 (W 0.00465199) | 1.22081 ± 0.00737044 (W 0.010096) | 0.903301 ± 0.00170069 (W 0.00188564) | · | 🔴 faer-fork 1.36× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 1.209 ± 0.00427172 (W 0.00593976) | 1.23402 ± 0.00770458 (W 0.0251582) | 0.945413 ± 0.000932747 (W 0.00258201) | · | 🔴 faer-fork 1.28× slower than `lapack-mkl` |  |
| `solve/n511/b1` | 6.3618 ± 0.0235936 (W 0.0123828) | 6.58691 ± 0.0699342 (W 0.0746757) | 5.53851 ± 0.0621799 (W 0.0156175) | · | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `solve/n513/b1` | 6.38623 ± 0.0346736 (W 0.0142992) | 6.55637 ± 0.0594335 (W 0.0850915) | 5.63574 ± 0.0562049 (W 0.00592192) | · | 🔴 faer-fork 1.13× slower than `lapack-mkl` |  |
| `svd_thin/n255/b1` | 16.4661 ± 0.0364208 (W 0.035376) | 22.2712 ± 0.0873378 (W 0.0221869) | 16.1298 ± 0.0618406 (W 0.0246471) | 🔵 faer-fork 1.35× faster than `faer-upstream` | · |  |
| `svd_thin/n257/b1` | 13.9054 ± 0.0316806 (W 0.0193679) | 17.7902 ± 0.0110332 (W 0.0264028) | 16.3976 ± 0.0248274 (W 0.00674813) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 77.2309 ± 0.217786 (W 0.0993218) | 87.5611 ± 0.0737407 (W 0.0855076) | 84.5443 ± 5.22221 (W 0.0862059) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` | `!` between-start range over 5% |
| `svd_thin/n513/b1` | 74.267 ± 0.174591 (W 0.0611361) | 76.6255 ± 0.149286 (W 0.0455829) | 85.4404 ± 0.197208 (W 0.0930885) | · | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `svd_values/n255/b1` | 7.82259 ± 0.0177474 (W 0.0165862) | 17.1448 ± 0.0964494 (W 0.029518) | 7.69335 ± 0.253232 (W 0.00929474) | 🔵 faer-fork 2.19× faster than `faer-upstream` | · | `!` between-start range over 5% |
| `svd_values/n257/b1` | 7.50668 ± 0.0537533 (W 0.0212715) | 13.4085 ± 0.168049 (W 0.0144397) | 7.84646 ± 0.00830586 (W 0.00716157) | 🔵 faer-fork 1.79× faster than `faer-upstream` | · |  |
| `svd_values/n511/b1` | 41.1023 ± 0.174168 (W 0.0743441) | 58.0239 ± 0.0200704 (W 0.0535691) | 40.8059 ± 0.0537298 (W 0.0434149) | 🔵 faer-fork 1.41× faster than `faer-upstream` | · |  |
| `svd_values/n513/b1` | 39.1424 ± 0.0544435 (W 0.0483777) | 48.4806 ± 0.0466881 (W 0.038292) | 41.2236 ± 0.0748369 (W 0.0299195) | 🔵 faer-fork 1.24× faster than `faer-upstream` | 🔵 faer-fork 1.05× faster than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.021881 ± 0.000141846 (W 0.000119038) | 0.023364 ± 0.000312058 (W 7.18136e-05) | - | 🔵 faer-fork 1.07× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.022141 ± 8.24035e-05 (W 0.00010414) | 0.023945 ± 7.13933e-05 (W 0.00154008) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n511/b1` | 0.055323 ± 0.00147549 (W 0.000352708) | 0.08596 ± 0.00133351 (W 0.0016617) | - | 🔵 faer-fork 1.55× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.055803 ± 0.000546932 (W 0.000239329) | 0.061344 ± 0.000611737 (W 0.000230279) | - | 🔵 faer-fork 1.10× faster than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-boundary, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.598215 ± 0.00316239 (W 0.00387701) | 0.711657 ± 0.000303185 (W 0.0161158) | 0.404392 ± 0.000978135 (W 0.00466405) | 🔵 faer-fork 1.19× faster than `faer-upstream` | 🔴 faer-fork 1.48× slower than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.573138 ± 0.0127026 (W 0.00319085) | 0.655528 ± 0.0178596 (W 0.0168764) | 0.423819 ± 0.00728697 (W 0.0107611) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.35× slower than `lapack-mkl` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 2.29403 ± 0.00613758 (W 0.00810667) | 2.47817 ± 0.00352942 (W 0.0654881) | 1.77753 ± 0.0279842 (W 0.0152856) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.29× slower than `lapack-mkl` |  |
| `cholesky/n513/b1` | 2.19269 ± 0.0198488 (W 0.00978261) | 2.34435 ± 0.00238501 (W 0.0172785) | 1.82682 ± 0.0306069 (W 0.00858425) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.20× slower than `lapack-mkl` |  |
| `eigh/n255/b1` | 7.72942 ± 0.0412204 (W 0.00667629) | 11.1931 ± 0.0412703 (W 0.0266554) | 7.61583 ± 0.0328271 (W 0.0167887) | 🔵 faer-fork 1.45× faster than `faer-upstream` | · |  |
| `eigh/n257/b1` | 7.70649 ± 0.0195254 (W 0.0088527) | 11.151 ± 0.0244666 (W 0.0355762) | 7.74016 ± 0.0114463 (W 0.0128765) | 🔵 faer-fork 1.45× faster than `faer-upstream` | · |  |
| `eigh/n511/b1` | 30.3954 ± 0.0270453 (W 0.0363133) | 39.1153 ± 0.150798 (W 0.166116) | 35.3234 ± 0.0244727 (W 0.06326) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.16× faster than `lapack-mkl` |  |
| `eigh/n513/b1` | 30.7407 ± 0.0664782 (W 0.0261228) | 39.2941 ± 0.101236 (W 0.286021) | 35.3692 ± 0.0534913 (W 0.0492756) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 3.13395 ± 0.0123923 (W 0.00912844) | 5.7476 ± 0.0215189 (W 0.0154516) | - | 🔵 faer-fork 1.83× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.74135 ± 0.0149494 (W 0.0034058) | 4.36596 ± 0.0680233 (W 0.00729278) | - | 🔵 faer-fork 2.51× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 13.9928 ± 0.0767916 (W 0.0348643) | 22.571 ± 0.0763358 (W 0.056737) | - | 🔵 faer-fork 1.61× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 8.09187 ± 0.0883035 (W 0.0344102) | 16.7836 ± 0.0325392 (W 0.0267849) | - | 🔵 faer-fork 2.07× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.18414 ± 0.00476054 (W 0.00157686) | 1.24805 ± 0.00348249 (W 0.0164851) | 0.685115 ± 0.00258361 (W 0.00373517) | 🔵 faer-fork 1.05× faster than `faer-upstream` | 🔴 faer-fork 1.73× slower than `lapack-mkl` |  |
| `lu/n257/b1` | 1.06433 ± 0.00354077 (W 0.002485) | 1.09945 ± 0.00601007 (W 0.011932) | 0.705994 ± 0.00229024 (W 0.00297588) | · | 🔴 faer-fork 1.51× slower than `lapack-mkl` |  |
| `lu/n511/b1` | 5.10853 ± 0.0230047 (W 0.015975) | 5.22183 ± 0.0296067 (W 0.0240144) | 3.26057 ± 0.0101172 (W 0.00772199) | · | 🔴 faer-fork 1.57× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 4.88143 ± 0.0198662 (W 0.0098513) | 4.96087 ± 0.024269 (W 0.05283) | 3.32391 ± 0.0090098 (W 0.0124298) | · | 🔴 faer-fork 1.47× slower than `lapack-mkl` |  |
| `qr/n255/b1` | 2.3128 ± 0.00536105 (W 0.00322312) | 4.15709 ± 0.01301 (W 0.0194788) | 3.01768 ± 0.0028649 (W 0.00420545) | 🔵 faer-fork 1.80× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 2.35671 ± 0.00287982 (W 0.00687391) | 4.22848 ± 0.0145236 (W 0.032121) | 3.07448 ± 0.00314796 (W 0.00886863) | 🔵 faer-fork 1.79× faster than `faer-upstream` | 🔵 faer-fork 1.30× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 11.6149 ± 0.0635508 (W 0.014239) | 18.3441 ± 0.266609 (W 0.277217) | 12.8734 ± 0.0297831 (W 0.017115) | 🔵 faer-fork 1.58× faster than `faer-upstream` | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `qr/n513/b1` | 12.3232 ± 0.0376405 (W 0.0391494) | 18.5523 ± 0.230685 (W 0.299104) | 12.8645 ± 0.0232779 (W 0.0226926) | 🔵 faer-fork 1.51× faster than `faer-upstream` | · |  |
| `qr_factor/n255/b1` | 1.29678 ± 0.00196256 (W 0.00750712) | 3.5467 ± 0.0198146 (W 0.0269996) | 1.66268 ± 0.00396381 (W 0.0041386) | 🔵 faer-fork 2.73× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `qr_factor/n257/b1` | 1.34792 ± 0.00812975 (W 0.00419746) | 3.64492 ± 0.00906711 (W 0.0139355) | 1.7247 ± 0.00670079 (W 0.00539674) | 🔵 faer-fork 2.70× faster than `faer-upstream` | 🔵 faer-fork 1.28× faster than `lapack-mkl` |  |
| `qr_factor/n511/b1` | 5.03263 ± 0.0199482 (W 0.00716467) | 14.1891 ± 0.0553882 (W 0.102364) | 5.79115 ± 0.0145195 (W 0.00880623) | 🔵 faer-fork 2.82× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 5.68675 ± 0.0229633 (W 0.0101495) | 14.4555 ± 0.145829 (W 0.159325) | 5.95519 ± 0.00751235 (W 0.00840338) | 🔵 faer-fork 2.54× faster than `faer-upstream` | · |  |
| `solve/n255/b1` | 1.1168 ± 0.00318366 (W 0.00277837) | 1.13157 ± 0.00172059 (W 0.0135838) | 0.685624 ± 0.00405944 (W 0.0023074) | · | 🔴 faer-fork 1.63× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 1.07673 ± 0.00392488 (W 0.00192152) | 1.1024 ± 0.00671127 (W 0.0178157) | 0.701105 ± 0.00329957 (W 0.00249872) | · | 🔴 faer-fork 1.54× slower than `lapack-mkl` |  |
| `solve/n511/b1` | 4.98762 ± 0.0455304 (W 0.0306356) | 5.20084 ± 0.0855589 (W 0.0363338) | 3.31464 ± 0.00249222 (W 0.0118483) | · | 🔴 faer-fork 1.50× slower than `lapack-mkl` |  |
| `solve/n513/b1` | 5.00484 ± 0.0647965 (W 0.0146726) | 4.9945 ± 0.0107901 (W 0.0385401) | 3.38919 ± 0.0061786 (W 0.00676509) | · | 🔴 faer-fork 1.48× slower than `lapack-mkl` |  |
| `svd_thin/n255/b1` | 14.5024 ± 0.0168492 (W 0.0195885) | 22.1642 ± 0.0157371 (W 0.057441) | 12.2593 ± 0.0298245 (W 0.0259305) | 🔵 faer-fork 1.53× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` |  |
| `svd_thin/n257/b1` | 11.8288 ± 0.010425 (W 0.0110886) | 17.6682 ± 0.285032 (W 0.0434364) | 12.5397 ± 0.0356266 (W 0.0213553) | 🔵 faer-fork 1.49× faster than `faer-upstream` | 🔵 faer-fork 1.06× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 58.1366 ± 0.0863634 (W 0.118114) | 74.7406 ± 0.311437 (W 0.299701) | 56.4109 ± 0.0432443 (W 0.297818) | 🔵 faer-fork 1.29× faster than `faer-upstream` | · |  |
| `svd_thin/n513/b1` | 54.9396 ± 0.0411243 (W 0.0685634) | 62.8315 ± 0.0363647 (W 0.254759) | 57.0328 ± 0.0574365 (W 0.0420092) | 🔵 faer-fork 1.14× faster than `faer-upstream` | · |  |
| `svd_values/n255/b1` | 7.34499 ± 0.0115397 (W 0.0150479) | 16.8541 ± 0.270004 (W 0.0163193) | 6.25897 ± 0.0323288 (W 0.0202648) | 🔵 faer-fork 2.29× faster than `faer-upstream` | 🔴 faer-fork 1.17× slower than `lapack-mkl` |  |
| `svd_values/n257/b1` | 6.97464 ± 0.00292433 (W 0.0137616) | 13.2324 ± 0.346573 (W 0.0222898) | 6.40701 ± 0.0144899 (W 0.00684609) | 🔵 faer-fork 1.90× faster than `faer-upstream` | 🔴 faer-fork 1.09× slower than `lapack-mkl` |  |
| `svd_values/n511/b1` | 33.166 ± 0.184377 (W 0.0454036) | 51.2965 ± 0.119814 (W 0.0548528) | 28.0441 ± 0.0520763 (W 0.0299982) | 🔵 faer-fork 1.55× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` |  |
| `svd_values/n513/b1` | 31.151 ± 0.117333 (W 0.0368625) | 41.7828 ± 0.0316953 (W 0.0800363) | 28.2357 ± 0.121459 (W 0.0587101) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.0217 ± 0.000100167 (W 8.43107e-05) | 0.023423 ± 9.02238e-05 (W 8.29458e-05) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.02192 ± 7.08543e-05 (W 9.02951e-05) | 0.023774 ± 0.000790211 (W 0.00178761) | - | 🔵 faer-fork 1.08× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n511/b1` | 0.050073 ± 0.00102602 (W 0.000184703) | 0.085829 ± 0.00100262 (W 0.00107626) | - | 🔵 faer-fork 1.71× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.050665 ± 0.000481333 (W 0.000316059) | 0.057808 ± 0.000403894 (W 0.000327934) | - | 🔵 faer-fork 1.14× faster than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-boundary, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.655973 ± 0.00252498 (W 0.00389028) | 0.727931 ± 0.00478023 (W 0.00703918) | 0.52615 ± 0.00264714 (W 0.00415945) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.25× slower than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.636286 ± 0.0125036 (W 0.00249743) | 0.690767 ± 0.00581933 (W 0.0108338) | 0.539535 ± 0.00859597 (W 0.00869019) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` |  |
| `cholesky/n511/b1` | 2.81371 ± 0.00307687 (W 0.00654408) | 3.0631 ± 0.0878509 (W 0.110647) | 2.8178 ± 0.00046352 (W 0.00532554) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · | `!` between-start range over 5% |
| `cholesky/n513/b1` | 2.75252 ± 0.0112892 (W 0.00732662) | 2.97744 ± 0.108509 (W 0.122035) | 2.90137 ± 0.00248125 (W 0.0096608) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔵 faer-fork 1.05× faster than `lapack-mkl` | `!` between-start range over 5% |
| `eigh/n255/b1` | 8.69105 ± 0.0166318 (W 0.0132915) | 11.3402 ± 0.0365806 (W 0.0103593) | 9.48541 ± 0.00810779 (W 0.00844511) | 🔵 faer-fork 1.30× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `eigh/n257/b1` | 8.67446 ± 0.0373275 (W 0.0131382) | 11.329 ± 0.0423761 (W 0.00769604) | 9.61785 ± 0.00548739 (W 0.00932556) | 🔵 faer-fork 1.31× faster than `faer-upstream` | 🔵 faer-fork 1.11× faster than `lapack-mkl` |  |
| `eigh/n511/b1` | 39.3297 ± 0.0219428 (W 0.0282781) | 44.8199 ± 0.107674 (W 0.0365565) | 50.1303 ± 0.0314411 (W 0.0314827) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |
| `eigh/n513/b1` | 39.7808 ± 0.0286206 (W 0.0397011) | 45.4473 ± 0.0866722 (W 0.0599748) | 50.5597 ± 0.0830338 (W 0.0497166) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔵 faer-fork 1.27× faster than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 3.31707 ± 0.0435821 (W 0.0142978) | 5.75898 ± 0.0299358 (W 0.00806274) | - | 🔵 faer-fork 1.74× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.94585 ± 0.012147 (W 0.00465608) | 4.3872 ± 0.0365915 (W 0.00431562) | - | 🔵 faer-fork 2.25× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 16.8045 ± 0.0515752 (W 0.0259145) | 24.7509 ± 0.091686 (W 0.0294496) | - | 🔵 faer-fork 1.47× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 10.9557 ± 0.0298914 (W 0.016982) | 18.9465 ± 0.0837348 (W 0.0141704) | - | 🔵 faer-fork 1.73× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.18403 ± 0.00921221 (W 0.00280575) | 1.32959 ± 0.0139157 (W 0.0122479) | 0.886682 ± 0.0012747 (W 0.00210699) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.34× slower than `lapack-mkl` |  |
| `lu/n257/b1` | 1.07879 ± 0.00150483 (W 0.00288455) | 1.22784 ± 0.004929 (W 0.0248975) | 0.935361 ± 0.00123967 (W 0.00248809) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.15× slower than `lapack-mkl` |  |
| `lu/n511/b1` | 5.761 ± 0.0332601 (W 0.0151203) | 6.30819 ± 0.0461024 (W 0.105964) | 5.21339 ± 0.0308275 (W 0.0101082) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔴 faer-fork 1.11× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 5.57072 ± 0.00476031 (W 0.0151004) | 6.08782 ± 0.0506814 (W 0.161769) | 5.32549 ± 0.0142827 (W 0.00967844) | 🔵 faer-fork 1.09× faster than `faer-upstream` | · |  |
| `qr/n255/b1` | 3.13853 ± 0.00164357 (W 0.00268107) | 4.16085 ± 0.00934152 (W 0.00891766) | 3.73246 ± 0.0197912 (W 0.0185745) | 🔵 faer-fork 1.33× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 3.21743 ± 0.00439735 (W 0.00669061) | 4.26001 ± 0.0203942 (W 0.0080993) | 3.86444 ± 0.0163036 (W 0.00512958) | 🔵 faer-fork 1.32× faster than `faer-upstream` | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 19.8694 ± 0.0101647 (W 0.0149947) | 21.7244 ± 0.0214202 (W 0.0254834) | 23.8911 ± 0.0584156 (W 0.0447381) | 🔵 faer-fork 1.09× faster than `faer-upstream` | 🔵 faer-fork 1.20× faster than `lapack-mkl` |  |
| `qr/n513/b1` | 20.2213 ± 0.0215583 (W 0.0181664) | 22.241 ± 0.0157323 (W 0.019601) | 24.0696 ± 0.0180178 (W 0.0372595) | 🔵 faer-fork 1.10× faster than `faer-upstream` | 🔵 faer-fork 1.19× faster than `lapack-mkl` |  |
| `qr_factor/n255/b1` | 1.52132 ± 0.00321782 (W 0.00313166) | 2.55456 ± 0.0169885 (W 0.00763761) | 1.57995 ± 0.00132602 (W 0.00348373) | 🔵 faer-fork 1.68× faster than `faer-upstream` | · |  |
| `qr_factor/n257/b1` | 1.56707 ± 0.00419857 (W 0.00437017) | 2.61179 ± 0.0148044 (W 0.00972474) | 1.64389 ± 0.00513664 (W 0.00441471) | 🔵 faer-fork 1.67× faster than `faer-upstream` | · |  |
| `qr_factor/n511/b1` | 8.88831 ± 0.0067576 (W 0.00800082) | 10.8613 ± 0.0395756 (W 0.0115674) | 10.8058 ± 0.0162544 (W 0.0150634) | 🔵 faer-fork 1.22× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 8.992 ± 0.00781517 (W 0.00632202) | 11.0666 ± 0.00514636 (W 0.0157797) | 10.9939 ± 0.00473608 (W 0.00996239) | 🔵 faer-fork 1.23× faster than `faer-upstream` | 🔵 faer-fork 1.22× faster than `lapack-mkl` |  |
| `solve/n255/b1` | 1.12026 ± 0.00548257 (W 0.0040446) | 1.24074 ± 0.00926761 (W 0.0111045) | 0.862681 ± 0.00258795 (W 0.00267573) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.30× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 1.09609 ± 0.00510377 (W 0.00461717) | 1.2403 ± 0.0143836 (W 0.0175858) | 0.9069 ± 0.00263018 (W 0.0022487) | 🔵 faer-fork 1.13× faster than `faer-upstream` | 🔴 faer-fork 1.21× slower than `lapack-mkl` |  |
| `solve/n511/b1` | 5.61234 ± 0.0144172 (W 0.0112868) | 6.25382 ± 0.081572 (W 0.113647) | 5.2436 ± 0.0281676 (W 0.00996887) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.07× slower than `lapack-mkl` |  |
| `solve/n513/b1` | 5.63637 ± 0.0017828 (W 0.0104116) | 6.23031 ± 0.0457603 (W 0.0954703) | 5.31609 ± 0.0328669 (W 0.0127346) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.06× slower than `lapack-mkl` |  |
| `svd_thin/n255/b1` | 16.3598 ± 0.0167896 (W 0.0253883) | 22.2875 ± 0.0635385 (W 0.0245684) | 15.8827 ± 0.0296394 (W 0.0271719) | 🔵 faer-fork 1.36× faster than `faer-upstream` | · |  |
| `svd_thin/n257/b1` | 13.8306 ± 0.0175535 (W 0.0303149) | 17.7323 ± 0.0261593 (W 0.026497) | 16.2001 ± 0.00395491 (W 0.0150598) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.17× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 76.8665 ± 0.0791913 (W 0.143744) | 87.4293 ± 0.0741844 (W 0.0546226) | 83.5195 ± 0.180104 (W 0.113447) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔵 faer-fork 1.09× faster than `lapack-mkl` |  |
| `svd_thin/n513/b1` | 74.0685 ± 0.120616 (W 0.0777083) | 76.4754 ± 0.201735 (W 0.0975948) | 84.1455 ± 0.101548 (W 0.125538) | · | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `svd_values/n255/b1` | 7.86996 ± 0.0266155 (W 0.0203319) | 17.0121 ± 0.076333 (W 0.0173067) | 7.6655 ± 0.0169272 (W 0.0115555) | 🔵 faer-fork 2.16× faster than `faer-upstream` | · |  |
| `svd_values/n257/b1` | 7.54905 ± 0.0415727 (W 0.0226666) | 13.6636 ± 0.166696 (W 0.0176373) | 7.82462 ± 0.0102456 (W 0.0102966) | 🔵 faer-fork 1.81× faster than `faer-upstream` | · |  |
| `svd_values/n511/b1` | 40.8291 ± 0.117964 (W 0.408695) | 57.7224 ± 0.0849767 (W 0.0867163) | 40.4725 ± 0.149931 (W 0.0239675) | 🔵 faer-fork 1.41× faster than `faer-upstream` | · |  |
| `svd_values/n513/b1` | 38.9951 ± 0.0519695 (W 0.0724713) | 48.2184 ± 0.0187845 (W 0.026234) | 40.9127 ± 0.0593726 (W 0.0329763) | 🔵 faer-fork 1.24× faster than `faer-upstream` | · |  |
| `triangular_solve/n255/b1` | 0.020658 ± 8.03762e-05 (W 0.000180312) | 0.024787 ± 0.000201927 (W 0.00178126) | - | 🔵 faer-fork 1.20× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.020969 ± 0.000750123 (W 0.000205355) | 0.025177 ± 0.0001205 (W 0.00201323) | - | 🔵 faer-fork 1.20× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n511/b1` | 0.057085 ± 0.0014167 (W 0.000540578) | 0.09152 ± 0.000889353 (W 0.000385164) | - | 🔵 faer-fork 1.60× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.056665 ± 0.00109209 (W 0.000431877) | 0.065703 ± 0.000319877 (W 0.000570518) | - | 🔵 faer-fork 1.16× faster than `faer-upstream` | - | `*` one row has no measurement here |

## linalg-boundary, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | faer-upstream (ms) | lapack-mkl (ms) | vs `faer-upstream` | vs `lapack-mkl` | notes |
|---|---|---|---|---|---|---|
| `cholesky/n255/b1` | 0.594294 ± 0.000978995 (W 0.00290385) | 0.711454 ± 0.00156773 (W 0.0124857) | 0.382391 ± 0.00109414 (W 0.00489725) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔴 faer-fork 1.55× slower than `lapack-mkl` |  |
| `cholesky/n257/b1` | 0.551178 ± 0.00307854 (W 0.00222247) | 0.658766 ± 0.00201989 (W 0.0194376) | 0.390155 ± 0.00245065 (W 0.00734066) | 🔵 faer-fork 1.20× faster than `faer-upstream` | 🔴 faer-fork 1.41× slower than `lapack-mkl` |  |
| `cholesky/n511/b1` | 2.24538 ± 0.00329465 (W 0.00460332) | 2.42176 ± 0.0215429 (W 0.0651244) | 1.70623 ± 0.0114115 (W 0.0113533) | 🔵 faer-fork 1.08× faster than `faer-upstream` | 🔴 faer-fork 1.32× slower than `lapack-mkl` |  |
| `cholesky/n513/b1` | 2.14636 ± 0.00581968 (W 0.00670282) | 2.28968 ± 0.0167229 (W 0.0629311) | 1.74581 ± 0.00673254 (W 0.0121751) | 🔵 faer-fork 1.07× faster than `faer-upstream` | 🔴 faer-fork 1.23× slower than `lapack-mkl` |  |
| `eigh/n255/b1` | 7.70063 ± 0.0135356 (W 0.00505912) | 11.1575 ± 0.0160307 (W 0.0383523) | 7.59027 ± 0.0143842 (W 0.0134638) | 🔵 faer-fork 1.45× faster than `faer-upstream` | · |  |
| `eigh/n257/b1` | 7.71406 ± 0.00739079 (W 0.00952248) | 11.1517 ± 0.020426 (W 0.0617711) | 7.69191 ± 0.0163766 (W 0.00931592) | 🔵 faer-fork 1.45× faster than `faer-upstream` | · |  |
| `eigh/n511/b1` | 30.3365 ± 0.0190286 (W 0.021349) | 39.0613 ± 0.0881946 (W 0.257321) | 35.0325 ± 0.020256 (W 0.0307754) | 🔵 faer-fork 1.29× faster than `faer-upstream` | 🔵 faer-fork 1.15× faster than `lapack-mkl` |  |
| `eigh/n513/b1` | 30.7016 ± 0.0413573 (W 0.024021) | 39.3976 ± 0.147954 (W 0.206226) | 35.0763 ± 0.0146761 (W 0.0734038) | 🔵 faer-fork 1.28× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `full_piv_lu/n255/b1` | 2.98971 ± 0.0168472 (W 0.0107043) | 5.71344 ± 0.0382318 (W 0.0147386) | - | 🔵 faer-fork 1.91× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.60489 ± 0.0227824 (W 0.0105571) | 4.35739 ± 0.0234252 (W 0.00565493) | - | 🔵 faer-fork 2.72× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 13.3852 ± 0.0599804 (W 0.0446479) | 22.3725 ± 0.0943118 (W 0.0186144) | - | 🔵 faer-fork 1.67× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 7.36903 ± 0.021576 (W 0.0139288) | 16.4266 ± 0.0786562 (W 0.0179741) | - | 🔵 faer-fork 2.23× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.07585 ± 0.00328112 (W 0.00339299) | 1.25179 ± 0.0085741 (W 0.00949536) | 0.661082 ± 0.000679014 (W 0.00435025) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔴 faer-fork 1.63× slower than `lapack-mkl` |  |
| `lu/n257/b1` | 0.951351 ± 0.00252212 (W 0.00184437) | 1.10079 ± 0.0101129 (W 0.0146074) | 0.6768 ± 0.00196432 (W 0.00320279) | 🔵 faer-fork 1.16× faster than `faer-upstream` | 🔴 faer-fork 1.41× slower than `lapack-mkl` |  |
| `lu/n511/b1` | 4.39536 ± 0.00921768 (W 0.00919077) | 4.99788 ± 0.00680113 (W 0.0314781) | 3.09588 ± 0.00661613 (W 0.00908549) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.42× slower than `lapack-mkl` |  |
| `lu/n513/b1` | 4.1774 ± 0.00167064 (W 0.00749766) | 4.6741 ± 0.0131842 (W 0.0321835) | 3.17568 ± 0.0262302 (W 0.0178272) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.32× slower than `lapack-mkl` |  |
| `qr/n255/b1` | 2.21012 ± 0.00135016 (W 0.00460879) | 4.11964 ± 0.03076 (W 0.0414255) | 2.92511 ± 0.0083121 (W 0.0093087) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr/n257/b1` | 2.25048 ± 0.00602571 (W 0.00447536) | 4.19068 ± 0.0545854 (W 0.0534638) | 2.97781 ± 0.00792463 (W 0.0122354) | 🔵 faer-fork 1.86× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr/n511/b1` | 10.8355 ± 0.027441 (W 0.0197555) | 18.0365 ± 0.0349738 (W 0.263505) | 12.3114 ± 0.00470917 (W 0.0206123) | 🔵 faer-fork 1.66× faster than `faer-upstream` | 🔵 faer-fork 1.14× faster than `lapack-mkl` |  |
| `qr/n513/b1` | 11.5809 ± 0.0151948 (W 0.00939149) | 18.3145 ± 0.187561 (W 0.202697) | 12.3518 ± 0.0274094 (W 0.019932) | 🔵 faer-fork 1.58× faster than `faer-upstream` | 🔵 faer-fork 1.07× faster than `lapack-mkl` |  |
| `qr_factor/n255/b1` | 1.2387 ± 0.00244321 (W 0.00623721) | 2.68704 ± 0.0178761 (W 0.0201536) | 1.62098 ± 0.00296439 (W 0.00371614) | 🔵 faer-fork 2.17× faster than `faer-upstream` | 🔵 faer-fork 1.31× faster than `lapack-mkl` |  |
| `qr_factor/n257/b1` | 1.2756 ± 0.00607264 (W 0.00639997) | 2.74236 ± 0.0167049 (W 0.015096) | 1.68099 ± 0.00250072 (W 0.00373276) | 🔵 faer-fork 2.15× faster than `faer-upstream` | 🔵 faer-fork 1.32× faster than `lapack-mkl` |  |
| `qr_factor/n511/b1` | 4.7141 ± 0.00547249 (W 0.00599983) | 9.8664 ± 0.044838 (W 0.101654) | 5.57067 ± 0.0110713 (W 0.00895672) | 🔵 faer-fork 2.09× faster than `faer-upstream` | 🔵 faer-fork 1.18× faster than `lapack-mkl` |  |
| `qr_factor/n513/b1` | 5.2775 ± 0.00459921 (W 0.0117122) | 9.89949 ± 0.0616998 (W 0.141985) | 5.71805 ± 0.00658142 (W 0.0106442) | 🔵 faer-fork 1.88× faster than `faer-upstream` | 🔵 faer-fork 1.08× faster than `lapack-mkl` |  |
| `solve/n255/b1` | 1.00477 ± 0.00471532 (W 0.00239908) | 1.12484 ± 0.00171271 (W 0.00547553) | 0.667733 ± 0.00166536 (W 0.00395911) | 🔵 faer-fork 1.12× faster than `faer-upstream` | 🔴 faer-fork 1.50× slower than `lapack-mkl` |  |
| `solve/n257/b1` | 0.969071 ± 0.00387787 (W 0.00185489) | 1.10578 ± 0.00763481 (W 0.0198352) | 0.685468 ± 0.00232962 (W 0.00398591) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.41× slower than `lapack-mkl` |  |
| `solve/n511/b1` | 4.24065 ± 0.00980156 (W 0.0140844) | 4.85213 ± 0.0586371 (W 0.0363758) | 3.14543 ± 0.00277682 (W 0.0133018) | 🔵 faer-fork 1.14× faster than `faer-upstream` | 🔴 faer-fork 1.35× slower than `lapack-mkl` |  |
| `solve/n513/b1` | 4.20133 ± 0.010389 (W 0.00402125) | 4.66863 ± 0.028046 (W 0.0443349) | 3.22745 ± 0.00460125 (W 0.0066158) | 🔵 faer-fork 1.11× faster than `faer-upstream` | 🔴 faer-fork 1.30× slower than `lapack-mkl` |  |
| `svd_thin/n255/b1` | 14.4184 ± 0.0538984 (W 0.0133994) | 22.069 ± 0.0544823 (W 0.0695809) | 12.0955 ± 0.0290567 (W 0.0207192) | 🔵 faer-fork 1.53× faster than `faer-upstream` | 🔴 faer-fork 1.19× slower than `lapack-mkl` |  |
| `svd_thin/n257/b1` | 11.7478 ± 0.0182514 (W 0.0194649) | 17.5455 ± 0.204566 (W 0.030385) | 12.3632 ± 0.0350855 (W 0.0301258) | 🔵 faer-fork 1.49× faster than `faer-upstream` | 🔵 faer-fork 1.05× faster than `lapack-mkl` |  |
| `svd_thin/n511/b1` | 57.9126 ± 0.143522 (W 0.0982225) | 74.4431 ± 0.38347 (W 0.339641) | 55.3198 ± 0.0563503 (W 0.0394058) | 🔵 faer-fork 1.29× faster than `faer-upstream` | · |  |
| `svd_thin/n513/b1` | 54.5991 ± 0.139567 (W 0.0674013) | 62.7352 ± 0.0435397 (W 0.231827) | 56.0089 ± 0.284948 (W 0.0446731) | 🔵 faer-fork 1.15× faster than `faer-upstream` | · |  |
| `svd_values/n255/b1` | 7.35963 ± 0.0211985 (W 0.0116306) | 16.9279 ± 0.178819 (W 0.0306189) | 6.25439 ± 0.0124345 (W 0.00962681) | 🔵 faer-fork 2.30× faster than `faer-upstream` | 🔴 faer-fork 1.18× slower than `lapack-mkl` |  |
| `svd_values/n257/b1` | 7.02121 ± 0.00776403 (W 0.0112531) | 13.2746 ± 0.0698816 (W 0.0301663) | 6.37252 ± 0.0207096 (W 0.00547981) | 🔵 faer-fork 1.89× faster than `faer-upstream` | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `svd_values/n511/b1` | 33.1831 ± 0.125772 (W 0.0840575) | 51.0254 ± 0.100532 (W 0.0470343) | 27.8672 ± 0.0288732 (W 0.0400871) | 🔵 faer-fork 1.54× faster than `faer-upstream` | 🔴 faer-fork 1.19× slower than `lapack-mkl` |  |
| `svd_values/n513/b1` | 30.8668 ± 0.0552016 (W 0.0486907) | 41.4624 ± 0.179296 (W 0.063481) | 28.1632 ± 0.0641424 (W 0.0326643) | 🔵 faer-fork 1.34× faster than `faer-upstream` | 🔴 faer-fork 1.10× slower than `lapack-mkl` |  |
| `triangular_solve/n255/b1` | 0.02143 ± 0.000867541 (W 0.000177827) | 0.024485 ± 0.000105548 (W 0.00173874) | - | 🔵 faer-fork 1.14× faster than `faer-upstream` | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n257/b1` | 0.02149 ± 0.000105987 (W 6.30079e-05) | 0.024776 ± 0.000160416 (W 0.000426027) | - | 🔵 faer-fork 1.15× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n511/b1` | 0.054351 ± 0.000340726 (W 0.000354946) | 0.090609 ± 0.0003505 (W 0.000519965) | - | 🔵 faer-fork 1.67× faster than `faer-upstream` | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.054041 ± 7.77839e-05 (W 0.000241585) | 0.062787 ± 0.000375673 (W 0.000493545) | - | 🔵 faer-fork 1.16× faster than `faer-upstream` | - | `*` one row has no measurement here |

Not applicable to this population's shapes and reported as skipped: `full_piv_lu/255`, `full_piv_lu/257`, `full_piv_lu/511`, `full_piv_lu/513`, `triangular_solve/255`, `triangular_solve/257`, `triangular_solve/511`, `triangular_solve/513`.

Repeated process sets describe observed repeatability under the recorded order schedule; they are not a paired baseline/candidate experiment and do not establish equal performance between engines.

# `faer-kernels-large` on `zen5-cpu`

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
- timestamp: `2026-11-01T08:40:30.078104Z`
- timing policy: v2, median of 5 reps, priming 250 ms (time-based, identical on every row)
- guards: idle window 3 s, max busy 5.0% including SMT siblings, 3 attempts
- command: `scripts/record_run.py zen5-cpu faer-kernels-large --checkout /home/shinaoka/.local/state/faer-measurement-checkouts/71b25ffb7ae3ce038ec25b35c91e526be41b9a63/t4a-faer --upstream extern/upstream-faer --vendor openblas --engines faer-fork,lapack-openblas --threads 4,8 --regimes linalg-large,gemm-large,linalg-boundary --shapes 1024,1024x1024x1024,255,257,511,513 --dtypes f64,c64 --reps 5 --aa 6 --prime-ms 250 --label pub-71b25ffb-20261031-large1024-openblas --no-publish`
- raw data: `data/results/zen5-cpu/faer-kernels-large/20261101T055425Z-pub-71b25ffb-20261031-large1024-openblas/`

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
- **Rows** — one row per engine in every table below:
  - `faer-fork` — The measured library: the tensor4all fork (`t4a-faer`, `[lib] name = "faer"`) at the checkout the harness linked by path. This is the row the campaign exists for; the fork's three perf experiments and the two correctness changes land here.
    Identity: the fork revision in this run's manifest (`library.commit`), pinned by `pins/t4a-faer.rev`
    Caveat: Both faer crates declare `[lib] name = "faer"`. They are distinct dependency keys (`faer_fork = { package = "t4a-faer" }`, `faer_upstream = { package = "faer" }`) and therefore distinct Rust crate identities, but their `Mat`, `Par` and trait types are not interchangeable: every adapter is written per arm, and shared transitive dependencies can unify Cargo features, so both arms declare equivalent feature sets and the resolved lock is recorded.
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
- CPU sets: 4T -> `4-7`, 8T -> `4-11`

Every timed cell matches a successful verification census, including operation variants.
Each cell is median of process medians ± sample SD of those medians; W is the median
within-process sample SD. All values are milliseconds. These are descriptive spreads,
not confidence intervals. The between-process spread includes the rotating-order schedule.
Each process retains 5 chronological calls; 6 complete process sets are recorded.
Spread guide (computed from this run's own rows): per-engine between-start range median 1.19%, worst 42.83% among cells of 1 us or more (a sub-microsecond row is timer and scheduler jitter, not kernel time); 84 of 736 engine cells exceed 5% and carry `!`; median within-process relative SD 0.23%. A cell whose `±`, `!` or `p` is as large as the difference you are reading is not evidence of a regression.
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

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 7.54417 ± 0.256564 (W 0.0146107) | 21.2461 ± 0.112947 (W 0.0547698) | 🔵 faer-fork 2.82× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n1024/b1` | 115.638 ± 0.537157 (W 0.246339) | 143.618 ± 0.935066 (W 0.486647) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 65.8351 ± 0.197483 (W 0.112956) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 17.9991 ± 3.09915 (W 0.0398509) | 33.8052 ± 1.59093 (W 0.230334) | 🔵 faer-fork 1.88× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 42.2409 ± 0.172654 (W 0.354967) | 107.266 ± 3.45056 (W 0.321161) | 🔵 faer-fork 2.54× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n1024/b1` | 19.4334 ± 0.140304 (W 0.0523756) | 52.1804 ± 0.412069 (W 0.112112) | 🔵 faer-fork 2.69× faster than `lapack-openblas` |  |
| `solve/n1024/b1` | 21.144 ± 0.0447428 (W 0.0331629) | 28.4918 ± 1.77079 (W 0.0498214) | 🔵 faer-fork 1.35× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n1024/b1` | 236.166 ± 0.783822 (W 0.623687) | 465.388 ± 5.02321 (W 3.51611) | 🔵 faer-fork 1.97× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 124.121 ± 0.670021 (W 0.177121) | 232.464 ± 3.76889 (W 0.451577) | 🔵 faer-fork 1.87× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.0837835 ± 0.00104709 (W 0.000536616) | - | - | `*` one row has no measurement here |

## linalg-large, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 6.33784 ± 0.0644926 (W 0.0242479) | 19.2521 ± 0.083421 (W 0.0554087) | 🔵 faer-fork 3.04× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 91.066 ± 0.123049 (W 0.234756) | 115.765 ± 0.817416 (W 0.284916) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 53.5983 ± 0.168875 (W 0.0989918) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 14.9523 ± 3.11439 (W 0.0427505) | 27.0713 ± 2.12355 (W 0.145866) | 🔵 faer-fork 1.81× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 24.0938 ± 0.114411 (W 0.131228) | 95.9483 ± 4.42227 (W 1.10057) | 🔵 faer-fork 3.98× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n1024/b1` | 10.4509 ± 0.112632 (W 0.022931) | 45.8434 ± 2.17666 (W 0.0779306) | 🔵 faer-fork 4.39× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n1024/b1` | 18.0126 ± 0.101861 (W 0.0628835) | 22.0105 ± 1.44255 (W 0.202239) | 🔵 faer-fork 1.22× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n1024/b1` | 174.278 ± 0.270682 (W 0.226102) | 419.522 ± 7.8098 (W 3.58671) | 🔵 faer-fork 2.41× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 97.3404 ± 0.320944 (W 0.185946) | 218.085 ± 4.28285 (W 0.945319) | 🔵 faer-fork 2.24× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.0712675 ± 0.000792198 (W 0.000397436) | - | - | `*` one row has no measurement here |

## linalg-large, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 5.22767 ± 0.013396 (W 0.008905) | 7.71665 ± 0.023239 (W 0.0377869) | 🔵 faer-fork 1.48× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 113.354 ± 0.292833 (W 0.377448) | 128.87 ± 0.373628 (W 0.289734) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 63.2446 ± 0.17272 (W 0.111667) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 15.4392 ± 2.85254 (W 0.0277283) | 13.8579 ± 0.0585574 (W 0.0306685) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 39.2221 ± 0.0553152 (W 0.0358517) | 85.1793 ± 0.74993 (W 0.123331) | 🔵 faer-fork 2.17× faster than `lapack-openblas` |  |
| `qr_factor/n1024/b1` | 17.1117 ± 0.026311 (W 0.0239139) | 37.9958 ± 0.159797 (W 0.0375102) | 🔵 faer-fork 2.22× faster than `lapack-openblas` |  |
| `solve/n1024/b1` | 18.5705 ± 0.0784364 (W 0.0505779) | 13.4446 ± 0.093258 (W 0.027651) | 🔴 faer-fork 1.38× slower than `lapack-openblas` |  |
| `svd_thin/n1024/b1` | 228.959 ± 0.624032 (W 0.440257) | 405.353 ± 7.64767 (W 1.53492) | 🔵 faer-fork 1.77× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 115.321 ± 0.557846 (W 0.106368) | 212.04 ± 5.36731 (W 0.716042) | 🔵 faer-fork 1.84× faster than `lapack-openblas` | `!` between-start range over 5% |
| `triangular_solve/n1024/b1` | 0.10887 ± 0.00143703 (W 0.000948039) | - | - | `*` one row has no measurement here |

## linalg-large, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 3.77387 ± 0.0357075 (W 0.0185101) | 5.87092 ± 0.0288151 (W 0.0198999) | 🔵 faer-fork 1.56× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 88.8558 ± 0.298261 (W 0.225317) | 101.639 ± 0.233874 (W 0.12712) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 50.8152 ± 0.327846 (W 0.0982197) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 12.2976 ± 2.77755 (W 0.0701641) | 7.79173 ± 0.039826 (W 0.0134687) | 🔴 faer-fork 1.58× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr/n1024/b1` | 21.5654 ± 0.055929 (W 0.0276109) | 71.1904 ± 0.372841 (W 0.0577301) | 🔵 faer-fork 3.30× faster than `lapack-openblas` |  |
| `qr_factor/n1024/b1` | 8.90904 ± 0.0182885 (W 0.0121629) | 30.8905 ± 0.185692 (W 0.0242483) | 🔵 faer-fork 3.47× faster than `lapack-openblas` |  |
| `solve/n1024/b1` | 15.5026 ± 0.0456732 (W 0.0369721) | 7.68083 ± 0.0434234 (W 0.017184) | 🔴 faer-fork 2.02× slower than `lapack-openblas` |  |
| `svd_thin/n1024/b1` | 167.434 ± 0.187586 (W 0.268031) | 364.983 ± 10.7255 (W 0.761536) | 🔵 faer-fork 2.18× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_values/n1024/b1` | 88.682 ± 0.21326 (W 0.0777579) | 198.566 ± 1.80766 (W 0.553647) | 🔵 faer-fork 2.24× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.092182 ± 0.00101566 (W 0.000788137) | - | - | `*` one row has no measurement here |

## linalg-large, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 19.6134 ± 0.0886867 (W 0.157701) | 35.8115 ± 0.212859 (W 0.0976756) | 🔵 faer-fork 1.83× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 244.725 ± 0.500329 (W 0.418401) | 425.007 ± 1.97848 (W 1.34576) | 🔵 faer-fork 1.74× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 141.277 ± 0.149945 (W 0.412685) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 38.9509 ± 0.079362 (W 0.0536828) | 52.8375 ± 2.33347 (W 0.87606) | 🔵 faer-fork 1.36× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n1024/b1` | 147.825 ± 0.193286 (W 0.165267) | 212.679 ± 4.72436 (W 2.66984) | 🔵 faer-fork 1.44× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n1024/b1` | 64.2498 ± 0.0724244 (W 0.0966873) | 105.924 ± 3.10769 (W 0.436785) | 🔵 faer-fork 1.65× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n1024/b1` | 39.3267 ± 0.136254 (W 0.149701) | 49.4186 ± 1.97557 (W 1.2604) | 🔵 faer-fork 1.26× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n1024/b1` | 565.754 ± 0.471684 (W 1.35457) | 766.389 ± 1.51646 (W 1.74685) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 315.363 ± 0.795799 (W 0.622975) | 347.854 ± 3.07572 (W 1.08122) | 🔵 faer-fork 1.10× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.201765 ± 0.00695474 (W 0.00362635) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-large, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 13.7086 ± 0.0989137 (W 0.132375) | 27.1842 ± 0.0858584 (W 0.0410806) | 🔵 faer-fork 1.98× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 165.975 ± 0.306516 (W 0.287535) | 230.782 ± 1.24912 (W 0.594662) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 81.4085 ± 0.333804 (W 0.384298) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 27.3636 ± 0.146812 (W 0.138045) | 38.1992 ± 0.773247 (W 0.530551) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `qr/n1024/b1` | 81.6622 ± 0.138664 (W 0.188366) | 158.081 ± 2.79214 (W 2.52089) | 🔵 faer-fork 1.94× faster than `lapack-openblas` |  |
| `qr_factor/n1024/b1` | 35.1013 ± 0.069077 (W 0.0685632) | 77.2192 ± 3.12722 (W 0.379065) | 🔵 faer-fork 2.20× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n1024/b1` | 27.2233 ± 0.0818334 (W 0.0791881) | 36.1118 ± 1.75219 (W 1.40961) | 🔵 faer-fork 1.33× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n1024/b1` | 353 ± 1.34312 (W 0.915591) | 593.55 ± 6.52933 (W 2.39488) | 🔵 faer-fork 1.68× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 194.457 ± 0.654348 (W 0.674768) | 280.588 ± 0.569531 (W 0.572782) | 🔵 faer-fork 1.44× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.136479 ± 0.00140301 (W 0.000916652) | - | - | `*` one row has no measurement here |

## linalg-large, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 16.8146 ± 0.0201968 (W 0.0208283) | 21.3502 ± 0.242778 (W 0.0244195) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 242.089 ± 13.1524 (W 0.503243) | 407.552 ± 2.74917 (W 1.49114) | 🔵 faer-fork 1.68× faster than `lapack-openblas` | `!` between-start range over 5% |
| `full_piv_lu/n1024/b1` | 136.586 ± 0.458381 (W 0.324535) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 34.4403 ± 0.0379149 (W 0.0264062) | 34.7244 ± 0.0736488 (W 0.0342278) | · |  |
| `qr/n1024/b1` | 142.896 ± 1.74045 (W 0.260377) | 188.582 ± 0.413864 (W 0.389028) | 🔵 faer-fork 1.32× faster than `lapack-openblas` |  |
| `qr_factor/n1024/b1` | 59.9556 ± 0.0789756 (W 0.0421305) | 88.8565 ± 0.1617 (W 0.0871847) | 🔵 faer-fork 1.48× faster than `lapack-openblas` |  |
| `solve/n1024/b1` | 34.4428 ± 0.0407837 (W 0.0352309) | 34.8453 ± 0.0569612 (W 0.0271934) | · |  |
| `svd_thin/n1024/b1` | 557.396 ± 0.816631 (W 1.13822) | 703.516 ± 3.79838 (W 2.55177) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 308.286 ± 1.01258 (W 0.641291) | 327.895 ± 3.64423 (W 0.980148) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.218354 ± 0.00245415 (W 0.00391079) | - | - | `*` one row has no measurement here |

## linalg-large, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n1024/b1` | 10.956 ± 0.0226256 (W 0.0167417) | 12.7633 ± 0.158673 (W 0.0125509) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `eigh/n1024/b1` | 163.37 ± 0.24805 (W 0.370743) | 213.077 ± 0.709466 (W 0.417804) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `full_piv_lu/n1024/b1` | 76.8984 ± 0.475174 (W 0.19933) | - | - | `*` one row has no measurement here |
| `lu/n1024/b1` | 22.5847 ± 0.0102878 (W 0.0200322) | 18.7647 ± 0.0337174 (W 0.0298803) | 🔴 faer-fork 1.20× slower than `lapack-openblas` |  |
| `qr/n1024/b1` | 76.7812 ± 0.166427 (W 0.0797521) | 130.758 ± 0.345657 (W 0.130065) | 🔵 faer-fork 1.70× faster than `lapack-openblas` |  |
| `qr_factor/n1024/b1` | 31.7783 ± 0.0725916 (W 0.03465) | 59.9672 ± 0.152483 (W 0.2259) | 🔵 faer-fork 1.89× faster than `lapack-openblas` |  |
| `solve/n1024/b1` | 22.3535 ± 0.0321768 (W 0.0245055) | 19.1562 ± 0.0220347 (W 0.0251812) | 🔴 faer-fork 1.17× slower than `lapack-openblas` |  |
| `svd_thin/n1024/b1` | 344.102 ± 0.607532 (W 1.02213) | 532.354 ± 1.08033 (W 1.68407) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `svd_values/n1024/b1` | 186.355 ± 1.17435 (W 0.500021) | 261.747 ± 1.42842 (W 0.683542) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `triangular_solve/n1024/b1` | 0.153576 ± 0.00349067 (W 0.00110057) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

Not applicable to this population's shapes and reported as skipped: `full_piv_lu/1024`, `triangular_solve/1024`.

## gemm-large, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 17.6059 ± 0.0268243 (W 0.0151151) | 20.5981 ± 0.0274827 (W 0.0328151) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |

## gemm-large, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 9.00981 ± 1.15934 (W 0.0115339) | 10.6611 ± 0.0258946 (W 0.0191821) | 🔵 faer-fork 1.18× faster than `lapack-openblas` | `!` between-start range over 5% |

## gemm-large, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 17.5899 ± 0.0232954 (W 0.0104298) | 20.606 ± 0.0380597 (W 0.0272592) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |

## gemm-large, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 9.01103 ± 0.0209399 (W 0.0107165) | 10.676 ± 0.0181822 (W 0.025774) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |

## gemm-large, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 69.9712 ± 0.0646849 (W 0.0552983) | 82.5833 ± 0.171945 (W 0.0434312) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |

## gemm-large, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 35.286 ± 0.0654555 (W 0.0403302) | 42.0204 ± 0.105282 (W 0.0439562) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |

## gemm-large, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 70.0271 ± 0.132306 (W 0.0840953) | 82.6987 ± 0.122351 (W 0.0437089) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |

## gemm-large, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `gemm/1024x1024x1024/b1` | 35.3024 ± 0.0912055 (W 0.0223467) | 42.1724 ± 0.042595 (W 0.0536132) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |

## linalg-boundary, f64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.230047 ± 0.00238715 (W 0.00182731) | 0.401723 ± 0.00250001 (W 0.00267304) | 🔵 faer-fork 1.75× faster than `lapack-openblas` |  |
| `cholesky/n257/b1` | 0.221904 ± 0.010399 (W 0.00233021) | 0.344844 ± 0.00271558 (W 0.00315648) | 🔵 faer-fork 1.55× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 0.948252 ± 0.00734882 (W 0.0041306) | 1.56664 ± 0.0208339 (W 0.00630801) | 🔵 faer-fork 1.65× faster than `lapack-openblas` |  |
| `cholesky/n513/b1` | 0.913728 ± 0.0257762 (W 0.00505707) | 1.58478 ± 0.0353832 (W 0.0059306) | 🔵 faer-fork 1.73× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n255/b1` | 6.41281 ± 0.0170499 (W 0.00877414) | 4.83852 ± 0.00933278 (W 0.00698365) | 🔴 faer-fork 1.33× slower than `lapack-openblas` |  |
| `eigh/n257/b1` | 6.48801 ± 0.0152352 (W 0.00888858) | 4.87847 ± 0.00658506 (W 0.00813697) | 🔴 faer-fork 1.33× slower than `lapack-openblas` |  |
| `eigh/n511/b1` | 24.1149 ± 0.0373669 (W 0.0262307) | 19.8472 ± 0.0875635 (W 0.0266847) | 🔴 faer-fork 1.22× slower than `lapack-openblas` |  |
| `eigh/n513/b1` | 24.4339 ± 0.102912 (W 0.034649) | 20.1995 ± 0.101777 (W 0.0322001) | 🔴 faer-fork 1.21× slower than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 2.03533 ± 0.0143793 (W 0.00793546) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.28776 ± 0.00964514 (W 0.0053505) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 12.3769 ± 0.612234 (W 0.0238395) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/n513/b1` | 7.23325 ± 0.0253956 (W 0.0103294) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.809246 ± 0.00731623 (W 0.00478751) | 0.744949 ± 0.130976 (W 0.00442758) | · | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n257/b1` | 0.811557 ± 0.00572262 (W 0.00330901) | 0.861639 ± 0.0108635 (W 0.00560327) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `lu/n511/b1` | 4.32156 ± 0.0242062 (W 0.0115519) | 4.12159 ± 0.061004 (W 0.0135873) | · |  |
| `lu/n513/b1` | 3.65512 ± 0.0161737 (W 0.0146765) | 4.13984 ± 0.0253 (W 0.00915698) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `qr/n255/b1` | 1.17942 ± 0.00413646 (W 0.00476382) | 2.52612 ± 0.0401319 (W 0.00455192) | 🔵 faer-fork 2.14× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 1.20975 ± 0.032196 (W 0.00377413) | 2.42214 ± 0.0377692 (W 0.00369463) | 🔵 faer-fork 2.00× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n511/b1` | 6.44031 ± 0.0130533 (W 0.0130216) | 10.2397 ± 0.209945 (W 0.0535272) | 🔵 faer-fork 1.59× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n513/b1` | 6.54579 ± 0.0234021 (W 0.0106389) | 10.5972 ± 0.0446311 (W 0.0146987) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `qr_factor/n255/b1` | 0.656787 ± 0.00263278 (W 0.00388909) | 1.26059 ± 0.0215708 (W 0.00346527) | 🔵 faer-fork 1.92× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 0.696403 ± 0.00317966 (W 0.00307528) | 1.19113 ± 0.0224195 (W 0.0029715) | 🔵 faer-fork 1.71× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n511/b1` | 3.22203 ± 0.00851627 (W 0.00962591) | 5.00553 ± 0.0837294 (W 0.0162438) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 3.23099 ± 0.00358445 (W 0.00701695) | 5.14306 ± 0.0586948 (W 0.010979) | 🔵 faer-fork 1.59× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 0.585819 ± 0.00379613 (W 0.00339839) | 0.591708 ± 0.0137572 (W 0.00246381) | · | `!` between-start range over 5% |
| `solve/n257/b1` | 0.548971 ± 0.00262042 (W 0.00278649) | 0.599465 ± 0.0147819 (W 0.00190577) | 🔵 faer-fork 1.09× faster than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n511/b1` | 4.13787 ± 0.542645 (W 0.0121386) | 3.02545 ± 0.0421236 (W 0.00601184) | 🔴 faer-fork 1.37× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 3.75328 ± 0.551452 (W 0.0204184) | 3.06254 ± 0.0211876 (W 0.00465428) | 🔴 faer-fork 1.23× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n255/b1` | 11.2616 ± 0.0166287 (W 0.0199228) | 11.1344 ± 0.0184682 (W 0.0179375) | · |  |
| `svd_thin/n257/b1` | 8.95286 ± 0.0259231 (W 0.0154842) | 11.2467 ± 0.0285306 (W 0.0156367) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 44.5787 ± 0.18211 (W 0.0638704) | 60.0414 ± 2.30824 (W 0.151357) | 🔵 faer-fork 1.35× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n513/b1` | 41.0433 ± 0.0535337 (W 0.0609229) | 58.8864 ± 0.265599 (W 0.0649769) | 🔵 faer-fork 1.43× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 5.32482 ± 0.0203129 (W 0.0125329) | 6.22784 ± 0.0426819 (W 0.00940521) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `svd_values/n257/b1` | 5.10822 ± 0.0359232 (W 0.0144893) | 6.27571 ± 0.0240272 (W 0.00698706) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 24.8818 ± 0.0820774 (W 0.0350023) | 36.3389 ± 0.242057 (W 0.0452629) | 🔵 faer-fork 1.46× faster than `lapack-openblas` |  |
| `svd_values/n513/b1` | 22.2696 ± 0.0606146 (W 0.0396285) | 36.4171 ± 0.286781 (W 0.027545) | 🔵 faer-fork 1.64× faster than `lapack-openblas` |  |
| `triangular_solve/n255/b1` | 0.012509 ± 0.000132862 (W 0.000102192) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.0132245 ± 0.000302151 (W 6.3963e-05) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.0296155 ± 0.000888757 (W 0.000133132) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.0298705 ± 0.0006748 (W 0.000211603) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, f64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.2226 ± 0.00124981 (W 0.00183572) | 0.402633 ± 0.00244199 (W 0.00271413) | 🔵 faer-fork 1.81× faster than `lapack-openblas` |  |
| `cholesky/n257/b1` | 0.199181 ± 0.00977374 (W 0.00188854) | 0.346552 ± 0.0030976 (W 0.00217191) | 🔵 faer-fork 1.74× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 0.807994 ± 0.00312983 (W 0.00305404) | 1.42762 ± 0.0532403 (W 0.00638035) | 🔵 faer-fork 1.77× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n513/b1` | 0.739685 ± 0.0275017 (W 0.00398868) | 1.46355 ± 0.0591245 (W 0.00816579) | 🔵 faer-fork 1.98× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n255/b1` | 6.16929 ± 0.0210194 (W 0.00816202) | 4.47352 ± 0.0232382 (W 0.0103226) | 🔴 faer-fork 1.38× slower than `lapack-openblas` |  |
| `eigh/n257/b1` | 6.18248 ± 0.0250974 (W 0.00976948) | 4.47941 ± 0.0157162 (W 0.00618835) | 🔴 faer-fork 1.38× slower than `lapack-openblas` |  |
| `eigh/n511/b1` | 21.5595 ± 0.0529318 (W 0.0300761) | 16.2572 ± 0.0807883 (W 0.0189357) | 🔴 faer-fork 1.33× slower than `lapack-openblas` |  |
| `eigh/n513/b1` | 21.9352 ± 0.0405398 (W 0.0288469) | 16.6031 ± 0.0355344 (W 0.0245635) | 🔴 faer-fork 1.32× slower than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 1.96347 ± 0.0111697 (W 0.0118003) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.23976 ± 0.013717 (W 0.0053209) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 10.6744 ± 0.0835186 (W 0.0195343) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 6.01904 ± 0.0331113 (W 0.0125863) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.69871 ± 0.110086 (W 0.00329653) | 0.695419 ± 0.128197 (W 0.00194614) | · | `!` between-start range over 5% |
| `lu/n257/b1` | 0.788714 ± 0.00342609 (W 0.00338868) | 0.774209 ± 0.0115018 (W 0.00650385) | · |  |
| `lu/n511/b1` | 4.01252 ± 0.0163422 (W 0.00952326) | 3.22021 ± 0.0507868 (W 0.00636394) | 🔴 faer-fork 1.25× slower than `lapack-openblas` |  |
| `lu/n513/b1` | 3.35224 ± 0.0136105 (W 0.0104258) | 3.25947 ± 0.00519872 (W 0.0106522) | · |  |
| `qr/n255/b1` | 1.01168 ± 0.00311626 (W 0.00169637) | 2.53741 ± 0.0464167 (W 0.00455653) | 🔵 faer-fork 2.51× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 1.02518 ± 0.00433307 (W 0.00158056) | 2.3909 ± 0.00775634 (W 0.00439521) | 🔵 faer-fork 2.33× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 4.12511 ± 0.0189904 (W 0.00892823) | 8.82801 ± 0.208105 (W 0.016889) | 🔵 faer-fork 2.14× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr/n513/b1` | 5.36968 ± 0.978167 (W 0.0156311) | 8.93733 ± 0.117117 (W 0.00942144) | 🔵 faer-fork 1.66× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n255/b1` | 0.611742 ± 0.00294816 (W 0.00294724) | 1.25945 ± 0.0321822 (W 0.00377785) | 🔵 faer-fork 2.06× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n257/b1` | 0.644562 ± 0.00363907 (W 0.00218627) | 1.16027 ± 0.0167576 (W 0.00298866) | 🔵 faer-fork 1.80× faster than `lapack-openblas` |  |
| `qr_factor/n511/b1` | 1.88063 ± 0.0048128 (W 0.00368068) | 4.26395 ± 0.0774279 (W 0.0112941) | 🔵 faer-fork 2.27× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 2.25904 ± 0.00357717 (W 0.00565202) | 4.2106 ± 0.069714 (W 0.0102135) | 🔵 faer-fork 1.86× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 0.577071 ± 0.00390754 (W 0.0024482) | 0.57182 ± 0.0105982 (W 0.00467533) | · | `!` between-start range over 5% |
| `solve/n257/b1` | 0.535314 ± 0.00273078 (W 0.00346214) | 0.554789 ± 0.0136039 (W 0.00317398) | · | `!` between-start range over 5% |
| `solve/n511/b1` | 3.88743 ± 0.68083 (W 0.0148287) | 2.30692 ± 0.0534277 (W 0.00775169) | 🔴 faer-fork 1.69× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 3.46239 ± 0.540602 (W 0.00987064) | 2.22426 ± 0.0577411 (W 0.00980204) | 🔴 faer-fork 1.56× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n255/b1` | 10.7899 ± 0.0223874 (W 0.0148138) | 11.0132 ± 0.0364063 (W 0.0131335) | · |  |
| `svd_thin/n257/b1` | 8.38805 ± 0.0175942 (W 0.0143161) | 10.9769 ± 0.055357 (W 0.0191849) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 39.1388 ± 0.108278 (W 0.0683139) | 55.8887 ± 3.01571 (W 0.11584) | 🔵 faer-fork 1.43× faster than `lapack-openblas` | `!` between-start range over 5% |
| `svd_thin/n513/b1` | 35.1922 ± 0.0668119 (W 0.0634446) | 54.5636 ± 0.371746 (W 0.0939848) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 5.2631 ± 0.0241041 (W 0.00948103) | 6.24612 ± 0.0414494 (W 0.00754338) | 🔵 faer-fork 1.19× faster than `lapack-openblas` |  |
| `svd_values/n257/b1` | 5.01987 ± 0.018376 (W 0.0120133) | 6.27305 ± 0.0222192 (W 0.00942723) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 22.9206 ± 0.0877384 (W 0.0251831) | 35.5991 ± 0.498487 (W 0.0363254) | 🔵 faer-fork 1.55× faster than `lapack-openblas` |  |
| `svd_values/n513/b1` | 20.142 ± 0.0586617 (W 0.0395861) | 35.9559 ± 0.261217 (W 0.0470335) | 🔵 faer-fork 1.79× faster than `lapack-openblas` |  |
| `triangular_solve/n255/b1` | 0.012303 ± 0.00015406 (W 7.1835e-05) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.0128745 ± 0.000361182 (W 0.000109174) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.0285685 ± 0.000494184 (W 0.000146194) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.030226 ± 0.000571299 (W 0.000204374) | - | - | `*` one row has no measurement here |

## linalg-boundary, f64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.229023 ± 0.00103594 (W 0.00197206) | 0.359865 ± 0.00255776 (W 0.00418853) | 🔵 faer-fork 1.57× faster than `lapack-openblas` |  |
| `cholesky/n257/b1` | 0.215446 ± 0.00722224 (W 0.00212063) | 0.301578 ± 0.00172635 (W 0.00271382) | 🔵 faer-fork 1.40× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 0.931507 ± 0.00648506 (W 0.00299597) | 1.37654 ± 0.00775027 (W 0.00425166) | 🔵 faer-fork 1.48× faster than `lapack-openblas` |  |
| `cholesky/n513/b1` | 0.893591 ± 0.0133779 (W 0.00288927) | 1.36627 ± 0.00570361 (W 0.00313654) | 🔵 faer-fork 1.53× faster than `lapack-openblas` |  |
| `eigh/n255/b1` | 6.42258 ± 0.020075 (W 0.00880416) | 4.75796 ± 0.0195583 (W 0.00594932) | 🔴 faer-fork 1.35× slower than `lapack-openblas` |  |
| `eigh/n257/b1` | 6.48418 ± 0.0141674 (W 0.00798901) | 4.82452 ± 0.0147058 (W 0.00534355) | 🔴 faer-fork 1.34× slower than `lapack-openblas` |  |
| `eigh/n511/b1` | 24.0441 ± 0.12252 (W 0.0259561) | 19.4353 ± 0.0487738 (W 0.0389095) | 🔴 faer-fork 1.24× slower than `lapack-openblas` |  |
| `eigh/n513/b1` | 24.324 ± 0.0761928 (W 0.0303513) | 19.7405 ± 0.075252 (W 0.0221472) | 🔴 faer-fork 1.23× slower than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 1.92281 ± 0.00875297 (W 0.00776988) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.17435 ± 0.00909118 (W 0.00418628) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 11.8476 ± 0.596027 (W 0.0318251) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `full_piv_lu/n513/b1` | 6.66634 ± 0.0290753 (W 0.0186304) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.70566 ± 0.00389138 (W 0.00639421) | 0.501876 ± 0.00301503 (W 0.00270237) | 🔴 faer-fork 1.41× slower than `lapack-openblas` |  |
| `lu/n257/b1` | 0.688165 ± 0.00604805 (W 0.0057653) | 0.512258 ± 0.00161297 (W 0.00277178) | 🔴 faer-fork 1.34× slower than `lapack-openblas` |  |
| `lu/n511/b1` | 3.72694 ± 0.0187279 (W 0.0108563) | 2.62901 ± 0.0128985 (W 0.0104951) | 🔴 faer-fork 1.42× slower than `lapack-openblas` |  |
| `lu/n513/b1` | 3.07522 ± 0.0194778 (W 0.013687) | 2.6517 ± 0.0343871 (W 0.00608197) | 🔴 faer-fork 1.16× slower than `lapack-openblas` |  |
| `qr/n255/b1` | 1.05845 ± 0.00260226 (W 0.00350532) | 2.28655 ± 0.0038219 (W 0.00437486) | 🔵 faer-fork 2.16× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 1.08837 ± 0.00356706 (W 0.00403214) | 2.19789 ± 0.00786971 (W 0.00562033) | 🔵 faer-fork 2.02× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 5.846 ± 0.016357 (W 0.00948904) | 9.31354 ± 0.0571525 (W 0.0221931) | 🔵 faer-fork 1.59× faster than `lapack-openblas` |  |
| `qr/n513/b1` | 5.94782 ± 0.0136876 (W 0.0103298) | 9.68748 ± 0.0523283 (W 0.0162114) | 🔵 faer-fork 1.63× faster than `lapack-openblas` |  |
| `qr_factor/n255/b1` | 0.575014 ± 0.00376503 (W 0.00276759) | 1.12673 ± 0.00702559 (W 0.00304667) | 🔵 faer-fork 1.96× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 0.592262 ± 0.00371195 (W 0.00295376) | 1.07931 ± 0.00801696 (W 0.00390432) | 🔵 faer-fork 1.82× faster than `lapack-openblas` |  |
| `qr_factor/n511/b1` | 2.90948 ± 0.00748356 (W 0.00403962) | 4.55133 ± 0.0144577 (W 0.00795185) | 🔵 faer-fork 1.56× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 2.8899 ± 0.00973982 (W 0.00653551) | 4.68285 ± 0.0130716 (W 0.0091322) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 0.483086 ± 0.00261624 (W 0.00183081) | 0.484735 ± 0.00249435 (W 0.00327285) | · |  |
| `solve/n257/b1` | 0.445214 ± 0.00333838 (W 0.00319759) | 0.491577 ± 0.00113354 (W 0.00372306) | 🔵 faer-fork 1.10× faster than `lapack-openblas` |  |
| `solve/n511/b1` | 3.57461 ± 0.490376 (W 0.0168716) | 2.5834 ± 0.00997532 (W 0.00568034) | 🔴 faer-fork 1.38× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 3.1632 ± 0.497481 (W 0.00835641) | 2.60522 ± 0.0104275 (W 0.00915473) | 🔴 faer-fork 1.21× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n255/b1` | 11.3499 ± 0.0299926 (W 0.0159275) | 10.8601 ± 0.0257487 (W 0.0184528) | · |  |
| `svd_thin/n257/b1` | 8.93516 ± 0.0154756 (W 0.0144065) | 11.0255 ± 0.03374 (W 0.0152105) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 44.541 ± 0.183991 (W 0.0503181) | 56.3345 ± 0.544739 (W 0.0452574) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `svd_thin/n513/b1` | 40.8727 ± 0.0807319 (W 0.0575993) | 57.328 ± 0.147202 (W 0.053257) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 5.2735 ± 0.0206102 (W 0.0129842) | 6.08203 ± 0.0138542 (W 0.0100624) | 🔵 faer-fork 1.15× faster than `lapack-openblas` |  |
| `svd_values/n257/b1` | 5.144 ± 0.0348144 (W 0.0128599) | 6.19719 ± 0.0275092 (W 0.00835845) | 🔵 faer-fork 1.20× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 24.7205 ± 0.12131 (W 0.0296085) | 35.21 ± 0.268247 (W 0.0296647) | 🔵 faer-fork 1.42× faster than `lapack-openblas` |  |
| `svd_values/n513/b1` | 22.1499 ± 0.0778098 (W 0.026784) | 35.9469 ± 0.331593 (W 0.0623014) | 🔵 faer-fork 1.62× faster than `lapack-openblas` |  |
| `triangular_solve/n255/b1` | 0.014848 ± 0.000131401 (W 0.000201991) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.0158195 ± 0.000551047 (W 0.00021695) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.038146 ± 0.00103314 (W 0.000424302) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.0378505 ± 0.000849805 (W 0.000500211) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, f64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.220415 ± 0.000773164 (W 0.00179062) | 0.361649 ± 0.00233068 (W 0.00298378) | 🔵 faer-fork 1.64× faster than `lapack-openblas` |  |
| `cholesky/n257/b1` | 0.196471 ± 0.00872142 (W 0.00202702) | 0.303066 ± 0.00291107 (W 0.00386498) | 🔵 faer-fork 1.54× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 0.80346 ± 0.0161833 (W 0.00273396) | 1.2243 ± 0.00428157 (W 0.00432591) | 🔵 faer-fork 1.52× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n513/b1` | 0.73168 ± 0.0230501 (W 0.00336539) | 1.23448 ± 0.0100889 (W 0.00369068) | 🔵 faer-fork 1.69× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n255/b1` | 6.1465 ± 0.0123431 (W 0.0137075) | 4.41245 ± 0.0137521 (W 0.00526092) | 🔴 faer-fork 1.39× slower than `lapack-openblas` |  |
| `eigh/n257/b1` | 6.13274 ± 0.0218301 (W 0.00793151) | 4.41856 ± 0.0126129 (W 0.00480307) | 🔴 faer-fork 1.39× slower than `lapack-openblas` |  |
| `eigh/n511/b1` | 21.4351 ± 0.056496 (W 0.0150551) | 15.8382 ± 0.0552775 (W 0.0141295) | 🔴 faer-fork 1.35× slower than `lapack-openblas` |  |
| `eigh/n513/b1` | 21.8225 ± 0.0524263 (W 0.0196435) | 16.1143 ± 0.046031 (W 0.0136716) | 🔴 faer-fork 1.35× slower than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 1.88143 ± 0.0134397 (W 0.0101028) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.13884 ± 0.0118869 (W 0.00600714) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 10.1478 ± 0.0486336 (W 0.0208297) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 5.47159 ± 0.0218785 (W 0.00914797) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 0.58851 ± 0.108767 (W 0.00384493) | 0.440052 ± 0.00343722 (W 0.00367605) | 🔴 faer-fork 1.34× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `lu/n257/b1` | 0.66352 ± 0.00324113 (W 0.00283675) | 0.447941 ± 0.00270435 (W 0.00277816) | 🔴 faer-fork 1.48× slower than `lapack-openblas` |  |
| `lu/n511/b1` | 3.4427 ± 0.00875939 (W 0.010572) | 1.74841 ± 0.0120862 (W 0.00515514) | 🔴 faer-fork 1.97× slower than `lapack-openblas` |  |
| `lu/n513/b1` | 2.78575 ± 0.00670737 (W 0.00628858) | 1.76632 ± 0.011494 (W 0.0069765) | 🔴 faer-fork 1.58× slower than `lapack-openblas` |  |
| `qr/n255/b1` | 0.886764 ± 0.00300843 (W 0.00186407) | 2.26998 ± 0.0299582 (W 0.00529517) | 🔵 faer-fork 2.56× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 0.907954 ± 0.00340541 (W 0.00145617) | 2.16005 ± 0.0086927 (W 0.00400145) | 🔵 faer-fork 2.38× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 3.54376 ± 0.0148436 (W 0.0092743) | 7.77568 ± 0.0213837 (W 0.00818045) | 🔵 faer-fork 2.19× faster than `lapack-openblas` |  |
| `qr/n513/b1` | 4.72157 ± 0.926917 (W 0.00857478) | 7.98896 ± 0.0327367 (W 0.00877081) | 🔵 faer-fork 1.69× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `qr_factor/n255/b1` | 0.562278 ± 0.004878 (W 0.00292934) | 1.11082 ± 0.0140064 (W 0.00277589) | 🔵 faer-fork 1.98× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 0.578151 ± 0.0040972 (W 0.00245977) | 1.06256 ± 0.00389976 (W 0.00263478) | 🔵 faer-fork 1.84× faster than `lapack-openblas` |  |
| `qr_factor/n511/b1` | 1.72439 ± 0.00673408 (W 0.00396664) | 3.76159 ± 0.0165377 (W 0.00641416) | 🔵 faer-fork 2.18× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 2.05081 ± 0.00864041 (W 0.00364505) | 3.8514 ± 0.0108885 (W 0.00839407) | 🔵 faer-fork 1.88× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 0.472841 ± 0.00345709 (W 0.00261437) | 0.44462 ± 0.00159879 (W 0.00322118) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `solve/n257/b1` | 0.432586 ± 0.00335895 (W 0.00251573) | 0.446501 ± 0.00210066 (W 0.00367797) | · |  |
| `solve/n511/b1` | 3.29536 ± 0.61415 (W 0.00772474) | 1.73905 ± 0.00657103 (W 0.00575061) | 🔴 faer-fork 1.89× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `solve/n513/b1` | 2.90051 ± 0.499645 (W 0.00467779) | 1.7565 ± 0.0115404 (W 0.00542593) | 🔴 faer-fork 1.65× slower than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_thin/n255/b1` | 10.8458 ± 0.0347165 (W 0.0198711) | 10.6797 ± 0.019012 (W 0.0163328) | · |  |
| `svd_thin/n257/b1` | 8.381 ± 0.0179702 (W 0.0129576) | 10.7809 ± 0.0210667 (W 0.0145629) | 🔵 faer-fork 1.29× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 38.989 ± 0.0975932 (W 0.0369777) | 52.4282 ± 0.300218 (W 0.0328589) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `svd_thin/n513/b1` | 34.9788 ± 0.104415 (W 0.0425746) | 53.1618 ± 0.345202 (W 0.0460239) | 🔵 faer-fork 1.52× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 5.24946 ± 0.0286697 (W 0.0085394) | 6.07667 ± 0.041038 (W 0.00558039) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `svd_values/n257/b1` | 5.05873 ± 0.0154926 (W 0.0069614) | 6.18062 ± 0.0257601 (W 0.00707602) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 22.785 ± 0.0528067 (W 0.0253663) | 35.0451 ± 0.251652 (W 0.0349655) | 🔵 faer-fork 1.54× faster than `lapack-openblas` |  |
| `svd_values/n513/b1` | 20.0225 ± 0.0377593 (W 0.0218188) | 35.6442 ± 0.370882 (W 0.0308291) | 🔵 faer-fork 1.78× faster than `lapack-openblas` |  |
| `triangular_solve/n255/b1` | 0.0147225 ± 0.000100361 (W 0.000179689) | - | - | `*` one row has no measurement here; dispatch-dominated (row under 20 us) |
| `triangular_solve/n257/b1` | 0.014888 ± 0.000581021 (W 0.000174781) | - | - | `*` one row has no measurement here; `!` between-start range over 5%; dispatch-dominated (row under 20 us) |
| `triangular_solve/n511/b1` | 0.036498 ± 0.000301543 (W 0.000442562) | - | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.037896 ± 0.000889813 (W 0.000319076) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, c64, c order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.656629 ± 0.0025359 (W 0.00326103) | 0.689748 ± 0.00354605 (W 0.00289631) | · |  |
| `cholesky/n257/b1` | 0.628882 ± 0.0104011 (W 0.00415492) | 0.679061 ± 0.00462291 (W 0.00392866) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `cholesky/n511/b1` | 2.87661 ± 0.00977755 (W 0.0101019) | 3.92857 ± 0.0070977 (W 0.0112518) | 🔵 faer-fork 1.37× faster than `lapack-openblas` |  |
| `cholesky/n513/b1` | 2.8575 ± 0.0224411 (W 0.011846) | 3.97787 ± 0.0643927 (W 0.0109096) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `eigh/n255/b1` | 8.74453 ± 0.0279201 (W 0.0119429) | 11.4652 ± 0.0430397 (W 0.0132102) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `eigh/n257/b1` | 8.70183 ± 0.038492 (W 0.00865914) | 11.7698 ± 0.0830983 (W 0.0406972) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `eigh/n511/b1` | 39.3842 ± 0.04413 (W 0.0376096) | 54.1613 ± 0.102934 (W 0.046583) | 🔵 faer-fork 1.38× faster than `lapack-openblas` |  |
| `eigh/n513/b1` | 39.9375 ± 0.0838039 (W 0.234055) | 54.6029 ± 0.652621 (W 0.0458382) | 🔵 faer-fork 1.37× faster than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 3.44336 ± 0.0226626 (W 0.0103993) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 2.07388 ± 0.00886324 (W 0.00476743) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 17.4299 ± 0.0915827 (W 0.0274966) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 11.6449 ± 0.214141 (W 0.0359341) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.28908 ± 0.00647492 (W 0.0053495) | 1.36764 ± 0.00790889 (W 0.0027429) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `lu/n257/b1` | 1.18387 ± 0.00617127 (W 0.00409406) | 1.38279 ± 0.00455268 (W 0.00370684) | 🔵 faer-fork 1.17× faster than `lapack-openblas` |  |
| `lu/n511/b1` | 6.52371 ± 0.0437249 (W 0.0138642) | 6.3962 ± 0.0400138 (W 0.0338803) | · |  |
| `lu/n513/b1` | 6.33837 ± 0.0234236 (W 0.0262657) | 6.33679 ± 0.0668715 (W 0.0161784) | · |  |
| `qr/n255/b1` | 3.24797 ± 0.00931967 (W 0.00681548) | 5.33081 ± 0.0172228 (W 0.011418) | 🔵 faer-fork 1.64× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 3.32757 ± 0.00890066 (W 0.008116) | 5.80109 ± 0.0283762 (W 0.011015) | 🔵 faer-fork 1.74× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 20.7179 ± 0.056424 (W 0.029726) | 27.1218 ± 0.17382 (W 0.0236276) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `qr/n513/b1` | 21.0726 ± 0.0151651 (W 0.0298338) | 28.4545 ± 0.141461 (W 0.0601727) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `qr_factor/n255/b1` | 1.6178 ± 0.00529445 (W 0.00544906) | 2.64063 ± 0.0141183 (W 0.00405447) | 🔵 faer-fork 1.63× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 1.68594 ± 0.0044928 (W 0.00452189) | 2.86397 ± 0.0110684 (W 0.0062867) | 🔵 faer-fork 1.70× faster than `lapack-openblas` |  |
| `qr_factor/n511/b1` | 9.43262 ± 0.0363155 (W 0.0107275) | 13.2235 ± 0.0125257 (W 0.0145545) | 🔵 faer-fork 1.40× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 9.67856 ± 0.0379511 (W 0.019199) | 14.054 ± 0.0242178 (W 0.0199154) | 🔵 faer-fork 1.45× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 1.22514 ± 0.00517482 (W 0.00389516) | 1.33377 ± 0.00347166 (W 0.00485514) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `solve/n257/b1` | 1.20385 ± 0.00535559 (W 0.00440029) | 1.36007 ± 0.00989068 (W 0.00302285) | 🔵 faer-fork 1.13× faster than `lapack-openblas` |  |
| `solve/n511/b1` | 6.39391 ± 0.0152739 (W 0.0197555) | 6.35122 ± 0.0629561 (W 0.0279537) | · |  |
| `solve/n513/b1` | 6.39488 ± 0.0268795 (W 0.0222214) | 6.43023 ± 0.120371 (W 0.0134381) | · |  |
| `svd_thin/n255/b1` | 16.4164 ± 0.0345808 (W 0.0279047) | 16.1737 ± 0.0579027 (W 0.0292323) | · |  |
| `svd_thin/n257/b1` | 13.8538 ± 0.0255218 (W 0.0147711) | 16.984 ± 0.0372529 (W 0.0172428) | 🔵 faer-fork 1.23× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 76.8077 ± 0.269225 (W 0.0789656) | 81.3488 ± 0.14516 (W 0.0750711) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `svd_thin/n513/b1` | 74.1494 ± 0.171579 (W 0.103224) | 84.3634 ± 0.275363 (W 0.263968) | 🔵 faer-fork 1.14× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 7.83855 ± 0.0280862 (W 0.0108081) | 7.99594 ± 0.0205947 (W 0.013436) | · |  |
| `svd_values/n257/b1` | 7.48491 ± 0.035002 (W 0.0150344) | 8.30082 ± 0.0350573 (W 0.012461) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 40.8374 ± 0.218091 (W 0.0450991) | 36.6676 ± 0.122256 (W 0.0433714) | 🔴 faer-fork 1.11× slower than `lapack-openblas` |  |
| `svd_values/n513/b1` | 39.0558 ± 0.138858 (W 0.193965) | 37.6209 ± 0.0854639 (W 0.0468688) | · |  |
| `triangular_solve/n255/b1` | 0.0216505 ± 0.000139856 (W 0.000114882) | - | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.0220205 ± 0.000193407 (W 0.000152959) | - | - | `*` one row has no measurement here |
| `triangular_solve/n511/b1` | 0.0549825 ± 0.00289003 (W 0.000372729) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.055343 ± 0.000843381 (W 0.000372927) | - | - | `*` one row has no measurement here |

## linalg-boundary, c64, c order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.598155 ± 0.00345356 (W 0.00302753) | 0.956031 ± 0.00244093 (W 0.00375872) | 🔵 faer-fork 1.60× faster than `lapack-openblas` |  |
| `cholesky/n257/b1` | 0.574898 ± 0.0130897 (W 0.00300823) | 0.62458 ± 0.00700109 (W 0.00237324) | 🔵 faer-fork 1.09× faster than `lapack-openblas` | `!` between-start range over 5% |
| `cholesky/n511/b1` | 2.28938 ± 0.0216331 (W 0.00878208) | 3.08891 ± 0.0171153 (W 0.00678138) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `cholesky/n513/b1` | 2.21186 ± 0.027564 (W 0.00608402) | 2.8597 ± 0.0921969 (W 0.00864689) | 🔵 faer-fork 1.29× faster than `lapack-openblas` | `!` between-start range over 5% |
| `eigh/n255/b1` | 7.71288 ± 0.0198445 (W 0.00770406) | 10.2077 ± 0.0222914 (W 0.0137862) | 🔵 faer-fork 1.32× faster than `lapack-openblas` |  |
| `eigh/n257/b1` | 7.72735 ± 0.0176918 (W 0.00655348) | 10.4741 ± 0.0273273 (W 0.0250329) | 🔵 faer-fork 1.36× faster than `lapack-openblas` |  |
| `eigh/n511/b1` | 30.3499 ± 0.0497622 (W 0.0236227) | 41.4151 ± 0.0953432 (W 0.0663651) | 🔵 faer-fork 1.36× faster than `lapack-openblas` |  |
| `eigh/n513/b1` | 30.7655 ± 0.0702561 (W 0.0516183) | 41.6867 ± 0.366647 (W 0.0589285) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 3.13176 ± 0.0235895 (W 0.00946469) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.72864 ± 0.0195907 (W 0.00610732) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 13.9976 ± 0.054114 (W 0.0404309) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 8.14115 ± 0.0492483 (W 0.0152538) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.18596 ± 0.00280464 (W 0.00314977) | 1.00948 ± 0.0102198 (W 0.00281824) | 🔴 faer-fork 1.17× slower than `lapack-openblas` |  |
| `lu/n257/b1` | 1.05991 ± 0.00591669 (W 0.00353244) | 1.01425 ± 0.00907024 (W 0.00286909) | · |  |
| `lu/n511/b1` | 5.15291 ± 0.015806 (W 0.0162799) | 4.09623 ± 0.0187925 (W 0.0292488) | 🔴 faer-fork 1.26× slower than `lapack-openblas` |  |
| `lu/n513/b1` | 4.93406 ± 0.0316024 (W 0.0173272) | 4.15087 ± 0.0160195 (W 0.0181002) | 🔴 faer-fork 1.19× slower than `lapack-openblas` |  |
| `qr/n255/b1` | 2.31257 ± 0.0116311 (W 0.00874244) | 4.81163 ± 0.0125817 (W 0.00561209) | 🔵 faer-fork 2.08× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 2.3608 ± 0.00654178 (W 0.0051463) | 5.09013 ± 0.0108803 (W 0.00538094) | 🔵 faer-fork 2.16× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 11.7535 ± 0.0563303 (W 0.0244107) | 20.6577 ± 0.107159 (W 0.0296221) | 🔵 faer-fork 1.76× faster than `lapack-openblas` |  |
| `qr/n513/b1` | 12.3394 ± 0.0839786 (W 0.0293213) | 21.1874 ± 0.0590591 (W 0.0473156) | 🔵 faer-fork 1.72× faster than `lapack-openblas` |  |
| `qr_factor/n255/b1` | 1.30537 ± 0.00473024 (W 0.00449926) | 2.37272 ± 0.00752227 (W 0.00483629) | 🔵 faer-fork 1.82× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 1.3571 ± 0.0052596 (W 0.00369263) | 2.51762 ± 0.00671943 (W 0.00508673) | 🔵 faer-fork 1.86× faster than `lapack-openblas` |  |
| `qr_factor/n511/b1` | 5.04392 ± 0.0151337 (W 0.00671113) | 10.1085 ± 0.0934899 (W 0.0234501) | 🔵 faer-fork 2.00× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 5.72129 ± 0.0155861 (W 0.013902) | 10.4677 ± 0.107779 (W 0.0350107) | 🔵 faer-fork 1.83× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 1.11371 ± 0.00493776 (W 0.00321043) | 0.98646 ± 0.0140075 (W 0.002612) | 🔴 faer-fork 1.13× slower than `lapack-openblas` |  |
| `solve/n257/b1` | 1.07448 ± 0.00834162 (W 0.00396132) | 0.992781 ± 0.0121508 (W 0.00258472) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `solve/n511/b1` | 4.99781 ± 0.0336732 (W 0.0134718) | 4.03629 ± 0.0816607 (W 0.00959553) | 🔴 faer-fork 1.24× slower than `lapack-openblas` | `!` between-start range over 5% |
| `solve/n513/b1` | 4.96496 ± 0.0364968 (W 0.0126186) | 4.18183 ± 0.0716758 (W 0.0223633) | 🔴 faer-fork 1.19× slower than `lapack-openblas` |  |
| `svd_thin/n255/b1` | 14.498 ± 0.105814 (W 0.0197031) | 14.0331 ± 0.0460867 (W 0.0248043) | · |  |
| `svd_thin/n257/b1` | 11.8115 ± 0.0831409 (W 0.0222696) | 14.7153 ± 0.0319075 (W 0.0232259) | 🔵 faer-fork 1.25× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 58.0484 ± 0.295924 (W 0.0472893) | 61.0099 ± 0.206204 (W 0.0772764) | · |  |
| `svd_thin/n513/b1` | 54.7208 ± 0.273664 (W 0.0758813) | 68.0752 ± 5.14591 (W 0.0774585) | 🔵 faer-fork 1.24× faster than `lapack-openblas` | `!` between-start range over 5%; `p` position effect over 5% |
| `svd_values/n255/b1` | 7.35978 ± 0.0189118 (W 0.0108602) | 7.36803 ± 0.0209178 (W 0.00839974) | · |  |
| `svd_values/n257/b1` | 6.99264 ± 0.0266434 (W 0.00897788) | 7.63201 ± 0.00927807 (W 0.0105168) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 33.3865 ± 0.145897 (W 0.048209) | 29.0484 ± 0.094589 (W 0.0433035) | 🔴 faer-fork 1.15× slower than `lapack-openblas` |  |
| `svd_values/n513/b1` | 31.0752 ± 0.1343 (W 0.0543897) | 29.6979 ± 0.10946 (W 0.0372971) | · |  |
| `triangular_solve/n255/b1` | 0.02135 ± 0.000169799 (W 0.000111979) | - | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.0217155 ± 9.49746e-05 (W 9.27643e-05) | - | - | `*` one row has no measurement here |
| `triangular_solve/n511/b1` | 0.049948 ± 0.00128373 (W 0.000388749) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.0501485 ± 0.000963779 (W 0.000343045) | - | - | `*` one row has no measurement here |

## linalg-boundary, c64, f order, 4T (CPU 4-7)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.654807 ± 0.00126334 (W 0.00288955) | 0.648756 ± 0.00360427 (W 0.00310362) | · |  |
| `cholesky/n257/b1` | 0.621857 ± 0.00930036 (W 0.00357663) | 0.636794 ± 0.00177875 (W 0.00240871) | · |  |
| `cholesky/n511/b1` | 2.80931 ± 0.0184594 (W 0.007216) | 3.56914 ± 0.01422 (W 0.0103493) | 🔵 faer-fork 1.27× faster than `lapack-openblas` |  |
| `cholesky/n513/b1` | 2.78363 ± 0.0209538 (W 0.00953361) | 3.57598 ± 0.0402176 (W 0.00815387) | 🔵 faer-fork 1.28× faster than `lapack-openblas` |  |
| `eigh/n255/b1` | 8.73817 ± 0.0199291 (W 0.013093) | 11.3387 ± 0.0374219 (W 0.0186659) | 🔵 faer-fork 1.30× faster than `lapack-openblas` |  |
| `eigh/n257/b1` | 8.69103 ± 0.0291844 (W 0.00722051) | 11.677 ± 0.0234448 (W 0.0129023) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `eigh/n511/b1` | 39.3463 ± 0.0518982 (W 0.0328827) | 53.29 ± 0.0932624 (W 0.0454201) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `eigh/n513/b1` | 39.8085 ± 0.0488386 (W 0.0332488) | 53.7464 ± 0.0763333 (W 0.0320262) | 🔵 faer-fork 1.35× faster than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 3.31554 ± 0.0194655 (W 0.0110406) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.9525 ± 0.0135577 (W 0.00321574) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 16.84 ± 0.0666717 (W 0.0213519) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 10.9356 ± 0.040625 (W 0.0171693) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.18644 ± 0.00500727 (W 0.00390165) | 1.25571 ± 0.00598204 (W 0.00376583) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `lu/n257/b1` | 1.0822 ± 0.00635212 (W 0.00305593) | 1.27333 ± 0.00404752 (W 0.0042844) | 🔵 faer-fork 1.18× faster than `lapack-openblas` |  |
| `lu/n511/b1` | 5.7572 ± 0.0240466 (W 0.0121496) | 5.43608 ± 0.0317322 (W 0.00607021) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `lu/n513/b1` | 5.58806 ± 0.0327335 (W 0.0153642) | 5.49341 ± 0.0250541 (W 0.00766902) | · |  |
| `qr/n255/b1` | 3.13903 ± 0.0073256 (W 0.00262539) | 5.0654 ± 0.0206103 (W 0.00675925) | 🔵 faer-fork 1.61× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 3.21767 ± 0.00392034 (W 0.00354051) | 5.52319 ± 0.0260109 (W 0.00713581) | 🔵 faer-fork 1.72× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 19.9029 ± 0.0574981 (W 0.0218949) | 25.1587 ± 0.0622724 (W 0.0294118) | 🔵 faer-fork 1.26× faster than `lapack-openblas` |  |
| `qr/n513/b1` | 20.3031 ± 0.0154394 (W 0.0179699) | 26.6013 ± 0.0967644 (W 0.0364453) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `qr_factor/n255/b1` | 1.53039 ± 0.00246099 (W 0.00333535) | 2.51947 ± 0.00627039 (W 0.00351518) | 🔵 faer-fork 1.65× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 1.57371 ± 0.00127408 (W 0.00302881) | 2.74482 ± 0.013669 (W 0.0049393) | 🔵 faer-fork 1.74× faster than `lapack-openblas` |  |
| `qr_factor/n511/b1` | 8.91522 ± 0.0314202 (W 0.0088644) | 12.3874 ± 0.0137986 (W 0.00928935) | 🔵 faer-fork 1.39× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 9.03541 ± 0.0243413 (W 0.00955584) | 13.1396 ± 0.00931398 (W 0.0156019) | 🔵 faer-fork 1.45× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 1.12143 ± 0.00884114 (W 0.0042406) | 1.24375 ± 0.00674528 (W 0.00415815) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `solve/n257/b1` | 1.09611 ± 0.00799144 (W 0.0042173) | 1.2722 ± 0.00390908 (W 0.00367077) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `solve/n511/b1` | 5.62039 ± 0.0252346 (W 0.0131872) | 5.48583 ± 0.0275962 (W 0.00669531) | · |  |
| `solve/n513/b1` | 5.61601 ± 0.0568679 (W 0.0103757) | 5.5433 ± 0.0302313 (W 0.00848441) | · |  |
| `svd_thin/n255/b1` | 16.3428 ± 0.0269403 (W 0.0297962) | 15.7706 ± 0.0250253 (W 0.0195137) | · |  |
| `svd_thin/n257/b1` | 13.7696 ± 0.0462165 (W 0.0219177) | 16.6324 ± 0.0448416 (W 0.0206123) | 🔵 faer-fork 1.21× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 76.7142 ± 0.255901 (W 0.236903) | 78.9282 ± 0.168853 (W 0.0641762) | · |  |
| `svd_thin/n513/b1` | 73.8708 ± 0.116488 (W 0.0930182) | 81.7781 ± 0.152528 (W 0.0758289) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 7.86663 ± 0.0281024 (W 0.0147476) | 7.86952 ± 0.0197026 (W 0.0137079) | · |  |
| `svd_values/n257/b1` | 7.51163 ± 0.0296319 (W 0.0145223) | 8.20418 ± 0.0337839 (W 0.00998051) | 🔵 faer-fork 1.09× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 40.7525 ± 0.218886 (W 0.253529) | 35.7093 ± 0.0616976 (W 0.0297601) | 🔴 faer-fork 1.14× slower than `lapack-openblas` |  |
| `svd_values/n513/b1` | 38.8316 ± 0.137202 (W 0.0526485) | 36.6616 ± 0.0776508 (W 0.0420767) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `triangular_solve/n255/b1` | 0.020543 ± 0.00022522 (W 0.00111126) | - | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.0211745 ± 0.000339055 (W 0.000239371) | - | - | `*` one row has no measurement here |
| `triangular_solve/n511/b1` | 0.0573515 ± 0.00232638 (W 0.000376102) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |
| `triangular_solve/n513/b1` | 0.057432 ± 0.00134611 (W 0.000494967) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

## linalg-boundary, c64, f order, 8T (CPU 4-11)

| case | faer-fork (ms) | lapack-openblas (ms) | vs `lapack-openblas` | notes |
|---|---|---|---|---|
| `cholesky/n255/b1` | 0.593268 ± 0.00192776 (W 0.00286016) | 0.91597 ± 0.00250485 (W 0.00231691) | 🔵 faer-fork 1.54× faster than `lapack-openblas` |  |
| `cholesky/n257/b1` | 0.551343 ± 0.00955149 (W 0.00280968) | 0.584591 ± 0.00243151 (W 0.00337594) | 🔵 faer-fork 1.06× faster than `lapack-openblas` |  |
| `cholesky/n511/b1` | 2.23036 ± 0.012263 (W 0.00396034) | 2.76349 ± 0.0106096 (W 0.00812984) | 🔵 faer-fork 1.24× faster than `lapack-openblas` |  |
| `cholesky/n513/b1` | 2.15266 ± 0.020626 (W 0.00473324) | 2.48954 ± 0.0437204 (W 0.00594046) | 🔵 faer-fork 1.16× faster than `lapack-openblas` |  |
| `eigh/n255/b1` | 7.71987 ± 0.00944327 (W 0.00604591) | 10.0959 ± 0.0288976 (W 0.0114858) | 🔵 faer-fork 1.31× faster than `lapack-openblas` |  |
| `eigh/n257/b1` | 7.7084 ± 0.0144551 (W 0.00461558) | 10.3614 ± 0.0182732 (W 0.0170235) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `eigh/n511/b1` | 30.3081 ± 0.0370944 (W 0.0259588) | 40.583 ± 0.0963503 (W 0.216673) | 🔵 faer-fork 1.34× faster than `lapack-openblas` |  |
| `eigh/n513/b1` | 30.7051 ± 0.0567052 (W 0.0417938) | 40.8245 ± 0.124936 (W 0.0474749) | 🔵 faer-fork 1.33× faster than `lapack-openblas` |  |
| `full_piv_lu/n255/b1` | 3.00292 ± 0.0235515 (W 0.00605646) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n257/b1` | 1.60963 ± 0.0165277 (W 0.00682431) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n511/b1` | 13.2674 ± 0.0651854 (W 0.0245605) | - | - | `*` one row has no measurement here |
| `full_piv_lu/n513/b1` | 7.37691 ± 0.0418607 (W 0.0130688) | - | - | `*` one row has no measurement here |
| `lu/n255/b1` | 1.08283 ± 0.0032329 (W 0.00458317) | 0.882009 ± 0.0149229 (W 0.00254728) | 🔴 faer-fork 1.23× slower than `lapack-openblas` |  |
| `lu/n257/b1` | 0.949341 ± 0.00568799 (W 0.00316539) | 0.895841 ± 0.00342799 (W 0.00250612) | 🔴 faer-fork 1.06× slower than `lapack-openblas` |  |
| `lu/n511/b1` | 4.38691 ± 0.0118744 (W 0.0132876) | 3.20022 ± 0.0264975 (W 0.00661931) | 🔴 faer-fork 1.37× slower than `lapack-openblas` |  |
| `lu/n513/b1` | 4.18459 ± 0.0358828 (W 0.00570079) | 3.24338 ± 0.0180372 (W 0.00818124) | 🔴 faer-fork 1.29× slower than `lapack-openblas` |  |
| `qr/n255/b1` | 2.21215 ± 0.0103274 (W 0.00561525) | 4.53785 ± 0.0221553 (W 0.00537082) | 🔵 faer-fork 2.05× faster than `lapack-openblas` |  |
| `qr/n257/b1` | 2.24947 ± 0.00928215 (W 0.00586973) | 4.82834 ± 0.0197423 (W 0.00969416) | 🔵 faer-fork 2.15× faster than `lapack-openblas` |  |
| `qr/n511/b1` | 10.8716 ± 0.0206331 (W 0.015432) | 18.735 ± 0.0278285 (W 0.0200078) | 🔵 faer-fork 1.72× faster than `lapack-openblas` |  |
| `qr/n513/b1` | 11.5675 ± 0.0305691 (W 0.0276879) | 19.5186 ± 0.119621 (W 0.0353886) | 🔵 faer-fork 1.69× faster than `lapack-openblas` |  |
| `qr_factor/n255/b1` | 1.24653 ± 0.00295703 (W 0.00332778) | 2.24864 ± 0.00621466 (W 0.00600615) | 🔵 faer-fork 1.80× faster than `lapack-openblas` |  |
| `qr_factor/n257/b1` | 1.28114 ± 0.0269157 (W 0.00486583) | 2.38691 ± 0.00414477 (W 0.00348938) | 🔵 faer-fork 1.86× faster than `lapack-openblas` | `!` between-start range over 5% |
| `qr_factor/n511/b1` | 4.73745 ± 0.0101176 (W 0.00859943) | 9.18168 ± 0.0332476 (W 0.0163992) | 🔵 faer-fork 1.94× faster than `lapack-openblas` |  |
| `qr_factor/n513/b1` | 5.29677 ± 0.0170189 (W 0.00849452) | 9.56979 ± 0.03052 (W 0.0110697) | 🔵 faer-fork 1.81× faster than `lapack-openblas` |  |
| `solve/n255/b1` | 1.01361 ± 0.00214183 (W 0.0026918) | 0.891856 ± 0.00296415 (W 0.0030503) | 🔴 faer-fork 1.14× slower than `lapack-openblas` |  |
| `solve/n257/b1` | 0.970476 ± 0.0042275 (W 0.00231111) | 0.899264 ± 0.00535828 (W 0.00316242) | 🔴 faer-fork 1.08× slower than `lapack-openblas` |  |
| `solve/n511/b1` | 4.23357 ± 0.00451345 (W 0.00741277) | 3.28388 ± 0.0137771 (W 0.00568253) | 🔴 faer-fork 1.29× slower than `lapack-openblas` |  |
| `solve/n513/b1` | 4.17924 ± 0.0118408 (W 0.00922295) | 3.29897 ± 0.0221416 (W 0.00718515) | 🔴 faer-fork 1.27× slower than `lapack-openblas` |  |
| `svd_thin/n255/b1` | 14.3806 ± 0.109446 (W 0.0149587) | 13.6446 ± 0.045442 (W 0.0322046) | 🔴 faer-fork 1.05× slower than `lapack-openblas` |  |
| `svd_thin/n257/b1` | 11.7302 ± 0.086568 (W 0.0199236) | 14.3567 ± 0.0480719 (W 0.0205331) | 🔵 faer-fork 1.22× faster than `lapack-openblas` |  |
| `svd_thin/n511/b1` | 57.9934 ± 0.18363 (W 0.0834968) | 58.5445 ± 0.155203 (W 0.0596019) | · |  |
| `svd_thin/n513/b1` | 54.5022 ± 0.296628 (W 0.119526) | 60.7538 ± 0.209681 (W 0.0763711) | 🔵 faer-fork 1.11× faster than `lapack-openblas` |  |
| `svd_values/n255/b1` | 7.37972 ± 0.0188383 (W 0.0123818) | 7.24875 ± 0.0163379 (W 0.00616706) | · |  |
| `svd_values/n257/b1` | 7.01409 ± 0.0211419 (W 0.00668583) | 7.54678 ± 0.00707324 (W 0.00805851) | 🔵 faer-fork 1.08× faster than `lapack-openblas` |  |
| `svd_values/n511/b1` | 33.0602 ± 0.186576 (W 0.0324099) | 28.1135 ± 0.0718112 (W 0.0296278) | 🔴 faer-fork 1.18× slower than `lapack-openblas` |  |
| `svd_values/n513/b1` | 30.8566 ± 0.136638 (W 0.0444854) | 28.8366 ± 0.0973577 (W 0.0296334) | 🔴 faer-fork 1.07× slower than `lapack-openblas` |  |
| `triangular_solve/n255/b1` | 0.021355 ± 0.000186699 (W 0.00124021) | - | - | `*` one row has no measurement here |
| `triangular_solve/n257/b1` | 0.02163 ± 0.000220303 (W 0.000118852) | - | - | `*` one row has no measurement here |
| `triangular_solve/n511/b1` | 0.0569215 ± 0.000881615 (W 0.000324776) | - | - | `*` one row has no measurement here |
| `triangular_solve/n513/b1` | 0.0573625 ± 0.00144809 (W 0.000499906) | - | - | `*` one row has no measurement here; `!` between-start range over 5% |

Not applicable to this population's shapes and reported as skipped: `full_piv_lu/255`, `full_piv_lu/257`, `full_piv_lu/511`, `full_piv_lu/513`, `triangular_solve/255`, `triangular_solve/257`, `triangular_solve/511`, `triangular_solve/513`.

Repeated process sets describe observed repeatability under the recorded order schedule; they are not a paired baseline/candidate experiment and do not establish equal performance between engines.

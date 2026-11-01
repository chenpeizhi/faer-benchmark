#!/usr/bin/env python3
"""Join the two vendor arms of one recording into a single browser-viewable page.

    scripts/gen_comparison.py --mkl <run dir> --openblas <run dir> --out <file.html>

One binary links one vendor library, so `faer-fork` is measured beside MKL in one
run and beside OpenBLAS in the other; `faer-upstream` is only in the MKL arm
because the three-row rotation needs three engines. This joins the two runs of
the *same* recorded revision on the cell key and prints, for every cell, what the
fork took against each baseline it was measured with.

It is a view over recorded data, not a new measurement: a cell that one arm does
not carry is shown as a dash, and the per-arm Markdown pages plus their manifests
stay authoritative for the control statement and the verification record.
"""
import argparse, csv, glob, html, pathlib, statistics, subprocess, sys
import yaml

KEY = ('regime', 'family', 'dtype', 'order', 'm', 'n', 'k', 'batch', 'threads', 'note')


def load_sets(run_dir):
    """Per-cell, per-process-set values of one arm, for the control's between-start range."""
    run = pathlib.Path(run_dir)
    cells = {}
    for path in sorted(glob.glob(str(run / 'run*.csv'))):
        with open(path) as handle:
            for row in csv.DictReader(handle):
                if row.get('status') != 'ok' or row.get('total_ms') in (None, ''):
                    continue
                cells.setdefault(tuple(row[k] for k in KEY), {}).setdefault(row['row'], []).append(
                    float(row['total_ms']))
    return cells


def control(previous_mkl, current_mkl):
    """The unchanged row between two recordings: median ratio and cells outside their range.

    `faer-upstream` is built from the same commit in both, so it is the machine-state
    control the campaign's merge rule uses; this is the same statement for a publication.
    """
    before, after = load_sets(previous_mkl), load_sets(current_mkl)
    ratios, outside, n = [], 0, 0
    for key, rows in after.items():
        cur = rows.get('faer-upstream')
        old = before.get(key, {}).get('faer-upstream')
        if not cur or not old:
            continue
        prev, now = statistics.median(old), statistics.median(cur)
        if not prev:
            continue
        n += 1
        ratios.append(now / prev)
        if not (min(old) <= now <= max(old)):
            outside += 1
    if not n:
        return None
    return {'cells': n, 'median': statistics.median(ratios), 'outside': outside}


def load(run_dir):
    run = pathlib.Path(run_dir)
    manifest = yaml.safe_load((run / 'run.yaml').read_text())
    cells = {}
    for path in sorted(glob.glob(str(run / 'run*.csv'))):
        with open(path) as handle:
            for row in csv.DictReader(handle):
                if row.get('status') != 'ok' or row.get('total_ms') in (None, ''):
                    continue
                key = tuple(row[k] for k in KEY)
                cells.setdefault(key, {})[row['row']] = float(row['total_ms'])
    return manifest, cells


def fmt(x):
    if x is None:
        return '-'
    if x >= 100:
        return f'{x:.1f}'
    if x >= 10:
        return f'{x:.2f}'
    if x >= 1:
        return f'{x:.3f}'
    return f'{x:.4g}'


def ratio(a, b):
    return a / b if a and b else None


def cls(r):
    if r is None:
        return ''
    if r <= 0.95:
        return ' class="win"'
    if r >= 1.05:
        return ' class="loss"'
    return ''


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--mkl', required=True, help='run directory of the three-engine arm')
    ap.add_argument('--openblas', required=True, help='run directory of the two-engine arm')
    ap.add_argument('--out', required=True)
    ap.add_argument('--control-mkl', help='an earlier MKL arm to state the unchanged row against')
    args = ap.parse_args(argv)

    mkl, mkl_cells = load(args.mkl)
    ctrl = control(args.control_mkl, args.mkl) if args.control_mkl else None
    ob, ob_cells = load(args.openblas)
    if mkl['library']['commit'] != ob['library']['commit']:
        sys.exit('ERROR: the two arms are not the same measured revision')
    if mkl.get('upstream', {}).get('commit') != ob.get('upstream', {}).get('commit'):
        sys.exit('ERROR: the two arms are not the same upstream revision')

    keys = sorted(set(mkl_cells) | set(ob_cells))
    rows = []
    for key in keys:
        a, b = mkl_cells.get(key, {}), ob_cells.get(key, {})
        fork_m, fork_o = a.get('faer-fork'), b.get('faer-fork')
        up, mk, obl = a.get('faer-upstream'), a.get('lapack-mkl'), b.get('lapack-openblas')
        rows.append((key, fork_m, fork_o, up, mk, obl,
                     ratio(up, fork_m), ratio(obl, fork_o), ratio(mk, fork_m)))

    # summary over the cells the MKL arm carries (that is where all four meet)
    mkl_pairs = [r for r in rows if r[1] and r[3]]
    ob_pairs = [r for r in rows if r[2] and r[6]]
    med_up = statistics.median([r[3] / r[1] for r in mkl_pairs]) if mkl_pairs else None
    med_ob = statistics.median([r[6] / r[2] for r in ob_pairs]) if ob_pairs else None

    control_html = ''
    if ctrl:
        control_html = (
            '<p class="note"><strong>Control.</strong> <code>faer-upstream</code> is the same '
            'commit in both recordings, so it measures the machine rather than the change: '
            f'between <code>{mkl["upstream"]["commit"][:12]}</code> on the previous arm and this one, '
            f'over {ctrl["cells"]} cells its median ratio is <strong>{fmt(ctrl["median"])}</strong> '
            f'and <strong>{ctrl["outside"]}</strong> cells fall outside their between-start range. '
            'The campaign\'s rule reads the median (within 2% means the machine reproduced) and '
            'reports the tail rather than refusing on it: a range taken from three process sets is '
            'narrow, so a tail of this size at these timings is expected, and it is the median that '
            'says the two recordings are comparable.</p>')

    revision = mkl['library']['commit']
    title = f"{mkl['suite_id']} on {mkl['target_profile']} - fork against upstream, OpenBLAS and MKL"
    parts = [f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
 body {{ font: 14px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif; margin: 2rem auto; max-width: 1200px; padding: 0 1rem; color: #1a1a1a; }}
 h1 {{ font-size: 1.4rem; }} h2 {{ font-size: 1.1rem; margin-top: 2rem; }}
 table {{ border-collapse: collapse; width: 100%; margin: .6rem 0 1.5rem; font-variant-numeric: tabular-nums; }}
 th, td {{ border-bottom: 1px solid #e3e3e3; padding: .25rem .4rem; text-align: right; white-space: nowrap; }}
 th {{ background: #f5f5f5; font-weight: 600; position: sticky; top: 0; }}
 td.k, th.k {{ text-align: left; }}
 td.win {{ background: #e7f6e7; }} td.loss {{ background: #fbe9e9; }}
 .note {{ color: #555; max-width: 70rem; }} code {{ background: #f2f2f2; padding: 0 .2rem; }}
</style></head><body>
<h1>{html.escape(title)}</h1>
<p class="note">Every cell below was measured in one binary beside one vendor library. The
<code>faer-fork</code> column is the measured revision; <code>faer-upstream</code> is the same
upstream commit built into the MKL arm as the unchanged row; <code>lapack-openblas</code> and
<code>lapack-mkl</code> are the vendor arms from their own runs. Times are milliseconds, the
recorded median of five calls after 250 ms of untimed priming. Ratios are <em>baseline over fork</em>,
so above 1.00 the fork is faster; the cells outside 0.95-1.05 are tinted.</p>
<ul>
 <li>measured revision: <code>{revision}</code> ({html.escape(str(mkl['library'].get('version')))})</li>
 <li>upstream: <code>{mkl['upstream']['commit']}</code> ({html.escape(str(mkl['upstream'].get('ref')))})</li>
 <li>MKL: {html.escape(str(mkl['vendor'].get('name')))} {html.escape(str(mkl['vendor'].get('version')))} ({html.escape(str(mkl['vendor'].get('linkage')))})</li>
 <li>OpenBLAS: {html.escape(str(ob['vendor'].get('name')))} {html.escape(str(ob['vendor'].get('version')))} ({html.escape(str(ob['vendor'].get('linkage')))})</li>
 <li>hardware profile: <code>{mkl['target_profile']}</code>; measured CPUs {html.escape(str(mkl['threads']['cpu_sets']))}; observer {html.escape(str(mkl['threads']['observer'].get('affinity')))}</li>
 <lI>timing policy: v{mkl['timing_policy']['version']}, {mkl['timing_policy']['repetitions']} calls, median, priming {mkl['timing_policy']['minimum_untimed_priming_ms']} ms; guards: idle {mkl['guards']['idle_window_seconds']} s, max {mkl['guards']['max_busy_percent']}% busy, {mkl['guards']['attempts']} attempts</li>
 <li>recorded: <code>{mkl['timestamp']}</code> (MKL arm) and <code>{ob['timestamp']}</code> (OpenBLAS arm)</li>
 <li>harness <code>{mkl['harness']['commit'][:12]}</code>, toolkit <code>{mkl['toolkit']['commit'][:12]}</code></li>
</ul>
{control_html}
<p class="note">This page is a join, not a control comparison: the control statement (the unchanged
row's ratio against a baseline run) lives in each arm's own page, and the verification record in its
manifest. A dash means that arm did not carry the cell.</p>
<p class="note">Cells with a baseline row: {len(mkl_pairs)} against <code>faer-upstream</code>, {len(ob_pairs)}
against <code>lapack-openblas</code>. Median baseline/fork ratio (above 1.00 means the fork is faster): upstream {fmt(med_up)}, OpenBLAS {fmt(med_ob)}.</p>
"""]

    by_regime = {}
    for r in rows:
        by_regime.setdefault(r[0][0], []).append(r)
    for regime in sorted(by_regime):
        parts.append(f'<h2>{html.escape(regime)}</h2>\n<table>\n<thead><tr>'
                     '<th class="k">family</th><th class="k">shape</th><th>dtype</th><th>order</th><th>threads</th>'
                     '<th>fork (ms)</th><th>upstream (ms)</th><th>upstream/fork</th>'
                     '<th>OpenBLAS (ms)</th><th>OpenBLAS/fork</th><th>MKL (ms)</th><th>MKL/fork</th></tr></thead><tbody>')
        for key, fork_m, fork_o, up, mk, obl, r_up, r_ob, r_mk in sorted(
                by_regime[regime], key=lambda r: (r[0][1], r[0][2], r[0][3], int(r[0][8]) if r[0][8].isdigit() else 0, int(r[0][4]), int(r[0][5]), r[0][9])):
            shape = key[4] + 'x' + key[5] + ('x' + key[6] if key[6] not in ('', '0') else '')
            label = f' {key[9]}' if key[9] else ''
            fork = fork_m if fork_m is not None else fork_o
            parts.append(
                f'<tr><td class="k">{html.escape(key[1])}</td><td class="k">{html.escape(shape)}{html.escape(label)}</td>'
                f'<td>{key[2]}</td><td>{key[3]}</td><td>{key[8]}</td>'
                f'<td>{fmt(fork)}</td><td>{fmt(up)}</td><td{cls(r_up)}>{fmt(r_up)}</td>'
                f'<td>{fmt(obl)}</td><td{cls(r_ob)}>{fmt(r_ob)}</td>'
                f'<td>{fmt(mk)}</td><td{cls(r_mk)}>{fmt(r_mk)}</td></tr>')
        parts.append('</tbody></table>')

    parts.append('</body></html>\n')
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(parts))
    print(f'wrote {out} from {len(rows)} cells '
          f'({len(mkl_pairs)} with an upstream row, {len(ob_pairs)} with an OpenBLAS row)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

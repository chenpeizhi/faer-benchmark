#!/usr/bin/env python3
"""Write the site under `result/`: the landing page, the history, the charts and the joined view.

    python3 scripts/gen_site.py [--repo-ref main]

Nothing it writes is committed (see `.gitignore`); the Pages workflow runs it on every deploy from
the committed `data/`, `result/` and `pins/`. The landing page, the history, the HTML copy of every
result page and the charts declared in `benchmarks/campaign.yaml` (`figures:`, `trend:`) are the
toolkit's (`campaign_toolkit.site`). What is this campaign's own is the four-way view: the MKL and
OpenBLAS arms of the current `faer-kernels` pages joined on the cell key by `gen_comparison.py`,
written to `result/zen5-cpu/faer-kernels/<rev12>-comparison.html` and linked from the landing page.
"""
import argparse
import html
import pathlib
import re
import sys

from campaign_toolkit import descriptor, figures, gen_index, site
from campaign_toolkit.campaign import load

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gen_comparison  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
PIN = 'pins/t4a-faer.rev'
SUITE = 'faer-kernels'
MEASURED = '71b25ffb7ae3ce038ec25b35c91e526be41b9a63'
RELEASE = '325e482b6532624d06236ad6991a41c57b0c23d1'
UPSTREAM = '0539947ffb757a739d7e703a7d2fa0c792a909c1'
CAVEAT = ('measured at 71b25ffb, the commit immediately before the 0.28.0 release commit 325e482; '
          'the only difference is Cargo.lock and faer/Cargo.toml (threadteam 0.2.0 in the measured '
          'build, 0.3.0 as shipped, plus the version string). Single-thread numbers apply to 0.28.0 '
          'as released; multi-thread numbers carry that threadteam difference and will be '
          're-measured in the next campaign.')
LIMITATION = 'multi-thread figures include threadteam 0.2.0 and are not final for the 0.3.0 runtime.'


def release_recording_pages(found):
    """The disclosed predecessor recording, never relabelled as measured at the release pin."""
    if found['resolved'].get('library') != RELEASE or found['resolved'].get('upstream') != UPSTREAM:
        return []
    return [p for p in found['pages'] if p['library_commit'] == MEASURED
            and p['upstream_commit'] == UPSTREAM and p['profile'] == 'zen5-cpu'
            and p['suite'] in (SUITE, 'faer-kernels-large') and p['vendor'] in ('mkl', 'openblas')]


def current_arms():
    """Current arms, or the explicitly disclosed release predecessor, and the earlier MKL control."""
    descriptor.set_root(ROOT)
    found = gen_index.collect()
    current, history = gen_index.split_pages(found['pages'], found['declared'], found['resolved'])
    pages = {c['vendor']: c['page'] for c in current if c['suite'] == SUITE and c['page'] is not None}
    if not pages:
        pages = {p['vendor']: p for p in release_recording_pages(found) if p['suite'] == SUITE}
    arms = {vendor: page['run_dir'] for vendor, page in pages.items()}
    revision = pages['mkl']['commit'] if 'mkl' in pages else None
    # history is newest first; the control is the newest MKL arm of another revision
    earlier = [r for r in history if r['suite'] == SUITE and r['vendor'] == 'mkl' and r['commit'] != revision]
    control = earlier[0]['run_dir'] if earlier else None
    return arms, control


def write_comparison():
    """Write the four-way view under its measured revision; None without both arms."""
    arms, control = current_arms()
    if 'mkl' not in arms or 'openblas' not in arms:
        return None
    rev = load(arms['mkl'] / 'run.yaml')['library']['commit'][:12]
    out = ROOT / 'result' / 'zen5-cpu' / SUITE / f'{rev}-comparison.html'
    argv = ['--mkl', str(arms['mkl']), '--openblas', str(arms['openblas']), '--out', str(out)]
    if control is not None:
        argv += ['--control-mkl', str(control)]
    gen_comparison.main(argv)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-ref', default='main', help='the branch the site is published from')
    args = ap.parse_args(argv)
    index = ROOT / 'result' / 'index.html'
    comparison = write_comparison()
    extra = '''<section>
<h2>71b25ffb recording: scope and provenance</h2>
<ul>
<li>Recorded on evo (zen5-cpu), fork <code>71b25ffb7ae3ce038ec25b35c91e526be41b9a63</code>,
upstream <code>0539947ffb757a739d7e703a7d2fa0c792a909c1</code>, harness <code>eeeaa36388c515a992d5056f4211e4a6cb92ba54</code>.</li>
<li>The actual measurement toolkit was <code>74e50e8199cb2c2f07e810744a0943fc3a8c1170</code>,
not the original renderer requirements pin <code>b71624bef111ce941bddaedcce3fdb6eab40f9eb</code>;
updating the CI dependency does not change this recorded measurement identity.</li>
<li>Evo was reserved for measurement, but the recorded <code>host.role=development</code> is unchanged:
these reports retain their profile's <strong>provisional</strong> designation.</li>
<li><strong>OpenBLAS arm: Cooperlake kernel, not Zen5-optimized.</strong>
OpenBLAS 0.3.32 DYNAMIC_ARCH reported <code>vendor.corename=Cooperlake</code> on the
AMD Ryzen AI 9 HX 470 (CPU family 26, model 36). Comparisons with MKL 2026.2 describe
these builds and dispatched kernels, not a general vendor ranking on Zen5.</li>
<li>Coverage is <strong>partial</strong> relative to the complete declarations: f64/c64,
small suite at 1/4/8T and the 1024 + boundary tier at 4/8T. No n=1024 Seq was measured;
Pfaffian is not a measured family, so this is not a Pfaffian performance claim.</li>
<li>The wrong-pin partial <code>20261031T222831Z-pub-3a8edf02-20261031-mkl</code>
is preserved locally and explicitly excluded from this publication. One rejected small-OpenBLAS
8T attempt is retained in its raw archive, not counted as an accepted sample.</li>
</ul>
</section>'''
    extra += f'<p><strong>Release caveat:</strong> {html.escape(CAVEAT)}</p>\n'
    extra += f'<p><strong>Known limitation:</strong> {html.escape(LIMITATION)}</p>\n'
    recorded = release_recording_pages(gen_index.collect())
    if recorded:
        extra += '<h2>Predecessor recording at 71b25ffb (not re-measured at 325e482)</h2>\n<ul>'
        for page in recorded:
            link = pathlib.PurePosixPath(page['page']).relative_to('result').with_suffix('.html')
            label = f"{page['profile']} / {page['suite']} / {page['vendor']}"
            extra += f'<li><a href="{html.escape(str(link))}">{html.escape(label)}</a></li>'
        extra += '</ul>\n'
        runs = [(p['run_dir'], load(p['run_dir'] / 'run.yaml')) for p in recorded]
        charts = figures.throughput_figures(descriptor.current().data['figures']['throughput'], runs,
                                            index.parent / 'recordings' / '71b25ffb' / 'figures')
        extra += figures.grid_html(index.parent, charts)
    if comparison is not None:
        cells = len(re.findall(r'<tr><td class="k">', comparison.read_text()))
        rel = comparison.relative_to(index.parent)
        extra += ('<h2>The four-way view</h2>\n'
                 f'<p><a href="{rel}">The same recording against upstream, OpenBLAS and MKL in one '
                 f'table ({cells} cells)</a>, with the unchanged row\'s control in its header.</p>')
    site.write_site(index.parent, pins=[PIN], repo_ref=args.repo_ref, title='faer benchmark results',
                    intro=('Release pin and published recordings, one section per hardware profile. '
                           'The predecessor recording below retains its measured revision and '
                           'threadteam limitation; it is not a new measurement of the release.'),
                    extra_html=extra, root=ROOT)
    return 0


if __name__ == '__main__':
    sys.exit(main())

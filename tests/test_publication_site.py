"""Publication identity checks; no build or measurement is run."""
import pathlib
import re
import sys
import unittest
from unittest import mock

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import gen_site  # noqa: E402


class PublicationSiteTest(unittest.TestCase):
    def test_predecessor_is_selected_only_for_the_disclosed_release_pair(self):
        page = dict(library_commit=gen_site.MEASURED, upstream_commit=gen_site.UPSTREAM,
                    profile='zen5-cpu', suite='faer-kernels', vendor='mkl')
        resolved = dict(library=gen_site.RELEASE, upstream=gen_site.UPSTREAM)
        rejected = [dict(page, **change) for change in (
            dict(library_commit='0' * 40), dict(upstream_commit='0' * 40),
            dict(profile='zen2-cpu'), dict(suite='other'), dict(vendor='other'))]
        found = dict(pages=[page, *rejected], resolved=resolved)
        self.assertEqual(gen_site.release_recording_pages(found), [page])
        for change in (dict(library='0' * 40), dict(upstream='0' * 40)):
            with self.subTest(change=change):
                self.assertEqual(gen_site.release_recording_pages(
                    dict(found, resolved=dict(resolved, **change))), [])

    def test_comparison_filename_is_the_measured_commit_not_the_release_pin(self):
        arms = {v: pathlib.Path('/unused') / v for v in ('mkl', 'openblas')}
        with mock.patch.object(gen_site, 'current_arms', return_value=(arms, None)), \
             mock.patch.object(gen_site, 'load', return_value={'library': {'commit': gen_site.MEASURED}}), \
             mock.patch.object(gen_site.gen_comparison, 'main') as comparison:
            out = gen_site.write_comparison()
        self.assertEqual(out.name, gen_site.MEASURED[:12] + '-comparison.html')
        args = comparison.call_args.args[0]
        self.assertEqual(args[args.index('--out') + 1], str(out))

    def test_rendered_predecessor_assets_survive_site_cleanup(self):
        gen_site.descriptor.set_root(ROOT)
        recorded = gen_site.release_recording_pages(gen_site.gen_index.collect())
        if not recorded:
            self.skipTest('the disclosed release pair is not the active pin')
        self.assertEqual(gen_site.main([]), 0)
        index = (ROOT / 'result/index.html').read_text()
        self.assertIn(gen_site.CAVEAT, index)
        self.assertIn(gen_site.LIMITATION, index)
        for page in recorded:
            link = pathlib.PurePosixPath(page['page']).relative_to('result').with_suffix('.html')
            self.assertIn(f'href="{link}"', index)
            self.assertTrue((ROOT / 'result' / link).is_file())
        images = re.findall(r'<img src="([^"]+)"', index)
        self.assertTrue(any('recordings/71b25ffb/figures/' in image for image in images))
        for image in images:
            self.assertTrue((ROOT / 'result' / image).is_file(), image)

    def test_both_report_declarations_keep_the_exact_site_caveat_and_limitation(self):
        for suite in ('faer-kernels', 'faer-kernels-large'):
            with self.subTest(suite=suite):
                data = yaml.safe_load((ROOT / 'benchmarks/suites' / (suite + '.yaml')).read_text())
                self.assertIn(gen_site.CAVEAT, data['engines_doc']['faer-fork']['caveat'])
                self.assertTrue(any(gen_site.LIMITATION in s
                                    for s in data['workloads']['known_blind_spots']))


if __name__ == '__main__':
    unittest.main()

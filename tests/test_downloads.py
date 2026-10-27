import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('downloads', Path(__file__).parents[1] / 'scripts/check_downloads.py')
downloads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloads)


class Response(io.BytesIO):
    pass


class DownloadContractTests(unittest.TestCase):
    def setUp(self):
        self.payload = b'signed installer fixture'
        self.digest = hashlib.sha256(self.payload).hexdigest()
        self.release = dict(tag_name='files-stable-v1.2.3', draft=False, prerelease=False, assets=[])
        for alias, versioned in downloads.pairs('1.2.3').items():
            for name in (alias, versioned, alias + '.sha256'):
                self.release['assets'].append(dict(name=name, size=len(self.payload), digest='sha256:' + self.digest))

    def fake_request(self, url, method='GET'):
        if url.startswith(downloads.API):
            return Response(json.dumps(self.release).encode())
        name = url.rsplit('/', 1)[1]
        if name.endswith('.sha256'):
            return Response((self.digest + '  ' + name[:-7] + '\n').encode())
        return Response(self.payload)

    def test_qualification_builds_never_satisfy_stable_contract(self):
        for change in ({'draft': True}, {'prerelease': True}, {'tag_name': 'files-qualification-v1.2.3'}):
            release = copy.deepcopy(self.release)
            release.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                downloads.validate_release(release)

    def test_missing_architecture_or_checksum_fails(self):
        for asset in self.release['assets']:
            release = copy.deepcopy(self.release)
            release['assets'] = [item for item in release['assets'] if item['name'] != asset['name']]
            with self.subTest(asset=asset['name']), self.assertRaisesRegex(ValueError, 'Missing'):
                downloads.validate_release(release)

    def test_anonymous_latest_and_pinned_downloads(self):
        for tag in (None, 'files-stable-v1.2.3'):
            for verify_bytes in (False, True):
                with patch.object(downloads, 'request', side_effect=self.fake_request):
                    downloads.check(tag, verify_bytes)

    def test_corrupt_installer_fails_byte_verification(self):
        original = self.fake_request
        def corrupt(url, method='GET'):
            if url.endswith('.msi'):
                return Response(b'broken')
            return original(url, method)
        with patch.object(downloads, 'request', side_effect=corrupt), self.assertRaisesRegex(ValueError, 'mismatch'):
            downloads.check(verify_bytes=True)

    def test_alias_digest_must_match_versioned_digest(self):
        self.release['assets'][0]['digest'] = 'sha256:' + '0' * 64
        with patch.object(downloads, 'request', side_effect=self.fake_request), self.assertRaisesRegex(ValueError, 'digest'):
            downloads.check()

    def test_no_authorization_header_even_with_token_environment(self):
        response = Response(b'')
        response.url = downloads.WEB
        with patch.dict('os.environ', GH_TOKEN='unused', GITHUB_TOKEN='unused'), patch.object(downloads, 'urlopen', return_value=response) as opened:
            downloads.request(downloads.WEB)
        self.assertNotIn('Authorization', opened.call_args.args[0].headers)

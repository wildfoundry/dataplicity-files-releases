"""Check the public Files download contract without sending GitHub credentials."""
import argparse
import hashlib
import json
import re
import sys
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

REPOSITORY = 'wildfoundry/dataplicity-files-releases'
WEB = f'https://github.com/{REPOSITORY}/releases'
API = f'https://api.github.com/repos/{REPOSITORY}/releases'
HOSTS = {'github.com', 'release-assets.githubusercontent.com', 'api.github.com'}


def request(url, method='GET'):
    # Deliberately ignore GH_TOKEN/GITHUB_TOKEN: customers must not need either.
    response = urlopen(Request(url, method=method, headers={
        'User-Agent': 'Dataplicity-Files-download-check',
    }), timeout=60)
    if urlparse(response.url).scheme != 'https' or urlparse(response.url).hostname not in HOSTS:
        response.close()
        raise ValueError('Unexpected download destination')
    return response


def pairs(version):
    return {
        'Dataplicity-Files-macos-arm64.dmg': f'Dataplicity-Files-{version}-macos-arm64.dmg',
        **{f'dataplicity-files-windows-{arch}.msi': f'dataplicity-files-{version}-windows-{arch}.msi'
           for arch in ('x64', 'arm64')},
    }


def validate_release(release):
    match = re.fullmatch(r'files-stable-v(\d+\.\d+\.\d+)', release['tag_name'])
    if not match or release.get('draft') or release.get('prerelease'):
        raise ValueError('Expected a published, normal stable Files release')
    assets = {asset['name']: asset for asset in release['assets']}
    for alias, versioned in pairs(match[1]).items():
        for name in (alias, alias + '.sha256', versioned):
            if name not in assets or assets[name]['size'] <= 0:
                raise ValueError('Missing or empty public asset: ' + name)
        if assets[alias]['size'] != assets[versioned]['size']:
            raise ValueError('Alias size differs from versioned installer: ' + alias)
    return pairs(match[1]), assets


def check(tag=None, verify_bytes=False):
    endpoint = API + ('/tags/' + quote(tag, safe='') if tag else '/latest')
    try:
        with request(endpoint) as response:
            release = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            raise ValueError('No public stable release exists at ' + endpoint) from error
        raise
    names, assets = validate_release(release)
    pinned = WEB + '/download/' + quote(release['tag_name'], safe='')
    selected = pinned if tag else WEB + '/latest/download'
    for alias, versioned in names.items():
        with request(selected + '/' + alias + '.sha256') as response:
            checksum = response.read(4097).decode().strip()
        if not re.fullmatch(r'[0-9a-f]{64}  ' + re.escape(alias), checksum):
            raise ValueError('Invalid alias checksum: ' + alias)
        expected = checksum.split()[0]
        for name, url in ((alias, selected + '/' + alias), (versioned, pinned + '/' + versioned)):
            if verify_bytes:
                digest = hashlib.sha256()
                size = 0
                with request(url) as response:
                    while chunk := response.read(1024 * 1024):
                        size += len(chunk)
                        if size > assets[name]['size']:
                            raise ValueError('Download exceeds declared size: ' + name)
                        digest.update(chunk)
                if size != assets[name]['size'] or digest.hexdigest() != expected:
                    raise ValueError('Downloaded installer checksum/size mismatch: ' + name)
            else:
                if assets[name].get('digest') != 'sha256:' + expected:
                    raise ValueError('Missing or mismatched GitHub asset digest; retry with --verify-bytes: ' + name)
                with request(url, 'HEAD'):
                    pass
        print('OK ' + selected + '/' + alias)
    print('Verified release: ' + release['tag_name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', help='Check an older stable tag for manual rollback; default: latest')
    parser.add_argument('--verify-bytes', action='store_true', help='Download and hash every installer')
    args = parser.parse_args()
    try:
        check(args.tag, args.verify_bytes)
    except (ValueError, HTTPError) as error:
        sys.exit(str(error))

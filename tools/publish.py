#!/usr/bin/env python3
"""publish.py - put an app's new version in this source's catalog.

    python3 tools/publish.py path/to/<id>@<version>.tgz [--icon icon.png] [--dry-run]

What it does:
  1. checks the package: an OAP package named <id>@<x.y.z>.tgz, whose package.json names the same
     id and version, with no BMW oap-sdk inside (not ours to give; the Store makes it on the car);
  2. records it in apps.json (the app must be listed there: title, description, author, repo);
  3. writes catalog.json (MGU Store catalog, schema 2) for every app;
  4. uploads the package, the icon and catalog.json to the release named `catalog`, replacing
     the app's older package;
  5. updates the table of apps in README.md.
Then commit and push (it prints the command). Needs gh, logged in with write access to this repo.
"""
import hashlib, json, os, re, subprocess, sys, tarfile

REPO = 'jarnesence/mgu-apps'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = 'https://github.com/%s/releases/download/catalog/' % REPO


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def gh(*args, check=True):
    return subprocess.run(['gh'] + list(args), check=check, capture_output=True, text=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    icon = sys.argv[sys.argv.index('--icon') + 1] if '--icon' in sys.argv else None
    if not args: sys.exit(__doc__)
    tgz = args[0]
    m = re.match(r'^([a-z][a-z0-9_]*)@(\d+\.\d+\.\d+)\.tgz$', os.path.basename(tgz))
    if not m: sys.exit('the package must be named <id>@<x.y.z>.tgz')
    app, ver = m.group(1), m.group(2)
    with tarfile.open(tgz, 'r:gz') as t:
        names = t.getnames()
        if any('node_modules/oap-sdk' in n for n in names): sys.exit('BMW oap-sdk is inside the package: build it without (the Store makes it on the car)')
        pj = next((n for n in names if n in ('package/package.json', 'package.json')), None)
        if not pj: sys.exit('no package.json in the package')
        pkg = json.load(t.extractfile(pj))
    if pkg.get('name') != app or pkg.get('version') != ver: sys.exit('package.json says %s@%s, the file name %s@%s' % (pkg.get('name'), pkg.get('version'), app, ver))
    apps = json.load(open(os.path.join(ROOT, 'apps.json')))
    if app not in apps: sys.exit('%s is not in apps.json: add its title, description, author and repo first' % app)
    a = apps[app]
    old = a.get('artifact')
    a['version'] = ver
    a['artifact'] = {'name': os.path.basename(tgz), 'size': os.path.getsize(tgz), 'sha256': sha(tgz)}
    if icon:
        dst = os.path.join(ROOT, 'icons', app + '.png')
        if os.path.abspath(icon) != os.path.abspath(dst): open(dst, 'wb').write(open(icon, 'rb').read())
    json.dump(apps, open(os.path.join(ROOT, 'apps.json'), 'w'), indent=2); open(os.path.join(ROOT, 'apps.json'), 'a').write('\n')

    comps = []
    for aid, x in sorted(apps.items()):
        if not x.get('artifact'): continue
        c = {'id': aid, 'kind': 'app', 'title': x['title'], 'description': x['description'], 'author': x['author'], 'version': x['version'],
             'artifact': dict(x['artifact'], url=DL + x['artifact']['name']), 'uninstallable': True, 'mguHmi': x.get('mguHmi', ['ID7'])}
        ip = os.path.join(ROOT, 'icons', aid + '.png')
        if os.path.exists(ip):
            if os.path.getsize(ip) > 128 * 1024: sys.exit('icons/%s.png is over 128 KiB' % aid)
            c['icon'] = aid + '.png'; c['iconSha256'] = sha(ip)
        comps.append(c)
    cat = {'schema': 2, 'components': comps}
    json.dump(cat, open(os.path.join(ROOT, 'catalog.json'), 'w'), indent=2); open(os.path.join(ROOT, 'catalog.json'), 'a').write('\n')

    # the README's table of apps
    rows = ['| | App | Version | For | |', '|---|---|---|---|---|']
    for aid, x in sorted(apps.items()):
        if not x.get('artifact'): continue
        rows.append('| <img src="icons/%s.png" width="64"> | **[%s](https://github.com/%s)**<br>%s | %s | %s | %s |' % (
            aid, x['title'], x['repo'], x['description'], x['version'], ' · '.join({'ID7': 'iDrive 7', 'ID8': 'iDrive 8'}[h] for h in x.get('mguHmi', ['ID7'])), x.get('needs', '')))
    rp = os.path.join(ROOT, 'README.md'); r = open(rp).read()
    r = re.sub(r'(<!-- apps -->\n).*?(\n<!-- /apps -->)', lambda mm: mm.group(1) + '\n'.join(rows) + mm.group(2), r, flags=re.S)
    open(rp, 'w').write(r)
    print('catalog: %d apps; %s %s (%d KiB)' % (len(comps), app, ver, os.path.getsize(tgz) // 1024))
    if dry: return

    if gh('release', 'view', 'catalog', '--repo', REPO, check=False).returncode != 0:
        gh('release', 'create', 'catalog', '--repo', REPO, '--title', 'catalog', '--notes',
           'The MGU Store reads this release: catalog.json lists every app of this source, with the packages and icons beside it. Add the source in the Store as jarnesence/mgu-apps (Releases).')
    up = [tgz, os.path.join(ROOT, 'catalog.json')] + ([os.path.join(ROOT, 'icons', app + '.png')] if os.path.exists(os.path.join(ROOT, 'icons', app + '.png')) else [])
    gh('release', 'upload', 'catalog', '--repo', REPO, '--clobber', *up)
    if old and old.get('name') != os.path.basename(tgz):
        gh('release', 'delete-asset', 'catalog', old['name'], '--repo', REPO, '--yes', check=False)
    print('uploaded. Now: git add -A && git commit -m "%s %s" && git push' % (app, ver))


if __name__ == '__main__':
    main()

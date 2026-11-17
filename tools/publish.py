#!/usr/bin/env python3
"""publish.py - put an app's new version in this source's catalog.

    python3 tools/publish.py path/to/<id>@<version>.tgz [--icon icon.png] [--dry-run]
    python3 tools/publish.py --remove <id> [--dry-run]       take a component out of this source

Which GitHub repository this source is: source.json beside apps.json ({"repo": "owner/name"}),
else idrive-labs/mgu-apps. A private repository's catalog points at the assets' API URLs, which
the Store downloads with its token (mgu-store docs/PUBLISHING.md, "artifact"); a public one's at
their release downloads.

An entry of apps.json says what its package is:
  (default)        an OAP package built off the car (package.json inside), e.g. Sideways
  "build": "unit"  an app's source package, built on the head unit (mgu-app.json + <id>@<v>/package.json)
  "kind": "tool"   a tool kit (component.json), installed with the app that requires it; no card of its own
"texts" (by Store language: title, description) and "requires" go to the catalog as they are.

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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(ROOT, 'source.json')
REPO = json.load(open(_src))['repo'] if os.path.exists(_src) else 'idrive-labs/mgu-apps'
DL = 'https://github.com/%s/releases/download/catalog/' % REPO


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def gh(*args, check=True):
    return subprocess.run(['gh'] + list(args), check=check, capture_output=True, text=True)


def write_all(apps, url):
    """catalog.json and the page (cards, the list of apps), from apps.json; url(name) -> a package's URL"""
    comps = []
    for aid, x in sorted(apps.items()):
        if not x.get('artifact'): continue
        u = url(x['artifact']['name'])
        if u is None:
            print('  %s: its package is not in the release yet, left out of this catalog' % aid)
            continue
        c = {'id': aid, 'kind': x.get('kind', 'app'), 'title': x['title'], 'description': x['description'], 'author': x['author'], 'version': x['version'],
             'artifact': dict(x['artifact'], url=u), 'uninstallable': True, 'mguHmi': x.get('mguHmi', ['ID7'])}
        if x.get('build'): c['build'] = x['build']
        if x.get('requires'): c['requires'] = x['requires']
        if x.get('texts'): c['texts'] = x['texts']
        ip = os.path.join(ROOT, 'icons', aid + '.png')
        if os.path.exists(ip):
            if os.path.getsize(ip) > 128 * 1024: sys.exit('icons/%s.png is over 128 KiB' % aid)
            c['icon'] = aid + '.png'; c['iconSha256'] = sha(ip)
        comps.append(c)
    cat = {'schema': 2, 'components': comps}
    json.dump(cat, open(os.path.join(ROOT, 'catalog.json'), 'w'), indent=2); open(os.path.join(ROOT, 'catalog.json'), 'a').write('\n')

    # the page: the cards, and the list of apps under THE APPS
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'art.py')], check=True, capture_output=True)
    blocks = []
    for aid, x in sorted(apps.items()):
        if not x.get('artifact') or x.get('kind') == 'tool': continue   # a tool comes with its app: no card
        repo = x['repo']
        blocks.append('<a href="https://github.com/%s"><img src="art/card-%s.png" alt="%s: %s" width="100%%"></a>\n\n'
                      '<p align="center"><a href="https://github.com/%s"><b>%s</b></a> &nbsp;·&nbsp; <a href="https://github.com/%s/releases/latest">Latest release</a> &nbsp;·&nbsp; '
                      'version %s &nbsp;·&nbsp; needs %s</p>' % (repo, aid, x['title'], x.get('tagline', ''), repo, x['title'], repo, x['version'], x.get('needs', 'nothing else')))
    rp = os.path.join(ROOT, 'README.md'); r = open(rp).read()
    r = re.sub(r'(<!-- apps -->\n).*?(\n<!-- /apps -->)', lambda mm: mm.group(1) + '\n<br>\n\n'.join(blocks) + mm.group(2), r, flags=re.S)
    open(rp, 'w').write(r)
    return comps


def private():
    return gh('api', 'repos/' + REPO, '--jq', '.private').stdout.strip() == 'true'


def asset_urls():
    out = gh('api', 'repos/%s/releases/tags/catalog' % REPO, '--jq', '.assets[] | .name + " " + .url').stdout.split('\n')
    return dict(l.split(' ', 1) for l in out if l.strip())


def ensure_release():
    if gh('release', 'view', 'catalog', '--repo', REPO, check=False).returncode != 0:
        gh('release', 'create', 'catalog', '--repo', REPO, '--title', 'catalog', '--notes',
           'The MGU Store reads this release: catalog.json lists every app of this source, with the packages and icons beside it. Add the source in the Store as %s (Releases).' % REPO)


def finish(apps):
    """the final catalog (with a private repository's asset URLs) up beside the packages"""
    if private():
        urls = asset_urls()
        write_all(apps, lambda name: urls.get(name))
    gh('release', 'upload', 'catalog', '--repo', REPO, '--clobber', os.path.join(ROOT, 'catalog.json'))


def remove(app, dry):
    apps = json.load(open(os.path.join(ROOT, 'apps.json')))
    if app not in apps: sys.exit('%s is not in apps.json' % app)
    x = apps.pop(app)
    json.dump(apps, open(os.path.join(ROOT, 'apps.json'), 'w'), indent=2); open(os.path.join(ROOT, 'apps.json'), 'a').write('\n')
    for f in (os.path.join(ROOT, 'icons', app + '.png'), os.path.join(ROOT, 'art', 'card-%s.png' % app)):
        if os.path.exists(f): os.remove(f)
    comps = write_all(apps, lambda name: DL + name)
    print('catalog: %d components; %s removed' % (len(comps), app))
    if dry: return
    if x.get('artifact'):
        gh('release', 'delete-asset', 'catalog', x['artifact']['name'], '--repo', REPO, '--yes', check=False)
    gh('release', 'delete-asset', 'catalog', app + '.png', '--repo', REPO, '--yes', check=False)
    finish(apps)
    print('removed from %s. Now commit and push this folder.' % REPO)


def main():
    if '--remove' in sys.argv:
        return remove(sys.argv[sys.argv.index('--remove') + 1], '--dry-run' in sys.argv)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    icon = sys.argv[sys.argv.index('--icon') + 1] if '--icon' in sys.argv else None
    if not args: sys.exit(__doc__)
    tgz = args[0]
    m = re.match(r'^([a-z][a-z0-9_-]*)@(\d+\.\d+\.\d+)\.tgz$', os.path.basename(tgz))
    if not m: sys.exit('the package must be named <id>@<x.y.z>.tgz')
    app, ver = m.group(1), m.group(2)
    apps = json.load(open(os.path.join(ROOT, 'apps.json')))
    if app not in apps: sys.exit('%s is not in apps.json: add its title, description, author and repo first' % app)
    a = apps[app]
    with tarfile.open(tgz, 'r:gz') as t:
        names = [n[2:] if n.startswith('./') else n for n in t.getnames()]
        if any('node_modules/oap-sdk' in n for n in names): sys.exit('BMW oap-sdk is inside the package: build it without (the Store makes it on the car)')
        get = lambda n: json.load(t.extractfile(next(x for x in t.getnames() if (x[2:] if x.startswith('./') else x) == n)))
        if a.get('kind') == 'tool':
            if 'component.json' not in names: sys.exit('a tool kit has component.json at its top')
            pkg = get('component.json'); pid, pver = pkg.get('id'), pkg.get('version')
        elif a.get('build') == 'unit':
            if 'mgu-app.json' not in names: sys.exit('a source package has mgu-app.json at its top')
            man = get('mgu-app.json'); pkg = get('%s@%s/package.json' % (app, ver))
            if (man.get('id'), man.get('version')) != (app, ver): sys.exit('mgu-app.json says %s@%s' % (man.get('id'), man.get('version')))
            pid, pver = pkg.get('name'), pkg.get('version')
        else:
            pj = next((n for n in names if n in ('package/package.json', 'package.json')), None)
            if not pj: sys.exit('no package.json in the package')
            pkg = get(pj); pid, pver = pkg.get('name'), pkg.get('version')
    if pid != app or pver != ver: sys.exit('the package says %s@%s, the file name %s@%s' % (pid, pver, app, ver))
    old = a.get('artifact')
    a['version'] = ver
    a['artifact'] = {'name': os.path.basename(tgz), 'size': os.path.getsize(tgz), 'sha256': sha(tgz)}
    if icon:
        dst = os.path.join(ROOT, 'icons', app + '.png')
        if os.path.abspath(icon) != os.path.abspath(dst): open(dst, 'wb').write(open(icon, 'rb').read())
    json.dump(apps, open(os.path.join(ROOT, 'apps.json'), 'w'), indent=2); open(os.path.join(ROOT, 'apps.json'), 'a').write('\n')

    comps = write_all(apps, lambda name: DL + name)
    print('catalog: %d components; %s %s (%d KiB)' % (len(comps), app, ver, os.path.getsize(tgz) // 1024))
    if dry: return

    ensure_release()
    up = [tgz] + ([os.path.join(ROOT, 'icons', app + '.png')] if os.path.exists(os.path.join(ROOT, 'icons', app + '.png')) else [])
    gh('release', 'upload', 'catalog', '--repo', REPO, '--clobber', *up)
    if old and old.get('name') != os.path.basename(tgz):
        gh('release', 'delete-asset', 'catalog', old['name'], '--repo', REPO, '--yes', check=False)
    finish(apps)
    print('uploaded. Now: git add -A && git commit -m "%s %s" && git push' % (app, ver))


if __name__ == '__main__':
    main()

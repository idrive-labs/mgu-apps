<p align="center">
  <img src="art/banner-m.jpg" alt="iDrive Labs: BMW iDrive 7 & 8 telemetry and MGU apps" width="100%">
</p>

<p align="center">
  <img alt="iDrive 7 and 8" src="https://img.shields.io/badge/iDrive-7%20%26%208-009ADA?style=for-the-badge&labelColor=1a1d26">
  <img alt="MGU Store source" src="https://img.shields.io/badge/MGU%20Store-source-003399?style=for-the-badge&labelColor=1a1d26">
  <img alt="Free" src="https://img.shields.io/badge/apps-free-E11B22?style=for-the-badge&labelColor=1a1d26">
</p>

<p align="center"><b>Apps for the centre display of your BMW.</b> Add this source to the MGU Store once,<br>and every app from it installs and updates right from the car.</p>

<img src="art/h-add.png" alt="Add the source" width="100%">

<img src="art/steps.png" alt="1 Open the Store: Settings, Add source. 2 Add idrive-labs/mgu-apps, Releases. 3 Install." width="100%">

The source to type in the Store:

```
idrive-labs/mgu-apps
```

You need a BMW with an **iDrive 7 (MGU)** or **iDrive 8** head unit, with root access and the
[MGU Store](https://github.com/robertnisipeanu/mgu-store). Everything an app needs comes with it.

<img src="art/h-apps.png" alt="The apps" width="100%">

<!-- apps -->
<a href="https://github.com/idrive-labs/sideways"><img src="art/card-sideways.png" alt="Sideways: Drift telemetry on your centre display" width="100%"></a>

<p align="center"><a href="https://github.com/idrive-labs/sideways"><b>Sideways</b></a> &nbsp;·&nbsp; <a href="https://github.com/idrive-labs/sideways/releases/latest">Latest release</a> &nbsp;·&nbsp; version 0.6.6 &nbsp;·&nbsp; needs internet for the leaderboard</p>
<!-- /apps -->

> [!WARNING]
> Unofficial apps, not affiliated with or endorsed by BMW AG.

<details>
<summary>For the author: publishing a version</summary>

Each app is built in its own repository into an OAP package, `<id>@<version>.tgz`. A new app gets
an entry in `apps.json` first: title, tagline, description, author, repository, the head units it
is for (`mguHmi`), what it needs, the Store components it requires (`requires`), and a preview image in `previews/`. Then:

```sh
python3 tools/publish.py path/to/<id>@<version>.tgz --icon path/to/icon.png
git add -A && git commit -m "<id> <version>" && git push
```

`publish.py` checks the package, writes `catalog.json`, uploads the package, the icon and the
catalog to the `catalog` release (what the Store reads), draws the cards (`tools/art.py`) and
fills in the list of apps above.
</details>

---

<p align="center">
  <sub>Built for fun by <a href="https://github.com/jarnesence">Járn</a> · <a href="https://github.com/idrive-labs">iDrive Labs</a> · Unofficial hobby project, not affiliated with BMW AG.</sub>
</p>

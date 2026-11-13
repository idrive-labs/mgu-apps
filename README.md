<p align="center">
  <img src="icons/sideways.png" width="84" alt="">
</p>

<h1 align="center">jarnesence · apps for BMW iDrive 7 & 8</h1>

<p align="center">
  An app source for the <a href="https://github.com/robertnisipeanu/mgu-store">MGU Store</a>.<br>
  Add it once, and every app here installs and updates from your car.
</p>

## Add this source to your car

1. Open the **MGU Store** on the head unit.
2. **Settings → Add source**, type **`jarnesence/mgu-apps`**, and choose **Releases**.
3. The apps below appear in the Store. Install the ones you want.

New apps and updates show up in the Store by themselves.

> [!NOTE]
> You need a BMW with an iDrive 7 (MGU) or iDrive 8 head unit, with root access and the MGU
> Store. Apps that draw on the screen need a renderer (**mgu-render**, from the Store's default
> sources).

## Apps

<!-- apps -->
| | App | Version | For | |
|---|---|---|---|---|
| <img src="icons/sideways.png" width="64"> | **[Sideways](https://github.com/jarnesence/sideways)**<br>Drift telemetry: live drift angle, chained drift scoring, replays with a freestyle camera, video export to your phone and a worldwide leaderboard. | 0.6.4 | iDrive 7 · iDrive 8 | a renderer (mgu-render); internet for the leaderboard |
<!-- /apps -->

## For the author: publishing a version

Each app lives in its own repository and builds its OAP package there (for Sideways:
`tools/release.sh`, which writes `dist/release/sideways@<version>.tgz`). Then, here:

```sh
python3 tools/publish.py ../idrive-drift/dist/release/sideways@0.6.4.tgz --icon ../idrive-drift/platform/icon.png
git add -A && git commit -m "sideways 0.6.4" && git push
```

`publish.py` checks the package: its name and version must match, and BMW's oap-sdk must not be
inside (the Store makes it on the car from a stock app). It then writes `catalog.json`, uploads
the package, its icon and the catalog to the release named `catalog` (which is what the Store
reads), and updates the table above. A new app gets an entry in `apps.json` first: its title,
description, author, repository, the head units it is for (`mguHmi`) and what it needs.

Unofficial, not affiliated with or endorsed by BMW AG.

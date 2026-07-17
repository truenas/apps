# GitLab

[GitLab](https://about.gitlab.com) is a self-hosted Git repository manager with CI/CD,
Container Registry, and Pages. Packaged via the
[sameersbn/docker-gitlab](https://github.com/sameersbn/docker-gitlab) image, which runs
GitLab as non-root (root start + `USERMAP` remap to 568) across separate containers
(gitlab + postgres + redis, plus an optional `registry:2` container for the Container
Registry). Configuration is done through environment variables.

## amd64 only

The `sameersbn/gitlab` image is built for **linux/amd64 only** — it will not run on arm64
TrueNAS hosts. This is the trade-off for the non-root, multi-container packaging.

## Initial root password

On first boot the root password is taken from the **Initial Root Password** field if set;
otherwise GitLab generates a random one. Change it after first login.

## Upgrading — do not skip versions

GitLab does not allow skipping milestone versions; jumping e.g. 17.x straight to 19.x
can corrupt your data. Upgrade one milestone at a time. The catalog keeps the last version
of each milestone line available (`to_keep_versions.yaml`); if you fall behind, install
the kept milestone first, then step forward. Full paths:
https://docs.gitlab.com/update/upgrade_paths/
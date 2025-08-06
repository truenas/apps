module.exports = {
  extends: [],
  // https://docs.renovatebot.com/self-hosted-configuration/#dryrun
  dryRun: null,
  // https://docs.renovatebot.com/configuration-options/#gitauthor
  gitAuthor: "bugclerk <bugclerk@ixsystems.com>",
  // https://docs.renovatebot.com/self-hosted-configuration/#onboarding
  onboarding: false,
  // https://docs.renovatebot.com/configuration-options/#dependencydashboard
  dependencyDashboard: true,
  // https://docs.renovatebot.com/self-hosted-configuration/#platform
  platform: "github",
  // https://docs.renovatebot.com/self-hosted-configuration/#repositories
  repositories: ["truenas/apps"],
  // https://docs.renovatebot.com/self-hosted-configuration/#allowpostupgradecommandtemplating
  allowPostUpgradeCommandTemplating: true,
  // https://docs.renovatebot.com/self-hosted-configuration/#allowedpostupgradecommands
  // TODO: Restrict this.
  allowedPostUpgradeCommands: ["^.*"],
  enabledManagers: ["custom.regex", "github-actions"],
  customManagers: [
    {
      customType: "regex",
      // Match only ix_values.yaml files in the ix-dev directory
      fileMatch: ["^ix-dev/.*/ix_values\\.yaml$"],
      // Matches the repository name and the tag of each image
      matchStrings: [
        '\\s{4}repository: (?<depName>[^\\s]+)\\n\\s{4}tag: "?(?<currentValue>[^\\s"]+)"?',
      ],
      // Use the docker datasource on matched images
      datasourceTemplate: "docker",
    },
  ],
  packageRules: [
    {
      matchManagers: ["custom.regex"],
      matchDatasources: ["docker"],
      postUpgradeTasks: {
        // What to "git add" after the commands are run
        fileFilters: [
          "ix-dev/**/app.yaml", // For the version update
          "ix-dev/**/templates/**", // For the app lib versioned dir
        ],
        // Execute the following commands for every dep.
        executionMode: "update",
        commands: [
          // https://docs.renovatebot.com/templates/#other-available-fields
          "./.github/scripts/renovate_bump.sh {{{packageFileDir}}} patch {{{depName}}} {{{newVersion}}}",
        ],
      },
    },
    {
      matchManagers: ["github-actions"],
      addLabels: ["actions"],
      groupName: "gh-actions",
      additionalBranchPrefix: "gh-actions",
    },
    {
      matchDatasources: ["docker"],
      matchUpdateTypes: ["major"],
      labels: ["major"],
    },
    {
      matchDatasources: ["docker"],
      matchUpdateTypes: ["minor"],
      groupName: "updates-patch-minor",
      labels: ["minor"],
    },
    {
      matchDatasources: ["docker"],
      matchUpdateTypes: ["patch"],
      groupName: "updates-patch-minor",
      labels: ["patch"],
    },
    {
      matchDatasources: ["docker"],
      labels: ["enterprise"],
      groupName: "enterprise",
      matchFileNames: ["ix-dev/enterprise/**"],
    },
    // Custom versioning matching
    // https://docs.renovatebot.com/modules/versioning/regex/#rangesconstraints
    customVersioning(
      // There are tags with date format (24.08.0), but newer versions are semver
      // We still limit major to 1 digit, as we don't want to match "24.08.0" as a major version
      // This is something that we need to investigate if one of the images start having 2 digit major versions
      "^(?<major>\\d{1})\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      [
        "ghcr.io/linuxserver/deluge",
        "ghcr.io/linuxserver/heimdall",
        "ghcr.io/linuxserver/transmission",
      ]
    ),
    customVersioning(
      // 1.16.1 - There are some tags like 1.120.20221218 that are not semver and are too old
      "^(?<major>\\d{1})\\.(?<minor>\\d{2})\\.(?<patch>\\d+)$",
      ["ghcr.io/linuxserver/kasm"]
    ),
    customVersioning(
      // The current major version is 2.x.x, but there is a random 5.x.x tag.
      // So we limit it to 0-4 for major. Date issue mentioned above still stands
      "^(?<major>[0-4]{1})\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["ghcr.io/linuxserver/diskover", "ghcr.io/linuxserver/calibre-web"]
    ),
    customVersioning(
      "^(?<build>[a-z0-9]+)-ls(?<major>\\d{1})(?<minor>\\d{1})(?<patch>\\d{1})$",
      ["ghcr.io/linuxserver/tvheadend"]
    ),
    customVersioning(
      // v0.8.1-omnibus
      "^v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-omnibus$",
      ["ghcr.io/analogj/scrutiny"]
    ),
    customVersioning(
      // 1.40.2.8395-c67dce28e
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)\\.(?<build>[a-z0-9-]+)$",
      ["plexinc/pms-docker"]
    ),
    customVersioning(
      // Older versions was 20220101 and newer versions are 240101
      "^(?<major>\\d{2})(?<minor>\\d{2})(?<patch>\\d{2})$",
      ["photoprism/photoprism"]
    ),
    customVersioning(
      // RELEASE.2024-08-26T15-33-07Z
      "^RELEASE\\.(?<major>\\d+)-(?<minor>\\d+)-(?<patch>\\d+)T\\d+-\\d+-\\d+Z$",
      ["minio/minio"]
    ),
    customVersioning(
      // version-6.0.0
      "^version-(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["fireflyiii/core", "fireflyiii/data-importer"]
    ),
    customVersioning(
      // 2024-08-29
      "^(?<major>\\d+)-(?<minor>\\d+)-(?<patch>\\d+)$",
      ["alexta69/metube"]
    ),
    customVersioning(
      // 2.462.1-jdk17
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-jdk17$",
      ["jenkins/jenkins"]
    ),
    customVersioning(
      // 1d42f9ac3-v1.68.2-go1.18.8
      "^[a-z0-9]{9}-v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-go\\d+\\.\\d+\\.\\d+$",
      ["storjlabs/storagenode"]
    ),
    customVersioning(
      // 1.2.3.4, but not 1.2.0.4 (3rd digit 0 equals beta)
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>[1-9]\\d*)\\.(?<build>\\d+)$",
      ["emby/embyserver"]
    ),
    customVersioning(
      // 2023.12.31-3535377c9
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-.+$",
      ["searxng/searxng"]
    ),
    customVersioning(
      // tailscale considers beta releases when minor part ends with an odd number
      "^v(?<major>\\d+)\\.(?<minor>\\d+[02468]+)\\.(?<patch>\\d+)$",
      ["ghcr.io/tailscale/tailscale"]
    ),
    customVersioning(
      // 3.0.0.0-full
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)\\.(?<build>\\d+)-full$",
      ["apache/tika"]
    ),
    customVersioning(
      // 2.0.0-beta.1
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-beta\\.(?<build>\\d+)$",
      ["ghcr.io/louislam/uptime-kuma"]
    ),
    customVersioning(
      // postgresql-v2.15.1
      "^postgresql-v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["ghcr.io/umami-software/umami"]
    ),
    customVersioning(
      // 20250122_091948  {year}{month}{day}_{build}
      "^(?<major>\\d{4})(?<minor>\\d{2})(?<patch>\\d{2})_(?<build>\\d+)$",
      ["ghcr.io/nextcloud-releases/aio-imaginary"]
    ),
    customVersioning(
      // 2024.10.22-7ca5933
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-(?<build>.+)$",
      ["ghcr.io/corentinth/it-tools"]
    ),
    customVersioning(
      // 2.5.x -- Yes x is exact value and not a placeholder
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.x$",
      ["uroni/urbackup-server"]
    ),
    customVersioning(
      // 1.1.11-1 or 1.1.11
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)(-(?<build>\\d+))?$",
      ["rustdesk/rustdesk-server"]
    ),
    customVersioning(
      // 9.0.2-stable
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-stable$",
      ["lmscommunity/lyrionmusicserver"]
    ),
    customVersioning(
      // 2.1.0.3-beta
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)\\.(?<build>\\d+)-stable$",
      ["duplicati/duplicati"]
    ),
    customVersioning(
      // 18.0-20250218
      "^(?<major>\\d+)\\.(?<minor>\\d+)-(?<patch>\\d+)$",
      ["odoo/odoo"]
    ),
    customVersioning(
      // 1.0.0-hash
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-(?<build>.+)$",
      ["ixsystems/nextcloud-notify-push"]
    ),
    customVersioning(
      // 1.0.0-fpm-hash
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-fpm-(?<build>.+)$",
      ["ixsystems/nextcloud-fpm"]
    ),
    customVersioning(
      // v0.137.0-noble-lite
      "^v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-noble-(?<compatibility>full|nvidia|lite)$",
      ["ghcr.io/koush/scrypted"]
    ),
    customVersioning(
      // 24.7
      "^v(?<major>\\d+)\\.(?<minor>\\d+)$",
      ["nzbgetcom/nzbget"]
    ),
    customVersioning(
      // tshock-1.4.4.9-5.2.0-3
      "^tshock-1\\.4\\.4\\.9-(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)(-(?<build>\\d+))?$",
      ["ryshe/terraria"]
    ),
    customVersioning(
      // 335
      "^(?<patch>\\d+)$",
      ["quay.io/cockpit/ws"]
    ),
    customVersioning(
      // 0.3_0.18
      "^(?<major>\\d+)\\.(?<minor>\\d+)_(?<patch>\\d+)\\.(?<build>\\d+)$",
      ["ghcr.io/magicgrants/monero-lws"]
    ),
    customVersioning(
      // 6.1.4.2
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)\\.(?<build>\\d+)$",
      ["ghcr.io/justarchinet/archisteamfarm"]
    ),
    customVersioning(
      // 0.1.4.2
      "^0\\.(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["ghcr.io/sassanix/warracker/main"]
    ),
    customVersioning(
      // amd64-3.3.13
      "^amd64-(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["joplin/server"]
    ),
    customVersioning(
      // v1.52.0-jammy
      "^v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-(?<build>(noble|jammy))$",
      ["mcr.microsoft.com/playwright"]
    ),
    customVersioning(
      // i2p-2.8.1
      "^i2p-(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)(-(?<build>\\d+))?$",
      ["geti2p/i2p"]
    ),
    customVersioning(
      // 0.18.0-rootless
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-rootless$",
      ["ghcr.io/sysadminsmedia/homebox"]
    ),
    customVersioning(
      // 17-3.5
      "^17-(?<major>\\d+)\\.(?<minor>\\d+)$",
      ["postgis/postgis"]
    ),
    customVersioning(
      // 2.4-dev
      "^(?<major>\\d+)\\.(?<minor>\\d+)-dev$",
      ["wger/server"]
    ),
    customVersioning(
      // 15-vectorchord0.3.0-pgvectors0.2.0
      "^15-vectorchord(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-pgvectors0.2.0$",
      ["ghcr.io/immich-app/postgres"]
    ),
    customVersioning(
      // v1.134.0(-cuda|rocm|openvino)?
      "^v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)(?:-(?<compatibility>cuda|rocm|openvino))?$",
      ["ghcr.io/immich-app/immich-machine-learning"]
    ),
    customVersioning(
      // stable-2.0.55
      "^stable-(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["factoriotools/factorio"]
    ),
    customVersioning(
      // 5.15.24.18
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)\\.(?<build>\\d+)$",
      ["mbentley/omada-controller"]
    ),
    customVersioning(
      // apache-2.37.0
      "^apache-(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["kimai/kimai2"]
    ),
  ],
};

function customVersioning(versioningRegex, packages) {
  return {
    matchDatasources: ["docker"],
    versioning: `regex:${versioningRegex}`,
    matchPackageNames: packages,
  };
}

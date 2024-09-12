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
      groupName: "enterprise",
      labels: ["enterprise"],
      matchFileNames: ["ix-dev/enterprise/**"],
    },
    // Custom versioning matching
    customVersioning(
      // There are tags with date format (24.08.0), but newer versions are semver
      "^(?<major>\\d{2})\\.(?<minor>\\d+)\\.(?<patch>\\d+)$",
      ["linuxserver/deluge", "linuxserver/diskover"]
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
      "^(?<major>\\d+)\\.(?<minor>\\d+)-jdk17",
      ["jenkins/jenkins"]
    ),
    customVersioning(
      // 1d42f9ac3-v1.68.2-go1.18.8
      "^[a-z0-9]{9}-v(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>\\d+)-go\\d+\\.\\d+\\.\\d+$",
      ["storjlabs/storagenode"]
    ),
    customVersioning(
      // 1.2.3.4, but not 1.2.0.4 (3rd digit 0 equals beta)
      "^(?<major>\\d+)\\.(?<minor>\\d+)\\.(?<patch>([1-9]\\d*))\\.(?<build>\\d+)$",
      ["emby/embyserver"]
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

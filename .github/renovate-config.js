module.exports = {
  extends: [],
  // https://docs.renovatebot.com/self-hosted-configuration/#dryrun
  dryRun: false,
  // https://docs.renovatebot.com/configuration-options/#gitauthor
  gitAuthor: "ix-bot <ix-bot@users.noreply.github.com>",
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
  enabledManagers: ["regex", "github-actions"],
  customManagers: [
    {
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
      matchManagers: ["regex"],
      matchDatasources: ["docker"],
      postUpgradeTasks: {
        // What to "git add" after the commands are run
        fileFilters: [
          "ix-dev/**/app.yaml",      // For the version update
          "ix-dev/**/templates/**",  // For the app lib versioned dir
        ],
        // Execute the following commands for every dep.
        executionMode: "update",
        commands: [
          // If the app is in the renovate.log, don't bump again.
          // TODO: change echo command to a bump version script
          "grep {{{packageFileDir}}} ./renovate.log || echo 'bumping {{{packageFileDir}}}' >> ./renovate.log",
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
  ],
};

module.exports = {
  // https://docs.renovatebot.com/self-hosted-configuration/#dryrun
  dryRun: false,
  // https://docs.renovatebot.com/configuration-options/#gitauthor
  gitAuthor: "ix-bot",
  // https://docs.renovatebot.com/self-hosted-configuration/#onboarding
  onboarding: false,
  // https://docs.renovatebot.com/self-hosted-configuration/#platform
  platform: "github",
  // https://docs.renovatebot.com/self-hosted-configuration/#repositories
  repositories: ["truenas/apps"],
  // https://docs.renovatebot.com/self-hosted-configuration/#allowpostupgradecommandtemplating
  allowPostUpgradeCommandTemplating: true,
  // https://docs.renovatebot.com/self-hosted-configuration/#allowedpostupgradecommands
  // TODO: Restrict this.
  allowedPostUpgradeCommands: ["^.*"],
  customManagers: [
    {
      fileMatch: ["^.*ix_values\\.yaml$"],
      matchStrings: [
        "\\s{4}repository: (?<depName>[^\\s]+)\\n\\s{4}tag: (?<currentValue>[^\\s]+)",
      ],
      datasourceTemplate: "docker",
    },
  ],
  packageRules: [
    {
      matchDatasources: ["docker"],
      matchUpdateTypes: ["major"],
      postUpgradeTasks: {
        fileFilters: ["**/app.yaml"],
        executionMode: "branch",
        commands: [
          "echo {{{packageFileDir}}}, {{{depName}}}, {{{currentValue}}} - {{{newValue}}}",
        ],
      },
    },
  ],
};

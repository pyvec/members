# Pyvec Members

Collects information about the activists in the Czech Python user group and dumps it into a JSON file.

## Status

Ugly proof of concept.

## Usage

-   Login to GitHub as [Pyvec Pusher](https://github.com/pyvecpusher), a shared account for automating, which is a member of both [Pyvec](https://github.com/pyvec/) and [PyLaidesCZ](https://github.com/pyladiescz) organizations
-   [Generate a GitHub token](https://github.com/settings/tokens) with `public_repo` and `read:org` scopes
-   Login to Slack as the [Pyvec Slack](http://pyvec.slack.com/) owner
-   [Create a new Slack App](https://api.slack.com/apps) with `usergroups:read`, `users:read`, and `users:read.email` permissions
-   Generate an OAuth access token for the app (install the app for the Pyvec workspace)
-   Run:

    ```shell
    $ SLACK_API_TOKEN=... GITHUB_TOKEN=... python main.py > members.json
    ```

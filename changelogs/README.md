# Changelog fragments

Every release/** branch must add at least one fragment under `fragments/`
describing its changes, then run `antsibull-changelog release` and commit
the result, checked with [antsibull-changelog](https://github.com/ansible-community/antsibull-changelog).

Note that `fragments/` won't exist until the first fragment is added - git
doesn't track empty directories, and ansible-test's own changelog sanity
test rejects anything in there that isn't a `.yml`/`.yaml` fragment (no
README allowed inside it, unlike this one).

Add a YAML file named after the change, e.g. `fragments/fix-pdu-config-diff.yml`:

```yaml
bugfixes:
  - pdu_config - include newly created PDUs in check-mode diff output.
```

Valid top-level keys: `major_changes`, `minor_changes`, `breaking_changes`,
`deprecated_features`, `removed_features`, `security_fixes`, `bugfixes`,
`known_issues`. Each is a list of one-line, user-facing descriptions.

Once your fragment is added, run `antsibull-changelog release` and commit
everything it changes: `changelogs/changelog.yml`, `CHANGELOG.rst`, and the
now-consumed fragment file(s) it deletes. Don't edit CHANGELOG.rst by hand -
release-readiness re-runs `antsibull-changelog release` and fails the build
if that produces any further changes, i.e. if this step was skipped or is
out of date.

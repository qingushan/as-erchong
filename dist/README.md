# Runtime distribution

This directory is consumed by the stable AScript bootstrap.

- Run `python tools/build_runtime_release.py` after application code or UI
  changes.
- Commit the generated `latest.json` and content-addressed ZIP.
- Push the release commit to the GitHub `runtime` branch.
- Do not edit `latest.json` or a release ZIP manually.

The loader tries jsDelivr first and GitHub Raw second. The GitHub repository
must be public for anonymous devices to download either URL.

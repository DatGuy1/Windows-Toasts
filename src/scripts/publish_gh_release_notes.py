"""
Taken from https://github.com/pytest-dev/pytest/blob/main/scripts/publish-gh-release-notes.py

Script used to publish GitHub release notes extracted from CHANGELOG.rst.

This script is meant to be executed after a successful deployment in GitHub actions.

Uses the following environment variables:

* GIT_TAG: the name of the tag of the current commit.
* GH_RELEASE_NOTES_TOKEN: a personal access token with 'repo' permissions.

  Create one at:

    https://github.com/settings/tokens

  This token should be set in a secret in the repository, which is exposed as an
  environment variable in the main.yml workflow file.

The script also requires ``pandoc`` to be previously installed in the system.

Requires Python3.6+.
"""
import os
import re
import sys
from pathlib import Path

import github3
import pypandoc


def upload_package_assets(created_release):
    dist_path = Path(__file__).parent.parent / "dist"
    for built_file in os.listdir(dist_path):
        with open(os.path.join(dist_path, built_file), "rb") as file:
            created_release.upload_asset(content_type="application/zip", name=built_file, asset=file)


def publish_github_release(slug, token, tag_name, body):
    github = github3.login(token=token)
    owner, repo = slug.split("/")
    repo = github.repository(owner, repo)
    return repo.create_release(tag_name=tag_name, body=body)


def parse_changelog(tag_name):
    p = Path(__file__).parent.parent / "CHANGELOG.rst"
    changelog_lines = p.read_text(encoding="UTF-8").splitlines()

    title_regex = re.compile(r"(\d\.\d+\.\d+) \(\d{4}-\d{2}-\d{2}\)")
    consuming_version = False
    version_lines = []
    for line in changelog_lines:
        m = title_regex.match(line)
        if m:
            # found the version we want: start to consume lines until we find the next version title
            if m.group(1) == tag_name:
                consuming_version = True
            # found a new version title while parsing the version we want: break out
            elif consuming_version:
                break
        if consuming_version:
            version_lines.append(line)

    return "\n".join(version_lines)


def convert_rst_to_md(text):
    return pypandoc.convert_text(text, "md", format="rst", extra_args=["--wrap=preserve"])


def main(argv):
    if len(argv) > 1:
        tag_name = argv[1]
    else:
        tag_name = os.environ.get("GITHUB_REF")
        if not tag_name:
            print("tag_name not given and $GITHUB_REF not set", file=sys.stderr)
            return 1
        if tag_name.startswith("refs/tags/"):
            tag_name = tag_name[len("refs/tags/"):]

    token = os.environ.get("GH_RELEASE_NOTES_TOKEN")
    if not token:
        print("GH_RELEASE_NOTES_TOKEN not set", file=sys.stderr)
        return 1

    slug = os.environ.get("GITHUB_REPOSITORY")
    if not slug:
        print("GITHUB_REPOSITORY not set", file=sys.stderr)
        return 1

    rst_body = parse_changelog(tag_name.lstrip("v"))
    md_body = convert_rst_to_md(rst_body)

    github_release = publish_github_release(slug, token, tag_name, md_body)
    if not github_release:
        print("Could not publish release notes:", file=sys.stderr)
        print(md_body, file=sys.stderr)
        return 5

    upload_package_assets(github_release)

    print()
    print(f"Release notes for {tag_name} published successfully:")
    print(f"https://github.com/{slug}/releases/tag/{tag_name}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

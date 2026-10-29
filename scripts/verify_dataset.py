#!/usr/bin/env python3
"""Verify the reference ZIP or extracted JSONL files; standard library only."""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import zipfile

DATASET = "four_communities_2026-01_v1"
ZIP_SHA256 = "c80b9cd21a09313e5cfc17c70b38111b45357aa1db0a0af77e48446ca6b49403"
START = 1767225600
END = 1769904000


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(open_file):
    with open_file("manifest.json") as stream:
        manifest = json.load(stream)
    total = 0
    for community in manifest["communities"]:
        name = community["subreddit"]
        for filename in ("submissions.jsonl", "comments.jsonl"):
            expected = community["files"][filename]
            digest = hashlib.sha256()
            count = size = 0
            ids = set()
            with open_file(name + "/" + filename) as stream:
                for line in stream:
                    digest.update(line)
                    size += len(line)
                    row = json.loads(line)
                    if row["subreddit"].lower() != name.lower():
                        raise ValueError("Unexpected subreddit in " + filename)
                    if not START <= row["created_utc"] < END:
                        raise ValueError("Timestamp outside January 2026")
                    if row["id"] in ids:
                        raise ValueError("Duplicate ID: " + row["id"])
                    ids.add(row["id"])
                    count += 1
            if (count, size, digest.hexdigest()) != (
                expected["records"], expected["bytes"], expected["sha256"]
            ):
                raise ValueError("Count, size or SHA-256 mismatch: " + name + "/" + filename)
            total += count
            print("OK", name + "/" + filename, "records=" + str(count))
    print("Verified", total, "JSONL records.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--archive", type=Path, help="Original downloaded ZIP")
    source.add_argument("--root", type=Path, help="Extracted dataset directory")
    args = parser.parse_args()
    with ExitStack() as stack:
        if args.archive:
            if sha256(args.archive) != ZIP_SHA256:
                raise ValueError("ZIP SHA-256 mismatch")
            print("OK archive SHA-256")
            archive = stack.enter_context(zipfile.ZipFile(args.archive))
            verify(lambda relative: archive.open(DATASET + "/" + relative))
        else:
            verify(lambda relative: (args.root / relative).open("rb"))


if __name__ == "__main__":
    main()

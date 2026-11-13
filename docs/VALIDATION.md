# Validation record

Verified in GitHub Actions on 13 November 2026, Ubuntu 24.04, Python 3.12, Node 24 and Chromium through Playwright 1.56.1.

The pre-publication acceptance run passed before this standalone repository was created. Current public runs: https://github.com/VarshaThondalapally/repair-scope/actions

- 101 Python tests passed, including the two actual HTTP integration tests.
- 23 Node tests passed, including ranking/score parity on 150 development queries.
- 10 browser acceptance tests passed against the built, self-contained static page.
- Browser tests downloaded and read actual CSV and JSON files; checked custom and invalid catalog uploads; blocked unknown-code selection; tested companion-work approval and override invalidation; invalidated approvals after finding/unit edits; cancelled catalog changes without losing work; and checked 390px viewport overflow.
- The original baseline hashes are unchanged. The original matcher has an explicit no-text-conversion Git attribute to preserve its original bytes across Windows and Linux.

The automated phone-width check does not establish that the interface is ideal on every device. No independent practitioner usability study or OEM/catalog validation has been performed.

Local Windows execution still cannot run socket-based HTTP/browser tests because network access is restricted. Local checks passed 99 Python tests (two skipped) and 23 Node tests. The remote acceptance run supplies the missing HTTP and browser evidence.

RepairScope is published as a standalone public repository. The included workflow repeats these checks on main before deploying. A publicly accessible hosted URL remains unverified until Pages deployment succeeds.

The synthetic benchmark remains a development regression check, not independent field accuracy. No authentic OEM catalog, dealership integration, warranty submission, or customer deployment has been validated.


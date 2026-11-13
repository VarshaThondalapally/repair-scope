param([string]$RepositoryName = "repair-scope")
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
if ($RepositoryName -notmatch '^[a-zA-Z0-9._-]+$') { throw "Invalid repository name." }
gh auth status
if ($LASTEXITCODE -ne 0) { throw "Sign in first with: gh auth login --web --git-protocol https" }
$ownerLogin = (gh api user --jq .login).Trim()
if ($LASTEXITCODE -ne 0 -or $ownerLogin -ne "VarshaThondalapally") { throw "Sign in to the expected VarshaThondalapally account." }
python tools/benchmark.py
if ($LASTEXITCODE -ne 0) { throw "Benchmark failed." }
python tools/build_web.py
if ($LASTEXITCODE -ne 0) { throw "Build failed." }
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Python tests failed." }
node --test tests/web-engine.test.mjs tests/draft.test.mjs
if ($LASTEXITCODE -ne 0) { throw "Browser engine tests failed." }
$repoFullName = "$ownerLogin/$RepositoryName"
$remoteUrl = "https://github.com/$repoFullName.git"
if (-not (Test-Path -LiteralPath ".git")) {
    git init -b main
    if ($LASTEXITCODE -ne 0) { throw "Could not initialize the local repository." }
}
gh repo view $repoFullName --json name *> $null
if ($LASTEXITCODE -ne 0) {
    gh repo create $repoFullName --public --description "Inspection findings to catalog-grounded, human-reviewed repair-order drafts. Reproducible evaluation and browser-local demo."
    if ($LASTEXITCODE -ne 0) { throw "Could not create the repository." }
}
$originUrl = git config --get remote.origin.url
if ($LASTEXITCODE -eq 0 -and $originUrl -ne $remoteUrl) { throw "Origin points to another repository; no changes were pushed." }
if (-not $originUrl) { git remote add origin $remoteUrl }
git add --all
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git -c user.name="Varsha Thondalapally" -c user.email="161989553+VarshaThondalapally@users.noreply.github.com" commit -m "Prepare reviewed inspection-to-code demo and reproducible benchmarks"
    if ($LASTEXITCODE -ne 0) { throw "Commit failed." }
}
gh auth setup-git
if ($LASTEXITCODE -ne 0) { throw "Could not configure authenticated Git." }
git push --set-upstream origin main
if ($LASTEXITCODE -ne 0) { throw "Push failed. Existing history has not been overwritten." }
gh api "repos/$repoFullName/pages" --silent 2>$null
if ($LASTEXITCODE -ne 0) {
    gh api --method POST "repos/$repoFullName/pages" -f build_type=workflow --silent
    if ($LASTEXITCODE -ne 0) { throw "Source was pushed, but Pages could not be enabled." }
}
gh workflow run pages.yml --repo $repoFullName
if ($LASTEXITCODE -ne 0) { throw "Source was pushed, but the publish workflow could not be started." }
Write-Output "Source: https://github.com/$repoFullName"
Write-Output "Track deployment: https://github.com/$repoFullName/actions"
Write-Output "The live URL is available after the deployment succeeds. It has not been verified by this script."

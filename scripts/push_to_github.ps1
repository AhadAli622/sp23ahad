<#
Push helper for LearnPath project.

Usage:
  # provide remote URL as parameter
  .\scripts\push_to_github.ps1 -RemoteUrl "https://github.com/yourname/learnpath.git"

  # or set environment variable REMOTE_URL and run without args
  $env:REMOTE_URL = "https://github.com/yourname/learnpath.git"
  .\scripts\push_to_github.ps1

Notes:
 - This script will initialize git if not present, create a simple commit, add the remote and push to the default branch (main or master).
 - You will be prompted for credentials if using HTTPS, or it will use your SSH key if the remote uses SSH.
#>

param(
    [string]$RemoteUrl
)

Set-StrictMode -Version Latest

Push-Location -LiteralPath (Resolve-Path ".." -Relative)
try {
    $repoRoot = Get-Location
    Write-Host "Repo root: $repoRoot"

    if (-not $RemoteUrl) {
        $RemoteUrl = $env:REMOTE_URL
    }

    # Initialize git if needed
    if (-not (Test-Path -Path ".git")) {
        Write-Host "Initializing new git repository..."
        git init
        # create initial commit if no commits exist
        git add -A
        git commit -m "chore: initial commit" -q
    }

    # Ensure .gitignore exists
    if (-not (Test-Path -Path ".gitignore")) {
        Write-Host "Creating .gitignore"
        @"__pycache__/
instance/learning_path.db
.venv/
"@ | Out-File -FilePath .gitignore -Encoding utf8
        git add .gitignore
        git commit -m "chore: add .gitignore" -q
    }

    # Stage any remaining changes and commit
    git add -A
    $status = git status --porcelain
    if ($status) {
        git commit -m "chore: project update" -q || Write-Host "No commit created (nothing to commit)"
    } else {
        Write-Host "No changes to commit."
    }

    if (-not $RemoteUrl) {
        Write-Host "No remote URL provided. Skipping remote add/push."
        return
    }

    # Add remote if not exists or update it
    $remotes = git remote
    if ($remotes -notcontains 'origin') {
        Write-Host "Adding remote origin -> $RemoteUrl"
        git remote add origin $RemoteUrl
    } else {
        Write-Host "Remote 'origin' exists. Setting URL to $RemoteUrl"
        git remote set-url origin $RemoteUrl
    }

    # Determine default branch name
    $branch = git rev-parse --abbrev-ref HEAD 2>$null
    if (-not $branch -or $branch -eq 'HEAD') {
        # create main branch if none
        $branch = 'main'
        git branch -M $branch
    }

    Write-Host "Pushing to origin/$branch ..."
    git push -u origin $branch
    Write-Host "Push complete."
}
finally {
    Pop-Location
}

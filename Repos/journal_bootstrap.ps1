# Self-heal for journal pipeline
$repoRoot   = 'E:\A.I. Development\Repos'
$scriptPath = Join-Path $repoRoot 'add-chapter.ps1'
$needed     = @'
param([Parameter(Mandatory=$true)][string]$Title)

$logFile = "JOURNEY_LOG.md"
$stamp   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$cwd     = (Get-Location).Path
$user    = $env:USERNAME

$entry = @"
## $Title

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection ($stamp | $cwd | $user):**
What I learned or want to remember.

---
"@

Add-Content -Path $logFile -Value $entry
Write-Host "✅ Added chapter: $Title" -ForegroundColor Green

if (Test-Path ".git") {
  $branch = "journal/" + (Get-Date -Format "yyyy-MM-dd")

  git checkout -B $branch              | Out-Null
  git add $logFile
  git commit -m "Journal: $Title"      | Out-Null
  Write-Host "📦 Committed to $branch" -ForegroundColor Cyan

  if (git rev-parse --verify main 2>$null) {
    git checkout main                  | Out-Null
    git merge --no-ff $branch -m "Merge $branch" | Out-Null
    if ((git remote) -match '^origin$') { git push origin main | Out-Null }
    git checkout $branch               | Out-Null
    Write-Host "
# ===== 0) Settings
$repoRoot   = "E:\A.I. Development\Repos"
$scriptPath = Join-Path $repoRoot "add-chapter.ps1"
$bootstrap  = Join-Path $repoRoot "journal_bootstrap.ps1"
$blockTag   = "# BEGIN JOURNAL PIPELINE"
$blockEnd   = "# END JOURNAL PIPELINE"

# ===== 1) add-chapter.ps1 content (idempotent)
$chapterScript = @'
param([Parameter(Mandatory=$true)][string]$Title)

$logFile = "JOURNEY_LOG.md"
$stamp   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$cwd     = (Get-Location).Path
$user    = $env:USERNAME

$entry = @"
## $Title

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection ($stamp | $cwd | $user):**
What I learned or want to remember.

---
"@

Add-Content -Path $logFile -Value $entry
Write-Host "✅ Added chapter: $Title" -ForegroundColor Green

if (Test-Path ".git") {
  $branch = "journal/" + (Get-Date -Format "yyyy-MM-dd")

  git checkout -B $branch              | Out-Null
  git add $logFile
  git commit -m "Journal: $Title"      | Out-Null
  Write-Host "📦 Committed to $branch" -ForegroundColor Cyan

  if (git rev-parse --verify main 2>$null) {
    git checkout main                  | Out-Null
    git merge --no-ff $branch -m "Merge $branch" | Out-Null
    if ((git remote) -match '^origin$') { git push origin main | Out-Null }
    git checkout $branch               | Out-Null
    Write-Host "🔄 Merged into main" -ForegroundColor Yellow
  }

  if ((git remote) -match '^origin$') {
    git push -u origin $branch         | Out-Null
    Write-Host "☁️  Pushed $branch"    -ForegroundColor Green
  }

  $activeBranch = (git rev-parse --abbrev-ref HEAD).Trim()
  $lastCommit   = (git rev-parse --short HEAD).Trim()
  Write-Host "📌 Branch: $activeBranch" -ForegroundColor Magenta
  Write-Host "📝 Commit: $lastCommit"   -ForegroundColor White
}

if (Get-Command code -ErrorAction SilentlyContinue) { code -g $logFile }
'@
if (-not (Test-Path $repoRoot)) { New-Item -ItemType Directory -Force -Path $repoRoot | Out-Null }
if ((-not (Test-Path $scriptPath)) -or ((Get-Content $scriptPath -Raw) -ne $needed)) {
  $needed | Set-Content -Path $scriptPath -Encoding UTF8
}
# Ensure profile block exists
$PROFILE | Out-Null

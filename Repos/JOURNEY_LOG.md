param(
  [Parameter(Mandatory=$true)][string]$Title
)

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
Write-Host "✅ Added chapter: $Title"

# Git commit flow
if (Test-Path ".git") {
  $branch = "journal/" + (Get-Date -Format "yyyy-MM-dd")
  git checkout -B $branch | Out-Null
  git add $logFile
  git commit -m "Journal: $Title" | Out-Null
  Write-Host "📦 Committed to branch $branch"
}

# Open in VS Code
if (Get-Command code -ErrorAction SilentlyContinue) {
  code -g $logFile
}
## Chapter 9 – My First Automated Commit

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:32:51 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 10 – Next Experiment

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:35:00 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 2025-09-24 – Daily Notes

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:38:28 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 2025-09-24 – Daily Notes

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:40:10 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 11 – Manual Title

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:40:11 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## new-chapter -Title "Chapter 12 – Status Check"

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:42:04 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 13 – Verification Test

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:48:18 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 2025-09-24 – Daily Notes

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 01:49:21 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 14 - Auto Profile Test

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 02:11:07 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter 2025-09-24 - Daily Notes

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 02:11:08 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---
## Chapter – Hardened pipeline test

- key accomplishment 1
- key accomplishment 2
- key accomplishment 3

**Reflection (2025-09-24 02:23:36 | E:\A.I. Development\Repos | kyleh):**
What I learned or want to remember.

---

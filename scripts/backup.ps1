# Backup models, logs, and configs
${date} = Get-Date -Format yyyyMMdd_HHmmss
$backupDir = "..\backups\backup_${date}"
New-Item -ItemType Directory -Path $backupDir
Copy-Item -Path "..\ollama\models" -Destination $backupDir -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "..\ollama\logs" -Destination $backupDir -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "..\ollama\*.json" -Destination $backupDir -ErrorAction SilentlyContinue

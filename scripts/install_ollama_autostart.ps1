# PowerShell script to add Ollama server to Windows startup
$TaskName = "OllamaServerAutoStart"
$OllamaPath = "$PSScriptRoot\..\ollama\ollama.exe"
$Action = New-ScheduledTaskAction -Execute $OllamaPath -Argument "serve"
$Trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "Auto-start Ollama server at login" -Force

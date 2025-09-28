# Watchdog to keep Ollama server running
$ollamaPath = "..\ollama\ollama.exe"
while ($true) {
    $proc = Start-Process -FilePath $ollamaPath -ArgumentList 'serve' -PassThru
    $proc.WaitForExit()
    Start-Sleep -Seconds 5
}

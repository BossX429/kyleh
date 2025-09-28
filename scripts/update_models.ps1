# Pull latest models for Ollama
$models = @('llama3.2', 'gemma3', 'mistral')
foreach ($model in $models) {
    & "..\ollama\ollama.exe" pull $model
}

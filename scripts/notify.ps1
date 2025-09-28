# Send notification (example: Slack webhook)
param([string]$Message)
$webhookUrl = "https://hooks.slack.com/services/your/webhook/url"
$payload = @{text = $Message} | ConvertTo-Json
Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $payload -ContentType 'application/json'

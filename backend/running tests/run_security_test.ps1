# Run Bandit scan
bandit -r app/ -c bandit.yml -f html -o bandit_report.html

# Run safety check for dependencies
pip install safety
safety check --full-report -o html > safety_report.html

# Open reports
Start-Process bandit_report.html
Start-Process safety_report.html

# Check for critical findings
$banditResults = Get-Content bandit_report.html -Raw
if ($banditResults -match "HIGH") {
    Write-Host "❌ Critical vulnerabilities found!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ No critical vulnerabilities detected" -ForegroundColor Green
}
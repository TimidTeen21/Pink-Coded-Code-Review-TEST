$baseUrl = "http://localhost:8000/api/v1"
$testUserId = "test_user_ps1"

function Test-TemplateEndpoint {
    param($code, $level)
    try {
        $response = irm "$baseUrl/explanations/template/$($code)?level=$($level)"
        if (-not $response.title) { throw "Invalid response format" }
        Write-Output "SUCCESS: $($code) template for $($level)"
        return $true
    } catch {
        Write-Output "ERROR: $($_.Exception.Message)"
        return $false
    }
}

function Test-FeedbackEndpoint {
    try {
        $body = @{
            user_id = $testUserId
            issue_code = "E501"
            was_helpful = $true
        } | ConvertTo-Json
        
        $response = irm "$baseUrl/feedback/explanation" -Method POST -Body $body -ContentType "application/json"
        if ($response.status -ne "received") { throw "Feedback not processed" }
        Write-Output "SUCCESS: Feedback recorded - $($response | ConvertTo-Json)"
        return $true
    } catch {
        Write-Output "ERROR: $($_.Exception.Message)"
        return $false
    }
}

# Run tests
$templateTest = Test-TemplateEndpoint -code "E501" -level "intermediate"
$feedbackTest = Test-FeedbackEndpoint

if ($templateTest -and $feedbackTest) {
    Write-Output "`n✅ ALL ENDPOINT TESTS PASSED"
} else {
    Write-Output "`n❌ SOME TESTS FAILED"
}
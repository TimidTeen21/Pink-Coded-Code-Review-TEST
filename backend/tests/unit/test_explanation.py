def test_explanation_generation():
    mock_engine = MagicMock()
    mock_engine.generate_explanation.return_value = {
        "why": "Test reason",
        "fix": "Test fix"
    }
    
    response = client.get("/api/v1/explanations?issue_code=E501&message=Test&user_id=123")
    assert response.status_code == 200
    assert "Test reason" in response.json()["why"]
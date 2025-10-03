def check_ayushman_eligibility(card_number=None):
    """
    Mock Ayushman card validation
    In real implementation, integrate with government API
    """
    if not card_number:
        return {"eligible": False, "message": "No card number provided"}
    
    # Mock validation - in real app, call government API
    card_prefix = card_number[:3] if card_number else ""
    
    # Simple mock check
    if card_prefix in ["AYU", "PMJ", "HIN"]:
        return {
            "eligible": True,
            "message": "Ayushman Bharat card is valid",
            "coverage_amount": 500000,
            "valid_until": "2025-12-31"
        }
    else:
        return {
            "eligible": False,
            "message": "Invalid or expired Ayushman card"
        }
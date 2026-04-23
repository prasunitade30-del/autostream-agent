def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Mock API function to capture a qualified lead.
    In production, this would POST to a CRM like HubSpot or Salesforce.
    """
    print("\n" + "="*50)
    print(" Lead captured SUCCESSFULLY")
    print(f"   Name     : {name}")
    print(f"   Email    : {email}")
    print(f"   Platform : {platform}")
    print("="*50 + "\n")
    return f"Lead captured successfully: {name}, {email}, {platform}"
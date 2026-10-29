from services.otp_service import clean_phone

def test_clean_phone_adds_plush_prefix():
    raw_number = "917351500283"

    result = clean_phone(raw_number)

    assert result == "+917351500283"
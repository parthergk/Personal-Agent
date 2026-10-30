import pytest
from fastapi import HTTPException
from routes.auth import register_or_send_otp, RegisterRequest

@pytest.mark.asyncio
async def test_register_reject_short_number():
    request = RegisterRequest(phone="123", name=None)

    with pytest.raises(HTTPException) as exc_info:
        await register_or_send_otp(request, db=None)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Please provide a valid phone number"

@pytest.mark.asyncio
async def test_register_reject_invalid_format():
    request = RegisterRequest(phone="+0123456789", name=None)

    with pytest.raises(HTTPException) as exc_info:
        await register_or_send_otp(request, db=None)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid phone number format. Please include country code (e.g. +91 98765 43210)."
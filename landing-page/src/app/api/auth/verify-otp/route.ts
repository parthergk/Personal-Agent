import { NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const { phone, otp, name } = body;

    if (!phone || !otp) {
      return NextResponse.json(
        { success: false, error: "Phone number and OTP code are required" },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    const backendRes = await fetch(`${BACKEND_URL}/verify-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: phone.trim(), otp: otp.trim(), name }),
      cache: "no-store",
    });

    const data = await backendRes.json().catch(() => null);

    if (!backendRes.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data?.detail || data?.message || "Invalid verification code",
        },
        { status: backendRes.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("verify-otp proxy error:", error);
    return NextResponse.json(
      {
        success: false,
        error:
          "Unable to reach the authentication service. Please ensure the backend server is running.",
      },
      { status: 503 }
    );
  }
}

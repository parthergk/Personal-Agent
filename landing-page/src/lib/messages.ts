/**
 * Centralized user-facing messages.
 *
 * All text displayed to end users should come from this file so that messages
 * remain consistent, safe, and easy to update in one place.
 *
 * Rules enforced here:
 *  - No internal URLs, server names, framework names, or IP addresses.
 *  - No raw exception messages, stack traces, or backend error strings.
 *  - No OTP values, tokens, passwords, or other secrets.
 */

// ─── OTP / Registration flow ──────────────────────────────────────────────────

export const MSG = {
  // Phone & Name step
  NAME_REQUIRED: "Please enter your name.",
  PHONE_INVALID: "Please enter a valid phone number.",

  // Sending OTP
  OTP_SEND_SUCCESS: "Verification code sent to your WhatsApp.",
  OTP_SEND_COOLDOWN_GENERIC: "Please wait before requesting a new code.",
  OTP_SEND_FAILED:
    "We couldn't send your verification code. Please try again.",
  OTP_SEND_NETWORK:
    "We're unable to verify your number right now. Please try again shortly.",

  // Verifying OTP
  OTP_INCOMPLETE: "Please enter all 6 digits.",
  OTP_INVALID:
    "The verification code you entered is incorrect. Please check it and try again.",
  OTP_EXPIRED:
    "Your verification code has expired. Please request a new one.",
  OTP_TOO_MANY_ATTEMPTS:
    "Too many incorrect attempts. Please request a new verification code.",
  OTP_VERIFY_FAILED: "We couldn't verify your code. Please try again.",
  OTP_VERIFY_NETWORK:
    "Something went wrong. Please check your connection and try again.",

  // Success
  VERIFIED_SUCCESS: "Your number has been verified successfully.",

  // Generic fallback
  UNEXPECTED: "Something went wrong. Please try again in a moment.",
} as const;

// ─── Safe API error mapper ────────────────────────────────────────────────────

/**
 * Maps known backend `detail` strings (returned by the API's structured error
 * responses) to safe, user-friendly messages.  Falls back to `fallback` for
 * any unrecognised detail so that raw technical text never reaches the UI.
 *
 * Only add entries here for detail strings that the API deliberately sends and
 * that are safe to display (after sanitisation).
 */
const KNOWN_DETAIL_MAP: Record<string, string> = {
  // /register — cooldown
  "Please wait before requesting a new code.":
    MSG.OTP_SEND_COOLDOWN_GENERIC,

  // /verify-otp — structured reasons returned via HTTP 400
  "Too many incorrect attempts. Please request a new verification code.":
    MSG.OTP_TOO_MANY_ATTEMPTS,
  "Verification code has expired. Please request a new one.": MSG.OTP_EXPIRED,
  "Invalid verification code. Please check and try again.": MSG.OTP_INVALID,

  // /register — phone validation
  "Please provide a valid phone number": MSG.PHONE_INVALID,
  "Invalid phone number format. Please include country code (e.g. +91 98765 43210).":
    "Please enter your phone number with the country code (e.g. +91 98765 43210).",

  // /verify-otp — missing fields
  "Phone number and OTP code are required": MSG.OTP_INCOMPLETE,
};

/**
 * Returns a safe user-facing error message from a parsed API response body.
 *
 * @param data     - Parsed JSON body from the API response (may be {}).
 * @param fallback - The message to show when no known mapping is found.
 */
export function safeApiError(
  data: Record<string, unknown>,
  fallback: string
): string {
  // The API returns structured errors as `detail` (FastAPI convention) or
  // `message` (our custom success/error payloads).
  const raw =
    typeof data.detail === "string"
      ? data.detail
      : typeof data.message === "string"
      ? data.message
      : null;

  if (raw && KNOWN_DETAIL_MAP[raw]) {
    return KNOWN_DETAIL_MAP[raw];
  }

  // Do not expose unknown raw strings — return the safe fallback.
  return fallback;
}

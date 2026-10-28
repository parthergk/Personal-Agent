"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import CornerBox from "@/components/CornerBox";
import { MSG, safeApiError } from "@/lib/messages";

interface Country {
  name: string;
  code: string;
  dialCode: string;
  flag: string;
  placeholder: string;
}

const COUNTRIES: Country[] = [
  { name: "India", code: "IN", dialCode: "+91", flag: "🇮🇳", placeholder: "5550 000 000" },
  { name: "United States", code: "US", dialCode: "+1", flag: "🇺🇸", placeholder: "(555) 000-0000" },
  { name: "United Kingdom", code: "GB", dialCode: "+44", flag: "🇬🇧", placeholder: "7911 123456" },
  { name: "Canada", code: "CA", dialCode: "+1", flag: "🇨🇦", placeholder: "(555) 000-0000" },
  { name: "United Arab Emirates", code: "AE", dialCode: "+971", flag: "🇦🇪", placeholder: "50 123 4567" },
  { name: "Singapore", code: "SG", dialCode: "+65", flag: "🇸🇬", placeholder: "8123 4567" },
  { name: "Germany", code: "DE", dialCode: "+49", flag: "🇩🇪", placeholder: "151 12345678" },
  { name: "Australia", code: "AU", dialCode: "+61", flag: "🇦🇺", placeholder: "412 345 678" },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WHATSAPP_BOT_NUMBER = process.env.NEXT_PUBLIC_WHATSAPP_BOT_NUMBER;

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [selectedCountry, setSelectedCountry] = useState<Country>(COUNTRIES[0]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState<"phone" | "otp" | "already_registered">("phone");
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [otpError, setOtpError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [verifiedSuccess, setVerifiedSuccess] = useState(false);
  const [cooldownSeconds, setCooldownSeconds] = useState(0);

  const fullPhoneNumber = `${selectedCountry.dialCode} ${phoneNumber.trim()}`;

  // 60-second cooldown timer for Resend code
  useEffect(() => {
    if (cooldownSeconds <= 0) return;
    const interval = setInterval(() => {
      setCooldownSeconds((prev) => Math.max(prev - 1, 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [cooldownSeconds]);

  const handleSendCode = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (cooldownSeconds > 0) return;

    setOtpError("");
    setStatusMessage("");

    const trimmedName = name.trim();
    if (!trimmedName) {
      setOtpError(MSG.NAME_REQUIRED);
      return;
    }

    const cleanNum = phoneNumber.replace(/\D/g, "");
    if (!cleanNum || cleanNum.length < 5) {
      setOtpError(MSG.PHONE_INVALID);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: fullPhoneNumber, name: trimmedName }),
      });

      const data = await response.json().catch(() => ({}));

      // Case 1: User already registered and active
      if (data.already_registered) {
        setStep("already_registered");
        return;
      }

      // Case 2: Cooldown active — show a safe, time-aware message
      if (data.cooldown) {
        const remaining = typeof data.remaining_seconds === "number" ? data.remaining_seconds : 60;
        setCooldownSeconds(remaining);
        setOtpError(
          remaining > 0
            ? `Please wait ${remaining} seconds before requesting a new code.`
            : MSG.OTP_SEND_COOLDOWN_GENERIC
        );
        return;
      }

      // Case 3: Success
      if (response.ok && data.success) {
        setStep("otp");
        setCooldownSeconds(60);
        setStatusMessage(MSG.OTP_SEND_SUCCESS);
      } else {
        setOtpError(safeApiError(data as Record<string, unknown>, MSG.OTP_SEND_FAILED));
      }
    } catch {
      setOtpError(MSG.OTP_SEND_NETWORK);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      // Handle paste
      const digits = value.replace(/\D/g, "").slice(0, 6).split("");
      const newOtp = [...otp];
      digits.forEach((d, i) => {
        if (i < 6) newOtp[i] = d;
      });
      setOtp(newOtp);
      const nextIdx = Math.min(digits.length, 5);
      const nextInput = document.getElementById(`otp-input-${nextIdx}`);
      if (nextInput) (nextInput as HTMLInputElement).focus();
      return;
    }

    const digit = value.replace(/\D/g, "");
    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);

    // Auto focus next input
    if (digit && index < 5) {
      const nextInput = document.getElementById(`otp-input-${index + 1}`);
      if (nextInput) (nextInput as HTMLInputElement).focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      const prevInput = document.getElementById(`otp-input-${index - 1}`);
      if (prevInput) (prevInput as HTMLInputElement).focus();
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    const enteredCode = otp.join("");
    if (enteredCode.length < 6) {
      setOtpError(MSG.OTP_INCOMPLETE);
      return;
    }

    setIsLoading(true);
    setOtpError("");

    try {
      const response = await fetch(`${API_BASE_URL}/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: fullPhoneNumber,
          otp: enteredCode,
          name: name.trim() || undefined,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok && data.success) {
        setVerifiedSuccess(true);
      } else {
        setOtpError(safeApiError(data as Record<string, unknown>, MSG.OTP_VERIFY_FAILED));
      }
    } catch {
      setOtpError(MSG.OTP_VERIFY_NETWORK);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <main className="relative min-h-svh w-full overflow-x-hidden bg-[#f6f4ef] text-[#171717] flex flex-col justify-between">
      {/* ─── TOP NAVIGATION ─── */}
      <header className="w-full max-w-[1360px] mx-auto px-5 sm:px-12 pt-6 sm:pt-10 flex items-center justify-between text-[11px] sm:text-xs font-mono tracking-[0.16em] sm:tracking-[0.25em] font-medium uppercase z-20">
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="group relative inline-flex items-center gap-2 select-none"
          >
            {/* VXYAK with selection box */}
            <span className="relative inline-flex items-center justify-center px-1.5 py-0.5">
              <span>VXYAK</span>
              <CornerBox hoverOnly dimension="58 x 15" />
            </span>

            {/* Subtitle */}
            <span className="text-neutral-500 font-normal tracking-[0.16em] sm:tracking-[0.25em]">
              / AGENT
            </span>
          </Link>
        </div>

        <nav className="flex items-center gap-5 sm:gap-12">
          <Link
            href="/"
            className="group relative inline-flex items-center justify-center px-1.5 py-0.5 select-none"
          >
            <span>HOME</span>
            <CornerBox hoverOnly dimension="52 x 15" />
          </Link>
        </nav>
      </header>

      {/* ─── CENTER AUTH CONTAINER ─── */}
      <section className="relative w-full max-w-[540px] mx-auto px-5 sm:px-8 py-16 sm:py-24 flex flex-col items-center justify-center text-center">
        {step === "phone" ? (
          <div className="w-full flex flex-col items-center">
            {/* Heading */}
            <h1 className="font-serif text-4xl sm:text-5xl font-normal leading-tight tracking-tight text-[#171717]">
              Register in to Vxyak
            </h1>

            {/* Subheading */}
            <p className="mt-3 font-mono text-xs sm:text-[13px] tracking-wide text-neutral-600">
              Enter your name and phone number to receive an OTP.
            </p>

            {/* Form */}
            <form onSubmit={handleSendCode} className="w-full max-w-[390px] mt-8 flex flex-col items-center">
              {/* Name input */}
              <div className="relative w-full mb-3">
                <div className="flex items-center h-11 w-full bg-white border border-neutral-300 px-3 shadow-xs focus-within:border-[#171717] focus-within:ring-1 focus-within:ring-[#171717] transition-all">
                  <input
                    type="text"
                    id="name-input"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                    autoComplete="name"
                    className="w-full bg-transparent font-mono text-xs sm:text-[13px] tracking-wider text-[#171717] outline-none placeholder:text-neutral-400"
                    autoFocus
                    required
                  />
                </div>
              </div>

              {/* Phone input with country selector */}
              <div className="relative w-full">
                <div className="flex items-center h-11 w-full bg-white border border-neutral-300 px-3 shadow-xs focus-within:border-[#171717] focus-within:ring-1 focus-within:ring-[#171717] transition-all">
                  {/* Country dropdown trigger */}
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                      className="flex items-center gap-1.5 cursor-pointer py-0.5 px-1 hover:bg-neutral-100 transition-colors select-none"
                      aria-label="Select Country"
                    >
                      <span className="text-lg leading-none" role="img" aria-label={selectedCountry.name}>
                        {selectedCountry.flag}
                      </span>
                      <svg
                        className={`w-3.5 h-3.5 text-neutral-600 transition-transform ${
                          isDropdownOpen ? "rotate-180" : ""
                        }`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {/* Country select popover */}
                    {isDropdownOpen && (
                      <div className="absolute top-full left-0 mt-2 w-64 bg-white border border-neutral-200 shadow-lg py-1.5 z-50 text-left max-h-60 overflow-y-auto">
                        {COUNTRIES.map((country) => (
                          <button
                            key={country.code}
                            type="button"
                            onClick={() => {
                              setSelectedCountry(country);
                              setIsDropdownOpen(false);
                            }}
                            className={`w-full px-3 py-2 text-xs font-mono flex items-center justify-between hover:bg-neutral-100 transition-colors text-left ${
                              selectedCountry.code === country.code ? "bg-neutral-50 font-medium" : ""
                            }`}
                          >
                            <span className="flex items-center gap-2">
                              <span className="text-base">{country.flag}</span>
                              <span className="text-neutral-800">{country.name}</span>
                            </span>
                            <span className="text-neutral-500">{country.dialCode}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Vertical separator */}
                  <div className="w-[1px] h-5 bg-neutral-300 mx-2.5" />

                  {/* Dial Code Prefix */}
                  <span className="font-mono text-xs sm:text-[13px] text-neutral-700 tracking-wider mr-1.5 select-none">
                    {selectedCountry.dialCode}
                  </span>

                  {/* Phone input */}
                  <input
                    type="tel"
                    id="phone-input"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder={selectedCountry.placeholder}
                    className="w-full bg-transparent font-mono text-xs sm:text-[13px] tracking-wider text-[#171717] outline-none placeholder:text-neutral-400"
                    required
                  />
                </div>
              </div>

              {/* Error message */}
              {otpError && (
                <p className="w-full mt-2 text-left font-mono text-[11px] text-red-600">
                  {otpError}
                </p>
              )}

              {/* Legal disclaimer */}
              <p className="w-full mt-5 mb-6 text-left font-mono text-[11px] leading-relaxed text-neutral-600">
                Click on the &ldquo;Send Code&rdquo; button, I agree to VXYAK&apos;s{" "}
                <Link href="#terms" className="underline underline-offset-2 hover:text-[#171717]">
                  Terms of Service
                </Link>{" "}
                and acknowledge the{" "}
                <Link href="#privacy" className="underline underline-offset-2 hover:text-[#171717]">
                  Privacy Policy
                </Link>
                .
              </p>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 px-6 bg-[#171717] text-[#f6f4ef] font-mono text-xs sm:text-[13px] tracking-[0.14em] hover:bg-neutral-800 transition duration-200 shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed select-none"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-[#f6f4ef]" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                    <span>Sending code...</span>
                  </>
                ) : (
                  <>
                    <span>Send code</span>
                    <span>&rarr;</span>
                  </>
                )}
              </button>
            </form>
          </div>
        ) : step === "already_registered" ? (
          /* User Already Registered Screen */
          <div className="w-full max-w-[390px] flex flex-col items-center">
            <h1 className="font-serif text-3xl sm:text-4xl font-normal leading-tight tracking-tight text-[#171717]">
              Already Registered
            </h1>
            <p className="mt-3 font-mono text-xs sm:text-[13px] tracking-wide text-neutral-600 leading-relaxed">
              Your account for <span className="font-semibold text-neutral-800">{fullPhoneNumber}</span> is already active.
            </p>
            <div className="mt-8 w-full flex flex-col gap-3">
              <a
                href={`https://wa.me/${WHATSAPP_BOT_NUMBER}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full py-3.5 px-6 bg-[#171717] text-[#f6f4ef] font-mono text-xs sm:text-[13px] tracking-[0.14em] hover:bg-neutral-800 transition duration-200 shadow-sm inline-flex items-center justify-center gap-2 select-none"
              >
                Open WhatsApp &rarr;
              </a>
              <button
                type="button"
                onClick={() => {
                  setStep("phone");
                  setPhoneNumber("");
                  setOtpError("");
                }}
                className="w-full py-3 px-6 border border-neutral-300 text-neutral-700 font-mono text-xs hover:bg-neutral-100 transition duration-200 cursor-pointer select-none"
              >
                Use a different number
              </button>
            </div>
          </div>
        ) : verifiedSuccess ? (
          /* Verification Success Screen */
          <div className="w-full max-w-[390px] flex flex-col items-center">
            <h1 className="font-serif text-3xl sm:text-4xl font-normal leading-tight tracking-tight text-[#171717]">
              Welcome to Vxyak{name.trim() ? `, ${name.trim()}` : ""}
            </h1>
            <p className="mt-3 font-mono text-xs sm:text-[13px] tracking-wide text-neutral-600">
              Your agent has been connected to {fullPhoneNumber}.
            </p>
            <div className="mt-8 w-full">
              <a
                href={`https://wa.me/${WHATSAPP_BOT_NUMBER}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full py-3.5 px-6 bg-[#171717] text-[#f6f4ef] font-mono text-xs sm:text-[13px] tracking-[0.14em] hover:bg-neutral-800 transition duration-200 shadow-sm inline-flex items-center justify-center gap-2 select-none"
              >
                Go to WhatsApp &rarr;
              </a>
            </div>
          </div>
        ) : (
          /* OTP Verification Step */
          <div className="w-full max-w-[390px] flex flex-col items-center">
            <h1 className="font-serif text-3xl sm:text-4xl font-normal leading-tight tracking-tight text-[#171717]">
              Enter verification code
            </h1>

            <p className="mt-3 font-mono text-xs sm:text-[13px] tracking-wide text-neutral-600">
              We sent a code to <span className="font-semibold text-neutral-800">{fullPhoneNumber}</span>
            </p>

            {statusMessage && (
              <div className="mt-3 px-3 py-1.5 bg-neutral-200/60 text-[11px] font-mono text-neutral-800">
                {statusMessage}
              </div>
            )}

            <form onSubmit={handleVerifyOtp} className="w-full mt-4 flex flex-col items-center">
              {/* 6 Digit Inputs */}
              <div className="flex items-center justify-between gap-2 w-full my-4">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    id={`otp-input-${idx}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleOtpChange(idx, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                    className="w-11 h-11 text-center font-mono text-lg font-medium border border-neutral-300 bg-white focus:border-[#171717] focus:ring-1 focus:ring-[#171717] outline-none transition-all shadow-xs"
                    autoFocus={idx === 0}
                  />
                ))}
              </div>

              {otpError && (
                <p className="w-full mt-1 mb-2 text-center font-mono text-[11px] text-red-600">
                  {otpError}
                </p>
              )}

              {/* Verify Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-3 py-3.5 px-6 bg-[#171717] text-[#f6f4ef] font-mono text-xs sm:text-[13px] tracking-[0.14em] hover:bg-neutral-800 transition duration-200 shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed select-none"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-[#f6f4ef]" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <span>Verify & Continue</span>
                    <span>&rarr;</span>
                  </>
                )}
              </button>

              {/* Resend and Edit options */}
              <div className="mt-6 flex items-center justify-between w-full font-mono text-[11px] text-neutral-600">
                <button
                  type="button"
                  onClick={() => handleSendCode()}
                  disabled={cooldownSeconds > 0 || isLoading}
                  className="hover:text-[#171717] underline underline-offset-2 cursor-pointer disabled:opacity-50 disabled:no-underline disabled:cursor-not-allowed"
                >
                  {cooldownSeconds > 0 ? `Resend code (${cooldownSeconds}s)` : "Resend code"}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setStep("phone");
                    setOtpError("");
                    setOtp(["", "", "", "", "", ""]);
                  }}
                  className="hover:text-[#171717] underline underline-offset-2 cursor-pointer"
                >
                  Change phone number
                </button>
              </div>
            </form>
          </div>
        )}
      </section>

      {/* ─── FOOTER ─── */}
      <footer className="w-full max-w-[1360px] mx-auto px-6 sm:px-12 mt-8 md:mt-6 font-mono text-[10px] sm:text-[11px] tracking-wider text-neutral-600">
        <div className="w-full pt-4 pb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-4 border-t border-neutral-500/50">
          <div>&copy; 2026 Vxyak.</div>
          <div className="flex items-center gap-3">
            <Link href="/privacy" className="hover:opacity-75 transition-opacity">
              Privacy Policy
            </Link>
            <span>|</span>
            <Link href="/terms" className="hover:opacity-75 transition-opacity">
              Terms of Service
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}

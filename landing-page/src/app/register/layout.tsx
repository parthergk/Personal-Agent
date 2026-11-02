import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Get Started / Log In",
  description:
    "Create your account or log in to VXYAK — your personal AI agent that lives natively inside WhatsApp.",
  alternates: {
    canonical: "/register",
  },
};

export default function RegisterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

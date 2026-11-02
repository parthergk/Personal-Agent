import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono, Newsreader } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://vxyak.in";
const siteDescription =
  "Your world, in quiet sync. Organize plans, automate busywork, and live better with your personal AI agent. Focus on what matters.";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "VXYAK — Personal AI Agent",
    template: "%s | VXYAK",
  },
  description: siteDescription,
  keywords: [
    "personal ai agent",
    "ai personal assistant",
    "task automation agent",
    "whatsapp ai assistant",
    "smart life organizer",
    "productivity ai agent",
    "ai daily planner",
    "executive assistant ai",
    "automated reminders",
    "vxyak",
    "vxyak agent",
  ],
  authors: [{ name: "Gaurav Kumar (Parther)", url: "https://parther.vercel.app" }],
  creator: "Gaurav Kumar (Parther)",
  publisher: "VXYAK",

  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },

  alternates: {
    canonical: "/",
  },

  openGraph: {
    title: "VXYAK — Personal AI Agent",
    description: siteDescription,
    url: "/",
    siteName: "VXYAK",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        type: "image/png",
        alt: "VXYAK — Personal AI Agent",
      },
    ],
  },

  twitter: {
    card: "summary_large_image",
    title: "VXYAK — Personal AI Agent",
    description: siteDescription,
    creator: "@parther_gk",
    images: ["/og-image.png"],
  },

  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon-16x16.png", type: "image/png", sizes: "16x16" },
      { url: "/favicon-32x32.png", type: "image/png", sizes: "32x32" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
    other: [
      {
        rel: "icon",
        url: "/android-chrome-192x192.png",
        sizes: "192x192",
        type: "image/png",
      },
      {
        rel: "icon",
        url: "/android-chrome-512x512.png",
        sizes: "512x512",
        type: "image/png",
      },
    ],
  },

  manifest: "/site.webmanifest",
};

// Organization Schema
const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "VXYAK",
  url: siteUrl,
  logo: `${siteUrl}/android-chrome-512x512.png`,
  image: `${siteUrl}/og-image.png`,
  description: siteDescription,
  sameAs: [
    "https://www.instagram.com/vxyak.in/",
    "https://www.linkedin.com/company/vxyak/",
  ],
  founder: {
    "@type": "Person",
    name: "Gaurav Kumar",
    alternateName: "Parther",
    url: "https://parther.vercel.app",
    sameAs: [
      "https://www.linkedin.com/in/gaurav-kumar-b5a76626b/",
      "https://x.com/parther_gk",
      "https://github.com/parthergk",
      "https://www.instagram.com/parther.in",
    ],
  },
  contactPoint: {
    "@type": "ContactPoint",
    contactType: "Customer Support",
    availableLanguage: ["English"],
  },
};

// Software Application Schema
const softwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "VXYAK",
  description: siteDescription,
  url: siteUrl,
  applicationCategory: "ProductivityApplication",
  operatingSystem: "Web, WhatsApp",
  logo: `${siteUrl}/android-chrome-512x512.png`,
  image: `${siteUrl}/og-image.png`,
  screenshot: `${siteUrl}/og-image.png`,
  author: {
    "@type": "Person",
    name: "Gaurav Kumar",
    alternateName: "Parther",
    url: "https://parther.vercel.app",
  },
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
    availability: "https://schema.org/InStock",
  },
  featureList: [
    "Natural language conversation on WhatsApp",
    "Automated personal reminders and task tracking",
    "Weekly planning and daily organization",
    "Calendar synchronization and schedule management",
  ],
};

// WebSite Schema
const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "VXYAK",
  alternateName: "VXYAK Personal AI Agent",
  url: siteUrl,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${newsreader.variable} h-full antialiased`}
    >
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(organizationSchema),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(softwareSchema),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(websiteSchema),
          }}
        />
      </head>
      <body className="min-h-full flex flex-col font-mono text-[#171717]">{children}</body>
    </html>
  );
}

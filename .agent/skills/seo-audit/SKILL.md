---
name: seo-audit
description: >-
  Use this skill when auditing, implementing, or optimizing technical SEO, metadata,
  Open Graph cards, Twitter cards, Schema.org JSON-LD structured data, sitemaps, robots.txt,
  or social share images for web applications and landing pages (especially Next.js App Router).
---

# Complete Technical & On-Page SEO Runbook

A standardized guide for auditing and implementing production-grade SEO, social sharing cards, and Schema.org structured data.

---

## 1. Search Engine Crawler Setup

### `robots.ts` (Next.js App Router)
Create `src/app/robots.ts` to instruct search engine bots on crawl boundaries:
```typescript
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://yourdomain.com";

  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/"],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
```

### `sitemap.ts` (Next.js App Router)
Create `src/app/sitemap.ts` to list all indexable routes with priorities:
```typescript
import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://yourdomain.com";

  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: "weekly", priority: 1.0 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.9 },
    { url: `${baseUrl}/register`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
    { url: `${baseUrl}/privacy`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${baseUrl}/terms`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
  ];
}
```

---

## 2. Core Metadata Configuration (`layout.tsx`)

Always configure `metadataBase` to avoid Next.js deployment warnings with social images:

```typescript
import type { Metadata, Viewport } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://yourdomain.com";
const siteDescription = "Concise description (140-160 characters) explaining the product value proposition.";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "BrandName — Primary Tagline",
    template: "%s | BrandName",
  },
  description: siteDescription,
  keywords: ["keyword 1", "keyword 2", "brand name"],
  authors: [{ name: "Founder Name (Alias)", url: "https://active-portfolio-or-linkedin.com" }],
  creator: "Founder Name (Alias)",
  publisher: "BrandName",

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
    title: "BrandName — Primary Tagline",
    description: siteDescription,
    url: "/",
    siteName: "BrandName",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/og-image.png", // Must be 1200 x 630 px
        width: 1200,
        height: 630,
        type: "image/png",
        alt: "BrandName — Primary Tagline",
      },
    ],
  },

  twitter: {
    card: "summary_large_image",
    title: "BrandName — Primary Tagline",
    description: siteDescription,
    creator: "@twitter_handle",
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
      { rel: "icon", url: "/android-chrome-192x192.png", sizes: "192x192", type: "image/png" },
      { rel: "icon", url: "/android-chrome-512x512.png", sizes: "512x512", type: "image/png" },
    ],
  },

  manifest: "/site.webmanifest",
};
```

---

## 3. Social & Brand Image Rules

| Asset | Standard Path | Recommended Dimensions | Ratio | Rule |
| :--- | :--- | :--- | :--- | :--- |
| **OpenGraph Banner** | `/og-image.png` | **1200 × 630 px** | **1.91 : 1** | **Never use a 1:1 square logo here.** Square images will be cropped or letterboxed with gray bars on Twitter, LinkedIn, and WhatsApp. |
| **Knowledge Graph Logo** | `/android-chrome-512x512.png` | **512 × 512 px** | **1 : 1** | Google requires a minimum 112×112 square image for Knowledge Panels. |
| **App Icon** | `/android-chrome-192x192.png` | **192 × 192 px** | **1 : 1** | PWA install & Android home screens. |
| **Apple Touch Icon** | `/apple-touch-icon.png` | **180 × 180 px** | **1 : 1** | iOS Safari bookmark & home screen. |

---

## 4. Schema.org Structured Data (JSON-LD)

Place JSON-LD scripts inside the root `<head>` or route wrapper:

### Organization Schema
```typescript
const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "BrandName",
  url: siteUrl,
  logo: `${siteUrl}/android-chrome-512x512.png`,
  image: `${siteUrl}/og-image.png`,
  description: siteDescription,
  founder: {
    "@type": "Person",
    name: "Legal Name",
    alternateName: "Online Alias / Brand Handle",
    url: "https://active-portfolio-or-linkedin.com",
    sameAs: [
      "https://www.linkedin.com/in/...",
      "https://x.com/...",
      "https://github.com/...",
      "https://www.instagram.com/...",
    ],
  },
  contactPoint: {
    "@type": "ContactPoint",
    contactType: "Customer Support",
    availableLanguage: ["English"],
  },
};
```
> [!IMPORTANT]
> **Expired Domain Rule**: Never link expired or squatted domains in `founder.url` or `sameAs`. Use an active live portfolio, LinkedIn, or GitHub profile.

### SoftwareApplication Schema
```typescript
const softwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "BrandName",
  description: siteDescription,
  url: siteUrl,
  applicationCategory: "ProductivityApplication",
  operatingSystem: "Web, iOS, Android",
  logo: `${siteUrl}/android-chrome-512x512.png`,
  image: `${siteUrl}/og-image.png`,
  screenshot: `${siteUrl}/og-image.png`,
  author: {
    "@type": "Person",
    name: "Legal Name",
    alternateName: "Online Alias",
    url: "https://active-portfolio-or-linkedin.com",
  },
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
    availability: "https://schema.org/InStock",
  },
  featureList: [
    "Feature description 1",
    "Feature description 2",
  ],
};
```

### Route-Level Breadcrumbs & AboutPage Schema (`about/page.tsx`)
```typescript
const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: siteUrl },
    { "@type": "ListItem", position: 2, name: "About", item: `${siteUrl}/about` },
  ],
};

const aboutPageSchema = {
  "@context": "https://schema.org",
  "@type": "AboutPage",
  name: "About BrandName",
  url: `${siteUrl}/about`,
  description: "Detailed description of the page purpose.",
  mainEntity: {
    "@type": "Organization",
    name: "BrandName",
    foundingDate: "2026",
    url: siteUrl,
    logo: `${siteUrl}/android-chrome-512x512.png`,
  },
};
```

---

## 5. Web Manifest & Favicons Checklist

Check [`public/site.webmanifest`](file:///d:/projects/Personal-Agent/landing-page/public/site.webmanifest):
```json
{
  "name": "Full Brand Name",
  "short_name": "ShortName",
  "description": "App description",
  "icons": [
    { "src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone",
  "start_url": "/"
}
```
* Ensure `name` and `short_name` are never empty.

---

## 6. On-Page Semantic HTML Checklist

1. **Headings**:
   - Only **one** `<h1>` per page.
   - Proper nesting: `<h2>` comes after `<h1>`, `<h3>` after `<h2>`.
2. **Anchor Links**:
   - Every `<a href="#section">` must have a corresponding `<section id="section">` or element in the DOM.
3. **Images**:
   - Always supply descriptive `alt` text.
   - Use `priority` on above-the-fold hero images.
   - Ensure image paths point to valid `/img/...` or `/...` locations.
4. **Verification**:
   - Run `npm run build` or `next build` to verify all static routes, TypeScript types, and sitemaps render without error.

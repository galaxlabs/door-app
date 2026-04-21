import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/layout/Providers";
import LocaleSync from "@/components/layout/LocaleSync";

export const metadata: Metadata = {
  title: "Door App Admin",
  description: "QR interaction, queue, communication platform",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" dir="ltr">
      <body>
        <LocaleSync />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

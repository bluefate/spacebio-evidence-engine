import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Space Biology Evidence Engine",
  description: "Citation-first evidence workspace for space biology publications.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

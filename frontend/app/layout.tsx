import type { Metadata } from "next";
import NavBar from "@/components/NavBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "BreadGo MVP",
  description: "BreadGo food rescue marketplace MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>
        <div className="app-shell">
          <NavBar />
          <main className="page">{children}</main>
        </div>
      </body>
    </html>
  );
}

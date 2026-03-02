import type { Metadata } from "next";
import BackendStatusBanner from "@/components/BackendStatusBanner";
import "./globals.css";

export const metadata: Metadata = {
  title: "Patent-GPT | TRIZ 기반 AI 특허 아이디어 발굴",
  description:
    "40가지 발명 원리로 당신의 문제를 혁신적인 특허 아이디어로 전환합니다",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap"
        />
      </head>
      <body className="min-h-screen bg-bg-base font-pretendard antialiased">
        <BackendStatusBanner />
        {children}
      </body>
    </html>
  );
}

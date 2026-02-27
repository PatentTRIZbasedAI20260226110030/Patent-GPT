import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "bg-base": "#0A0A0F",
        "bg-surface": "#13131A",
        "bg-elevated": "#1C1C28",
        primary: {
          DEFAULT: "#6366F1",
          hover: "#4F46E5",
          glow: "rgba(99, 102, 241, 0.2)",
        },
        success: "#10B981",
        warning: "#F59E0B",
        error: "#EF4444",
        "text-primary": "#F1F5F9",
        "text-secondary": "#94A3B8",
        "text-muted": "#475569",
        border: "#1E293B",
        "border-active": "#6366F1",
      },
      fontFamily: {
        pretendard: ['"Pretendard"', "Noto Sans KR", "sans-serif"],
      },
      fontSize: {
        display: ["48px", { lineHeight: "1.1", fontWeight: "800" }],
        h1: ["32px", { lineHeight: "1.2", fontWeight: "700" }],
        h2: ["24px", { lineHeight: "1.3", fontWeight: "600" }],
        h3: ["18px", { lineHeight: "1.4", fontWeight: "600" }],
        "body-l": ["16px", { lineHeight: "1.6", fontWeight: "400" }],
        "body-m": ["14px", { lineHeight: "1.6", fontWeight: "400" }],
        caption: ["12px", { lineHeight: "1.5", fontWeight: "400" }],
        label: ["13px", { lineHeight: "1.4", fontWeight: "500" }],
      },
      maxWidth: {
        content: "1200px",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
      borderRadius: {
        input: "8px",
        card: "12px",
      },
      boxShadow: {
        "focus-ring": "0 0 0 3px rgba(99, 102, 241, 0.2)",
      },
    },
  },
  plugins: [],
};

export default config;

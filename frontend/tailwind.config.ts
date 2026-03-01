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
        "bg-base": "#F7F8FA",
        "bg-surface": "#FFFFFF",
        "bg-elevated": "#F2F3F5",
        primary: {
          DEFAULT: "#2563EB",
          hover: "#1D4ED8",
          glow: "rgba(37, 99, 235, 0.2)",
        },
        success: "#059669",
        warning: "#D97706",
        error: "#DC2626",
        "text-primary": "#111827",
        "text-secondary": "#4B5563",
        "text-muted": "#9CA3AF",
        border: "#E5E7EB",
        "border-active": "#2563EB",
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

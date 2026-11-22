/** Design tokens live here only. Components reference `legal-*` classes, never raw hex. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        legal: {
          ink: "#000000",
          blue: "#005BAB",
          "blue-bright": "#0075DE",
          "blue-tint": "#E6F3FE",
          paper: "#F9F9F8",
          teal: "#BDE6E4",
          white: "#FFFFFF",
        },
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      fontSize: {
        hero: ["72px", { lineHeight: "1.05", letterSpacing: "-0.03em", fontWeight: "700" }],
        "hero-md": ["56px", { lineHeight: "1.08", letterSpacing: "-0.025em", fontWeight: "700" }],
        "hero-sm": ["40px", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "700" }],
        section: ["54px", { lineHeight: "1.1", letterSpacing: "-0.025em", fontWeight: "700" }],
        "section-sm": ["36px", { lineHeight: "1.15", letterSpacing: "-0.02em", fontWeight: "700" }],
      },
      borderRadius: { sm: "4px", DEFAULT: "8px", lg: "12px" },
      maxWidth: { page: "1200px" },
      boxShadow: { subtle: "0 1px 2px rgba(0,0,0,0.04)" },
    },
  },
  plugins: [],
};

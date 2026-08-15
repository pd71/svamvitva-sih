import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "SVAMITVA AI Feature Extraction Platform",
  description: "AI-powered geospatial intelligence for automated village mapping from drone orthophotos",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0b1120] text-slate-100 flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 max-w-[1600px] w-full mx-auto p-4 md:p-6">
          {children}
        </main>
        <footer className="bg-[#0f172a] border-t border-[#2a3854] py-3 text-center text-xs text-slate-500">
          SVAMITVA AI Feature Extraction Platform • Smart India Hackathon 2025 • Team Nerdvana
        </footer>
      </body>
    </html>
  );
}

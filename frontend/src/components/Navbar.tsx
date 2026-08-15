"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Layers, 
  Map as MapIcon, 
  BarChart3, 
  CheckSquare, 
  FileSpreadsheet, 
  Cpu,
  Compass
} from "lucide-react";

const navItems = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Analysis", href: "/analysis", icon: Layers },
  { label: "GIS Map", href: "/gis", icon: MapIcon },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Review", href: "/review", icon: CheckSquare },
  { label: "Reports", href: "/reports", icon: FileSpreadsheet },
  { label: "Architecture", href: "/architecture", icon: Cpu },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="bg-[#0f172a] border-b border-[#2a3854] sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-4 py-3 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand Header */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-sky-500 to-blue-700 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Compass className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-wide uppercase">
                SVAMITVA AI Feature Extraction Platform
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800 font-mono">
                SIH 2025 • DJS_26_SW_08
              </span>
            </div>
            <p className="text-xs text-slate-400">
              AI-powered geospatial intelligence for automated village mapping • Team Nerdvana
            </p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex items-center space-x-1 bg-[#161f33] p-1 rounded-lg border border-[#2a3854] overflow-x-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-sky-600 text-white shadow-md shadow-sky-600/30"
                    : "text-slate-300 hover:text-white hover:bg-slate-800"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

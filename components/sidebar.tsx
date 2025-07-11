"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  FileText,
  CheckSquare,
  Settings,
  BarChart4,
  Brain,
  Search,
  Calculator,
  Shield,
  Presentation,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";

const routes = [
  {
    icon: LayoutDashboard,
    label: "Dashboard",
    href: "/dashboard",
  },
  {
    icon: Search,
    label: "Prospect AI",
    href: "/dashboard/prospect-ai",
  },
  {
    icon: FileText,
    label: "Diligence Navigator",
    href: "/dashboard/diligence",
  },
  {
    icon: Calculator,
    label: "Valuation Hub",
    href: "/dashboard/valuation",
  },
  {
    icon: Shield,
    label: "Compliance Guardian",
    href: "/dashboard/compliance",
  },
  {
    icon: Presentation,
    label: "PitchCraft Suite",
    href: "/dashboard/pitchcraft",
  },
  {
    icon: BarChart4,
    label: "Deals",
    href: "/dashboard/deals",
  },
  {
    icon: Users,
    label: "Clients",
    href: "/dashboard/clients",
  },
  {
    icon: Settings,
    label: "Settings",
    href: "/dashboard/settings",
  },
];

interface SidebarProps {
  isMobileMenuOpen?: boolean;
  onMobileMenuClose?: () => void;
}

export default function Sidebar({ isMobileMenuOpen, onMobileMenuClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={onMobileMenuClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        h-full flex flex-col overflow-y-auto bg-dealverse-navy border-r border-dealverse-blue/10 shadow-2xl
        fixed md:relative z-50 md:z-auto
        w-64 md:w-64
        transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Header with Logo */}
        <div className="p-unit-3 border-b border-dealverse-blue/20">
          <div className="flex items-center justify-between">
            <Link href="/dashboard">
              <div className="flex items-center space-x-unit-2 group dealverse-focus">
                <div className="w-10 h-10 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <span className="text-white font-bold text-base">DV</span>
                </div>
                <h1 className="font-bold text-h3 text-white group-hover:text-dealverse-blue transition-colors duration-300">
                  DealVerse OS
                </h1>
              </div>
            </Link>

            {/* Mobile Close Button */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden text-white hover:bg-dealverse-blue/20 dealverse-focus"
              onClick={onMobileMenuClose}
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Navigation Menu */}
        <div className="flex flex-col w-full pt-unit-3 px-unit-2 space-y-unit-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={`flex items-center gap-x-unit-2 text-sm font-medium p-unit-2 rounded-xl transition-all duration-300 group dealverse-focus ${
                pathname === route.href
                  ? "text-white bg-gradient-to-r from-dealverse-blue to-dealverse-blue/80 shadow-lg shadow-dealverse-blue/25"
                  : "text-dealverse-light-gray hover:text-white hover:bg-dealverse-blue/10 hover:shadow-md"
              }`}
              onClick={() => {
                // Close mobile menu when navigation item is clicked
                if (onMobileMenuClose) {
                  onMobileMenuClose();
                }
              }}
            >
              <route.icon className={`h-5 w-5 transition-transform duration-300 ${
                pathname === route.href ? "scale-110 text-white" : "group-hover:scale-110"
              }`} />
              <span className="font-medium">{route.label}</span>
            </Link>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-auto p-unit-3 border-t border-dealverse-blue/20">
          <div className="text-caption text-dealverse-light-gray/60 text-center">
            DealVerse OS v1.0
          </div>
        </div>
      </div>
    </>
  );
}
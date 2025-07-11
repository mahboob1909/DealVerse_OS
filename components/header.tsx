"use client";

// Temporarily disabled Clerk UserButton for development
// import { UserButton } from "@clerk/nextjs";
import { ModeToggle } from "@/components/mode-toggle";
import { Bell, Search, Settings, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

interface HeaderProps {
  onMobileMenuToggle?: () => void;
  isMobileMenuOpen?: boolean;
}

export default function Header({ onMobileMenuToggle, isMobileMenuOpen }: HeaderProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <div className="px-unit-2 md:px-unit-4 py-unit-2 border-b border-dealverse-blue/10 h-16 md:h-20 flex items-center justify-between bg-white/50 dark:bg-dealverse-navy/50 backdrop-blur-sm">
      {/* Mobile Menu Button */}
      <div className="flex items-center space-x-unit-2">
        <Button
          variant="ghost"
          size="sm"
          className="md:hidden hover:bg-dealverse-blue/10 dealverse-focus"
          onClick={onMobileMenuToggle}
          aria-label="Toggle mobile menu"
        >
          {isMobileMenuOpen ? (
            <X className="h-5 w-5 text-dealverse-medium-gray" />
          ) : (
            <Menu className="h-5 w-5 text-dealverse-medium-gray" />
          )}
        </Button>

        {/* Logo for mobile */}
        <div className="md:hidden">
          <div className="w-8 h-8 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">DV</span>
          </div>
        </div>
      </div>

      {/* Search Bar - Desktop */}
      <div className="hidden md:flex flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
          <Input
            placeholder="Search deals, clients, documents..."
            className="pl-10 bg-white dark:bg-dealverse-navy border-dealverse-blue/20 focus:border-dealverse-blue focus:ring-dealverse-blue/20 dealverse-focus"
          />
        </div>
      </div>

      {/* Mobile Search Toggle */}
      <div className="md:hidden">
        <Button
          variant="ghost"
          size="sm"
          className="hover:bg-dealverse-blue/10 dealverse-focus"
          onClick={() => setIsSearchOpen(!isSearchOpen)}
          aria-label="Toggle search"
        >
          <Search className="h-5 w-5 text-dealverse-medium-gray" />
        </Button>
      </div>

      {/* Right Side Controls */}
      <div className="flex items-center gap-x-unit-1 md:gap-x-unit-2">
        {/* Notifications */}
        <Button
          variant="ghost"
          size="sm"
          className="relative hover:bg-dealverse-blue/10 dealverse-focus"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4 md:h-5 md:w-5 text-dealverse-medium-gray" />
          <span className="absolute -top-1 -right-1 h-2 w-2 md:h-3 md:w-3 bg-dealverse-coral rounded-full"></span>
        </Button>

        {/* Settings - Hidden on mobile */}
        <Button
          variant="ghost"
          size="sm"
          className="hidden sm:flex hover:bg-dealverse-blue/10 dealverse-focus"
          aria-label="Settings"
        >
          <Settings className="h-5 w-5 text-dealverse-medium-gray" />
        </Button>

        {/* Theme Toggle */}
        <div className="hidden sm:block">
          <ModeToggle />
        </div>

        {/* User Avatar */}
        <div className="w-8 h-8 md:w-10 md:h-10 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-full flex items-center justify-center text-white font-semibold shadow-lg hover:scale-105 transition-transform duration-200 cursor-pointer dealverse-focus">
          <span className="text-xs md:text-sm">U</span>
        </div>
      </div>

      {/* Mobile Search Bar - Expandable */}
      {isSearchOpen && (
        <div className="absolute top-full left-0 right-0 p-unit-2 bg-white dark:bg-dealverse-navy border-b border-dealverse-blue/10 md:hidden">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dealverse-medium-gray" />
            <Input
              placeholder="Search deals, clients, documents..."
              className="pl-10 bg-white dark:bg-dealverse-navy border-dealverse-blue/20 focus:border-dealverse-blue focus:ring-dealverse-blue/20 dealverse-focus"
              autoFocus
            />
          </div>
        </div>
      )}
    </div>
  );
}
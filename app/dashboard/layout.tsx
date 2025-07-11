"use client";

import Sidebar from "@/components/sidebar";
import Header from "@/components/header";
import { withAuth } from "@/lib/auth-context";
import { useState } from "react";

function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleMobileMenuClose = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="h-full min-h-screen">
      <div className="h-full flex bg-dealverse-light-gray dark:bg-dealverse-dark-gray">
        {/* Sidebar - Hidden on mobile, shown as overlay when menu is open */}
        <Sidebar
          isMobileMenuOpen={isMobileMenuOpen}
          onMobileMenuClose={handleMobileMenuClose}
        />

        {/* Main Content */}
        <div className="flex-1 h-full overflow-y-auto w-full md:w-auto">
          <Header
            onMobileMenuToggle={handleMobileMenuToggle}
            isMobileMenuOpen={isMobileMenuOpen}
          />
          <main className="p-unit-2 md:p-unit-4 lg:p-unit-6 bg-dealverse-light-gray dark:bg-dealverse-dark-gray min-h-[calc(100vh-4rem)] md:min-h-[calc(100vh-5rem)]">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default withAuth(DashboardLayout);
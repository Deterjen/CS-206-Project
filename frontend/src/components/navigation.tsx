// src/components/main-nav.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { GraduationCap } from "lucide-react";

export function MainNav() {
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check if user is logged in on client side
  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  // Don't show navigation on specific pages that have special layouts
  const excludedPaths = [
    "/auth/forgot-password",
    "/recommendations", // This has its own sidebar navigation
  ];

  // Add this condition to the excluded paths check in main-nav.tsx
  if (excludedPaths.some((path) => pathname === path) || pathname === "/auth") {
    return null;
  }

  // Determine if we're in the profile section
  const isProfileSection = pathname?.startsWith("/profile");

  const isLinkActive = (href: string) => {
    return pathname === href || (href !== "/" && pathname?.startsWith(href));
  };

  return (
    <header className="border-b w-full sticky top-0 bg-background/95 z-10">
      <div className="container mx-auto flex h-16 items-center justify-between px-8">
        <div className="flex items-center gap-2">
          <GraduationCap className="h-6 w-6" />
          <Link href="/">
            <span className="text-xl font-bold">Unify</span>
          </Link>
        </div>

        {!isProfileSection && (
          <nav className="hidden md:flex gap-6 pl-22">
            <Link
              href="/#features"
              className={`text-sm font-medium hover:underline ${
                isLinkActive("/#features") ? "text-primary font-bold" : ""
              }`}
            >
              Features
            </Link>
            <Link
              href="/#how-it-works"
              className={`text-sm font-medium hover:underline ${
                isLinkActive("/#how-it-works") ? "text-primary font-bold" : ""
              }`}
            >
              How It Works
            </Link>
            <Link
              href="/#testimonials"
              className={`text-sm font-medium hover:underline ${
                isLinkActive("/#testimonials") ? "text-primary font-bold" : ""
              }`}
            >
              Testimonials
            </Link>
          </nav>
        )}

        <div className="flex items-center gap-4">
          {!isLoggedIn ? (
            <>
              <Link href="/profile/setup">
                <Button variant="outline">Sign Up</Button>
              </Link>
              <Link href="/auth">
                <Button>Get Started</Button>
              </Link>
            </>
          ) : (
            <>
              {isProfileSection ? (
                <Link href="/recommendations">
                  <Button variant="outline">View Recommendations</Button>
                </Link>
              ) : (
                <Link href="/profile/dashboard">
                  <Button variant="outline">Dashboard</Button>
                </Link>
              )}
              <Link href="/profile/dashboard">
                <Button>My Profile</Button>
              </Link>
              <Button
                variant="ghost"
                onClick={() => {
                  localStorage.removeItem("token");
                  window.location.href = "/";
                }}
              >
                Logout
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

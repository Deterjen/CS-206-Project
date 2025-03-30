"use client";

import Link from "next/link";
import { GraduationCap, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/providers/AuthProvider";
import { usePathname } from "next/navigation";

export function Header() {
  const { user, logout } = useAuthContext();
  const pathname = usePathname();

  const isHomepage = pathname?.endsWith("/");

  return (
    <header className="border-b sticky top-0 bg-background/95 z-10">
      <div className="container mx-auto flex h-16 items-center justify-between px-8">
        <div className="flex items-center gap-2">
          <GraduationCap className="h-6 w-6" />
          <Link href="/">
            <span className="text-xl font-bold">Unify</span>
          </Link>
        </div>

        {isHomepage && (
          <nav className="hidden md:flex gap-6 pl-22">
            <Link
              href="#features"
              className="text-sm font-medium hover:underline"
            >
              Features
            </Link>
            <Link
              href="#how-it-works"
              className="text-sm font-medium hover:underline"
            >
              How It Works
            </Link>
            <Link
              href="#testimonials"
              className="text-sm font-medium hover:underline"
            >
              Testimonials
            </Link>
          </nav>
        )}

        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <Link
                href="/profile/dashboard"
                className="flex items-center gap-2"
              >
                <UserCircle className="h-6 w-6 text-gray-600" />
                <span className="text-sm font-medium">{user.username}</span>
              </Link>
              <Button variant="ghost" size="sm" onClick={logout}>
                Logout
              </Button>
            </div>
          ) : (
            <>
              <Link href="/auth">
                <Button variant="outline">Log In</Button>
              </Link>
              <Link href="/auth">
                <Button>Get Started</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

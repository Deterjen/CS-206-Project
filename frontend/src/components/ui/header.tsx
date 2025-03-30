"use client"

import Link from "next/link"
import { GraduationCap } from "lucide-react"
import { Button } from "@/components/ui/button"

interface HeaderProps {
  isAuthenticated?: boolean
  onLogout?: () => void
}

export function Header({ isAuthenticated = false, onLogout }: HeaderProps) {
  return (
    <header className="border-b sticky top-0 bg-background/95 z-10">
      <div className="container flex h-16 items-center justify-between px-8">
        <div className="flex items-center gap-2">
          <GraduationCap className="h-6 w-6" />
          <Link href="/">
            <span className="text-xl font-bold">Unify</span>
          </Link>
        </div>
        {!isAuthenticated ? (
          <>
            <nav className="hidden md:flex gap-6 pl-22">
              <Link href="/#features" className="text-sm font-medium hover:underline">
                Features
              </Link>
              <Link href="/#how-it-works" className="text-sm font-medium hover:underline">
                How It Works
              </Link>
              <Link href="/#testimonials" className="text-sm font-medium hover:underline">
                Testimonials
              </Link>
            </nav>
            <div className="flex items-center gap-4">
              <Link href="/auth">
                <Button variant="outline">Sign Up</Button>
              </Link>
              <Link href="/auth">
                <Button>Get Started</Button>
              </Link>
            </div>
          </>
        ) : (
          <div className="flex items-center gap-4">
            <Link href="/profile/dashboard">
              <Button variant="outline" size="sm" className="gap-2">
                My Profile
              </Button>
            </Link>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={onLogout}
              className="gap-2"
            >
              Logout
            </Button>
          </div>
        )}
      </div>
    </header>
  )
} 
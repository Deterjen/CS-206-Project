"use client"

import { GraduationCap } from "lucide-react"
import Link from "next/link"
import { ProfileForm } from "@/components/profile/ProfileForm"

export default function ProfileSetup() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <header className="border-b sticky top-0 bg-background/95 z-10">
        <div className="container flex h-16 items-center justify-between pl-8 pr-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            <Link href="/">
              <span className="text-xl font-bold">Unify</span>
            </Link>
          </div>
          <nav className="hidden md:flex items-center gap-x-8 pl-20 mr-10">
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
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-12">
        <h1 className="text-3xl font-bold text-center py-4">Profile Setup</h1>
        <ProfileForm />
      </div>
    </div>
  )
}
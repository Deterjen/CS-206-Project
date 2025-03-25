// src/app/layout.tsx - Modified
import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { MainNav } from "@/components/navigation"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Unify - Find Your Perfect University Match",
  description: "Personalized university recommendations based on your academic profile, preferences, and goals.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <MainNav />
          <main className="flex-1">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
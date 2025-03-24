"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { ProfileSetupForm } from "@/components/profile/ProfileSetupForm"
import { Header } from "@/components/ui/header"

export default function ProfileSetupPage() {
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/auth")
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("username")
    router.push("/auth")
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header isAuthenticated={true} onLogout={handleLogout} />
      <main className="flex-1 py-8">
        <ProfileSetupForm />
      </main>
    </div>
  )
}
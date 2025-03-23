"use client"
import Image from "next/image"
import { ChevronRight, Plus, User } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

interface ProfileProps {
  id: string
  name: string
  avatar: string
  title: string
  university: string
  connectionDegree?: number
  mutualConnections?: number
  skills: string[]
  matchScore: number
}

interface SimilarProfilesProps {
  profiles: ProfileProps[]
  onViewAll?: () => void
  onConnect?: (profileId: string) => void
  onViewProfile?: (profileId: string) => void
}

export default function SimilarProfiles({ profiles = [], onViewAll, onConnect, onViewProfile }: SimilarProfilesProps) {
  // If no profiles are provided, use sample data
  const displayProfiles =
    profiles.length > 0
      ? profiles
      : [
          {
            id: "1",
            name: "Alex Wong",
            avatar: "/placeholder.svg?height=100&width=100",
            title: "Business Administration Student",
            university: "Singapore Management University",
            connectionDegree: 2,
            mutualConnections: 12,
            skills: ["Entrepreneurship", "Marketing", "Leadership"],
            matchScore: 92,
          },
          {
            id: "2",
            name: "Sarah Chen",
            avatar: "/placeholder.svg?height=100&width=100",
            title: "Finance Student",
            university: "Singapore Management University",
            connectionDegree: 2,
            mutualConnections: 8,
            skills: ["Financial Analysis", "Investment", "Data Analytics"],
            matchScore: 88,
          },
          {
            id: "3",
            name: "Raj Patel",
            avatar: "/placeholder.svg?height=100&width=100",
            title: "Information Systems Student",
            university: "Singapore Management University",
            connectionDegree: 3,
            mutualConnections: 5,
            skills: ["Programming", "Data Science", "UI/UX Design"],
            matchScore: 85,
          },
        ]

  const handleConnect = (profileId: string) => {
    if (onConnect) {
      onConnect(profileId)
    }
  }

  const handleViewProfile = (profileId: string) => {
    if (onViewProfile) {
      onViewProfile(profileId)
    }
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">People with similar profiles</h2>
        <Button variant="ghost" className="text-sm text-primary flex items-center" onClick={onViewAll}>
          View all
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {displayProfiles.map((profile) => (
          <Card key={profile.id} className="overflow-hidden hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="relative h-16 w-16 rounded-full overflow-hidden flex-shrink-0 border">
                  <Image src={profile.avatar || "/placeholder.svg"} alt={profile.name} fill className="object-cover" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div>
                      <h3 className="font-medium text-base truncate">{profile.name}</h3>
                      <p className="text-sm text-muted-foreground truncate">{profile.title}</p>
                      <p className="text-sm text-muted-foreground truncate">{profile.university}</p>
                    </div>

                    <div className="flex-shrink-0">
                      <div className="bg-green-50 text-green-700 px-2 py-1 rounded text-xs font-medium">
                        {profile.matchScore}% Match
                      </div>
                    </div>
                  </div>

                  {profile.connectionDegree && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {profile.connectionDegree}
                      {getOrdinalSuffix(profile.connectionDegree)} degree connection
                      {profile.mutualConnections ? ` • ${profile.mutualConnections} mutual connections` : ""}
                    </p>
                  )}

                  <div className="mt-3">
                    <p className="text-xs font-medium text-muted-foreground mb-1">Skills</p>
                    <div className="flex flex-wrap gap-1">
                      {profile.skills.map((skill, index) => (
                        <span key={index} className="bg-muted text-xs px-2 py-0.5 rounded-full">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1 sm:flex-none"
                      onClick={() => handleConnect(profile.id)}
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Connect
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      className="flex-1 sm:flex-none"
                      onClick={() => handleViewProfile(profile.id)}
                    >
                      <User className="h-4 w-4 mr-1" />
                      View Profile
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Separator className="my-4" />

      <div className="flex justify-center">
        <Button variant="outline" className="w-full sm:w-auto" onClick={onViewAll}>
          View all similar profiles
        </Button>
      </div>
    </div>
  )
}

// Helper function to get ordinal suffix
function getOrdinalSuffix(n: number): string {
  const s = ["th", "st", "nd", "rd"]
  const v = n % 100
  return s[(v - 20) % 10] || s[v] || s[0]
}


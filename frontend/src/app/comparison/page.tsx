"use client"
import Image from "next/image"
import { Check } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface University {
  id: string
  name: string
  image: string
  profileMatch: number
  affinityScore: number
  whyItSuitsYou: string[]
  considerations: string[]
  similarStudentsFound: number
  averageSatisfaction: number
}

// Sample data
const universities: University[] = [
  {
    id: "1",
    name: "Singapore Management University",
    image: "/placeholder.svg?height=200&width=400",
    profileMatch: 70,
    affinityScore: 80,
    whyItSuitsYou: [
      "Learning style match: The university has many hands-on learners",
      "Career goal alignment: Many students aim for careers as Entrepreneur",
      "Strong alignment on campus culture importance",
      "Strong alignment on internship opportunities importance",
    ],
    considerations: ["You value extracurricular activities highly, but students at this university typically don't"],
    similarStudentsFound: 2,
    averageSatisfaction: 3.9,
  },
  {
    id: "2",
    name: "Singapore Management University",
    image: "/placeholder.svg?height=200&width=400",
    profileMatch: 70,
    affinityScore: 80,
    whyItSuitsYou: [
      "Learning style match: The university has many hands-on learners",
      "Career goal alignment: Many students aim for careers as Entrepreneur",
      "Strong alignment on campus culture importance",
      "Strong alignment on internship opportunities importance",
    ],
    considerations: ["You value extracurricular activities highly, but students at this university typically don't"],
    similarStudentsFound: 2,
    averageSatisfaction: 3.9,
  },
]

export default function ComparePage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Compare</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {universities.map((university) => (
          <Card key={university.id} className="overflow-hidden border rounded-lg">
            <CardContent className="p-0">
              <div className="p-4">
                <h2 className="text-xl font-bold mb-4">{university.name}</h2>
                <div className="relative h-48 w-full mb-6">
                  <Image
                    src={university.image || "/placeholder.svg"}
                    alt={university.name}
                    fill
                    className="object-cover"
                  />
                </div>

                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div>
                    <p className="text-center mb-2">Profile Match</p>
                    <div className="relative flex items-center justify-center">
                      <div className="absolute text-center">
                        <span className="text-lg font-bold">{university.profileMatch}%</span>
                      </div>
                      <div className="w-24 h-24">
                        <svg viewBox="0 0 100 100" className="w-full h-full">
                          <circle cx="50" cy="50" r="40" fill="none" stroke="#e6e6e6" strokeWidth="10" />
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke="#4ade80"
                            strokeWidth="10"
                            strokeDasharray={`${university.profileMatch * 2.51} 251`}
                            strokeDashoffset="62.75"
                            transform="rotate(-90 50 50)"
                          />
                        </svg>
                      </div>
                    </div>
                  </div>

                  <div>
                    <p className="text-center mb-2">Affinity Score</p>
                    <div className="relative flex items-center justify-center">
                      <div className="absolute text-center">
                        <span className="text-lg font-bold">{university.affinityScore}%</span>
                      </div>
                      <div className="w-24 h-24">
                        <svg viewBox="0 0 100 100" className="w-full h-full">
                          <circle cx="50" cy="50" r="40" fill="none" stroke="#e6e6e6" strokeWidth="10" />
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke="#4ade80"
                            strokeWidth="10"
                            strokeDasharray={`${university.affinityScore * 2.51} 251`}
                            strokeDashoffset="62.75"
                            transform="rotate(-90 50 50)"
                          />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-bold mb-2">Why it suits you:</h3>
                  <ul className="space-y-1">
                    {university.whyItSuitsYou.map((reason, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                        <span className="text-sm">{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mb-6">
                  <h3 className="font-bold mb-2">Considerations:</h3>
                  <ul className="space-y-1">
                    {university.considerations.map((consideration, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-sm">{consideration}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="text-sm">
                  <p>Similar Students found: {university.similarStudentsFound}</p>
                  <p>Average Satisfaction at this University: {university.averageSatisfaction}/5</p>
                </div>

                <div className="mt-4">
                  <Button variant="outline" className="w-full">
                    More Details
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}


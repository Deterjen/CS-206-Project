"use client"

import * as React from "react"
import Image from "next/image"
import Link from "next/link"
import { ChevronLeft, ChevronRight, MapPin, Search, ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"

interface University {
  id: string
  name: string
  location: string
  logo: string
  matchScore: number
  images: string[]
  benefits: string[]
  drawbacks: string[]
  suitabilityReasons: string[]
}

const universities: University[] = [
  {
    id: "1",
    name: "Singapore Management University",
    location: "Singapore",
    logo: "/placeholder.svg",
    matchScore: 95,
    images: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    benefits: ["Located in the city", "Offers many scholarships and financial aid", "Strong industry connections"],
    drawbacks: ["Highly competitive admission", "Higher living costs", "Intensive course load"],
    suitabilityReasons: [
      "Located in the city",
      "Offers many scholarships and financial aid",
      "Strong academic programs",
    ],
  },
  // Add more universities here
]

export default function RecommendationsPage() {
  const [selectedUniversity, setSelectedUniversity] = React.useState(universities[0])
  const [currentImageIndex, setCurrentImageIndex] = React.useState(0)

  return (
    <div className="flex min-h-screen">
      {/* Left Sidebar */}
      <div className="w-[400px] border-r">
        <div className="p-4 space-y-4">
          <h1 className="text-2xl font-semibold">Recommendations</h1>
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            <span>Singapore</span>
          </div>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search universities" className="pl-8" />
          </div>
          <div className="space-y-2">
            {universities.map((university) => (
              <Card
                key={university.id}
                className={`cursor-pointer transition-colors hover:bg-muted ${
                  selectedUniversity.id === university.id ? "bg-muted" : ""
                }`}
                onClick={() => setSelectedUniversity(university)}
              >
                <CardContent className="p-4 flex items-center gap-4">
                  <Image
                    src={university.logo || "/placeholder.svg"}
                    alt={university.name}
                    width={40}
                    height={40}
                    className="rounded-full"
                  />
                  <div className="flex-1">
                    <h3 className="font-medium">{university.name}</h3>
                    <p className="text-sm text-muted-foreground">Match Score: {university.matchScore}%</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="pt-4">
            <p className="text-sm text-muted-foreground">Not satisfied or changed your profile recently?</p>
            <Button variant="default" className="w-full mt-2">
              <Search className="mr-2 h-4 w-4" />
              Find Recommendations
            </Button>
            <div className="pt-2">
              <Link href="/comparison">
                <Button variant="outline" className="w-full">
                  <ArrowRight className="mr-2 h-4 w-4" />
                  Compare Universities
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto space-y-8">
          <h1 className="text-3xl font-semibold">{selectedUniversity.name}</h1>

          {/* Image Carousel */}
          <div className="relative aspect-[16/9] bg-muted rounded-lg overflow-hidden">
            <Image
              src={selectedUniversity.images[currentImageIndex] || "/placeholder.svg"}
              alt="University campus"
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-between p-4">
              <Button
                variant="outline"
                size="icon"
                onClick={() =>
                  setCurrentImageIndex((prev) => (prev === 0 ? selectedUniversity.images.length - 1 : prev - 1))
                }
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() =>
                  setCurrentImageIndex((prev) => (prev === selectedUniversity.images.length - 1 ? 0 : prev + 1))
                }
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Why it suits you */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">Why it suits you</h2>
            <ul className="space-y-2">
              {selectedUniversity.suitabilityReasons.map((reason, index) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  {reason}
                </li>
              ))}
            </ul>
          </section>

          {/* Benefits and Drawbacks */}
          <div className="grid md:grid-cols-2 gap-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">Benefits</h2>
              <ul className="space-y-2">
                {selectedUniversity.benefits.map((benefit, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    {benefit}
                  </li>
                ))}
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Drawbacks</h2>
              <ul className="space-y-2">
                {selectedUniversity.drawbacks.map((drawback, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-destructive" />
                    {drawback}
                  </li>
                ))}
              </ul>
            </section>
          </div>

          <Separator />

          <div className="flex justify-between">
            <Link href="/comparison">
              <Button variant="outline">Compare with Other Universities</Button>
            </Link>
            <Button size="lg">Apply Now</Button>
          </div>
        </div>
      </div>
    </div>
  )
}
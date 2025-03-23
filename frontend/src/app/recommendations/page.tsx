"use client"

import * as React from "react"
import Image from "next/image"
import Link from "next/link"
import { GraduationCap, ChevronLeft, ChevronRight, MapPin, Search, ArrowRight, User } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { recommendations, University } from "@/lib/api"

export default function RecommendationsPage() {
  const [selectedUniversity, setSelectedUniversity] = React.useState<University | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = React.useState(0);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [universities, setUniversities] = React.useState<University[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Fetch recommendations on component mount
  React.useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setIsLoading(true);
        const data = await recommendations.getRecommendations();
        setUniversities(data);
        if (data.length > 0) {
          setSelectedUniversity(data[0]);
        }
      } catch (err) {
        setError("Failed to load recommendations. Please try again later.");
        console.error("Error fetching recommendations:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  // Filter universities based on search query
  const filteredUniversities = React.useMemo(() => {
    if (!searchQuery.trim()) return universities;
    
    const query = searchQuery.toLowerCase();
    return universities.filter((university) => 
      university.name.toLowerCase().includes(query) ||
      university.location.toLowerCase().includes(query) ||
      university.benefits.some(benefit => benefit.toLowerCase().includes(query)) ||
      university.suitabilityReasons.some(reason => reason.toLowerCase().includes(query))
    );
  }, [searchQuery, universities]);

  // Update selected university when filtered results change
  React.useEffect(() => {
    if (filteredUniversities.length > 0 && !filteredUniversities.find(u => u.id === selectedUniversity?.id)) {
      setSelectedUniversity(filteredUniversities[0]);
    }
  }, [filteredUniversities, selectedUniversity]);

  // Get top 3 recommendations sorted by match score
  const topRecommendations = React.useMemo(() => {
    return [...universities].sort((a, b) => b.matchScore - a.matchScore).slice(0, 3);
  }, [universities]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-destructive">{error}</p>
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b sticky top-0 bg-background/95 z-10">
        <div className="container flex h-16 items-center justify-between px-8">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            <Link href="/">
              <span className="text-xl font-bold">Unify</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/profile/dashboard">
              <Button variant="outline" size="sm" className="gap-2">
                <User className="h-4 w-4" />
                My Profile
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="flex flex-1 px-6">
        {/* Left Sidebar */}
        <div className="w-[400px] border-r">
          <div className="p-4 space-y-4">
            <h2 className="text-xl font-semibold">Recommendations For You</h2>
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              <span>Singapore</span>
            </div>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search universities" 
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              {filteredUniversities.map((university) => (
                <Card
                  key={university.id}
                  className={`cursor-pointer transition-colors hover:bg-muted ${
                    selectedUniversity?.id === university.id ? "bg-muted" : ""
                  }`}
                  onClick={() => setSelectedUniversity(university)}
                >
                  <CardContent className="p-4 flex items-center gap-4">
                    <Image
                      src={university.logo}
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
              <p className="text-sm text-muted-foreground">
                {filteredUniversities.length === 0 
                  ? "No universities found matching your search"
                  : "Not satisfied or changed your profile recently?"
                }
              </p>
              <Button 
                variant="default" 
                className="w-full mt-2"
                onClick={() => setSearchQuery("")}
              >
                <Search className="mr-2 h-4 w-4" />
                {filteredUniversities.length === 0 ? "Clear Search" : "Find Recommendations"}
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
        {selectedUniversity && (
          <div className="flex-1 p-6">
            <div className="max-w-4xl mx-auto space-y-8">
              <h1 className="text-3xl font-semibold">{selectedUniversity.name}</h1>

              {/* Image Carousel */}
              <div className="relative aspect-[16/9] bg-muted rounded-lg overflow-hidden">
                <Image
                  src={selectedUniversity.images[currentImageIndex]}
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
        )}
      </div>
    </div>
  );
}
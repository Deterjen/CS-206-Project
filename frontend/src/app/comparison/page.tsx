"use client"

import * as React from "react"
import Link from "next/link"
import Image from "next/image"
import { ChevronLeft, GraduationCap } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { auth, recommendations, University } from "@/lib/api"
import { useRouter } from "next/navigation"

export default function ComparisonPage() {
  const router = useRouter();
  const [universities, setUniversities] = React.useState<University[]>([]);
  const [selectedUniversities, setSelectedUniversities] = React.useState<string[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // Fetch universities on component mount
  React.useEffect(() => {
    const fetchUniversities = async () => {
      try {
        setIsLoading(true);
        const data = await recommendations.getRecommendations();
        setUniversities(data);
        if (data.length > 0) {
          setSelectedUniversities([data[0].id]);
        }
      } catch (err) {
        setError("Failed to load universities. Please try again later.");
        console.error("Error fetching universities:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUniversities();
  }, []);

  const handleLogout = async () => {
    await auth.logout();
    router.push("/auth/login");
  };

  const addUniversity = () => {
    if (selectedUniversities.length < 3) {
      // Find the first university that isn't already selected
      const availableUniversities = universities.filter(u => !selectedUniversities.includes(u.id));
      if (availableUniversities.length > 0) {
        setSelectedUniversities([...selectedUniversities, availableUniversities[0].id]);
      }
    }
  };

  const updateUniversity = (index: number, universityId: string) => {
    const newSelected = [...selectedUniversities];
    newSelected[index] = universityId;
    setSelectedUniversities(newSelected);
  };

  const removeUniversity = (index: number) => {
    setSelectedUniversities(selectedUniversities.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading universities...</p>
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
                My Profile
              </Button>
            </Link>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={handleLogout}
              className="gap-2"
            >
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container py-8 max-w-7xl px-12">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/recommendations">
            <Button variant="outline" size="icon">
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Compare Universities</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {selectedUniversities.map((universityId, index) => {
            const university = universities.find(u => u.id === universityId)!;
            return (
              <Card key={index} className="relative">
                {selectedUniversities.length > 1 && (
                  <Button
                    variant="outline"
                    size="icon"
                    className="absolute right-2 top-2"
                    onClick={() => removeUniversity(index)}
                  >
                    ×
                  </Button>
                )}
                <CardHeader>
                  <Select value={universityId} onValueChange={(value) => updateUniversity(index, value)}>
                    <SelectTrigger>
                      <SelectValue>{university.name}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {universities.map((u) => (
                        <SelectItem key={u.id} value={u.id}>
                          {u.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-4">
                    <Image
                      src={university.logo}
                      alt={university.name}
                      width={60}
                      height={60}
                      className="rounded-full"
                    />
                    <div>
                      <p className="text-lg font-semibold">Match Score</p>
                      <p className="text-2xl font-bold text-primary">{university.matchScore}%</p>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="font-semibold mb-2">Benefits</h3>
                    <ul className="space-y-1">
                      {university.benefits.map((benefit, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Drawbacks</h3>
                    <ul className="space-y-1">
                      {university.drawbacks.map((drawback, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <span className="h-1.5 w-1.5 rounded-full bg-destructive" />
                          {drawback}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Why it suits you</h3>
                    <ul className="space-y-1">
                      {university.suitabilityReasons.map((reason, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            );
          })}

          {selectedUniversities.length < 3 && (
            <>
              {universities.length > selectedUniversities.length ? (
                <button
                  onClick={addUniversity}
                  className="h-full min-h-[200px] rounded-lg border-2 border-dashed border-muted-foreground/20 hover:border-muted-foreground/40 transition-colors"
                >
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <span className="text-2xl mb-2">+</span>
                    <span>Add University</span>
                    <span className="text-sm mt-1 text-muted-foreground">
                      {universities.length - selectedUniversities.length} more available
                    </span>
                  </div>
                </button>
              ) : (
                <div className="h-full min-h-[200px] rounded-lg border-2 border-dashed border-muted-foreground/20 flex items-center justify-center">
                  <div className="text-center text-muted-foreground px-4">
                    <p>No more universities available to compare</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}


"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProfileFormData } from "@/types/profile";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Link from "next/link";
import { GraduationCap, User } from "lucide-react";
import { auth } from "@/lib/api";

// Mock similar profiles (in a real app, this would come from your backend)
const mockSimilarProfiles = [
  {
    id: 1,
    name: "Alex Thompson",
    matchPercentage: 85,
    commonInterests: ["Computer Science", "Research", "Sports"],
    avatar: "/avatars/01.png",
  },
  {
    id: 2,
    name: "Sarah Chen",
    matchPercentage: 78,
    commonInterests: ["Biology", "Leadership", "Arts"],
    avatar: "/avatars/02.png",
  },
  {
    id: 3,
    name: "Jordan Lee",
    matchPercentage: 72,
    commonInterests: ["Engineering", "Volunteering", "Music"],
    avatar: "/avatars/03.png",
  },
];

export default function ProfileDashboard() {
  const router = useRouter();
  const [profile, setProfile] = useState<ProfileFormData | null>(null);

  useEffect(() => {
    // Fetch profile data from localStorage
    const storedProfile = localStorage.getItem("userProfile");
    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    }
  }, []);

  const handleLogout = async () => {
    await auth.logout();
    router.push("/auth/login");
  };

  if (!profile) {
    return <div>Loading...</div>;
  }

  const renderProfileSummary = () => {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Your Profile Summary</CardTitle>
          <CardDescription>Overview of your preferences and interests</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold">Academic Interests</h3>
              <ul className="list-disc list-inside">
                {profile.preferredFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold">Learning Style</h3>
              <p>{profile.learningStyle}</p>
            </div>
            <div>
              <h3 className="font-semibold">Extracurricular Activities</h3>
              <ul className="list-disc list-inside">
                {profile.extracurricularActivities.map((activity) => (
                  <li key={activity}>{activity}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold">Career Goals</h3>
              <p className="line-clamp-3">{profile.careerGoals}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderSimilarProfiles = () => {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Similar Profiles</CardTitle>
          <CardDescription>People who share your interests and goals</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockSimilarProfiles.map((profile) => (
              <div
                key={profile.id}
                className="flex items-center space-x-4 p-4 rounded-lg border"
              >
                <Avatar>
                  <AvatarImage src={profile.avatar} />
                  <AvatarFallback>{profile.name.split(" ").map(n => n[0]).join("")}</AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <h4 className="font-semibold">{profile.name}</h4>
                  <p className="text-sm text-muted-foreground">
                    {profile.commonInterests.join(" • ")}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-lg font-bold text-green-600">
                    {profile.matchPercentage}%
                  </span>
                  <p className="text-sm text-muted-foreground">match</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

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
            <Link href="/recommendations">
              <Button variant="outline" size="sm" className="gap-2">
                Find Universities
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
      <div className="container py-8 px-12">
        <h1 className="text-3xl font-bold mb-6">Profile Dashboard</h1>
        <div className="flex justify-between items-center mb-8">
          <div className="space-x-4">
            <Button
              variant="outline"
              onClick={() => router.push("/profile/setup")}
            >
              Edit Profile
            </Button>
          </div>
        </div>

        {renderProfileSummary()}
        {renderSimilarProfiles()}
      </div>
    </div>
  );
} 
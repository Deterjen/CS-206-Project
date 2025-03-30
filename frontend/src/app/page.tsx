import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  Users,
  DollarSign,
  Briefcase,
  MapPin,
  Building,
  Award,
  UserCircle,
  Search,
  BadgeCheck,
  BarChart,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MatchingAlgorithmVisualization from "@/components/matching-algo-vis";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen overflow-x-hidden">
      {/* Hero Section */}
      <section className="min-h-screen flex flex-col justify-center w-full bg-muted/50">
        <div className="container mx-auto px-4 md:px-8 py-16 flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-1.5 rounded-full mb-6 text-sm font-medium">
            <BadgeCheck className="h-4 w-4" />
            Simplify Your Search, Amplify Your Future!
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight max-w-3xl mb-6">
            Find the University That&apos;s{" "}
            <span className="text-primary">Made for You</span>
          </h1>

          <p className="mt-4 text-lg md:text-xl text-muted-foreground max-w-2xl">
            Too many options, too little clarity? Our AI matches you with
            universities where students like you thrive, based on your unique
            profile, preferences, and goals.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row gap-4">
            <Link href="/profile/setup">
              <Button size="lg" className="px-8">
                Find Your Match
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="#how-it-works">
              <Button size="lg" variant="outline">
                See How It Works
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Statement Section */}
      <section
        id="problem"
        className="min-h-screen flex flex-col justify-center w-full bg-muted/50"
      >
        <div className="container mx-auto px-4 md:px-8 lg:px-16 xl:px-24 py-16">
          <div className="flex flex-col lg:flex-row gap-12 items-center">
            <div className="lg:w-1/2">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                The University Search{" "}
                <span className="text-primary">
                  Shouldn&apos;t Be Overwhelming
                </span>
              </h2>
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <BarChart className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Information Overload
                    </h3>
                    <p className="text-muted-foreground">
                      Thousands of universities, countless programs, and
                      overwhelming data make it difficult to find your perfect
                      match.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <Users className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Hard to Assess Personal Fit
                    </h3>
                    <p className="text-muted-foreground">
                      Every student is unique, but university brochures and
                      websites can&apos;t tell you if you&apos;ll truly belong
                      there.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <DollarSign className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Complex Decision Factors
                    </h3>
                    <p className="text-muted-foreground">
                      Comparing admission criteria, costs, campus life, and
                      future outcomes across multiple institutions is
                      exhausting.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="lg:w-1/2">
              <Image
                src="/images/overwhelmed_student.webp"
                alt="Students overwhelmed by university choices"
                width={600}
                height={500}
                className="rounded-lg shadow-lg"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Multi-dimensional Analysis */}
      <section
        id="features"
        className="min-h-screen flex flex-col justify-center w-full bg-muted/50 relative"
      >
        <div className="container mx-auto px-4 md:px-8 lg:px-16 xl:px-24 py-16">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 relative z-10">
              Find Your Perfect Match Across{" "}
              <span className="text-primary">8 Key Dimensions</span>
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our smart matching algorithm analyzes your profile against real
              university students&apos; experiences to find where you&apos;ll
              thrive.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <BookOpen className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Academic Interest
                </h3>
                <p className="text-muted-foreground">
                  Match with universities offering strong programs in your field
                  with faculty expertise that aligns with your interests.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Social & Cultural
                </h3>
                <p className="text-muted-foreground">
                  Find a campus culture and community where you&apos;ll feel
                  welcome, included, and engaged.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <DollarSign className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Financial Feasibility
                </h3>
                <p className="text-muted-foreground">
                  Discover universities that match your budget with scholarship
                  opportunities and reasonable living costs.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Briefcase className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Career Prospects</h3>
                <p className="text-muted-foreground">
                  Connect with institutions that have strong industry
                  partnerships and employment outcomes in your field.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <MapPin className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Geographic Preferences
                </h3>
                <p className="text-muted-foreground">
                  Find universities in locations that match your urban/rural
                  preferences and desired proximity to opportunities.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Building className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Campus Facilities
                </h3>
                <p className="text-muted-foreground">
                  Match with universities offering the libraries, labs, housing,
                  and recreational spaces that matter to you.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Award className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Reputation & Brand
                </h3>
                <p className="text-muted-foreground">
                  Consider universities with strong rankings and reputation in
                  your specific areas of interest.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-background border border-border hover:border-primary/50 transition-all duration-300">
              <CardContent className="p-6">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <UserCircle className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Personal Fit</h3>
                <p className="text-muted-foreground">
                  Find a university environment that aligns with your
                  personality, whether you&apos;re introverted, extroverted, or
                  somewhere in between.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section
        id="how-it-works"
        className="min-h-screen flex flex-col justify-center w-full bg-muted/50"
      >
        <div className="container mx-auto px-4 md:px-8 lg:px-16 xl:px-24 py-16">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How Unify Works
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our data-driven approach combines real student experiences with your unique profile to
              find your perfect university match.
            </p>
          </div>

          <div className="flex flex-col lg:flex-row gap-8 lg:gap-16 items-center">
            <div className="lg:w-1/2">
              <div className="grid gap-8">
                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary text-white font-semibold flex items-center justify-center">
                    1
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Create Your Profile
                    </h3>
                    <p className="text-muted-foreground">
                      Tell us about your academic interests, personality
                      traits, preferences, extracurricular activities, and what
                      matters most to you in a university.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary text-white font-semibold flex items-center justify-center">
                    2
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Upload Documents
                    </h3>
                    <p className="text-muted-foreground">
                      Share your transcripts and resume to help our algorithm
                      better understand your academic strengths and
                      extracurricular involvement.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary text-white font-semibold flex items-center justify-center">
                    3
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Get Personalized Recommendations
                    </h3>
                    <p className="text-muted-foreground">
                      Our algorithm matches you with universities where students
                      with similar profiles thrive, analyzing fit across all 8
                      dimensions.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary text-white font-semibold flex items-center justify-center">
                    4
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Make Informed Decisions
                    </h3>
                    <p className="text-muted-foreground">
                      See detailed explanations for each recommendation, including
                      specific strengths and potential challenges to help you
                      confidently choose where to apply.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="lg:w-1/2">
              <Tabs defaultValue="profile" className="w-full">
                <TabsList className="grid grid-cols-4 mb-8">
                  <TabsTrigger value="profile">Step 1</TabsTrigger>
                  <TabsTrigger value="data">Step 2</TabsTrigger>
                  <TabsTrigger value="match">Step 3</TabsTrigger>
                  <TabsTrigger value="decide">Step 4</TabsTrigger>
                </TabsList>
                <TabsContent value="profile" className="mt-0">
                  <Image
                    src="/placeholder.svg?height=400&width=500"
                    alt="Creating your profile"
                    width={500}
                    height={400}
                    className="rounded-lg shadow-lg border border-border"
                  />
                </TabsContent>
                <TabsContent value="data" className="mt-0">
                  <Image
                    src="/placeholder.svg?height=400&width=500"
                    alt="Data processing"
                    width={500}
                    height={400}
                    className="rounded-lg shadow-lg border border-border"
                  />
                </TabsContent>
                <TabsContent value="match" className="mt-0">
                  <Image
                    src="/placeholder.svg?height=400&width=500"
                    alt="Matching algorithm"
                    width={500}
                    height={400}
                    className="rounded-lg shadow-lg border border-border"
                  />
                </TabsContent>
                <TabsContent value="decide" className="mt-0">
                  <Image
                    src="/placeholder.svg?height=400&width=500"
                    alt="Make informed decisions"
                    width={500}
                    height={400}
                    className="rounded-lg shadow-lg border border-border"
                  />
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </div>
      </section>

      {/* Data-driven approach */}
      <section className="min-h-screen flex flex-col justify-center w-full bg-muted/50">
        <div className="container mx-auto px-32 py-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Our <span className="text-primary">Data-Driven</span> Approach
              </h2>
              <p className="text-muted-foreground mb-8">
                We&apos;ve gathered detailed profiles from thousands of
                university students to create a comprehensive database that
                powers our smart matching algorithm.
              </p>

              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <Users className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Real Student Experiences
                    </h3>
                    <p className="text-muted-foreground">
                      Our database includes profiles from real students across
                      hundreds of universities, giving you authentic insights.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <Search className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Multi-dimensional Analysis
                    </h3>
                    <p className="text-muted-foreground">
                      We analyze compatibility across 8 key dimensions to find
                      your best university matches.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="mt-1 flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <BarChart className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Transparent Scoring
                    </h3>
                    <p className="text-muted-foreground">
                      We show you exactly why each university is recommended,
                      with detailed breakdown of your match score.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <MatchingAlgorithmVisualization />
            </div>
          </div>
        </div>
      </section>

      {/* University Showcase */}
      <section className="min-h-screen flex flex-col justify-center w-full bg-muted/50">
        <div className="container mx-auto px-32 py-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-6">
            Discover Universities That{" "}
            <span className="text-primary">Match Your Profile</span>
          </h2>
          <p className="text-center text-muted-foreground max-w-2xl mx-auto mb-16">
            Our algorithm analyzes data from thousands of current university
            students to find institutions where people like you thrive.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="bg-background relative overflow-hidden border border-border hover:border-primary/50 transition-all duration-300">
              <div className="absolute top-4 right-4 bg-primary text-primary-foreground text-sm font-medium px-2.5 py-0.5 rounded-full">
                95% Match
              </div>
              <div className="pt-6 px-6">
                <div className="h-16 w-16 rounded-full bg-muted mb-4 flex items-center justify-center">
                  <Image
                    src="/images/school.svg"
                    alt="University 1"
                    width={40}
                    height={40}
                  />
                </div>
                <h3 className="text-xl font-semibold mb-1">
                  Stanford University
                </h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Stanford, CA
                </p>
              </div>
              <CardContent className="p-6 pt-0">
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Strong computer science program</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Collaborative campus culture</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Excellent industry connections</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-background relative overflow-hidden border border-border hover:border-primary/50 transition-all duration-300">
              <div className="absolute top-4 right-4 bg-primary text-primary-foreground text-sm font-medium px-2.5 py-0.5 rounded-full">
                91% Match
              </div>
              <div className="pt-6 px-6">
                <div className="h-16 w-16 rounded-full bg-muted mb-4 flex items-center justify-center">
                  <Image
                    src="/images/school.svg"
                    alt="University 2"
                    width={40}
                    height={40}
                  />
                </div>
                <h3 className="text-xl font-semibold mb-1">UC Berkeley</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Berkeley, CA
                </p>
              </div>
              <CardContent className="p-6 pt-0">
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Diverse student body</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Research opportunities</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Active student organizations</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-background relative overflow-hidden border border-border hover:border-primary/50 transition-all duration-300">
              <div className="absolute top-4 right-4 bg-primary text-primary-foreground text-sm font-medium px-2.5 py-0.5 rounded-full">
                88% Match
              </div>
              <div className="pt-6 px-6">
                <div className="h-16 w-16 rounded-full bg-muted mb-4 flex items-center justify-center">
                  <Image
                    src="/images/school.svg"
                    alt="University 3"
                    width={40}
                    height={40}
                  />
                </div>
                <h3 className="text-xl font-semibold mb-1">MIT</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  Cambridge, MA
                </p>
              </div>
              <CardContent className="p-6 pt-0">
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Cutting-edge research facilities</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Innovation-focused community</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                    <p className="text-sm">Strong engineering programs</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="mt-12 text-center">
            <Link href="/recommendations">
              <Button size="lg">
                Explore More Universities
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section
        id="testimonials"
        className="min-h-screen flex flex-col justify-center w-full bg-muted/50"
      >
        <div className="container mx-auto px-32 py-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-6">
            From Confusion to <span className="text-primary">Clarity</span>
          </h2>
          <p className="text-center text-muted-foreground max-w-2xl mx-auto mb-16">
            See how students like you found their perfect university match with
            Unify.
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: "Alex Johnson",
                role: "Computer Science Student at Stanford",
                quote:
                  "Unify's multi-dimensional analysis matched me with Stanford based on my programming projects and collaborative work style. The academic and cultural fit was spot on!",
                matchScore: "95% Match",
              },
              {
                name: "Sarah Chen",
                role: "Business Major at NYU",
                quote:
                  "I was torn between 12 universities until Unify showed me where my profile matched best. The financial feasibility and career connections at NYU were exactly what I needed.",
                matchScore: "92% Match",
              },
              {
                name: "Michael Rodriguez",
                role: "Engineering Student at Georgia Tech",
                quote:
                  "The transparent recommendations showed me why Georgia Tech's hands-on approach and innovation ecosystem would fit my personality and learning style perfectly.",
                matchScore: "89% Match",
              },
            ].map((testimonial, i) => (
              <Card
                key={i}
                className="bg-background border border-border hover:border-primary/50 transition-all duration-300"
              >
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-6">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg
                        key={star}
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                        className="w-4 h-4 text-yellow-500"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ))}
                    <span className="ml-auto text-sm font-medium text-primary">
                      {testimonial.matchScore}
                    </span>
                  </div>
                  <p className="text-muted-foreground mb-6">
                    &quot;{testimonial.quote}&quot;
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-muted"></div>
                    <div>
                      <p className="font-medium">{testimonial.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary text-primary-foreground w-full">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-6">
            Ready to Find Your Perfect University Match?
          </h2>
          <p className="text-xl mb-10 max-w-2xl mx-auto opacity-90">
            Create your profile today and get personalized recommendations based
            on real student experiences.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/profile/setup">
              <Button size="lg" variant="secondary" className="px-8">
                Create Your Profile
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/auth">
              <Button
                size="lg"
                variant="outline"
                className="bg-transparent border-white text-white hover:bg-white/10 px-8"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

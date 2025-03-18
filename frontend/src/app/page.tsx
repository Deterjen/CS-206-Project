import Image from "next/image";
import Link from "next/link";
import { ArrowRight, GraduationCap, Search, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen snap-y snap-proximity overflow-y-scroll h-screen">
      {/* Navigation */}
      <header className="border-b w-full sticky top-0 bg-background/95 z-10">
        <div className="container mx-auto flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            <span className="text-xl font-bold">Unify</span>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="#features" className="text-sm font-medium hover:underline">
              Features
            </Link>
            <Link href="#how-it-works" className="text-sm font-medium hover:underline">
              How It Works
            </Link>
            <Link href="#testimonials" className="text-sm font-medium hover:underline">
              Testimonials
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/profile/setup">
              <Button variant="outline">Sign Up</Button>
            </Link>
            <Link href="/auth">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 md:py-28 w-full snap-center">
        <div className="container mx-auto flex flex-col items-center text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight max-w-3xl">
            Find Your Perfect University Match
          </h1>
          <p className="mt-6 text-xl text-muted-foreground max-w-2xl">
            Personalized university recommendations based on your academic profile, preferences, and goals. Take the
            guesswork out of college applications.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4">
            <Link href="/profile/setup">
              <Button size="lg" className="px-8">
                Create Your Profile
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="#how-it-works">
              <Button size="lg" variant="outline">
                Learn More
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section id="features" className="py-20 bg-muted/50 w-full snap-center">
        <div className="container mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">Why Choose Unify</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 place-items-center">
            <div className="bg-background p-6 rounded-lg shadow-sm text-center max-w-md">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4 mx-auto">
                <UserCircle className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Comprehensive Profiles</h3>
              <p className="text-muted-foreground">
                Create detailed academic profiles including GPA, extracurriculars, achievements, and personal preferences.
              </p>
            </div>
            <div className="bg-background p-6 rounded-lg shadow-sm text-center max-w-md">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4 mx-auto">
                <Search className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Smart Recommendations</h3>
              <p className="text-muted-foreground">
                Our algorithm matches your profile with universities that align with your academic strengths and personal goals.
              </p>
            </div>
            <div className="bg-background p-6 rounded-lg shadow-sm text-center max-w-md">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4 mx-auto">
                <GraduationCap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Detailed Insights</h3>
              <p className="text-muted-foreground">
                Get personalized insights on why each university is a good match, including benefits and potential drawbacks.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 w-full snap-center">
        <div className="container mx-auto px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">How It Works</h2>
          <div className="grid md:grid-cols-2 gap-12 items-center justify-items-center">
            <div>
              <Image
                src="/placeholder.svg?height=400&width=500"
                alt="Profile setup illustration"
                width={500}
                height={400}
                className="rounded-lg shadow-lg"
              />
            </div>
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                  1
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Create Your Profile</h3>
                  <p className="text-muted-foreground">
                    Enter your academic information, extracurricular activities, achievements, and preferences.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                  2
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Upload Documents</h3>
                  <p className="text-muted-foreground">
                    Upload your transcripts and resume to enhance your recommendations.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                  3
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Get Recommendations</h3>
                  <p className="text-muted-foreground">
                    Receive personalized university recommendations based on your profile.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                  4
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Apply with Confidence</h3>
                  <p className="text-muted-foreground">
                    Use our insights to make informed decisions about where to apply.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* University Showcase */}
      <section className="py-20 bg-muted/50 w-full snap-center">
        <div className="container mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-6">Find Your Perfect Match</h2>
          <p className="text-center text-muted-foreground max-w-2xl mx-auto mb-16">
            Our platform connects you with universities that align with your academic profile and personal goals.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 place-items-center">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="bg-background p-10 rounded-lg shadow-sm flex flex-col items-center"
                style={{ minHeight: "300px", maxWidth: "300px" }} // Explicit inline styles as fallback
              >
                <div className="h-40 w-40 rounded-full bg-muted mb-8 flex items-center justify-center">
                  <Image
                    src={`/images/school.svg?text=Uni${i}`}
                    alt={`University ${i}`}
                    width={80}
                    height={80}
                    className="rounded-full"
                  />
                </div>
                <h3 className="text-center font-medium text-xl">University {i}</h3>
              </div>
            ))}
          </div>
          <div className="mt-12 text-center">
            <Link href="/recommendations">
              <Button size="lg">
                Explore Universities
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 w-full snap-center">
        <div className="container mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">What Our Users Say</h2>
          <div className="grid md:grid-cols-3 gap-8 place-items-center">
            {[
              {
                name: "Alex Johnson",
                role: "Computer Science Student",
                quote:
                  "Unify helped me find universities that perfectly matched my academic profile and career goals. I got accepted to my top choice!",
              },
              {
                name: "Sarah Chen",
                role: "Business Major",
                quote:
                  "The detailed insights about each university helped me make an informed decision. The recommendation algorithm is spot on!",
              },
              {
                name: "Michael Rodriguez",
                role: "Engineering Student",
                quote:
                  "I was overwhelmed by all the university options until I used Unify. The personalized recommendations made the process so much easier.",
              },
            ].map((testimonial, i) => (
              <div key={i} className="bg-background p-6 rounded-lg shadow-sm">
                <div className="flex items-center gap-2 mb-4">
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
                </div>
                <p className="text-muted-foreground mb-4">"{testimonial.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-muted"></div>
                  <div>
                    <p className="font-medium">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary text-primary-foreground w-full snap-center">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Find Your Perfect University?</h2>
          <p className="text-xl mb-10 max-w-2xl mx-auto opacity-90">
            Create your profile today and get personalized university recommendations.
          </p>
          <Link href="/auth">
            <Button size="lg" variant="secondary" className="px-8">
              Get Started Now
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 w-full">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 place-items-center">
            <div className="text-center">
              <h3 className="font-semibold mb-4">Unify</h3>
              <div className="flex items-center gap-2 mb-4 justify-center">
                <GraduationCap className="h-5 w-5" />
                <span className="font-medium">Unify</span>
              </div>
              <p className="text-sm text-muted-foreground">Helping students find their perfect university match.</p>
            </div>
            <div className="text-center">
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="#features" className="text-muted-foreground hover:text-foreground">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="#how-it-works" className="text-muted-foreground hover:text-foreground">
                    How It Works
                  </Link>
                </li>
                <li>
                  <Link href="#testimonials" className="text-muted-foreground hover:text-foreground">
                    Testimonials
                  </Link>
                </li>
              </ul>
            </div>
            <div className="text-center">
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="#" className="text-muted-foreground hover:text-foreground">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-muted-foreground hover:text-foreground">
                    University Guide
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-muted-foreground hover:text-foreground">
                    Application Tips
                  </Link>
                </li>
              </ul>
            </div>
            <div className="text-center">
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="#" className="text-muted-foreground hover:text-foreground">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-muted-foreground hover:text-foreground">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-muted-foreground hover:text-foreground">
                    Privacy Policy
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>© {new Date().getFullYear()} Unify. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
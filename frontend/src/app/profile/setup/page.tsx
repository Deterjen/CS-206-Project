"use client"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import Link from "next/link"
import { GraduationCap } from "lucide-react"

const profileFormSchema = z.object({
  fullName: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
  email: z.string().email(),
  gpa: z.string().regex(/^\d*\.?\d*$/, {
    message: "Please enter a valid GPA.",
  }),
  major: z.string().min(1, {
    message: "Please select your major.",
  }),
  extracurriculars: z.string(),
  achievements: z.string(),
})

export default function ProfileSetup() {
  const router = useRouter()
  const form = useForm<z.infer<typeof profileFormSchema>>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      fullName: "",
      email: "",
      gpa: "",
      major: "",
      extracurriculars: "",
      achievements: "",
    },
  })

  function onSubmit(values: z.infer<typeof profileFormSchema>) {
    console.log(values)
    router.push("/profile/dashboard")
  }

  return (
    <div className="container flex h-screen min-w-screen flex-col gap-y-6">
      {/* Navigation */}
        <header className="border-b sticky top-0 bg-background/95 z-10">
          <div className="container flex h-16 items-center justify-between pl-8 pr-4">
            <div className="flex items-center gap-2">
              <GraduationCap className="h-6 w-6" />
              <Link href="/">
                <span className="text-xl font-bold">Unify</span>
              </Link>
            </div>
            <nav className="hidden md:flex items-center gap-x-8 pl-20 mr-10">
              <Link href="/#features" className="text-sm font-medium hover:underline">
                Features
              </Link>
              <Link href="/#how-it-works" className="text-sm font-medium hover:underline">
                How It Works
              </Link>
              <Link href="/#testimonials" className="text-sm font-medium hover:underline">
                Testimonials
              </Link>
            </nav>
          </div>
        </header>
      <div className="flex items-center justify-center">
        <Card>
          <CardHeader>
            <CardTitle>Profile Setup</CardTitle>
            <CardDescription>Complete your profile to get personalized university recommendations.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="fullName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Full Name</FormLabel>
                      <FormControl>
                        <Input placeholder="John Doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input placeholder="john@example.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="gpa"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>GPA</FormLabel>
                      <FormControl>
                        <Input placeholder="4.0" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="major"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Major</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select your major" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="cs">Computer Science</SelectItem>
                          <SelectItem value="business">Business</SelectItem>
                          <SelectItem value="engineering">Engineering</SelectItem>
                          <SelectItem value="arts">Arts & Humanities</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="extracurriculars"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Extracurricular Activities</FormLabel>
                      <FormControl>
                        <Textarea placeholder="List your extracurricular activities..." {...field} />
                      </FormControl>
                      <FormDescription>Include clubs, sports, volunteer work, etc.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="achievements"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Achievements</FormLabel>
                      <FormControl>
                        <Textarea placeholder="List your academic achievements..." {...field} />
                      </FormControl>
                      <FormDescription>Include awards, honors, certifications, etc.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit" className="w-full">
                  Save Profile
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Loader2 } from "lucide-react"
import { RatingScale } from "@/components/ui/rating-scale"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { ProfileFormData } from "@/types/profile"
import { recommendationService } from "@/api/services"

import {
  FIELD_OPTIONS,
  LEARNING_STYLES,
  ACTIVITY_OPTIONS,
  REGION_OPTIONS,
  SETTING_OPTIONS,
  LIVING_OPTIONS,
  FACILITY_OPTIONS,
  PERSONALITY_TRAITS,
  STUDENT_POPULATION_OPTIONS,
} from "@/constants/formOptions"

const profileSchema = z.object({
  // Section 1: Academic Preferences
  preferred_fields: z.array(z.string()).min(1, "Select at least one field"),
  learning_style: z.string().min(1, "Select a learning style"),
  career_goals: z.string().min(1, "Enter your career goals"),
  further_education: z.string(),

  // Section 2: Extracurricular Activities
  culture_importance: z.number().min(1).max(10),
  interested_activities: z.array(z.string()),
  weekly_extracurricular_hours: z.string(),
  passionate_activities: z.string(),

  // Section 3: Career & Network
  internship_importance: z.number().min(1).max(10),
  leadership_interest: z.boolean(),
  alumni_network_value: z.number().min(1).max(10),

  // Section 4: Financial & Location
  affordability_importance: z.number().min(1).max(10),
  yearly_budget: z.number().min(0),
  financial_aid_interest: z.boolean(),
  preferred_region: z.string(),
  preferred_setting: z.string(),
  preferred_living_arrangement: z.string(),

  // Section 5: Personal Preferences
  important_facilities: z.array(z.string()),
  modern_amenities_importance: z.number().min(1).max(10),
  ranking_importance: z.number().min(1).max(10),
  alumni_testimonial_influence: z.number().min(1).max(10),
  important_selection_factors: z.array(z.string()),
  personality_traits: z.array(z.string()),
  preferred_student_population: z.string(),
  lifestyle_preferences: z.string(),
})

export function ProfileSetupForm() {
  const router = useRouter()
  const [currentSection, setCurrentSection] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      preferred_fields: [],
      learning_style: "",
      career_goals: "",
      further_education: "No",
      culture_importance: 5,
      interested_activities: [],
      weekly_extracurricular_hours: "0-5 hours",
      passionate_activities: "",
      internship_importance: 5,
      leadership_interest: false,
      alumni_network_value: 5,
      affordability_importance: 5,
      yearly_budget: 20000,
      financial_aid_interest: false,
      preferred_region: "",
      preferred_setting: "Urban",
      preferred_living_arrangement: "On Campus",
      important_facilities: [],
      modern_amenities_importance: 5,
      ranking_importance: 5,
      alumni_testimonial_influence: 5,
      important_selection_factors: [],
      personality_traits: [],
      preferred_student_population: "Medium",
      lifestyle_preferences: "",
    },
  })

  const onSubmit = async (data: ProfileFormData) => {
    setIsSubmitting(true)
    setError(null)
    try {
      const username = localStorage.getItem("username")
      if (!username) {
        throw new Error("User not found")
      }

      // Validate all required fields
      const requiredFields = {
        preferred_fields: "Preferred fields of study",
        learning_style: "Learning style",
        career_goals: "Career goals",
        culture_importance: "Campus culture importance",
        internship_importance: "Internship importance",
        alumni_network_value: "Alumni network value",
        affordability_importance: "Affordability importance",
        yearly_budget: "Yearly budget",
        preferred_region: "Preferred region",
        preferred_setting: "Campus setting",
        preferred_living_arrangement: "Living arrangement",
        modern_amenities_importance: "Modern amenities importance",
        ranking_importance: "University ranking importance",
        alumni_testimonial_influence: "Alumni testimonial influence",
        preferred_student_population: "Student population preference",
      }

      const missingFields = Object.entries(requiredFields).filter(([key, _]) => {
        const value = data[key as keyof ProfileFormData]
        return value === null || value === undefined || value === "" || (Array.isArray(value) && value.length === 0)
      })

      if (missingFields.length > 0) {
        const missingFieldNames = missingFields.map(([_, label]) => label).join(", ")
        throw new Error(`Please fill in all required fields: ${missingFieldNames}`)
      }

      // Validate numeric fields
      const numericFields = {
        yearly_budget: "Yearly budget",
        culture_importance: "Campus culture importance",
        internship_importance: "Internship importance",
        alumni_network_value: "Alumni network value",
        affordability_importance: "Affordability importance",
        modern_amenities_importance: "Modern amenities importance",
        ranking_importance: "University ranking importance",
        alumni_testimonial_influence: "Alumni testimonial influence",
      }

      const invalidNumericFields = Object.entries(numericFields).filter(([key, _]) => {
        const value = data[key as keyof ProfileFormData]
        return typeof value !== "number" || isNaN(value) || value < 0
      })

      if (invalidNumericFields.length > 0) {
        const invalidFieldNames = invalidNumericFields.map(([_, label]) => label).join(", ")
        throw new Error(`Invalid values for: ${invalidFieldNames}`)
      }

      // Validate array fields
      const arrayFields = {
        preferred_fields: "Preferred fields of study",
        interested_activities: "Interested activities",
        important_facilities: "Important facilities",
        personality_traits: "Personality traits",
      }

      const invalidArrayFields = Object.entries(arrayFields).filter(([key, _]) => {
        const value = data[key as keyof ProfileFormData]
        return !Array.isArray(value)
      })

      if (invalidArrayFields.length > 0) {
        const invalidFieldNames = invalidArrayFields.map(([_, label]) => label).join(", ")
        throw new Error(`Invalid values for: ${invalidFieldNames}`)
      }

      // Validate string fields
      const stringFields = {
        career_goals: "Career goals",
        passionate_activities: "Passionate activities",
        lifestyle_preferences: "Lifestyle preferences",
      }

      const invalidStringFields = Object.entries(stringFields).filter(([key, _]) => {
        const value = data[key as keyof ProfileFormData]
        return typeof value !== "string" || value.trim() === ""
      })

      if (invalidStringFields.length > 0) {
        const invalidFieldNames = invalidStringFields.map(([_, label]) => label).join(", ")
        throw new Error(`Please provide valid text for: ${invalidFieldNames}`)
      }

      // If all validations pass, submit the data
      await recommendationService.saveQuestionnaire(username, data)
      router.push("/recommendations")
    } catch (error) {
      console.error("Error submitting profile:", error)
      setError(error instanceof Error ? error.message : "Failed to save your profile. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderSection = () => {
    switch (currentSection) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Academic Preferences</h2>

            <FormField
              control={form.control}
              name="preferred_fields"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Fields of Study</FormLabel>
                  <div className="grid grid-cols-2 gap-2">
                    {FIELD_OPTIONS.map((option) => (
                      <div key={option} className="flex items-center space-x-2">
                        <Checkbox
                          id={`field-${option}`}
                          checked={Array.isArray(field.value) && field.value.includes(option)}
                          onCheckedChange={(checked) => {
                            const currentValue = Array.isArray(field.value) ? field.value : []
                            if (checked) {
                              field.onChange([...currentValue, option])
                            } else {
                              field.onChange(currentValue.filter((v) => v !== option))
                            }
                          }}
                        />
                        <label
                          htmlFor={`field-${option}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {option}
                        </label>
                      </div>
                    ))}
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="learning_style"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Learning Style</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select your learning style" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {LEARNING_STYLES.map((style) => (
                        <SelectItem key={style} value={style}>
                          {style}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="career_goals"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Career Goals</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Describe your career goals and aspirations..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="further_education"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Plans for Further Education</FormLabel>
                  <RadioGroup onValueChange={field.onChange} defaultValue={field.value}>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="Yes" id="yes" />
                      <label htmlFor="yes">Yes</label>
                      <RadioGroupItem value="No" id="no" />
                      <label htmlFor="no">No</label>
                    </div>
                  </RadioGroup>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Extracurricular Activities</h2>

            <FormField
              control={form.control}
              name="culture_importance"
              render={({ field }) => (
                <FormItem id="culture-importance-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How important is campus culture to you?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="interested_activities"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Interested Activities</FormLabel>
                  <div className="grid grid-cols-2 gap-2">
                    {ACTIVITY_OPTIONS.map((option) => (
                      <div key={option} className="flex items-center space-x-2">
                        <Checkbox
                          id={`activity-${option}`}
                          checked={Array.isArray(field.value) && field.value.includes(option)}
                          onCheckedChange={(checked) => {
                            const currentValue = Array.isArray(field.value) ? field.value : []
                            if (checked) {
                              field.onChange([...currentValue, option])
                            } else {
                              field.onChange(currentValue.filter((v) => v !== option))
                            }
                          }}
                        />
                        <label
                          htmlFor={`activity-${option}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {option}
                        </label>
                      </div>
                    ))}
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="weekly_extracurricular_hours"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Weekly Extracurricular Hours</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select hours" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="0-5 hours">0-5 hours</SelectItem>
                      <SelectItem value="6-10 hours">6-10 hours</SelectItem>
                      <SelectItem value="11-15 hours">11-15 hours</SelectItem>
                      <SelectItem value="15+ hours">15+ hours</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="passionate_activities"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Passionate Activities</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Describe activities you're passionate about..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Career & Network</h2>

            <FormField
              control={form.control}
              name="internship_importance"
              render={({ field }) => (
                <FormItem id="internship-importance-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How important are internship opportunities?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="leadership_interest"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Interested in Leadership Roles</FormLabel>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="alumni_network_value"
              render={({ field }) => (
                <FormItem id="alumni-network-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How important is the alumni network?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        )

      case 4:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Financial & Location</h2>

            <FormField
              control={form.control}
              name="affordability_importance"
              render={({ field }) => (
                <FormItem id="affordability-importance-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How important is affordability?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="yearly_budget"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Yearly Budget (USD)</FormLabel>
                  <FormControl>
                    <Input type="number" {...field} onChange={(e) => field.onChange(Number(e.target.value))} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="financial_aid_interest"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Interested in Financial Aid</FormLabel>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="preferred_region"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Region</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select region" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {REGION_OPTIONS.map((region) => (
                        <SelectItem key={region} value={region}>
                          {region}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="preferred_setting"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Campus Setting</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select setting" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {SETTING_OPTIONS.map((setting) => (
                        <SelectItem key={setting} value={setting}>
                          {setting}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="preferred_living_arrangement"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Living Arrangement</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select arrangement" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {LIVING_OPTIONS.map((option) => (
                        <SelectItem key={option} value={option}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        )

      case 5:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Personal Preferences</h2>

            <FormField
              control={form.control}
              name="important_facilities"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Important Facilities</FormLabel>
                  <div className="grid grid-cols-2 gap-2">
                    {FACILITY_OPTIONS.map((option) => (
                      <div key={option} className="flex items-center space-x-2">
                        <Checkbox
                          id={`facility-${option}`}
                          checked={field.value?.includes(option) || false}
                          onCheckedChange={(checked) => {
                            const currentValue = field.value || []
                            if (checked) {
                              field.onChange([...currentValue, option])
                            } else {
                              field.onChange(currentValue.filter((v) => v !== option))
                            }
                          }}
                        />
                        <label
                          htmlFor={`facility-${option}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {option}
                        </label>
                      </div>
                    ))}
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="modern_amenities_importance"
              render={({ field }) => (
                <FormItem id="modern-amenities-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How important are modern amenities?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="ranking_importance"
              render={({ field }) => (
                <FormItem id="ranking-importance-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How important is university ranking?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="alumni_testimonial_influence"
              render={({ field }) => (
                <FormItem id="alumni-testimonial-field">
                  <RatingScale
                    value={field.value}
                    onChange={(newValue) => {
                      field.onChange(newValue)
                    }}
                    label="How influential are alumni testimonials?"
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="personality_traits"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Personality Traits</FormLabel>
                  <div className="grid grid-cols-2 gap-2">
                    {PERSONALITY_TRAITS.map((trait) => (
                      <div key={trait} className="flex items-center space-x-2">
                        <Checkbox
                          id={`trait-${trait}`}
                          checked={field.value?.includes(trait) || false}
                          onCheckedChange={(checked) => {
                            const currentValue = field.value || []
                            if (checked) {
                              field.onChange([...currentValue, trait])
                            } else {
                              field.onChange(currentValue.filter((v) => v !== trait))
                            }
                          }}
                        />
                        <label
                          htmlFor={`trait-${trait}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {trait}
                        </label>
                      </div>
                    ))}
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="preferred_student_population"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Student Population</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select size" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {STUDENT_POPULATION_OPTIONS.map((option) => (
                        <SelectItem key={option} value={option}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="lifestyle_preferences"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Lifestyle Preferences</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Describe your preferred lifestyle and campus environment..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      {error && (
        <div className="mb-4 p-4 bg-destructive/10 text-destructive rounded-md">
          {error}
        </div>
      )}
      
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          <span className="text-sm text-muted-foreground">Section {currentSection} of 5</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full">
          <div
            className="h-full bg-primary rounded-full transition-all duration-300"
            style={{ width: `${(currentSection / 5) * 100}%` }}
          />
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          {renderSection()}

          <div className="flex justify-between pt-6">
            {currentSection > 1 && (
              <Button type="button" variant="outline" onClick={() => setCurrentSection((prev) => prev - 1)}>
                Previous
              </Button>
            )}

            {currentSection < 5 ? (
              <Button type="button" onClick={() => setCurrentSection((prev) => prev + 1)} className="ml-auto">
                Next
              </Button>
            ) : (
              <Button type="submit" disabled={isSubmitting} className="ml-auto">
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Submitting
                  </>
                ) : (
                  "Submit"
                )}
              </Button>
            )}
          </div>
        </form>
      </Form>
    </div>
  )
}


"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { ProfileFormData, formOptions } from "@/types/profile";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";

const formSchema = z.object({
  // Section 1
  preferredFields: z.array(z.string()).min(1, "Select at least one field"),
  learningStyle: z.string().min(1, "Select a learning style"),
  careerGoals: z.string().min(1, "Please enter your career goals"),
  furtherEducation: z.string().min(1, "Select an option"),

  // Section 2
  campusCultureImportance: z.number().min(1).max(10),
  extracurricularActivities: z.array(z.string()).min(1, "Select at least one activity"),
  extracurricularHours: z.string().min(1, "Select hours"),
  specificActivities: z.string().min(1, "Please enter specific activities"),

  // Section 3
  internshipImportance: z.number().min(1).max(10),
  leadershipInterest: z.string().min(1, "Select an option"),
  alumniNetworkValue: z.number().min(1).max(10),

  // Section 4
  affordabilityImportance: z.number().min(1).max(10),
  budget: z.string().min(1, "Please enter your budget"),
  scholarshipInterest: z.string().min(1, "Select an option"),

  // Section 5
  preferredRegion: z.string().min(1, "Please enter preferred region"),
  campusSetting: z.string().min(1, "Select campus setting"),
  livingArrangement: z.string().min(1, "Select living arrangement"),

  // Section 6
  importantFacilities: z.array(z.string()).min(1, "Select at least one facility"),
  modernAmenitiesImportance: z.number().min(1).max(10),

  // Section 7
  rankingImportance: z.number().min(1).max(10),
  testimonialInfluence: z.number().min(1).max(10),
  importantFactors: z.array(z.string()).min(1, "Select at least one factor"),

  // Section 8
  personalityTraits: z.array(z.string()).min(1, "Select at least one trait"),
  preferredStudentSize: z.string().min(1, "Select student size"),
  lifestylePreferences: z.string().min(1, "Please enter lifestyle preferences"),
});

export function ProfileForm() {
  const [currentSection, setCurrentSection] = useState(1);
  const form = useForm<ProfileFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      preferredFields: [],
      learningStyle: "",
      careerGoals: "",
      furtherEducation: "",
      campusCultureImportance: 5,
      extracurricularActivities: [],
      extracurricularHours: "",
      specificActivities: "",
      internshipImportance: 5,
      leadershipInterest: "",
      alumniNetworkValue: 5,
      affordabilityImportance: 5,
      budget: "",
      scholarshipInterest: "",
      preferredRegion: "",
      campusSetting: "",
      livingArrangement: "",
      importantFacilities: [],
      modernAmenitiesImportance: 5,
      rankingImportance: 5,
      testimonialInfluence: 5,
      importantFactors: [],
      personalityTraits: [],
      preferredStudentSize: "",
      lifestylePreferences: "",
    },
  });

  const router = useRouter();

  const onSubmit = async (data: ProfileFormData) => {
    try {
      // Store the form data in localStorage for now
      // In a real app, you'd send this to your backend
      localStorage.setItem('userProfile', JSON.stringify(data));
      
      // Redirect to the profile dashboard
      router.push('/profile/dashboard');
    } catch (error) {
      console.error('Error submitting profile:', error);
    }
  };

  const nextSection = async () => {
    const isValid = await form.trigger(getFieldsForSection(currentSection));
    if (isValid) {
      setCurrentSection((prev) => Math.min(prev + 1, 8));
    }
  };

  const previousSection = () => {
    setCurrentSection((prev) => Math.max(prev - 1, 1));
  };

  const getFieldsForSection = (section: number): Array<keyof ProfileFormData> => {
    switch (section) {
      case 1:
        return ['preferredFields', 'learningStyle', 'careerGoals', 'furtherEducation'];
      case 2:
        return ['campusCultureImportance', 'extracurricularActivities', 'extracurricularHours', 'specificActivities'];
      case 3:
        return ['internshipImportance', 'leadershipInterest', 'alumniNetworkValue'];
      case 4:
        return ['affordabilityImportance', 'budget', 'scholarshipInterest'];
      case 5:
        return ['preferredRegion', 'campusSetting', 'livingArrangement'];
      case 6:
        return ['importantFacilities', 'modernAmenitiesImportance'];
      case 7:
        return ['rankingImportance', 'testimonialInfluence', 'importantFactors'];
      case 8:
        return ['personalityTraits', 'preferredStudentSize', 'lifestylePreferences'];
      default:
        return [];
    }
  };

  const handleCheckboxChange = (
    field: { onChange: (value: string[]) => void; value?: string[] },
    option: string
  ) => {
    const currentValue = Array.isArray(field.value) ? field.value : [];
    const updatedValue = currentValue.includes(option)
      ? currentValue.filter((value) => value !== option)
      : [...currentValue, option];
    field.onChange(updatedValue);
  };

  const renderSection = () => {
    switch (currentSection) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Academic Interest Similarity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="preferredFields"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Fields of Study</FormLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {formOptions.preferredFields.map((option) => (
                        <FormItem key={option} className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={Array.isArray(field.value) && field.value.includes(option)}
                              onCheckedChange={() => handleCheckboxChange(field, option)}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{option}</FormLabel>
                        </FormItem>
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="learningStyle"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Learning Style</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select learning style" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.learningStyles.map((style) => (
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
                name="careerGoals"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Career Goals</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Describe your career goals..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="furtherEducation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Further Education Plans</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select option" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.furtherEducation.map((option) => (
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
            </CardContent>
          </Card>
        );
      case 2:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Social and Cultural Compatibility</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="campusCultureImportance"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>How important is campus culture to you?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Not Important (1)</span>
                          <span>Extremely Important (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="extracurricularActivities"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Which extracurricular activities interest you?</FormLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {formOptions.extracurricularActivities.map((activity) => (
                        <FormItem key={activity} className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={Array.isArray(field.value) && field.value.includes(activity)}
                              onCheckedChange={() => handleCheckboxChange(field, activity)}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{activity}</FormLabel>
                        </FormItem>
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="extracurricularHours"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Hours per week for extracurricular activities</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select hours" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.extracurricularHours.map((hours) => (
                          <SelectItem key={hours} value={hours}>
                            {hours}
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
                name="specificActivities"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Specific activities you are passionate about</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Describe specific activities you are passionate about..." 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        );
      case 3:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Career Prospects</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="internshipImportance"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>How important are internship opportunities?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Not Important (1)</span>
                          <span>Extremely Important (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="leadershipInterest"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Are you interested in leadership roles?</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select option" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.yesNo.map((option) => (
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
                name="alumniNetworkValue"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>How valuable is the university&apos;s alumni network?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Not Valuable (1)</span>
                          <span>Extremely Valuable (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        );
      case 4:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Financial Feasibility</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="affordabilityImportance"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>How important is affordability to you?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Not Important (1)</span>
                          <span>Extremely Important (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="budget"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Estimated Budget</FormLabel>
                    <FormControl>
                      <Input 
                        type="text"
                        placeholder="Enter your estimated budget..."
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scholarshipInterest"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Are you interested in scholarships?</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select option" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.yesNo.map((option) => (
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
            </CardContent>
          </Card>
        );
      case 5:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Location Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="preferredRegion"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Region</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Enter your preferred region..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="campusSetting"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Campus Setting</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select campus setting" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.campusSettings.map((setting) => (
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
                name="livingArrangement"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Living Arrangement</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select living arrangement" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.livingArrangements.map((arrangement) => (
                          <SelectItem key={arrangement} value={arrangement}>
                            {arrangement}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        );
      case 6:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Campus Facilities</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="importantFacilities"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Which campus facilities are most important to you?</FormLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {formOptions.facilities.map((facility) => (
                        <FormItem key={facility} className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={Array.isArray(field.value) && field.value.includes(facility)}
                              onCheckedChange={() => handleCheckboxChange(field, facility)}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{facility}</FormLabel>
                        </FormItem>
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="modernAmenitiesImportance"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>How important are modern amenities on campus to you?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Not Important (1)</span>
                          <span>Extremely Important (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        );
      case 7:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Reputation and Brand Value</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="rankingImportance"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>How important is the university&apos;s ranking to you?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Not Important (1)</span>
                          <span>Extremely Important (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="testimonialInfluence"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>Do testimonials from alumni influence your decision-making process?</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          value={[value]}
                          onValueChange={(vals) => onChange(vals[0])}
                          {...field}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>No Influence (1)</span>
                          <span>Heavy Influence (10)</span>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="importantFactors"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Which factors are most important when selecting a university?</FormLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {formOptions.importantFactors.map((factor) => (
                        <FormItem key={factor} className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={Array.isArray(field.value) && field.value.includes(factor)}
                              onCheckedChange={() => handleCheckboxChange(field, factor)}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{factor}</FormLabel>
                        </FormItem>
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        );
      case 8:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Personal Fit</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="personalityTraits"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>What personality traits best describe you?</FormLabel>
                    <div className="grid grid-cols-2 gap-2">
                      {formOptions.personalityTraits.map((trait) => (
                        <FormItem key={trait} className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={Array.isArray(field.value) && field.value.includes(trait)}
                              onCheckedChange={() => handleCheckboxChange(field, trait)}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{trait}</FormLabel>
                        </FormItem>
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="preferredStudentSize"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>What size of student population do you prefer on campus?</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value || ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select student size" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {formOptions.studentSizes.map((size) => (
                          <SelectItem key={size} value={size}>
                            {size}
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
                name="lifestylePreferences"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>What lifestyle preferences matter most while studying at university?</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Describe your lifestyle preferences..." 
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        );
      default:
        return null;
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {renderSection()}
        <div className="flex justify-between mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={previousSection}
            disabled={currentSection === 1}
          >
            Previous
          </Button>
          {currentSection < 8 ? (
            <Button type="button" onClick={nextSection}>
              Next
            </Button>
          ) : (
            <Button type="submit">Submit</Button>
          )}
        </div>
      </form>
    </Form>
  );
}

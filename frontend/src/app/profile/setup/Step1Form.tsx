"use client";

import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";

// ---------------------
// 1) Zod schema
// ---------------------
const Step1Schema = z.object({
  preferredFields: z.array(z.string()).min(1, "Select at least one field"),
  preferredFieldsOther: z.string().optional(), // store "other" text if user picks 'other'
  learningStyle: z.string().min(1, "Select your learning style"),
  careerGoals: z.string().min(1, "Describe your career goals"),
  furtherEducation: z.string().min(1, "Select yes/no/undecided"),
});

// ---------------------
// 2) Export the TS type
// ---------------------
export type Step1Data = z.infer<typeof Step1Schema>;

// ---------------------
// 3) Props interface
// ---------------------
interface Step1FormProps {
  // If you want to load previously entered data, add:
  initialData?: Step1Data | null;
  // Parent's "next" callback
  onNext: (data: Step1Data) => void;
  // If you want a Back button, add:
  onBack?: () => void;
}

// ---------------------
// 4) Component
// ---------------------
export default function Step1Form({
  initialData,
  onNext,
  onBack,
}: Step1FormProps) {
  // Use parent's data if present, else empty defaults
  const form = useForm<Step1Data>({
    resolver: zodResolver(Step1Schema),
    defaultValues: initialData || {
      preferredFields: [],
      preferredFieldsOther: "",
      learningStyle: "",
      careerGoals: "",
      furtherEducation: "",
    },
  });

  function handleSubmit(data: Step1Data) {
    onNext(data);
  }

  // The available options, plus "other"
  const fieldOptions = [
    { value: "business", label: "Business" },
    { value: "computing_it", label: "Computing/IT" },
    { value: "engineering", label: "Engineering" },
    { value: "sciences", label: "Sciences" },
    { value: "social_sciences", label: "Social Sciences" },
    { value: "arts_humanities", label: "Arts & Humanities" },
    { value: "medicine_health", label: "Medicine & Health" },
    { value: "law", label: "Law" },
    { value: "education", label: "Education" },
    { value: "other", label: "Other (please specify)" },
  ];

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 1: Academic Interest Similarity</h2>

        {/* Preferred fields (multiple select) */}
        <FormField
          control={form.control}
          name="preferredFields"
          render={() => (
            <FormItem>
              <FormLabel>What are your preferred fields of study or majors?</FormLabel>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {fieldOptions.map((opt) => (
                  <FormField
                    key={opt.value}
                    control={form.control}
                    name="preferredFields"
                    render={({ field }) => {
                      const currentValues = field.value || [];
                      const checked = currentValues.includes(opt.value);
                      return (
                        <FormItem className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={checked}
                              onCheckedChange={(chk) => {
                                if (chk) {
                                  field.onChange([...currentValues, opt.value]);
                                } else {
                                  field.onChange(
                                    currentValues.filter((v) => v !== opt.value)
                                  );
                                }
                              }}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">
                            {opt.label}
                          </FormLabel>
                        </FormItem>
                      );
                    }}
                  />
                ))}
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* If user selected "other", show text field */}
        {form.watch("preferredFields")?.includes("other") && (
          <FormField
            control={form.control}
            name="preferredFieldsOther"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Please specify your other field(s):</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g. Culinary Arts, Architecture, etc."
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Learning style (select) */}
        <FormField
          control={form.control}
          name="learningStyle"
          render={({ field }) => (
            <FormItem>
              <FormLabel>What is your preferred learning style?</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select learning style" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="hands_on">Hands-on/Practical</SelectItem>
                  <SelectItem value="visual">Visual</SelectItem>
                  <SelectItem value="auditory">Auditory</SelectItem>
                  <SelectItem value="theoretical">Theoretical</SelectItem>
                  <SelectItem value="group_based">Group-based</SelectItem>
                  <SelectItem value="self_paced">Self-paced/Individual</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Career goals (open text) */}
        <FormField
          control={form.control}
          name="careerGoals"
          render={({ field }) => (
            <FormItem>
              <FormLabel>What are your career goals or aspirations?</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Describe your career goals..."
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Further education plan */}
        <FormField
          control={form.control}
          name="furtherEducation"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Do you plan to pursue further education after completing your degree?
              </FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Yes, No, or Undecided" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="yes">Yes</SelectItem>
                  <SelectItem value="no">No</SelectItem>
                  <SelectItem value="undecided">Undecided</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-between">
          {/* If you want a back button on Step 1, show it. Otherwise remove. */}
          {onBack && (
            <Button type="button" variant="outline" onClick={onBack}>
              Back
            </Button>
          )}
          <Button type="submit">Next</Button>
        </div>
      </form>
    </Form>
  );
}

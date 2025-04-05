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
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

// Zod schema for Step 2
const Step2Schema = z.object({
  cultureImportance: z.number().min(1).max(10),
  extracurriculars: z.array(z.string()),
  extracurricularsOther: z.string().optional(),
  weeklyHours: z.string().min(1),
  passionateActivities: z.string().min(1),
});

export type Step2Data = z.infer<typeof Step2Schema>;

interface Step2FormProps {
  initialData?: Step2Data | null;
  onNext: (data: Step2Data) => void;
  onBack: () => void;
}

export default function Step2Form({ initialData, onNext, onBack }: Step2FormProps) {
  const form = useForm<Step2Data>({
    resolver: zodResolver(Step2Schema),
    defaultValues: initialData || {
      cultureImportance: 5,
      extracurriculars: [],
      extracurricularsOther: "",
      weeklyHours: "",
      passionateActivities: "",
    },
  });

  function handleSubmit(data: Step2Data) {
    onNext(data);
  }

  // The multi-select options
  const extracurricularOptions = [
    { value: "sports", label: "Sports" },
    { value: "arts_culture", label: "Arts & Culture" },
    { value: "academic_clubs", label: "Academic Clubs" },
    { value: "community_service", label: "Community Service" },
    { value: "professional_clubs", label: "Professional/Career Clubs" },
    { value: "social_clubs", label: "Social Clubs" },
    { value: "other", label: "Other (please specify)" },
  ];

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 2: Social and Cultural Compatibility</h2>

        {/* Range slider: campus culture importance */}
        <FormField
          control={form.control}
          name="cultureImportance"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How important is campus culture to you?</FormLabel>
              <FormControl>
                <div className="flex flex-col space-y-2">
                  <input
                    type="range"
                    min={1}
                    max={10}
                    step={1}
                    value={field.value}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                    className="accent-black"
                  />
                  <div>Value: {field.value}</div>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Extracurriculars (multiple) */}
        <FormField
          control={form.control}
          name="extracurriculars"
          render={() => (
            <FormItem>
              <FormLabel>Which extracurricular activities are you most interested in?</FormLabel>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {extracurricularOptions.map((opt) => (
                  <FormField
                    key={opt.value}
                    control={form.control}
                    name="extracurriculars"
                    render={({ field }) => {
                      const currentValues = field.value || [];
                      const checked = currentValues.includes(opt.value);
                      return (
                        <FormItem className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={checked}
                              onCheckedChange={(c) => {
                                if (c) {
                                  field.onChange([...currentValues, opt.value]);
                                } else {
                                  field.onChange(currentValues.filter((v) => v !== opt.value));
                                }
                              }}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">{opt.label}</FormLabel>
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

        {/* If user selected "other" */}
        {form.watch("extracurriculars")?.includes("other") && (
          <FormField
            control={form.control}
            name="extracurricularsOther"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Please specify other activities:</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. Gaming clubs, language clubs, etc." {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Hours per week (select) */}
        <FormField
          control={form.control}
          name="weeklyHours"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How many hours/week can you dedicate to extracurriculars?</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select hours" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="0 hours">0 (None)</SelectItem>
                  <SelectItem value="1-5 hours">1–5 hours</SelectItem>
                  <SelectItem value="6–10 hours">6–10 hours</SelectItem>
                  <SelectItem value="11-15 hours">11–15 hours</SelectItem>
                  <SelectItem value="16-20 hours">16–20 hours</SelectItem>
                  <SelectItem value="20+ hours">20+ hours</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Passionate activities (text) */}
        <FormField
          control={form.control}
          name="passionateActivities"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Are there any specific activities you are passionate about?</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Describe your passions..."
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-between">
          <Button type="button" variant="outline" onClick={onBack}>
            Back
          </Button>
          <Button type="submit">Next</Button>
        </div>
      </form>
    </Form>
  );
}

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
import { Input } from "@/components/ui/input";

// 1. Zod schema
const Step7Schema = z.object({
  rankingImportance: z.number().min(1).max(10),
  alumniTestimonialInfluence: z.number().min(1).max(10),
  selectionFactors: z.array(z.string()),
  selectionFactorsOther: z.string().optional(),
});

// 2. Type
export type Step7Data = z.infer<typeof Step7Schema>;

interface Step7FormProps {
  initialData?: Step7Data | null;
  onNext: (data: Step7Data) => void;
  onBack: () => void;
}

export default function Step7Form({ initialData, onNext, onBack }: Step7FormProps) {
  const form = useForm<Step7Data>({
    resolver: zodResolver(Step7Schema),
    defaultValues: initialData || {
      rankingImportance: 5,
      alumniTestimonialInfluence: 5,
      selectionFactors: [],
      selectionFactorsOther: "",
    },
  });

  // The multi-select options
  const factorOptions = [
    { value: "academic_reputation", label: "Academic Reputation" },
    { value: "location", label: "Location" },
    { value: "campus_culture", label: "Campus Culture" },
    { value: "affordability", label: "Affordability" },
    { value: "scholarship_opportunities", label: "Scholarship Opportunities" },
    { value: "internship_opportunities", label: "Internship Opportunities" },
    { value: "modern_facilities", label: "Modern Facilities" },
    { value: "alumni_network_strength", label: "Alumni Network Strength" },
    { value: "other", label: "Other (please specify)" },
  ];

  function handleSubmit(data: Step7Data) {
    onNext(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 7: Reputation and Brand Value</h2>

        {/* Ranking importance (range) */}
        <FormField
          control={form.control}
          name="rankingImportance"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How important is the university&apos;s ranking to you?</FormLabel>
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

        {/* Alumni testimonial influence (range) */}
        <FormField
          control={form.control}
          name="alumniTestimonialInfluence"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Do testimonials from alumni influence your decision?</FormLabel>
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

        {/* Important selection factors (multiple with other) */}
        <FormField
          control={form.control}
          name="selectionFactors"
          render={() => (
            <FormItem>
              <FormLabel>Which factors are most important when selecting a university?</FormLabel>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {factorOptions.map((opt) => (
                  <FormField
                    key={opt.value}
                    control={form.control}
                    name="selectionFactors"
                    render={({ field }) => {
                      const current = field.value || [];
                      const checked = current.includes(opt.value);
                      return (
                        <FormItem className="flex items-center space-x-2">
                          <FormControl>
                            <Checkbox
                              checked={checked}
                              onCheckedChange={(c) => {
                                if (c) {
                                  field.onChange([...current, opt.value]);
                                } else {
                                  field.onChange(current.filter((v) => v !== opt.value));
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
        {form.watch("selectionFactors")?.includes("other") && (
          <FormField
            control={form.control}
            name="selectionFactorsOther"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Please specify other selection factor(s):</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. Greek life, family tradition, etc." {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

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

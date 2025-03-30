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
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

// 1. Zod schema
const Step8Schema = z.object({
  personalityTraits: z.array(z.string()),
  personalityTraitsOther: z.string().optional(),
  studentPopulationSize: z.string().min(1, "Select a size"),
  lifestylePreferences: z.string().min(1, "Please describe your preferences"),
});

// 2. Type
export type Step8Data = z.infer<typeof Step8Schema>;

interface Step8FormProps {
  initialData?: Step8Data | null;
  onNext: (data: Step8Data) => void;
  onBack: () => void;
}

export default function Step8Form({ initialData, onNext, onBack }: Step8FormProps) {
  const form = useForm<Step8Data>({
    resolver: zodResolver(Step8Schema),
    defaultValues: initialData || {
      personalityTraits: [],
      personalityTraitsOther: "",
      studentPopulationSize: "",
      lifestylePreferences: "",
    },
  });

  const traitOptions = [
    { value: "extroverted", label: "Extroverted" },
    { value: "introverted", label: "Introverted" },
    { value: "ambivert", label: "Ambivert" },
    { value: "analytical", label: "Analytical" },
    { value: "creative", label: "Creative" },
    { value: "ambitious", label: "Ambitious" },
    { value: "practical_thinker", label: "Practical Thinker" },
    { value: "other", label: "Other (please specify)" },
  ];

  function handleSubmit(data: Step8Data) {
    onNext(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 8: Personal Fit</h2>

        {/* Personality traits (multiple + other) */}
        <FormField
          control={form.control}
          name="personalityTraits"
          render={() => (
            <FormItem>
              <FormLabel>What personality traits best describe you?</FormLabel>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {traitOptions.map((opt) => (
                  <FormField
                    key={opt.value}
                    control={form.control}
                    name="personalityTraits"
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
        {form.watch("personalityTraits")?.includes("other") && (
          <FormField
            control={form.control}
            name="personalityTraitsOther"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Please specify other trait(s):</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. Organized, empathetic, etc." {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Student population size (select) */}
        <FormField
          control={form.control}
          name="studentPopulationSize"
          render={({ field }) => (
            <FormItem>
              <FormLabel>What size of student population do you prefer?</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select size" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="small">&lt;5K students (Small)</SelectItem>
                  <SelectItem value="medium">~10K students (Medium)</SelectItem>
                  <SelectItem value="large">&gt;20K students (Large)</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Lifestyle preferences (text) */}
        <FormField
          control={form.control}
          name="lifestylePreferences"
          render={({ field }) => (
            <FormItem>
              <FormLabel>What lifestyle preferences matter most while studying?</FormLabel>
              <FormControl>
                <Textarea placeholder="Describe your lifestyle preferences..." className="resize-none" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-between">
          <Button type="button" variant="outline" onClick={onBack}>
            Back
          </Button>
          {/* On step 8, we'll call onNext => triggers final submit in parent */}
          <Button type="submit">Submit</Button>
        </div>
      </form>
    </Form>
  );
}

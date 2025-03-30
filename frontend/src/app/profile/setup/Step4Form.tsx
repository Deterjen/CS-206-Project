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
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

// 1. Zod schema
const Step4Schema = z.object({
  affordabilityImportance: z.number().min(1).max(10),
  yearlyBudget: z
    .string()
    .min(1, "Please enter your budget") // you can also parse it as number if you prefer
    .regex(/^\d+(\.\d+)?$/, "Budget must be numeric"), // optional numeric validation
  financialAidInterest: z.string().min(1, "Select yes or no"),
});

// 2. Type
export type Step4Data = z.infer<typeof Step4Schema>;

interface Step4FormProps {
  initialData?: Step4Data | null;
  onNext: (data: Step4Data) => void;
  onBack: () => void;
}

export default function Step4Form({ initialData, onNext, onBack }: Step4FormProps) {
  const form = useForm<Step4Data>({
    resolver: zodResolver(Step4Schema),
    defaultValues: initialData || {
      affordabilityImportance: 5,
      yearlyBudget: "",
      financialAidInterest: "",
    },
  });

  function handleSubmit(data: Step4Data) {
    onNext(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 4: Financial Feasibility</h2>

        {/* Affordability importance (range) */}
        <FormField
          control={form.control}
          name="affordabilityImportance"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How important is affordability when choosing a university?</FormLabel>
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

        {/* Budget (open ended numeric) */}
        <FormField
          control={form.control}
          name="yearlyBudget"
          render={({ field }) => (
            <FormItem>
              <FormLabel>What is your budget for tuition and living expenses per year?</FormLabel>
              <FormControl>
                <Input placeholder="e.g. 20000" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Financial aid interest */}
        <FormField
          control={form.control}
          name="financialAidInterest"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Are you looking for scholarships or financial aid?</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Yes or No" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="yes">Yes</SelectItem>
                  <SelectItem value="no">No</SelectItem>
                </SelectContent>
              </Select>
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

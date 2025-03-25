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
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

// 1. Zod schema
const Step3Schema = z.object({
  internshipImportance: z.number().min(1).max(10),
  leadershipInterest: z.string().min(1, "Select yes or no"),
  alumniNetworkValue: z.number().min(1).max(10),
});

// 2. Type for parent
export type Step3Data = z.infer<typeof Step3Schema>;

interface Step3FormProps {
  initialData?: Step3Data | null;
  onNext: (data: Step3Data) => void;
  onBack: () => void;
}

export default function Step3Form({ initialData, onNext, onBack }: Step3FormProps) {
  const form = useForm<Step3Data>({
    resolver: zodResolver(Step3Schema),
    defaultValues: initialData || {
      internshipImportance: 5,
      leadershipInterest: "",
      alumniNetworkValue: 5,
    },
  });

  function handleSubmit(data: Step3Data) {
    onNext(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 3: Career Prospects</h2>

        {/* Internship importance (range 1–10) */}
        <FormField
          control={form.control}
          name="internshipImportance"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How important are internship opportunities during your studies?</FormLabel>
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

        {/* Leadership interest (select) */}
        <FormField
          control={form.control}
          name="leadershipInterest"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Are you interested in leadership roles during university?</FormLabel>
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

        {/* Alumni network value (range 1–10) */}
        <FormField
          control={form.control}
          name="alumniNetworkValue"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How valuable is the university&apos;s alumni network?</FormLabel>
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

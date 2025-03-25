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
const Step5Schema = z.object({
  preferredRegion: z.string().min(1, "Please enter a region or country"),
  preferredSetting: z.string().min(1, "Select urban or rural"),
  preferredLivingArrangement: z.string().min(1, "Select a living arrangement"),
});

// 2. Type
export type Step5Data = z.infer<typeof Step5Schema>;

interface Step5FormProps {
  initialData?: Step5Data | null;
  onNext: (data: Step5Data) => void;
  onBack: () => void;
}

export default function Step5Form({ initialData, onNext, onBack }: Step5FormProps) {
  const form = useForm<Step5Data>({
    resolver: zodResolver(Step5Schema),
    defaultValues: initialData || {
      preferredRegion: "",
      preferredSetting: "",
      preferredLivingArrangement: "",
    },
  });

  function handleSubmit(data: Step5Data) {
    onNext(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 5: Geographic Preferences</h2>

        {/* Region or country (text) */}
        <FormField
          control={form.control}
          name="preferredRegion"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Which region or country do you prefer to study in?</FormLabel>
              <FormControl>
                <Input placeholder="e.g. United States, Europe, Asia..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Urban or rural */}
        <FormField
          control={form.control}
          name="preferredSetting"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Would you prefer an urban or rural campus setting?</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select setting" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="urban">Urban</SelectItem>
                  <SelectItem value="rural">Rural</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Living arrangement */}
        <FormField
          control={form.control}
          name="preferredLivingArrangement"
          render={({ field }) => (
            <FormItem>
              <FormLabel>What is your preferred living arrangement?</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select arrangement" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="on_campus">On Campus</SelectItem>
                  <SelectItem value="off_campus">Off Campus</SelectItem>
                  <SelectItem value="commute">Commute from Home</SelectItem>
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

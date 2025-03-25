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
const Step6Schema = z.object({
  importantFacilities: z.array(z.string()),
  importantFacilitiesOther: z.string().optional(),
  modernAmenitiesImportance: z.number().min(1).max(10),
});

// 2. Type
export type Step6Data = z.infer<typeof Step6Schema>;

interface Step6FormProps {
  initialData?: Step6Data | null;
  onNext: (data: Step6Data) => void;
  onBack: () => void;
}

export default function Step6Form({ initialData, onNext, onBack }: Step6FormProps) {
  const form = useForm<Step6Data>({
    resolver: zodResolver(Step6Schema),
    defaultValues: initialData || {
      importantFacilities: [],
      importantFacilitiesOther: "",
      modernAmenitiesImportance: 5,
    },
  });

  const facilityOptions = [
    { value: "sports_facilities", label: "Sports Facilities" },
    { value: "libraries", label: "Libraries and Study Spaces" },
    { value: "on_campus_housing", label: "On-Campus Housing" },
    { value: "support_centers", label: "Religious/Minority Support Centers" },
    { value: "modern_amenities", label: "Modern Amenities" },
    { value: "other", label: "Other (please specify)" },
  ];

  function handleSubmit(data: Step6Data) {
    onNext(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <h2 className="text-lg font-semibold">Section 6: Campus Facilities</h2>

        {/* Facilities (multiple with other) */}
        <FormField
          control={form.control}
          name="importantFacilities"
          render={() => (
            <FormItem>
              <FormLabel>Which campus facilities are most important to you?</FormLabel>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {facilityOptions.map((opt) => (
                  <FormField
                    key={opt.value}
                    control={form.control}
                    name="importantFacilities"
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
        {form.watch("importantFacilities")?.includes("other") && (
          <FormField
            control={form.control}
            name="importantFacilitiesOther"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Please specify other facility requirements:</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. Childcare center, music rooms, etc." {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Modern amenities importance (range) */}
        <FormField
          control={form.control}
          name="modernAmenitiesImportance"
          render={({ field }) => (
            <FormItem>
              <FormLabel>How important are modern amenities on campus?</FormLabel>
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


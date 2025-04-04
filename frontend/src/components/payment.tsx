"use client"
import { X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"

interface PaymentPopupProps {
  isOpen: boolean
  onClose: () => void
  onSelectPlan: (plan: "monthly" | "quarterly" | "annual" | "lifetime" | null) => void
}

export default function PaymentPopup({ isOpen, onClose, onSelectPlan }: PaymentPopupProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-4xl animate-in fade-in zoom-in duration-300">
        <Card className="border-2">
          <CardHeader className="relative pb-2">
            <Button variant="ghost" size="icon" className="absolute right-4 top-4" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
            <CardTitle className="text-xl">Upgrade Your Experience</CardTitle>
            <CardDescription>Choose a plan that works for you</CardDescription>
          </CardHeader>

          <CardContent className="pt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Monthly Plan */}
              <Card
                className="border hover:border-primary transition-colors cursor-pointer"
                onClick={() => onSelectPlan("monthly")}
              >
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="font-bold text-lg">Monthly</h3>
                    <p className="text-sm text-muted-foreground">Flexible option</p>
                  </div>

                  <div className="flex items-baseline mb-2">
                    <span className="text-3xl font-bold">$6</span>
                    <span className="text-muted-foreground ml-1">/month</span>
                  </div>
                </CardContent>
              </Card>

              {/* Quarterly Plan */}
              <Card
                className="border hover:border-primary transition-colors cursor-pointer relative"
                onClick={() => onSelectPlan("quarterly")}
              >
                <div className="absolute right-4 top-4 bg-primary/10 text-primary px-2 py-1 rounded-full text-xs font-medium">
                  Popular
                </div>
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="font-bold text-lg">Quarterly</h3>
                    <p className="text-sm text-muted-foreground">3-month access</p>
                  </div>

                  <div className="flex items-baseline mb-2">
                    <span className="text-3xl font-bold">$15</span>
                    <span className="text-muted-foreground ml-1">/3 months</span>
                  </div>

                  <div className="text-xs text-green-600 font-medium">
                    Save 17% compared to monthly
                  </div>
                </CardContent>
              </Card>

              {/* Annual Plan */}
              <Card
                className="border hover:border-primary transition-colors cursor-pointer relative"
                onClick={() => onSelectPlan("annual")}
              >
                <div className="absolute right-4 top-4 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                  Best Value
                </div>
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="font-bold text-lg">Annual</h3>
                    <p className="text-sm text-muted-foreground">12-month access</p>
                  </div>

                  <div className="flex items-baseline mb-2">
                    <span className="text-3xl font-bold">$30</span>
                    <span className="text-muted-foreground ml-1">/year</span>
                  </div>

                  <div className="text-xs text-green-600 font-medium">
                    Save 58% compared to monthly
                  </div>
                </CardContent>
              </Card>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button variant="ghost" className="w-full text-muted-foreground" onClick={() => onSelectPlan(null)}>
              No, thank you
            </Button>

            <p className="text-xs text-center text-muted-foreground">
              By subscribing, you agree to our Terms of Service and Privacy Policy. You can cancel your subscription at
              any time.
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
"use client"
import { Check, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

interface PaymentPopupProps {
  isOpen: boolean
  onClose: () => void
  onSelectPlan: (plan: "quarterly" | "annual" | null) => void
}

export default function PaymentPopup({ isOpen, onClose, onSelectPlan }: PaymentPopupProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-md animate-in fade-in zoom-in duration-300">
        <Card className="border-2">
          <CardHeader className="relative pb-2">
            <Button variant="ghost" size="icon" className="absolute right-4 top-4" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
            <CardTitle className="text-xl">Upgrade Your Experience</CardTitle>
            <CardDescription>Get unlimited access to all premium features</CardDescription>
          </CardHeader>

          <CardContent className="pt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Quarterly Plan */}
              <Card
                className="border-2 hover:border-primary transition-colors cursor-pointer"
                onClick={() => onSelectPlan("quarterly")}
              >
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-lg">Quarterly</h3>
                      <p className="text-sm text-muted-foreground">3-month access</p>
                    </div>
                    <div className="bg-primary/10 text-primary px-2 py-1 rounded-full text-xs font-medium">Popular</div>
                  </div>

                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold">$15</span>
                    <span className="text-muted-foreground ml-1">/3 months</span>
                  </div>

                  <Separator />

                  <ul className="space-y-2">
                    <li className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm">Full university profiles</span>
                    </li>
                    <li className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm">Connect with similar students</span>
                    </li>
                    <li className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm">Personalized recommendations</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              {/* Annual Plan */}
              <Card
                className="border-2 border-primary hover:bg-primary/5 transition-colors cursor-pointer"
                onClick={() => onSelectPlan("annual")}
              >
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-lg">Annual</h3>
                      <p className="text-sm text-muted-foreground">12-month access</p>
                    </div>
                    <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                      Best Value
                    </div>
                  </div>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold">$30</span>
                    <span className="text-muted-foreground ml-1">/year</span>
                  </div>

                  <div className="text-xs text-green-600 font-medium">Save 50% compared to quarterly plan</div>

                  <Separator />

                  <ul className="space-y-2">
                    <li className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm">All quarterly features</span>
                    </li>
                    <li className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm">Priority customer support</span>
                    </li>
                    <li className="flex items-start">
                      <Check className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm">Early access to new features</span>
                    </li>
                  </ul>
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

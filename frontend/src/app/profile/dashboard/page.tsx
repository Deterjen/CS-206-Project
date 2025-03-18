"use client"
import { Bell, GraduationCapIcon as Graduation, User } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileUpload } from "@/components/file-upload"

export default function ProfileDashboard() {
  return (
    <div className="container py-10 px-12">
      <h1 className="text-3xl font-bold mb-8">Profile Dashboard</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>Manage your personal details</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <User className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium">John Doe</p>
                <p className="text-sm text-muted-foreground">john@example.com</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Academic Details</CardTitle>
            <CardDescription>Your academic information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Graduation className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium">Computer Science</p>
                <p className="text-sm text-muted-foreground">GPA: 3.8</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
            <CardDescription>Recent updates and deadlines</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Bell className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium">2 New Updates</p>
                <p className="text-sm text-muted-foreground">Check your notifications</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2 lg:col-span-3">
          <CardHeader>
            <CardTitle>Documents</CardTitle>
            <CardDescription>Upload your transcripts and resume</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <h3 className="font-medium mb-2">Transcript</h3>
                <FileUpload
                  onUpload={async (file) => {
                    // Handle file upload
                    console.log("Uploading transcript:", file)
                  }}
                />
              </div>
              <div>
                <h3 className="font-medium mb-2">Resume</h3>
                <FileUpload
                  onUpload={async (file) => {
                    // Handle file upload
                    console.log("Uploading resume:", file)
                  }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
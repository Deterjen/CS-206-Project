"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { ArrowLeft, Check, ChevronDown, Info, MapPin, Plus, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface University {
    id: string;
    name: string;
    location: string;
    logo: string;
    matchScore: number;
    admissionRate: string;
    tuition: string;
    ranking: string;
    studentFacultyRatio: string;
    acceptanceRate: string;
    averageGPA: string;
    averageSAT: string;
    programs: string[];
    campusSize: string;
    housingOptions: string[];
    studentLife: string[];
    internationalStudents: string;
    financialAid: string;
    strengths: string[];
    weaknesses: string[];
  }  

// Sample university data
const universities: University[] = [
  {
    id: "1",
    name: "Singapore Management University",
    location: "Singapore",
    logo: "/placeholder.svg",
    matchScore: 95,
    admissionRate: "25%",
    tuition: "$36,000/year",
    ranking: "#11 in Asia",
    studentFacultyRatio: "15:1",
    acceptanceRate: "25%",
    averageGPA: "3.8",
    averageSAT: "1450",
    programs: ["Business", "Computer Science", "Economics", "Law"],
    campusSize: "Urban, 4.5 acres",
    housingOptions: ["On-campus dorms", "Off-campus apartments"],
    studentLife: ["100+ student organizations", "Active campus community"],
    internationalStudents: "20%",
    financialAid: "Available for international students",
    strengths: ["Strong industry connections", "Prime city location", "Excellent job placement"],
    weaknesses: ["Limited campus size", "Higher cost of living", "Competitive environment"],
  },
  {
    id: "2",
    name: "National University of Singapore",
    location: "Singapore",
    logo: "/placeholder.svg",
    matchScore: 88,
    admissionRate: "20%",
    tuition: "$32,000/year",
    ranking: "#3 in Asia",
    studentFacultyRatio: "18:1",
    acceptanceRate: "20%",
    averageGPA: "3.9",
    averageSAT: "1480",
    programs: ["Engineering", "Medicine", "Computer Science", "Business", "Arts"],
    campusSize: "Suburban, 150 acres",
    housingOptions: ["On-campus dorms", "Residential colleges", "Off-campus apartments"],
    studentLife: ["200+ student organizations", "Vibrant campus life"],
    internationalStudents: "25%",
    financialAid: "Merit scholarships available",
    strengths: ["Research opportunities", "Comprehensive programs", "Strong global reputation"],
    weaknesses: ["Large class sizes", "Competitive atmosphere", "Spread out campus"],
  },
  {
    id: "3",
    name: "Nanyang Technological University",
    location: "Singapore",
    logo: "/placeholder.svg",
    matchScore: 82,
    admissionRate: "30%",
    tuition: "$30,000/year",
    ranking: "#5 in Asia",
    studentFacultyRatio: "17:1",
    acceptanceRate: "30%",
    averageGPA: "3.7",
    averageSAT: "1420",
    programs: ["Engineering", "Science", "Business", "Humanities", "Art & Design"],
    campusSize: "Suburban, 200 acres",
    housingOptions: ["On-campus halls", "Student apartments"],
    studentLife: ["120+ student clubs", "Sports facilities"],
    internationalStudents: "22%",
    financialAid: "Need-based and merit scholarships",
    strengths: ["Modern facilities", "Strong STEM programs", "Beautiful campus"],
    weaknesses: ["Distance from city center", "Less business connections", "Fewer internship opportunities"],
  },
  {
    id: "4",
    name: "Hong Kong University",
    location: "Hong Kong",
    logo: "/placeholder.svg",
    matchScore: 79,
    admissionRate: "18%",
    tuition: "$38,000/year",
    ranking: "#4 in Asia",
    studentFacultyRatio: "16:1",
    acceptanceRate: "18%",
    averageGPA: "3.85",
    averageSAT: "1460",
    programs: ["Business", "Law", "Medicine", "Engineering", "Social Sciences"],
    campusSize: "Urban, 40 acres",
    housingOptions: ["Residential halls", "Off-campus housing"],
    studentLife: ["150+ student societies", "Cultural events"],
    internationalStudents: "30%",
    financialAid: "Limited scholarships for international students",
    strengths: ["Global perspective", "Strong alumni network", "Excellent location"],
    weaknesses: ["High cost of living", "Limited campus space", "Competitive admission"],
  },
]

export default function ComparisonPage() {
  const [selectedUniversities, setSelectedUniversities] = useState([universities[0], universities[1]])
  const [activeTab, setActiveTab] = useState("overview")

  const addUniversity = (university: University) => {
    if (selectedUniversities.length < 3 && !selectedUniversities.find((u) => u.id === university.id)) {
      setSelectedUniversities([...selectedUniversities, university])
    }
  }

  const removeUniversity = (universityId: string) => {
    if (selectedUniversities.length > 1) {
      setSelectedUniversities(selectedUniversities.filter((u) => u.id !== universityId))
    }
  }

  const replaceUniversity = (index: number, university: University) => {
    const newSelection = [...selectedUniversities]
    newSelection[index] = university
    setSelectedUniversities(newSelection)
  }

  return (
    <div className="min-h-screen flex flex-col px-12">
      <header className="border-b">
        <div className="container py-4">
          <div className="flex items-center justify-between">
            <Link
              href="/recommendations"
              className="flex items-center text-sm font-medium text-muted-foreground hover:text-primary"
            >
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back to Recommendations
            </Link>
            <h1 className="text-xl font-bold pr-12">University Comparison</h1>
            <div className="w-[100px]"></div> {/* Spacer for centering */}
          </div>
        </div>
      </header>

      <main className="flex-1 container py-6">
        {/* University Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {selectedUniversities.map((university, index) => (
            <Card key={university.id} className="relative">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-between">
                        <div className="flex items-center">
                          <Image
                            src={university.logo || "/placeholder.svg"}
                            alt={university.name}
                            width={24}
                            height={24}
                            className="mr-2 rounded-full"
                          />
                          <span className="truncate">{university.name}</span>
                        </div>
                        <ChevronDown className="h-4 w-4 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[300px] p-0" align="start">
                      <ScrollArea className="h-[300px]">
                        <div className="p-2">
                          {universities.map((uni) => (
                            <div
                              key={uni.id}
                              className={`flex items-center justify-between p-2 rounded-md cursor-pointer hover:bg-muted ${
                                university.id === uni.id ? "bg-muted" : ""
                              }`}
                              onClick={() => replaceUniversity(index, uni)}
                            >
                              <div className="flex items-center">
                                <Image
                                  src={uni.logo || "/placeholder.svg"}
                                  alt={uni.name}
                                  width={24}
                                  height={24}
                                  className="mr-2 rounded-full"
                                />
                                <span>{uni.name}</span>
                              </div>
                              {university.id === uni.id && <Check className="h-4 w-4" />}
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </PopoverContent>
                  </Popover>
                  {selectedUniversities.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 h-6 w-6"
                      onClick={() => removeUniversity(university.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                <div className="flex items-center text-sm text-muted-foreground mb-2">
                  <MapPin className="h-4 w-4 mr-1" />
                  {university.location}
                </div>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="bg-primary/10">
                    Match: {university.matchScore}%
                  </Badge>
                  <Badge variant="outline" className="bg-muted">
                    {university.ranking}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}

          {selectedUniversities.length < 3 && (
            <Card className="border-dashed">
              <CardContent className="p-4 flex items-center justify-center h-full">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="ghost" className="h-full w-full flex flex-col items-center gap-2">
                      <Plus className="h-6 w-6" />
                      <span>Add University</span>
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-[300px] p-0" align="start">
                    <ScrollArea className="h-[300px]">
                      <div className="p-2">
                        {universities
                          .filter((uni) => !selectedUniversities.find((u) => u.id === uni.id))
                          .map((uni) => (
                            <div
                              key={uni.id}
                              className="flex items-center p-2 rounded-md cursor-pointer hover:bg-muted"
                              onClick={() => addUniversity(uni)}
                            >
                              <Image
                                src={uni.logo || "/placeholder.svg"}
                                alt={uni.name}
                                width={24}
                                height={24}
                                className="mr-2 rounded-full"
                              />
                              <span>{uni.name}</span>
                            </div>
                          ))}
                      </div>
                    </ScrollArea>
                  </PopoverContent>
                </Popover>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Comparison Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-5 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="academics">Academics</TabsTrigger>
            <TabsTrigger value="admissions">Admissions</TabsTrigger>
            <TabsTrigger value="campus">Campus Life</TabsTrigger>
            <TabsTrigger value="costs">Costs & Aid</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Criteria</TableHead>
                  {selectedUniversities.map((uni) => (
                    <TableHead key={uni.id}>{uni.name}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Location</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.location}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Ranking</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.ranking}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Admission Rate</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.admissionRate}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Tuition</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.tuition}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Student-Faculty Ratio</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.studentFacultyRatio}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">International Students</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.internationalStudents}</TableCell>
                  ))}
                </TableRow>
              </TableBody>
            </Table>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {selectedUniversities.map((uni) => (
                <Card key={uni.id}>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-lg mb-3">{uni.name} Highlights</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Strengths</h4>
                        <ul className="space-y-1">
                          {uni.strengths.map((strength, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm">
                              <Check className="h-4 w-4 text-green-500 mt-0.5" />
                              <span>{strength}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Considerations</h4>
                        <ul className="space-y-1">
                          {uni.weaknesses.map((weakness, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm">
                              <Info className="h-4 w-4 text-amber-500 mt-0.5" />
                              <span>{weakness}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Academics Tab */}
          <TabsContent value="academics" className="space-y-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Programs</TableHead>
                  {selectedUniversities.map((uni) => (
                    <TableHead key={uni.id}>{uni.name}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {["Business", "Computer Science", "Engineering", "Medicine", "Law", "Arts & Humanities"].map(
                  (program) => (
                    <TableRow key={program}>
                      <TableCell className="font-medium">{program}</TableCell>
                      {selectedUniversities.map((uni) => (
                        <TableCell key={uni.id}>
                          {uni.programs.includes(program) ? (
                            <Check className="h-5 w-5 text-green-500" />
                          ) : (
                            <X className="h-5 w-5 text-muted-foreground" />
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ),
                )}
              </TableBody>
            </Table>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {selectedUniversities.map((uni) => (
                <Card key={uni.id}>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-lg mb-3">{uni.name}</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Available Programs</h4>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {uni.programs.map((program, idx) => (
                            <Badge key={idx} variant="secondary">
                              {program}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Student-Faculty Ratio</h4>
                        <p className="text-sm">{uni.studentFacultyRatio}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Admissions Tab */}
          <TabsContent value="admissions" className="space-y-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Criteria</TableHead>
                  {selectedUniversities.map((uni) => (
                    <TableHead key={uni.id}>{uni.name}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Acceptance Rate</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.acceptanceRate}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Average GPA</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.averageGPA}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Average SAT</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.averageSAT}</TableCell>
                  ))}
                </TableRow>
              </TableBody>
            </Table>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {selectedUniversities.map((uni) => (
                <Card key={uni.id}>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-lg mb-3">{uni.name}</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Admission Difficulty</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-primary rounded-full h-2"
                              style={{
                                width: `${100 - Number.parseInt(uni.acceptanceRate)}%`,
                              }}
                            ></div>
                          </div>
                          <span className="text-xs">{uni.acceptanceRate}</span>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Application Requirements</h4>
                        <ul className="space-y-1 text-sm">
                          <li>• Transcripts</li>
                          <li>• Standardized test scores</li>
                          <li>• Personal statement</li>
                          <li>• Letters of recommendation</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Campus Life Tab */}
          <TabsContent value="campus" className="space-y-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Criteria</TableHead>
                  {selectedUniversities.map((uni) => (
                    <TableHead key={uni.id}>{uni.name}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Campus Size</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.campusSize}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Housing Options</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>
                      <ul className="list-disc list-inside">
                        {uni.housingOptions.map((option, idx) => (
                          <li key={idx} className="text-sm">
                            {option}
                          </li>
                        ))}
                      </ul>
                    </TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Student Life</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>
                      <ul className="list-disc list-inside">
                        {uni.studentLife.map((item, idx) => (
                          <li key={idx} className="text-sm">
                            {item}
                          </li>
                        ))}
                      </ul>
                    </TableCell>
                  ))}
                </TableRow>
              </TableBody>
            </Table>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {selectedUniversities.map((uni) => (
                <Card key={uni.id}>
                  <CardContent className="p-0">
                    <div className="relative h-40 w-full">
                      <Image
                        src="/placeholder.svg?height=200&width=400"
                        alt={`${uni.name} campus`}
                        fill
                        className="object-cover rounded-t-lg"
                      />
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-lg mb-2">{uni.name}</h3>
                      <p className="text-sm text-muted-foreground mb-3">
                        {uni.location} • {uni.campusSize.split(",")[0]} Campus
                      </p>
                      <Separator className="my-3" />
                      <div className="space-y-2">
                        <div>
                          <h4 className="font-medium text-sm">Housing</h4>
                          <p className="text-sm text-muted-foreground">{uni.housingOptions.join(", ")}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Costs & Aid Tab */}
          <TabsContent value="costs" className="space-y-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Criteria</TableHead>
                  {selectedUniversities.map((uni) => (
                    <TableHead key={uni.id}>{uni.name}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Tuition</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.tuition}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Financial Aid</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>{uni.financialAid}</TableCell>
                  ))}
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Estimated Total Cost</TableCell>
                  {selectedUniversities.map((uni) => (
                    <TableCell key={uni.id}>
                      {`$${(Number.parseInt(uni.tuition.replace(/[^0-9]/g, "")) + 15000).toLocaleString()}/year`}
                    </TableCell>
                  ))}
                </TableRow>
              </TableBody>
            </Table>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {selectedUniversities.map((uni) => (
                <Card key={uni.id}>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-lg mb-3">{uni.name}</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Cost Breakdown</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Tuition</span>
                            <span>{uni.tuition}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Housing & Meals</span>
                            <span>$12,000/year</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Books & Supplies</span>
                            <span>$1,200/year</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Personal Expenses</span>
                            <span>$1,800/year</span>
                          </div>
                          <Separator className="my-1" />
                          <div className="flex justify-between font-medium">
                            <span>Total</span>
                            <span>{`$${(Number.parseInt(uni.tuition.replace(/[^0-9]/g, "")) + 15000).toLocaleString()}/year`}</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm text-muted-foreground mb-1">Financial Aid</h4>
                        <p className="text-sm">{uni.financialAid}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      <footer className="border-t py-6">
        <div className="container flex justify-between items-center">
          <p className="text-sm text-muted-foreground">
            Data is for comparison purposes only. Please verify with each university.
          </p>
          <div className="flex gap-4">
            <Button variant="outline" size="sm" asChild>
              <Link href="/recommendations">Back to Recommendations</Link>
            </Button>
            <Select>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Export Comparison" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">Export as PDF</SelectItem>
                <SelectItem value="csv">Export as CSV</SelectItem>
                <SelectItem value="email">Email Comparison</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </footer>
    </div>
  )
}


"use client";

import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from "recharts";

const MatchingAlgorithmVisualization = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [animationTriggered, setAnimationTriggered] = useState(false);

  // Sample data for student profile
  const studentProfile = {
    name: "Alex",
    interests: ["Computer Science", "AI", "Data Science"],
    preferences: {
      academic: 8.5,
      social: 7.0,
      financial: 6.5,
      career: 9.0,
      geographic: 5.5,
      facilities: 6.0,
      reputation: 8.0,
      personalFit: 7.5,
    },
  };

  // Sample university match data
  const universityMatches = [
    { name: "Stanford", score: 95, color: "#3366cc" },
    { name: "MIT", score: 88, color: "#dc3912" },
    { name: "Berkeley", score: 83, color: "#ff9900" },
    { name: "Harvard", score: 80, color: "#109618" },
    { name: "CMU", score: 78, color: "#990099" },
  ];

  // Dimension comparison data for top match
  const dimensionData = [
    { dimension: "Academic", userScore: 8.5, matchScore: 9.2 },
    { dimension: "Social", userScore: 7.0, matchScore: 7.5 },
    { dimension: "Financial", userScore: 6.5, matchScore: 6.0 },
    { dimension: "Career", userScore: 9.0, matchScore: 9.5 },
    { dimension: "Geographic", userScore: 5.5, matchScore: 6.0 },
    { dimension: "Facilities", userScore: 6.0, matchScore: 7.2 },
    { dimension: "Reputation", userScore: 8.0, matchScore: 9.8 },
    { dimension: "Personal Fit", userScore: 7.5, matchScore: 8.0 },
  ];

  // Radar chart data
  const radarData = dimensionData.map((item) => ({
    dimension: item.dimension,
    userPreference: item.userScore,
    universityScore: item.matchScore,
  }));

  // Trigger the step-by-step animation
  useEffect(() => {
    if (!animationTriggered) return;

    const timer = setTimeout(() => {
      if (activeStep < 3) {
        setActiveStep((prevStep) => prevStep + 1);
      } else {
        // Reset to step 0 after reaching the end
        setTimeout(() => {
          setActiveStep(0);
        }, 3000);
      }
    }, 4000);

    return () => clearTimeout(timer);
  }, [activeStep, animationTriggered]);

  // Start the animation when component is visible
  useEffect(() => {
    const handleScroll = () => {
      const element = document.getElementById("algorithm-visualization");
      if (element) {
        const rect = element.getBoundingClientRect();
        if (
          rect.top < window.innerHeight &&
          rect.bottom >= 0 &&
          !animationTriggered
        ) {
          setAnimationTriggered(true);
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    // Check initial position
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, [animationTriggered]);

  return (
    <div
      id="algorithm-visualization"
      className="w-full h-full bg-white rounded-lg border border-gray-200 shadow-lg overflow-hidden"
    >
      <div className="p-4">
        <div className="h-96 transition-all duration-500">
          {activeStep === 0 && (
            <div className="h-full flex flex-col">
              <h4 className="text-center font-semibold mb-2">
                Student Profile Analysis
              </h4>
              <div className="flex-1 flex flex-col items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mb-4 text-primary">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="40"
                    height="40"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
                <h5 className="text-lg font-bold">
                  {studentProfile.name}&apos;s Profile
                </h5>
                <div className="mt-4 grid grid-cols-2 gap-x-8 gap-y-2">
                  {Object.entries(studentProfile.preferences).map(
                    ([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-primary"></div>
                        <span className="capitalize">{key}:</span>
                        <span className="font-semibold">{value}/10</span>
                      </div>
                    )
                  )}
                </div>
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  {studentProfile.interests.map((interest) => (
                    <span
                      key={interest}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeStep === 1 && (
            <div className="h-full">
              <h4 className="text-center font-semibold mb-2">
                Dimension Matching Analysis
              </h4>
              <ResponsiveContainer width="100%" height="90%">
                <RadarChart outerRadius={90} data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis
                    dataKey="dimension"
                    tick={{ fill: "#666", fontSize: 12 }}
                  />
                  <PolarRadiusAxis angle={30} domain={[0, 10]} />
                  <Radar
                    name="Your Preferences"
                    dataKey="userPreference"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.3}
                  />
                  <Radar
                    name="Stanford University"
                    dataKey="universityScore"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.3}
                  />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {activeStep === 2 && (
            <div className="h-full">
              <h4 className="text-center font-semibold mb-2">
                University Match Ranking
              </h4>
              <ResponsiveContainer width="100%" height="90%">
                <BarChart
                  data={universityMatches}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip
                    formatter={(value) => [`${value}% Match`, "Score"]}
                    labelFormatter={(value) => `University: ${value}`}
                  />
                  <Bar dataKey="score" minPointSize={5}>
                    {universityMatches.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {activeStep === 3 && (
            <div className="h-full">
              <h4 className="text-center font-semibold mb-2">
                Similarity Mapping to Existing Students
              </h4>
              <div className="h-full flex items-center justify-center">
                <div className="relative w-full max-w-md h-64">
                  {/* Central student node */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                    <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-white">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                    </div>
                    <p className="text-center mt-1 text-sm font-semibold">
                      You
                    </p>
                  </div>

                  {/* Similar student nodes with connection lines */}
                  {[
                    { id: 1, name: "Sarah", x: 20, y: 20, similarity: 89 },
                    { id: 2, name: "Michael", x: 75, y: 30, similarity: 92 },
                    { id: 3, name: "Jessica", x: 85, y: 70, similarity: 78 },
                    { id: 4, name: "David", x: 70, y: 85, similarity: 83 },
                    { id: 5, name: "Emily", x: 25, y: 75, similarity: 90 },
                  ].map((student) => (
                    <React.Fragment key={student.id}>
                      {/* Connection line */}
                      <svg className="absolute top-0 left-0 w-full h-full z-0">
                        <line
                          x1="50%"
                          y1="50%"
                          x2={`${student.x}%`}
                          y2={`${student.y}%`}
                          stroke="#6366F1"
                          strokeWidth="2"
                          strokeOpacity={(student.similarity / 100) * 0.7 + 0.3}
                        />
                      </svg>

                      {/* Student node */}
                      <div
                        className="absolute z-5 transform -translate-x-1/2 -translate-y-1/2"
                        style={{
                          left: `${student.x}%`,
                          top: `${student.y}%`,
                        }}
                      >
                        <div className="w-12 h-12 rounded-full bg-blue-100 border-2 border-blue-400 flex items-center justify-center text-blue-600">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                          </svg>
                        </div>
                        <div className="text-center mt-1">
                          <p className="text-xs font-medium">{student.name}</p>
                          <p className="text-xs text-gray-500">
                            {student.similarity}%
                          </p>
                        </div>
                      </div>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-center gap-2 mt-4">
          {[0, 1, 2, 3].map((step) => (
            <button
              key={step}
              onClick={() => setActiveStep(step)}
              className={`w-3 h-3 rounded-full ${
                activeStep === step ? "bg-primary" : "bg-gray-300"
              }`}
              aria-label={`Step ${step + 1}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default MatchingAlgorithmVisualization;

import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const getUniversityImage = (universityName: string): string => {
  const nameToImageMap: Record<string, string> = {
    "National University of Singapore": "/images/NUS.png",
    "Nanyang Technological University": "/images/NTU.png",
    "Singapore Management University": "/images/SMU.png",
    "Singapore University of Technology and Design": "/images/SUTD.png",
    "Singapore Institute of Technology": "/images/SIT.png"
  };
  
  return nameToImageMap[universityName] || null;
};
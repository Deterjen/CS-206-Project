"use client"

import * as React from "react"
import { useDropzone } from "react-dropzone"
import { Cloud, File, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>
}

export function FileUpload({ onUpload }: FileUploadProps) {
  const [isUploading, setIsUploading] = React.useState(false)
  const [uploadProgress, setUploadProgress] = React.useState(0)

  const onDrop = React.useCallback(
    async (acceptedFiles: File[]) => {
      try {
        const file = acceptedFiles[0]
        if (!file) return

        setIsUploading(true)
        setUploadProgress(0)

        // Simulate upload progress
        const interval = setInterval(() => {
          setUploadProgress((prev) => {
            if (prev >= 95) {
              clearInterval(interval)
              return prev
            }
            return prev + 5
          })
        }, 100)

        await onUpload(file)
        setUploadProgress(100)
        setTimeout(() => {
          setIsUploading(false)
          setUploadProgress(0)
        }, 500)
      } catch (error) {
        console.error(error)
        setIsUploading(false)
        setUploadProgress(0)
      }
    },
    [onUpload],
  )

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxFiles: 1,
  })

  return (
    <div className="grid gap-4">
      <div
        {...getRootProps()}
        className="border-2 border-dashed rounded-lg p-8 text-center hover:bg-muted/50 transition-colors"
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-2">
          <Cloud className="h-8 w-8 text-muted-foreground" />
          {isDragActive ? <p>Drop the file here...</p> : <p>Drag & drop a file here, or click to select</p>}
          <p className="text-xs text-muted-foreground">Supports PDF, DOC, DOCX (up to 10MB)</p>
        </div>
      </div>
      {acceptedFiles[0] && (
        <div className="flex items-center gap-2 text-sm">
          <File className="h-4 w-4" />
          <span className="flex-1 truncate">{acceptedFiles[0].name}</span>
          {isUploading && (
            <div className="flex items-center gap-2">
              <Progress value={uploadProgress} className="w-24" />
              <Loader2 className="h-4 w-4 animate-spin" />
            </div>
          )}
        </div>
      )}
    </div>
  )
}


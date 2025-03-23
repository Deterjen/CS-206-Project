import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar skeleton */}
      <div className="w-[400px] border-r p-4 space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
      
      {/* Main content skeleton */}
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto space-y-8">
          <Skeleton className="h-10 w-80" />
          <Skeleton className="h-[300px] w-full" />
          <Skeleton className="h-8 w-60" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-6 w-full" />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
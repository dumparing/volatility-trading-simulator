export const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>
  );
};

export const CardSkeleton = () => {
  return (
    <div className="animate-pulse bg-white rounded-lg shadow-md p-6">
      <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-32 bg-gray-200 rounded mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  );
};

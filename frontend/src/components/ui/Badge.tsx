interface BadgeProps {
  level: 'high' | 'medium' | 'low';
  children: React.ReactNode;
}

export const Badge = ({ level, children }: BadgeProps) => {
  const colors = {
    high: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${colors[level]}`}>
      {children}
    </span>
  );
};

'use client';

interface TagsListProps {
  tags: string[];
}

export default function TagsList({ tags }: TagsListProps) {
  if (!tags || tags.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {tags.map((tag) => (
        <span key={tag} className="text-[10px] px-1.5 py-0.5 bg-zinc-800 text-zinc-500 rounded">
          {tag}
        </span>
      ))}
    </div>
  );
}

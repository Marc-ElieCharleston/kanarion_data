import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  href?: string;
  linkText?: string;
  comingSoon?: boolean;
}

export function FeatureCard({ title, description, icon, href, linkText, comingSoon }: FeatureCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>{icon}</span>
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="mb-4">{description}</CardDescription>
        {comingSoon ? (
          <div className="text-sm text-zinc-500">Coming soon...</div>
        ) : href && linkText ? (
          <Link href={href}>
            <Button variant="link" className="p-0 h-auto text-violet-400 hover:text-violet-300">
              {linkText} <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        ) : null}
      </CardContent>
    </Card>
  );
}

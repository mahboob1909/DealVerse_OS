"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ProspectAIPageTest() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex flex-col space-y-4">
        <h1 className="text-3xl font-bold tracking-tight">
          Prospect AI Test
        </h1>
        <p className="text-gray-600">
          Testing basic structure
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Test Card</CardTitle>
          <CardDescription>This is a test</CardDescription>
        </CardHeader>
        <CardContent>
          <Button>Test Button</Button>
        </CardContent>
      </Card>
    </div>
  );
}

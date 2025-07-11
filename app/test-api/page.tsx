"use client";

import { ApiTest } from "@/components/dashboard/api-test";

export default function TestApiPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-8 text-center">DealVerse OS API Test</h1>
      <ApiTest />
    </div>
  );
}

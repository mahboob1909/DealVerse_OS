'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';

export function ApiTest() {
  const [email, setEmail] = useState('admin@dealverse.com');
  const [password, setPassword] = useState('changethis');
  const [results, setResults] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const addResult = (message: string) => {
    setResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testLogin = async () => {
    setLoading(true);
    addResult('Testing login...');
    
    try {
      const response = await apiClient.login(email, password);
      if (response.data) {
        addResult('✅ Login successful!');
        
        // Test getting current user
        const userResponse = await apiClient.getCurrentUser();
        if (userResponse.data) {
          addResult(`✅ Got user: ${(userResponse.data as any)?.email || 'Unknown'}`);
        } else {
          addResult(`❌ Failed to get user: ${userResponse.error}`);
        }
        
        // Test presentations endpoint
        const presResponse = await apiClient.getPresentations();
        if (presResponse.data) {
          addResult(`✅ Got presentations: ${(presResponse.data as any)?.length || 0} items`);
        } else {
          addResult(`❌ Failed to get presentations: ${presResponse.error}`);
        }
        
        // Test templates endpoint
        const templatesResponse = await apiClient.getPresentationTemplates();
        if (templatesResponse.data) {
          addResult(`✅ Got templates: ${(templatesResponse.data as any)?.length || 0} items`);
        } else {
          addResult(`❌ Failed to get templates: ${templatesResponse.error}`);
        }
        
      } else {
        addResult(`❌ Login failed: ${response.error}`);
      }
    } catch (error) {
      addResult(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
    
    setLoading(false);
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>API Connection Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Email</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@dealverse.com"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="changethis"
            />
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button onClick={testLogin} disabled={loading}>
            {loading ? 'Testing...' : 'Test API Connection'}
          </Button>
          <Button variant="outline" onClick={clearResults}>
            Clear Results
          </Button>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
          <h3 className="font-medium mb-2">Test Results:</h3>
          {results.length === 0 ? (
            <p className="text-gray-500">No tests run yet</p>
          ) : (
            <div className="space-y-1">
              {results.map((result, index) => (
                <div key={index} className="text-sm font-mono">
                  {result}
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

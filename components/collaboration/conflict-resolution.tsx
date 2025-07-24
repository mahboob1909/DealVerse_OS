"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertTriangle,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  GitMerge,
  User,
  Edit3,
  Eye,
  ArrowRight
} from "lucide-react";
import { ConflictResolution as ConflictType } from "@/lib/types/collaboration";
import { formatDistanceToNow } from "date-fns";

interface ConflictResolutionProps {
  conflicts: ConflictType[];
  onResolveConflict: (
    conflictId: string, 
    resolution: ConflictType['resolution_strategy'], 
    content?: string
  ) => Promise<void>;
  currentUserId: string;
}

export function ConflictResolution({
  conflicts,
  onResolveConflict,
  currentUserId
}: ConflictResolutionProps) {
  const [selectedConflict, setSelectedConflict] = useState<string | null>(null);
  const [customResolution, setCustomResolution] = useState('');
  const [isResolving, setIsResolving] = useState(false);

  const handleResolveConflict = async (
    conflictId: string,
    strategy: ConflictType['resolution_strategy'],
    content?: string
  ) => {
    setIsResolving(true);
    try {
      await onResolveConflict(conflictId, strategy, content);
      setSelectedConflict(null);
      setCustomResolution('');
    } catch (error) {
      console.error('Failed to resolve conflict:', error);
    } finally {
      setIsResolving(false);
    }
  };

  const getConflictSeverity = (conflict: ConflictType) => {
    const editCount = conflict.conflicting_edits.length;
    if (editCount >= 5) return 'high';
    if (editCount >= 3) return 'medium';
    return 'low';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStrategyIcon = (strategy: ConflictType['resolution_strategy']) => {
    switch (strategy) {
      case 'merge': return <GitMerge className="h-4 w-4" />;
      case 'manual_resolve': return <Edit3 className="h-4 w-4" />;
      case 'choose_version': return <User className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getStrategyDescription = (strategy: ConflictType['resolution_strategy']) => {
    switch (strategy) {
      case 'merge': return 'Automatically merge compatible changes';
      case 'manual_resolve': return 'Manually resolve conflicts with custom content';
      case 'choose_version': return 'Accept the most recent change';
      default: return 'Unknown resolution strategy';
    }
  };

  if (conflicts.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Conflicts</h3>
          <p className="text-gray-600">All changes have been successfully synchronized.</p>
        </CardContent>
      </Card>
    );
  }

  const selectedConflictData = conflicts.find(c => c.conflict_id === selectedConflict);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            <span>Editing Conflicts</span>
            <Badge variant="destructive">{conflicts.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Multiple users have made conflicting changes to the same content. 
              Please review and resolve these conflicts to continue collaborating.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Conflicts List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Conflicts Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-96">
              <div className="space-y-3">
                {conflicts.map((conflict) => {
                  const severity = getConflictSeverity(conflict);
                  const isSelected = selectedConflict === conflict.conflict_id;

                  return (
                    <div
                      key={conflict.conflict_id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        isSelected 
                          ? 'border-blue-500 bg-blue-50' 
                          : `border-gray-200 hover:border-gray-300 ${getSeverityColor(severity)}`
                      }`}
                      onClick={() => setSelectedConflict(conflict.conflict_id)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant={severity === 'high' ? 'destructive' : severity === 'medium' ? 'default' : 'secondary'}>
                            {severity.toUpperCase()}
                          </Badge>
                          <span className="text-sm font-medium">
                            {conflict.conflicting_edits.length} conflicting edits
                          </span>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {conflict.resolved_at ? formatDistanceToNow(new Date(conflict.resolved_at), { addSuffix: true }) : 'Recently detected'}
                        </span>
                      </div>

                      <div className="text-sm text-gray-600 mb-2">
                        {conflict.conflicting_edits.length > 0 && conflict.conflicting_edits[0].position && (
                          <>
                            Position: {conflict.conflicting_edits[0].position.start}-{conflict.conflicting_edits[0].position.end}
                            {conflict.conflicting_edits[0].position.page && ` (Page ${conflict.conflicting_edits[0].position.page})`}
                          </>
                        )}
                      </div>

                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Users className="h-3 w-3" />
                        <span>
                          {conflict.conflicting_edits.map(edit => edit.user_name).join(', ')}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Conflict Details & Resolution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">
              {selectedConflictData ? 'Conflict Resolution' : 'Select a Conflict'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedConflictData ? (
              <div className="space-y-4">
                {/* Conflict Info */}
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium">
                      {selectedConflictData.resolved_at ? `Resolved ${formatDistanceToNow(new Date(selectedConflictData.resolved_at), { addSuffix: true })}` : 'Recently detected'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {selectedConflictData.conflicting_edits.length} users made changes to the same content
                  </div>
                </div>

                {/* Conflicting Edits */}
                <div className="space-y-3">
                  <h4 className="text-sm font-medium">Conflicting Changes:</h4>
                  {selectedConflictData.conflicting_edits.map((edit, index) => (
                    <div key={edit.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{edit.user_name}</span>
                          <Badge variant="outline" className="text-xs">
                            {edit.edit_type}
                          </Badge>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(edit.timestamp), { addSuffix: true })}
                        </span>
                      </div>
                      
                      <div className="text-sm">
                        <div className="mb-1 text-gray-600">Content:</div>
                        <div className="bg-gray-50 p-2 rounded text-xs font-mono">
                          {edit.content || edit.previous_content || 'No content'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <Separator />

                {/* Resolution Options */}
                <div className="space-y-3">
                  <h4 className="text-sm font-medium">Resolution Options:</h4>
                  
                  <Tabs defaultValue="auto" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="auto">Auto Merge</TabsTrigger>
                      <TabsTrigger value="last_writer">Last Writer</TabsTrigger>
                      <TabsTrigger value="manual">Manual</TabsTrigger>
                    </TabsList>

                    <TabsContent value="auto" className="space-y-3">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          {getStrategyIcon('merge')}
                          <span className="text-sm font-medium">Automatic Merge</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">
                          {getStrategyDescription('merge')}
                        </p>
                        <Button
                          onClick={() => handleResolveConflict(selectedConflictData.conflict_id, 'merge')}
                          disabled={isResolving}
                          className="w-full"
                        >
                          {isResolving ? 'Resolving...' : 'Auto Merge Changes'}
                        </Button>
                      </div>
                    </TabsContent>

                    <TabsContent value="last_writer" className="space-y-3">
                      <div className="p-3 bg-yellow-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          {getStrategyIcon('choose_version')}
                          <span className="text-sm font-medium">Last Writer Wins</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">
                          {getStrategyDescription('choose_version')}
                        </p>
                        
                        {/* Show the last edit */}
                        {selectedConflictData.conflicting_edits.length > 0 && (
                          <div className="mb-3 p-2 bg-white border rounded">
                            <div className="text-xs text-gray-600 mb-1">Most recent change by:</div>
                            <div className="text-sm font-medium">
                              {selectedConflictData.conflicting_edits[selectedConflictData.conflicting_edits.length - 1].user_name}
                            </div>
                          </div>
                        )}
                        
                        <Button
                          onClick={() => handleResolveConflict(selectedConflictData.conflict_id, 'choose_version')}
                          disabled={isResolving}
                          className="w-full"
                          variant="outline"
                        >
                          {isResolving ? 'Resolving...' : 'Accept Last Change'}
                        </Button>
                      </div>
                    </TabsContent>

                    <TabsContent value="manual" className="space-y-3">
                      <div className="p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          {getStrategyIcon('manual_resolve')}
                          <span className="text-sm font-medium">Manual Resolution</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">
                          {getStrategyDescription('manual_resolve')}
                        </p>
                        
                        <Textarea
                          value={customResolution}
                          onChange={(e) => setCustomResolution(e.target.value)}
                          placeholder="Enter the resolved content..."
                          className="mb-3"
                          rows={4}
                        />
                        
                        <Button
                          onClick={() => handleResolveConflict(
                            selectedConflictData.conflict_id, 
                            'manual_resolve', 
                            customResolution
                          )}
                          disabled={isResolving || !customResolution.trim()}
                          className="w-full"
                          variant="outline"
                        >
                          {isResolving ? 'Resolving...' : 'Apply Manual Resolution'}
                        </Button>
                      </div>
                    </TabsContent>
                  </Tabs>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select a conflict from the list to view details and resolution options.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

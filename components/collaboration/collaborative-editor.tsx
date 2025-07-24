"use client";

import { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  FileText,
  Users,
  MessageCircle,
  AlertTriangle,
  Save,
  History,
  Eye,
  Edit3,
  Lock,
  Unlock
} from "lucide-react";
import { useCollaboration } from "@/hooks/use-collaboration";
import { UserPresenceIndicator } from "./user-presence";
import { CollaborativeCursors } from "./live-cursors";
import { LiveComments } from "./live-comments";
import { ConflictResolution } from "./conflict-resolution";
import { Document } from "@/hooks/use-documents";

interface CollaborativeEditorProps {
  document: Document;
  currentUserId: string;
  onSave?: (content: string) => Promise<void>;
  onVersionCreate?: () => Promise<void>;
  readOnly?: boolean;
  showComments?: boolean;
  showPresence?: boolean;
  autoSave?: boolean;
  autoSaveInterval?: number;
}

export function CollaborativeEditor({
  document,
  currentUserId,
  onSave,
  onVersionCreate,
  readOnly = false,
  showComments = true,
  showPresence = true,
  autoSave = true,
  autoSaveInterval = 30000 // 30 seconds
}: CollaborativeEditorProps) {
  const [content, setContent] = useState((document as any).content || document.description || '');
  const [isEditing, setIsEditing] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [activeTab, setActiveTab] = useState('editor');

  const editorRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLTextAreaElement>(null);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Collaboration hook
  const {
    activeUsers,
    currentUser,
    cursors,
    updateCursorPosition,
    liveComments,
    addComment,
    updateComment,
    resolveComment,
    addReaction,
    documentEdits,
    applyEdit,
    conflicts,
    resolveConflict,
    joinDocument,
    leaveDocument,
    isConnected,
    connectionError
  } = useCollaboration({
    document_id: document.id,
    enable_cursor_tracking: !readOnly,
    enable_live_comments: showComments,
    enable_conflict_resolution: true,
    auto_save_interval: autoSaveInterval
  });

  // Join document collaboration session on mount
  useEffect(() => {
    joinDocument(document.id);
    return () => leaveDocument();
  }, [document.id, joinDocument, leaveDocument]);

  // Handle content changes
  const handleContentChange = useCallback((newContent: string) => {
    setContent(newContent);
    setHasUnsavedChanges(true);
    
    if (!readOnly) {
      // Create document edit for collaboration
      applyEdit({
        document_id: document.id,
        user_id: currentUserId,
        user_name: currentUser?.user_name || 'Unknown User',
        edit_type: 'replace',
        position: { start: 0, end: content.length },
        content: newContent,
        previous_content: content
      });
    }

    // Auto-save logic
    if (autoSave && onSave) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      
      autoSaveTimeoutRef.current = setTimeout(async () => {
        try {
          await onSave(newContent);
          setHasUnsavedChanges(false);
          setLastSaved(new Date());
        } catch (error) {
          console.error('Auto-save failed:', error);
        }
      }, autoSaveInterval);
    }
  }, [content, document.id, readOnly, autoSave, onSave, autoSaveInterval, applyEdit, currentUser?.user_name, currentUserId]);

  // Manual save
  const handleSave = async () => {
    if (!onSave || !hasUnsavedChanges) return;

    try {
      await onSave(content);
      setHasUnsavedChanges(false);
      setLastSaved(new Date());
      
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  // Handle cursor position updates
  const handleCursorUpdate = useCallback((position: { x: number; y: number; element_id?: string }) => {
    if (isEditing && !readOnly) {
      updateCursorPosition(position);
    }
  }, [isEditing, readOnly, updateCursorPosition]);

  // Handle text selection for collaborative editing
  const handleTextSelection = useCallback(() => {
    if (!contentRef.current || readOnly) return;

    const textarea = contentRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    if (start !== end) {
      const rect = textarea.getBoundingClientRect();
      updateCursorPosition({
        x: rect.left + 10, // Approximate cursor position
        y: rect.top + 20,
        element_id: textarea.id,
        selection: {
          start,
          end,
          text: content.substring(start, end)
        }
      });
    }
  }, [content, readOnly, updateCursorPosition]);

  // Cleanup auto-save timeout on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, []);

  const getConnectionStatus = () => {
    if (connectionError) return { status: 'error', message: connectionError };
    if (!isConnected) return { status: 'disconnected', message: 'Disconnected from collaboration server' };
    return { status: 'connected', message: `Connected with ${activeUsers.length} collaborator${activeUsers.length !== 1 ? 's' : ''}` };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5 text-dealverse-blue" />
          <div>
            <h2 className="font-semibold text-dealverse-navy">{document.title || document.filename}</h2>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>
                {readOnly ? 'Read-only' : isEditing ? 'Editing' : 'Viewing'}
              </span>
              {hasUnsavedChanges && (
                <>
                  <span>•</span>
                  <span className="text-yellow-600">Unsaved changes</span>
                </>
              )}
              {lastSaved && (
                <>
                  <span>•</span>
                  <span>Saved {lastSaved.toLocaleTimeString()}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Connection Status */}
          <Badge 
            variant={connectionStatus.status === 'connected' ? 'default' : 'destructive'}
            className="text-xs"
          >
            {connectionStatus.status === 'connected' ? (
              <Users className="h-3 w-3 mr-1" />
            ) : (
              <AlertTriangle className="h-3 w-3 mr-1" />
            )}
            {connectionStatus.message}
          </Badge>

          {/* Action Buttons */}
          {!readOnly && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                {isEditing ? (
                  <>
                    <Eye className="h-4 w-4 mr-1" />
                    Preview
                  </>
                ) : (
                  <>
                    <Edit3 className="h-4 w-4 mr-1" />
                    Edit
                  </>
                )}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={handleSave}
                disabled={!hasUnsavedChanges}
              >
                <Save className="h-4 w-4 mr-1" />
                Save
              </Button>

              {onVersionCreate && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onVersionCreate}
                >
                  <History className="h-4 w-4 mr-1" />
                  Version
                </Button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Connection Error Alert */}
      {connectionError && (
        <Alert variant="destructive" className="m-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{connectionError}</AlertDescription>
        </Alert>
      )}

      {/* Conflicts Alert */}
      {conflicts.length > 0 && (
        <Alert className="m-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {conflicts.length} editing conflict{conflicts.length > 1 ? 's' : ''} detected. 
            <Button variant="link" className="p-0 ml-1" onClick={() => setActiveTab('conflicts')}>
              Resolve now
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Editor/Viewer */}
        <div className="flex-1 flex flex-col">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="mx-4 mt-2 w-fit">
              <TabsTrigger value="editor">
                {isEditing ? 'Editor' : 'Viewer'}
              </TabsTrigger>
              {showComments && (
                <TabsTrigger value="comments" className="relative">
                  Comments
                  {liveComments.filter(c => !c.is_resolved).length > 0 && (
                    <Badge variant="destructive" className="ml-1 h-4 w-4 p-0 text-xs">
                      {liveComments.filter(c => !c.is_resolved).length}
                    </Badge>
                  )}
                </TabsTrigger>
              )}
              {conflicts.length > 0 && (
                <TabsTrigger value="conflicts" className="relative">
                  Conflicts
                  <Badge variant="destructive" className="ml-1 h-4 w-4 p-0 text-xs">
                    {conflicts.length}
                  </Badge>
                </TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="editor" className="flex-1 m-4 mt-2">
              <Card className="h-full">
                <CardContent className="p-0 h-full relative" ref={editorRef}>
                  {isEditing && !readOnly ? (
                    <textarea
                      ref={contentRef}
                      value={content}
                      onChange={(e) => handleContentChange(e.target.value)}
                      onSelect={handleTextSelection}
                      onFocus={() => setIsEditing(true)}
                      className="w-full h-full p-4 border-0 resize-none focus:outline-none font-mono text-sm"
                      placeholder="Start typing your document content..."
                      id="collaborative-editor"
                    />
                  ) : (
                    <div className="p-4 h-full overflow-auto">
                      <pre className="whitespace-pre-wrap font-mono text-sm">
                        {content || 'No content available'}
                      </pre>
                    </div>
                  )}

                  {/* Live Cursors Overlay */}
                  <CollaborativeCursors
                    cursors={cursors}
                    updateCursorPosition={handleCursorUpdate}
                    containerRef={editorRef}
                    enableTracking={isEditing && !readOnly}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            {showComments && (
              <TabsContent value="comments" className="flex-1 m-4 mt-2">
                <LiveComments
                  comments={liveComments}
                  currentUserId={currentUserId}
                  documentId={document.id}
                  onAddComment={addComment}
                  onUpdateComment={updateComment}
                  onResolveComment={resolveComment}
                  onAddReaction={addReaction}
                />
              </TabsContent>
            )}
          </Tabs>
        </div>
      </div>
    </div>
  );
}

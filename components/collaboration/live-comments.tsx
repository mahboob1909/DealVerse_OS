"use client";

import { useState, useRef, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  MessageCircle,
  Send,
  Reply,
  Check,
  MoreHorizontal,
  Smile,
  Pin,
  Trash2,
  Edit3,
  X
} from "lucide-react";
import { LiveComment, CommentReaction } from "@/lib/types/collaboration";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";

interface LiveCommentsProps {
  comments: LiveComment[];
  currentUserId: string;
  documentId: string;
  onAddComment: (comment: Omit<LiveComment, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  onUpdateComment: (commentId: string, updates: Partial<LiveComment>) => Promise<void>;
  onResolveComment: (commentId: string) => Promise<void>;
  onAddReaction: (commentId: string, emoji: string) => Promise<void>;
  showPositioned?: boolean;
  containerRef?: React.RefObject<HTMLElement>;
}

const EMOJI_OPTIONS = ['👍', '👎', '❤️', '😄', '😮', '😢', '🎉', '🔥'];

export function LiveComments({
  comments,
  currentUserId,
  documentId,
  onAddComment,
  onUpdateComment,
  onResolveComment,
  onAddReaction,
  showPositioned = false,
  containerRef
}: LiveCommentsProps) {
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [editingComment, setEditingComment] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [showResolved, setShowResolved] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Filter comments based on resolved status
  const filteredComments = comments.filter(comment => 
    showResolved || !comment.is_resolved
  );

  // Group comments by thread
  const commentThreads = filteredComments.reduce((threads, comment) => {
    const threadId = comment.thread_id || comment.id;
    if (!threads[threadId]) {
      threads[threadId] = [];
    }
    threads[threadId].push(comment);
    return threads;
  }, {} as Record<string, LiveComment[]>);

  // Sort threads by creation time
  const sortedThreads = Object.values(commentThreads).sort((a, b) => 
    new Date(a[0].created_at).getTime() - new Date(b[0].created_at).getTime()
  );

  const handleSubmitComment = async (parentCommentId?: string) => {
    if (!newComment.trim()) return;

    await onAddComment({
      content: newComment,
      author_id: currentUserId,
      author_name: '', // Will be filled by the hook
      document_id: documentId,
      thread_id: parentCommentId || undefined,
      parent_comment_id: parentCommentId,
      is_resolved: false
    });

    setNewComment('');
    setReplyingTo(null);
  };

  const handleEditComment = async (commentId: string) => {
    if (!editContent.trim()) return;

    await onUpdateComment(commentId, { content: editContent });
    setEditingComment(null);
    setEditContent('');
  };

  const startEditing = (comment: LiveComment) => {
    setEditingComment(comment.id);
    setEditContent(comment.content);
  };

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getReactionCount = (reactions: CommentReaction[], emoji: string) => {
    return reactions.filter(r => r.emoji === emoji).length;
  };

  const hasUserReacted = (reactions: CommentReaction[], emoji: string, userId: string) => {
    return reactions.some(r => r.emoji === emoji && r.user_id === userId);
  };

  // Auto-scroll to bottom when new comments are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [comments.length]);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4" />
            <span>Live Comments</span>
            <Badge variant="secondary" className="text-xs">
              {filteredComments.length}
            </Badge>
          </div>
          
          <div className="flex items-center gap-1">
            <Button
              variant={showResolved ? "default" : "ghost"}
              size="sm"
              onClick={() => setShowResolved(!showResolved)}
              className="h-auto px-2 py-1 text-xs"
            >
              {showResolved ? 'Hide' : 'Show'} Resolved
            </Button>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-4 p-4">
        {/* Comments List */}
        <ScrollArea className="flex-1" ref={scrollAreaRef}>
          <div className="space-y-4">
            <AnimatePresence>
              {sortedThreads.map((thread) => {
                const mainComment = thread[0];
                const replies = thread.slice(1);

                return (
                  <motion.div
                    key={mainComment.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`space-y-2 ${mainComment.is_resolved ? 'opacity-60' : ''}`}
                  >
                    {/* Main Comment */}
                    <div className="flex gap-3 group">
                      <Avatar className="h-8 w-8 flex-shrink-0">
                        <AvatarImage src={mainComment.author_avatar} alt={mainComment.author_name} />
                        <AvatarFallback className="text-xs">
                          {getUserInitials(mainComment.author_name)}
                        </AvatarFallback>
                      </Avatar>

                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{mainComment.author_name}</span>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(mainComment.created_at), { addSuffix: true })}
                          </span>
                          {mainComment.is_resolved && (
                            <Badge variant="outline" className="text-xs">
                              <Check className="h-3 w-3 mr-1" />
                              Resolved
                            </Badge>
                          )}
                        </div>

                        {editingComment === mainComment.id ? (
                          <div className="space-y-2">
                            <Textarea
                              value={editContent}
                              onChange={(e) => setEditContent(e.target.value)}
                              className="min-h-[60px] text-sm"
                              placeholder="Edit your comment..."
                            />
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => handleEditComment(mainComment.id)}
                                disabled={!editContent.trim()}
                              >
                                Save
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {
                                  setEditingComment(null);
                                  setEditContent('');
                                }}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <p className="text-sm text-gray-700">{mainComment.content}</p>

                            {/* Reactions */}
                            {mainComment.reactions && mainComment.reactions.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {EMOJI_OPTIONS.map(emoji => {
                                  const count = getReactionCount(mainComment.reactions!, emoji);
                                  if (count === 0) return null;

                                  const hasReacted = hasUserReacted(mainComment.reactions!, emoji, currentUserId);

                                  return (
                                    <Button
                                      key={emoji}
                                      variant={hasReacted ? "default" : "outline"}
                                      size="sm"
                                      className="h-6 px-2 text-xs"
                                      onClick={() => onAddReaction(mainComment.id, emoji)}
                                    >
                                      {emoji} {count}
                                    </Button>
                                  );
                                })}
                              </div>
                            )}

                            {/* Comment Actions */}
                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setReplyingTo(mainComment.id)}
                                className="h-auto px-2 py-1 text-xs"
                              >
                                <Reply className="h-3 w-3 mr-1" />
                                Reply
                              </Button>

                              {!mainComment.is_resolved && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => onResolveComment(mainComment.id)}
                                  className="h-auto px-2 py-1 text-xs"
                                >
                                  <Check className="h-3 w-3 mr-1" />
                                  Resolve
                                </Button>
                              )}

                              {mainComment.author_id === currentUserId && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => startEditing(mainComment)}
                                  className="h-auto px-2 py-1 text-xs"
                                >
                                  <Edit3 className="h-3 w-3 mr-1" />
                                  Edit
                                </Button>
                              )}

                              {/* Emoji Reactions */}
                              <Popover>
                                <PopoverTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-auto px-2 py-1 text-xs"
                                  >
                                    <Smile className="h-3 w-3" />
                                  </Button>
                                </PopoverTrigger>
                                <PopoverContent className="w-auto p-2">
                                  <div className="flex gap-1">
                                    {EMOJI_OPTIONS.map(emoji => (
                                      <Button
                                        key={emoji}
                                        variant="ghost"
                                        size="sm"
                                        className="h-8 w-8 p-0"
                                        onClick={() => onAddReaction(mainComment.id, emoji)}
                                      >
                                        {emoji}
                                      </Button>
                                    ))}
                                  </div>
                                </PopoverContent>
                              </Popover>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Replies */}
                    {replies.length > 0 && (
                      <div className="ml-11 space-y-2 border-l-2 border-gray-100 pl-4">
                        {replies.map(reply => (
                          <div key={reply.id} className="flex gap-3 group">
                            <Avatar className="h-6 w-6 flex-shrink-0">
                              <AvatarImage src={reply.author_avatar} alt={reply.author_name} />
                              <AvatarFallback className="text-xs">
                                {getUserInitials(reply.author_name)}
                              </AvatarFallback>
                            </Avatar>

                            <div className="flex-1 space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">{reply.author_name}</span>
                                <span className="text-xs text-muted-foreground">
                                  {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
                                </span>
                              </div>
                              <p className="text-sm text-gray-700">{reply.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Reply Input */}
                    {replyingTo === mainComment.id && (
                      <div className="ml-11 space-y-2">
                        <Textarea
                          value={newComment}
                          onChange={(e) => setNewComment(e.target.value)}
                          placeholder="Write a reply..."
                          className="min-h-[60px] text-sm"
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleSubmitComment(mainComment.id)}
                            disabled={!newComment.trim()}
                          >
                            <Send className="h-3 w-3 mr-1" />
                            Reply
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setReplyingTo(null);
                              setNewComment('');
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}

                    <Separator />
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {filteredComments.length === 0 && (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No comments yet. Start the conversation!
              </div>
            )}
          </div>
        </ScrollArea>

        {/* New Comment Input */}
        {!replyingTo && (
          <div className="space-y-2 border-t pt-4">
            <Textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              className="min-h-[80px] text-sm"
            />
            <div className="flex justify-between">
              <div className="text-xs text-muted-foreground">
                Press Ctrl+Enter to send
              </div>
              <Button
                size="sm"
                onClick={() => handleSubmitComment()}
                disabled={!newComment.trim()}
              >
                <Send className="h-3 w-3 mr-1" />
                Comment
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

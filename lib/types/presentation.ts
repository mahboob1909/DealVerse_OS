/**
 * TypeScript types for PitchCraft Suite
 */

export interface Presentation {
  id: string;
  title: string;
  description?: string;
  presentation_type: string;
  status: 'draft' | 'active' | 'review' | 'approved' | 'archived';
  version: number;
  is_current: boolean;
  slide_count: number;
  content_data: Record<string, any>;
  theme_settings: Record<string, any>;
  layout_settings: Record<string, any>;
  is_shared: boolean;
  access_level: 'private' | 'team' | 'organization' | 'public';
  collaborators: string[];
  tags: string[];
  notes?: string;
  thumbnail_url?: string;
  deal_value?: string;
  client_name?: string;
  target_audience?: string;
  presentation_date?: string;
  is_template: boolean;
  template_category?: string;
  template_description?: string;
  organization_id: string;
  deal_id?: string;
  created_by_id: string;
  last_modified_by_id?: string;
  parent_presentation_id?: string;
  created_at: string;
  updated_at: string;
}

export interface PresentationSlide {
  id: string;
  title?: string;
  slide_number: number;
  slide_type: string;
  content_data: Record<string, any>;
  layout_type: string;
  background_settings: Record<string, any>;
  elements: any[];
  animations: any[];
  transitions: Record<string, any>;
  notes?: string;
  duration_seconds?: number;
  is_hidden: boolean;
  presentation_id: string;
  created_at: string;
  updated_at: string;
}

export interface PresentationTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  template_data: Record<string, any>;
  default_slides: any[];
  theme_settings: Record<string, any>;
  usage_count: number;
  is_featured: boolean;
  is_public: boolean;
  thumbnail_url?: string;
  preview_images: string[];
  organization_id?: string;
  created_by_id?: string;
  created_at: string;
  updated_at: string;
}

export interface PresentationComment {
  id: string;
  content: string;
  comment_type: string;
  slide_id?: string;
  element_id?: string;
  position_x?: number;
  position_y?: number;
  is_resolved: boolean;
  resolved_by_id?: string;
  resolved_at?: string;
  presentation_id: string;
  author_id: string;
  parent_comment_id?: string;
  created_at: string;
  updated_at: string;
}

export interface PresentationCollaboration {
  id: string;
  activity_type: string;
  description?: string;
  activity_data: Record<string, any>;
  session_duration?: number;
  is_active: boolean;
  presentation_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Create/Update types
export interface CreatePresentationData {
  title: string;
  description?: string;
  presentation_type?: string;
  content_data?: Record<string, any>;
  theme_settings?: Record<string, any>;
  layout_settings?: Record<string, any>;
  is_shared?: boolean;
  access_level?: string;
  collaborators?: string[];
  tags?: string[];
  notes?: string;
  deal_value?: string;
  client_name?: string;
  target_audience?: string;
  presentation_date?: string;
  organization_id: string;
  deal_id?: string;
}

export interface UpdatePresentationData {
  title?: string;
  description?: string;
  presentation_type?: string;
  status?: string;
  content_data?: Record<string, any>;
  theme_settings?: Record<string, any>;
  layout_settings?: Record<string, any>;
  is_shared?: boolean;
  access_level?: string;
  collaborators?: string[];
  tags?: string[];
  notes?: string;
  deal_value?: string;
  client_name?: string;
  target_audience?: string;
  presentation_date?: string;
}

export interface CreateSlideData {
  title?: string;
  slide_number: number;
  slide_type?: string;
  content_data?: Record<string, any>;
  layout_type?: string;
  background_settings?: Record<string, any>;
  elements?: any[];
  animations?: any[];
  transitions?: Record<string, any>;
  notes?: string;
  duration_seconds?: number;
  is_hidden?: boolean;
}

export interface UpdateSlideData {
  title?: string;
  slide_number?: number;
  slide_type?: string;
  content_data?: Record<string, any>;
  layout_type?: string;
  background_settings?: Record<string, any>;
  elements?: any[];
  animations?: any[];
  transitions?: Record<string, any>;
  notes?: string;
  duration_seconds?: number;
  is_hidden?: boolean;
}

export interface CreateTemplateData {
  name: string;
  description?: string;
  category?: string;
  template_data?: Record<string, any>;
  default_slides?: any[];
  theme_settings?: Record<string, any>;
  is_featured?: boolean;
  is_public?: boolean;
  thumbnail_url?: string;
  preview_images?: string[];
  organization_id?: string;
}

export interface CreateCommentData {
  content: string;
  comment_type?: string;
  slide_id?: string;
  element_id?: string;
  position_x?: number;
  position_y?: number;
  parent_comment_id?: string;
}

// Filter types
export interface PresentationFilters {
  skip?: number;
  limit?: number;
  status?: string;
  presentation_type?: string;
  deal_id?: string;
  created_by_me?: boolean;
}

export interface TemplateFilters {
  skip?: number;
  limit?: number;
  category?: string;
  featured_only?: boolean;
  public_only?: boolean;
}

export interface CommentFilters {
  skip?: number;
  limit?: number;
  resolved_only?: boolean;
}

// Presentation types enum
export const PRESENTATION_TYPES = {
  INVESTMENT_PITCH: 'investment_pitch',
  MARKET_RESEARCH: 'market_research',
  FINANCIAL_ANALYSIS: 'financial_analysis',
  DUE_DILIGENCE: 'due_diligence',
  COMPLIANCE_REPORT: 'compliance_report',
  CUSTOM: 'custom',
} as const;

// Presentation status enum
export const PRESENTATION_STATUS = {
  DRAFT: 'draft',
  ACTIVE: 'active',
  REVIEW: 'review',
  APPROVED: 'approved',
  ARCHIVED: 'archived',
} as const;

// Access levels enum
export const ACCESS_LEVELS = {
  PRIVATE: 'private',
  TEAM: 'team',
  ORGANIZATION: 'organization',
  PUBLIC: 'public',
} as const;

// Slide types enum
export const SLIDE_TYPES = {
  TITLE: 'title',
  CONTENT: 'content',
  CHART: 'chart',
  IMAGE: 'image',
  TABLE: 'table',
  SECTION: 'section',
} as const;

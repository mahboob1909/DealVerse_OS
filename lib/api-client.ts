/**
 * API Client for DealVerse OS Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;

    // Get token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }



    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry the request with new token
            headers.Authorization = `Bearer ${this.token}`;
            const retryResponse = await fetch(url, {
              ...options,
              headers,
            });
            
            if (retryResponse.ok) {
              const data = await retryResponse.json();
              return { data };
            }
          }
          
          // Refresh failed, clear tokens and redirect to login
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
          throw new Error('Authentication failed');
        }

        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error('API request failed:', error);
      // Check if it's a network error
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return { error: 'Unable to connect to server. Please check your connection and try again.' };
      }
      return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = typeof window !== 'undefined' 
      ? localStorage.getItem('refresh_token') 
      : null;
    
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.setToken(data.access_token);
        if (typeof window !== 'undefined') {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }

    return false;
  }

  // Authentication endpoints
  async login(email: string, password: string) {
    return this.request<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>('/auth/login/json', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    organization_id: string;
  }) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout() {
    const result = await this.request('/auth/logout', { method: 'POST' });
    this.clearToken();
    return result;
  }

  // User endpoints
  async getCurrentUser() {
    return this.request('/users/me');
  }

  async updateCurrentUser(userData: any) {
    return this.request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async getUsers(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    
    return this.request(`/users?${query.toString()}`);
  }

  // Deal endpoints
  async getDeals(params?: {
    skip?: number;
    limit?: number;
    stage?: string;
    status?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.stage) query.append('stage', params.stage);
    if (params?.status) query.append('status', params.status);
    
    return this.request(`/deals?${query.toString()}`);
  }

  async getDeal(id: string) {
    return this.request(`/deals/${id}`);
  }

  async createDeal(dealData: any) {
    return this.request('/deals', {
      method: 'POST',
      body: JSON.stringify(dealData),
    });
  }

  async updateDeal(id: string, dealData: any) {
    return this.request(`/deals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(dealData),
    });
  }

  async deleteDeal(id: string) {
    return this.request(`/deals/${id}`, { method: 'DELETE' });
  }

  async getDealsStats() {
    return this.request('/deals/stats/summary');
  }

  // Client endpoints
  async getClients(params?: {
    skip?: number;
    limit?: number;
    client_type?: string;
    industry?: string;
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.client_type) query.append('client_type', params.client_type);
    if (params?.industry) query.append('industry', params.industry);
    if (params?.search) query.append('search', params.search);
    
    return this.request(`/clients?${query.toString()}`);
  }

  async getClient(id: string) {
    return this.request(`/clients/${id}`);
  }

  async createClient(clientData: any) {
    return this.request('/clients', {
      method: 'POST',
      body: JSON.stringify(clientData),
    });
  }

  async updateClient(id: string, clientData: any) {
    return this.request(`/clients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(clientData),
    });
  }

  async deleteClient(id: string) {
    return this.request(`/clients/${id}`, { method: 'DELETE' });
  }

  // Prospect AI endpoints
  async getProspects(params?: {
    skip?: number;
    limit?: number;
    query?: string;
    industry?: string;
    location?: string;
    min_revenue?: number;
    max_revenue?: number;
    min_ai_score?: number;
    status?: string;
    stage?: string;
    priority?: string;
    assigned_to_id?: string;
    sort_by?: string;
    sort_order?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.query) query.append('query', params.query);
    if (params?.industry) query.append('industry', params.industry);
    if (params?.location) query.append('location', params.location);
    if (params?.min_revenue) query.append('min_revenue', params.min_revenue.toString());
    if (params?.max_revenue) query.append('max_revenue', params.max_revenue.toString());
    if (params?.min_ai_score) query.append('min_ai_score', params.min_ai_score.toString());
    if (params?.status) query.append('status', params.status);
    if (params?.stage) query.append('stage', params.stage);
    if (params?.priority) query.append('priority', params.priority);
    if (params?.assigned_to_id) query.append('assigned_to_id', params.assigned_to_id);
    if (params?.sort_by) query.append('sort_by', params.sort_by);
    if (params?.sort_order) query.append('sort_order', params.sort_order);

    return this.request(`/prospects?${query.toString()}`);
  }

  async getProspect(id: string) {
    return this.request(`/prospects/${id}`);
  }

  async createProspect(prospectData: any) {
    return this.request('/prospects', {
      method: 'POST',
      body: JSON.stringify(prospectData),
    });
  }

  async updateProspect(id: string, prospectData: any) {
    return this.request(`/prospects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(prospectData),
    });
  }

  async deleteProspect(id: string) {
    return this.request(`/prospects/${id}`, {
      method: 'DELETE',
    });
  }

  async getProspectStatistics() {
    return this.request('/prospects/statistics');
  }

  async getHighPriorityProspects() {
    return this.request('/prospects/high-priority');
  }

  async analyzeProspect(analysisRequest: any) {
    return this.request('/prospects/analyze', {
      method: 'POST',
      body: JSON.stringify(analysisRequest),
    });
  }

  async scoreProspects(scoringRequest: any) {
    return this.request('/prospects/score', {
      method: 'POST',
      body: JSON.stringify(scoringRequest),
    });
  }

  async getMarketIntelligence(params?: {
    industry?: string;
    region?: string;
    time_period?: string;
    deal_type?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.industry) query.append('industry', params.industry);
    if (params?.region) query.append('region', params.region);
    if (params?.time_period) query.append('time_period', params.time_period);
    if (params?.deal_type) query.append('deal_type', params.deal_type);

    return this.request(`/prospects/market-intelligence?${query.toString()}`);
  }

  // Analytics endpoints
  async getDashboardAnalytics() {
    return this.request('/analytics/dashboard');
  }

  async getDealsPerformance(days: number = 30) {
    return this.request(`/analytics/deals/performance?days=${days}`);
  }

  async getClientInsights() {
    return this.request('/analytics/clients/insights');
  }

  async getTeamProductivity() {
    return this.request('/analytics/team/productivity');
  }

  async getExecutiveSummary() {
    return this.request('/analytics/reports/executive-summary');
  }

  // Document endpoints
  async getDocuments(params?: {
    skip?: number;
    limit?: number;
    document_type?: string;
    deal_id?: string;
    status?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.document_type) query.append('document_type', params.document_type);
    if (params?.deal_id) query.append('deal_id', params.deal_id);
    if (params?.status) query.append('status', params.status);

    return this.request(`/documents?${query.toString()}`);
  }

  async getDocument(id: string) {
    return this.request(`/documents/${id}`);
  }

  async createDocument(documentData: any) {
    return this.request('/documents', {
      method: 'POST',
      body: JSON.stringify(documentData),
    });
  }

  async uploadDocument(file: File, metadata: {
    title: string;
    document_type?: string;
    deal_id?: string;
    client_id?: string;
    is_confidential?: boolean;
  }) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', metadata.title);
    if (metadata.document_type) formData.append('document_type', metadata.document_type);
    if (metadata.deal_id) formData.append('deal_id', metadata.deal_id);
    if (metadata.client_id) formData.append('client_id', metadata.client_id);
    if (metadata.is_confidential !== undefined) formData.append('is_confidential', metadata.is_confidential.toString());

    const headers: Record<string, string> = {};
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${this.baseUrl}/documents/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error('Document upload failed:', error);
      return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  async updateDocument(id: string, documentData: any) {
    return this.request(`/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(documentData),
    });
  }

  async deleteDocument(id: string) {
    return this.request(`/documents/${id}`, { method: 'DELETE' });
  }

  // Document Analysis endpoints
  async analyzeDocument(id: string, analysisType?: string, focusAreas?: string[]) {
    return this.request(`/documents/${id}/analyze`, {
      method: 'POST',
      body: JSON.stringify({
        analysis_type: analysisType || 'full',
        focus_areas: focusAreas || ['financial', 'legal', 'risk']
      })
    });
  }

  async getDocumentAnalysis(id: string) {
    return this.request(`/documents/${id}/analysis`);
  }

  async assessDocumentRisk(documentIds: string[], assessmentType?: string) {
    return this.request('/documents/risk-assessment', {
      method: 'POST',
      body: JSON.stringify({
        document_ids: documentIds,
        assessment_type: assessmentType || 'comprehensive'
      })
    });
  }

  async getRiskAssessments(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    return this.request(`/documents/risk-assessments?${query}`);
  }

  async categorizeDocument(id: string) {
    return this.request(`/documents/${id}/categorize`);
  }

  async getDocumentAnalytics() {
    return this.request('/documents/analytics/statistics');
  }

  async getHighRiskDocuments(params?: { skip?: number; limit?: number; risk_threshold?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.risk_threshold) query.append('risk_threshold', params.risk_threshold.toString());
    return this.request(`/documents/high-risk?${query}`);
  }

  // Financial Models endpoints
  async getFinancialModels(params?: {
    skip?: number;
    limit?: number;
    model_type?: string;
    deal_id?: string;
    status?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.model_type) query.append('model_type', params.model_type);
    if (params?.deal_id) query.append('deal_id', params.deal_id);
    if (params?.status) query.append('status', params.status);

    return this.request(`/financial-models?${query.toString()}`);
  }

  async getFinancialModel(id: string) {
    return this.request(`/financial-models/${id}`);
  }

  async createFinancialModel(modelData: any) {
    return this.request('/financial-models', {
      method: 'POST',
      body: JSON.stringify(modelData),
    });
  }

  async updateFinancialModel(id: string, modelData: any) {
    return this.request(`/financial-models/${id}`, {
      method: 'PUT',
      body: JSON.stringify(modelData),
    });
  }

  async deleteFinancialModel(id: string) {
    return this.request(`/financial-models/${id}`, { method: 'DELETE' });
  }

  async createModelVersion(id: string, versionData: any) {
    return this.request(`/financial-models/${id}/versions`, {
      method: 'POST',
      body: JSON.stringify(versionData),
    });
  }

  async getModelVersions(id: string) {
    return this.request(`/financial-models/${id}/versions`);
  }

  async getModelStatistics() {
    return this.request('/financial-models/statistics');
  }

  // Organization endpoints
  async getCurrentOrganization() {
    return this.request('/organizations/me');
  }

  async updateCurrentOrganization(orgData: any) {
    return this.request('/organizations/me', {
      method: 'PUT',
      body: JSON.stringify(orgData),
    });
  }

  async getOrganizationStats() {
    return this.request('/organizations/me/stats');
  }

  // Presentation endpoints
  async getPresentations(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    presentation_type?: string;
    deal_id?: string;
    created_by_me?: boolean;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.status) query.append('status', params.status);
    if (params?.presentation_type) query.append('presentation_type', params.presentation_type);
    if (params?.deal_id) query.append('deal_id', params.deal_id);
    if (params?.created_by_me) query.append('created_by_me', params.created_by_me.toString());

    return this.request(`/presentations/?${query.toString()}`);
  }

  async getPresentation(id: string) {
    return this.request(`/presentations/${id}`);
  }

  async createPresentation(presentationData: any) {
    return this.request('/presentations/', {
      method: 'POST',
      body: JSON.stringify(presentationData),
    });
  }

  async updatePresentation(id: string, presentationData: any) {
    return this.request(`/presentations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(presentationData),
    });
  }

  async deletePresentation(id: string) {
    return this.request(`/presentations/${id}`, { method: 'DELETE' });
  }

  async createPresentationVersion(id: string) {
    return this.request(`/presentations/${id}/version`, { method: 'POST' });
  }

  async getPresentationsByDeal(dealId: string, params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());

    return this.request(`/presentations/deals/${dealId}?${query.toString()}`);
  }

  async getSharedPresentations(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());

    return this.request(`/presentations/shared?${query.toString()}`);
  }

  // Slide endpoints
  async getPresentationSlides(presentationId: string, params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());

    return this.request(`/presentations/${presentationId}/slides?${query.toString()}`);
  }

  async createSlide(presentationId: string, slideData: any) {
    return this.request(`/presentations/${presentationId}/slides/`, {
      method: 'POST',
      body: JSON.stringify(slideData),
    });
  }

  async getSlide(presentationId: string, slideId: string) {
    return this.request(`/presentations/${presentationId}/slides/${slideId}`);
  }

  async updateSlide(presentationId: string, slideId: string, slideData: any) {
    return this.request(`/presentations/${presentationId}/slides/${slideId}`, {
      method: 'PUT',
      body: JSON.stringify(slideData),
    });
  }

  async deleteSlide(presentationId: string, slideId: string) {
    return this.request(`/presentations/${presentationId}/slides/${slideId}`, { method: 'DELETE' });
  }

  async duplicateSlide(presentationId: string, slideId: string, newSlideNumber: number) {
    return this.request(`/presentations/${presentationId}/slides/${slideId}/duplicate?new_slide_number=${newSlideNumber}`, {
      method: 'POST',
    });
  }

  // Template endpoints
  async getPresentationTemplates(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    featured_only?: boolean;
    public_only?: boolean;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.category) query.append('category', params.category);
    if (params?.featured_only) query.append('featured_only', params.featured_only.toString());
    if (params?.public_only) query.append('public_only', params.public_only.toString());

    return this.request(`/presentations/templates/?${query.toString()}`);
  }

  async createPresentationTemplate(templateData: any) {
    return this.request('/presentations/templates/', {
      method: 'POST',
      body: JSON.stringify(templateData),
    });
  }

  async getPresentationTemplate(id: string) {
    return this.request(`/presentations/templates/${id}`);
  }

  async createPresentationFromTemplate(templateId: string, presentationData: any) {
    return this.request(`/presentations/templates/${templateId}/use`, {
      method: 'POST',
      body: JSON.stringify(presentationData),
    });
  }

  // Comment endpoints
  async getPresentationComments(presentationId: string, params?: {
    skip?: number;
    limit?: number;
    resolved_only?: boolean;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.resolved_only !== undefined) query.append('resolved_only', params.resolved_only.toString());

    return this.request(`/presentations/${presentationId}/comments?${query.toString()}`);
  }

  async createPresentationComment(presentationId: string, commentData: any) {
    return this.request(`/presentations/${presentationId}/comments/`, {
      method: 'POST',
      body: JSON.stringify(commentData),
    });
  }

  async resolvePresentationComment(presentationId: string, commentId: string) {
    return this.request(`/presentations/${presentationId}/comments/${commentId}/resolve`, {
      method: 'PUT',
    });
  }

  // Collaboration endpoints
  async getPresentationActivities(presentationId: string, params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());

    return this.request(`/presentations/${presentationId}/activities?${query.toString()}`);
  }

  async getPresentationActiveUsers(presentationId: string) {
    return this.request(`/presentations/${presentationId}/active-users`);
  }

  // Compliance endpoints
  async getComplianceDashboard() {
    return this.request('/compliance/dashboard');
  }

  async getComplianceCategories(params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.is_active !== undefined) query.append('is_active', params.is_active.toString());

    return this.request(`/compliance/categories?${query.toString()}`);
  }

  async getComplianceCategory(id: string) {
    return this.request(`/compliance/categories/${id}`);
  }

  async createComplianceCategory(categoryData: any) {
    return this.request('/compliance/categories', {
      method: 'POST',
      body: JSON.stringify(categoryData),
    });
  }

  async updateComplianceCategory(id: string, categoryData: any) {
    return this.request(`/compliance/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(categoryData),
    });
  }

  async deleteComplianceCategory(id: string) {
    return this.request(`/compliance/categories/${id}`, {
      method: 'DELETE',
    });
  }

  async getComplianceRequirements(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    category_id?: string;
    risk_level?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.status) query.append('status', params.status);
    if (params?.category_id) query.append('category_id', params.category_id);
    if (params?.risk_level) query.append('risk_level', params.risk_level);

    return this.request(`/compliance/requirements?${query.toString()}`);
  }

  async getComplianceRequirement(id: string) {
    return this.request(`/compliance/requirements/${id}`);
  }

  async createComplianceRequirement(requirementData: any) {
    return this.request('/compliance/requirements', {
      method: 'POST',
      body: JSON.stringify(requirementData),
    });
  }

  async updateComplianceRequirement(id: string, requirementData: any) {
    return this.request(`/compliance/requirements/${id}`, {
      method: 'PUT',
      body: JSON.stringify(requirementData),
    });
  }

  async deleteComplianceRequirement(id: string) {
    return this.request(`/compliance/requirements/${id}`, {
      method: 'DELETE',
    });
  }

  async getUpcomingComplianceReviews(params?: {
    days_ahead?: number;
    skip?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    if (params?.days_ahead) query.append('days_ahead', params.days_ahead.toString());
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());

    return this.request(`/compliance/requirements/upcoming-reviews?${query.toString()}`);
  }

  async getComplianceAssessments(params?: {
    skip?: number;
    limit?: number;
    assessment_type?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.assessment_type) query.append('assessment_type', params.assessment_type);

    return this.request(`/compliance/assessments?${query.toString()}`);
  }

  async getComplianceAssessment(id: string) {
    return this.request(`/compliance/assessments/${id}`);
  }

  async createComplianceAssessment(assessmentData: any) {
    return this.request('/compliance/assessments', {
      method: 'POST',
      body: JSON.stringify(assessmentData),
    });
  }

  async updateComplianceAssessment(id: string, assessmentData: any) {
    return this.request(`/compliance/assessments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(assessmentData),
    });
  }

  async getRegulatoryUpdates(params?: {
    skip?: number;
    limit?: number;
    regulation_type?: string;
    impact_level?: string;
    is_reviewed?: boolean;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.append('skip', params.skip.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.regulation_type) query.append('regulation_type', params.regulation_type);
    if (params?.impact_level) query.append('impact_level', params.impact_level);
    if (params?.is_reviewed !== undefined) query.append('is_reviewed', params.is_reviewed.toString());

    return this.request(`/compliance/regulatory-updates?${query.toString()}`);
  }

  async getRegulatoryUpdate(id: string) {
    return this.request(`/compliance/regulatory-updates/${id}`);
  }

  async createRegulatoryUpdate(updateData: any) {
    return this.request('/compliance/regulatory-updates', {
      method: 'POST',
      body: JSON.stringify(updateData),
    });
  }

  async updateRegulatoryUpdate(id: string, updateData: any) {
    return this.request(`/compliance/regulatory-updates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async markRegulatoryUpdateAsReviewed(id: string, reviewNotes?: string) {
    return this.request(`/compliance/regulatory-updates/${id}/review`, {
      method: 'PATCH',
      body: JSON.stringify({ review_notes: reviewNotes }),
    });
  }

  async generateComplianceAuditTrail(auditParams: any) {
    return this.request('/compliance/audit', {
      method: 'POST',
      body: JSON.stringify(auditParams),
    });
  }

  async runComplianceCheck(categoryId?: string) {
    const params = categoryId ? { category_id: categoryId } : {};
    return this.request('/compliance/check', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Export types for use in components
export type { ApiResponse };

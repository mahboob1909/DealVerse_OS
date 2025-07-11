# DealVerse OS - SaaS Architecture Documentation

## 1. Executive Summary

This document outlines the comprehensive technical architecture for DealVerse OS, a unified AI-powered investment banking platform. The architecture is designed to be scalable, secure, and maintainable, with a focus on enabling development by AI coding agents. The system follows modern microservices principles while maintaining simplicity for rapid development and deployment.

## 2. System Architecture Overview

DealVerse OS employs a modern, cloud-native architecture designed for scalability, reliability, and maintainability. The system is structured as a collection of loosely coupled services that communicate through well-defined APIs, enabling independent development, testing, and deployment of individual components.

### 2.1 High-Level Architecture

The architecture follows a three-tier pattern with clear separation of concerns:

**Presentation Layer (Frontend)**
- React.js single-page application (SPA)
- Responsive design supporting desktop, tablet, and mobile devices
- Real-time updates through WebSocket connections
- Progressive Web App (PWA) capabilities for offline functionality

**Application Layer (Backend Services)**
- Microservices architecture with domain-driven design
- RESTful APIs with OpenAPI 3.0 specification
- Event-driven communication between services
- Centralized authentication and authorization

**Data Layer**
- PostgreSQL for relational data and transactions
- MongoDB for document storage and unstructured data
- Redis for caching and session management
- Amazon S3 for file storage and document management

### 2.2 Core Services Architecture

The system is decomposed into the following core services, each responsible for specific business domains:

**User Management Service**
- User authentication and authorization
- Role-based access control (RBAC)
- User profile management
- Session management and security

**Deal Management Service**
- Deal lifecycle management
- Pipeline tracking and status updates
- Deal team assignment and collaboration
- Deal document organization

**Prospect AI Service**
- AI-powered deal sourcing and scoring
- Market intelligence aggregation
- Opportunity identification algorithms
- Predictive analytics for deal success

**Due Diligence Service**
- Document ingestion and processing
- AI-powered document analysis
- Risk assessment and flagging
- Compliance checking and reporting

**Financial Modeling Service**
- Collaborative modeling environment
- Version control for financial models
- Scenario analysis and sensitivity testing
- Automated chart and visualization generation

**Presentation Service**
- Pitchbook creation and management
- Template library and customization
- Real-time collaboration features
- Export and sharing capabilities

**Notification Service**
- Real-time notifications and alerts
- Email and in-app messaging
- Event-driven notification triggers
- User preference management

**Analytics Service**
- Business intelligence and reporting
- User behavior analytics
- Performance metrics and KPIs
- Data visualization and dashboards

## 3. Technology Stack

The technology stack is carefully selected to balance development speed, scalability, and maintainability while being suitable for AI-assisted development.

### 3.1 Frontend Technologies

**Core Framework**
- React.js 18+ with TypeScript for type safety and better development experience
- Next.js for server-side rendering and optimized performance
- React Router for client-side routing and navigation

**State Management**
- Redux Toolkit for global state management
- React Query for server state management and caching
- Context API for component-level state sharing

**UI Components and Styling**
- Material-UI (MUI) for consistent design system
- Styled-components for custom styling and theming
- Framer Motion for animations and micro-interactions

**Data Visualization**
- Chart.js and React-Chartjs-2 for interactive charts
- D3.js for custom data visualizations
- Plotly.js for advanced financial charts

**Development Tools**
- Webpack for module bundling and optimization
- ESLint and Prettier for code quality and formatting
- Jest and React Testing Library for unit testing

### 3.2 Backend Technologies

**Core Framework**
- Python 3.11+ for backend development
- Flask with Flask-RESTful for API development
- FastAPI for high-performance API endpoints requiring async processing

**Database and Storage**
- PostgreSQL 14+ for relational data with ACID compliance
- MongoDB 6+ for document storage and flexible schemas
- Redis 7+ for caching, session storage, and real-time features
- Amazon S3 for file storage with CDN integration

**AI and Machine Learning**
- TensorFlow 2.x for deep learning models
- scikit-learn for traditional machine learning algorithms
- spaCy for natural language processing
- pandas and NumPy for data manipulation and analysis

**Message Queue and Event Processing**
- Celery with Redis broker for asynchronous task processing
- Apache Kafka for event streaming and service communication
- WebSocket support through Flask-SocketIO for real-time features

**Security and Authentication**
- JWT (JSON Web Tokens) for stateless authentication
- OAuth 2.0 for third-party integrations
- bcrypt for password hashing
- Flask-CORS for cross-origin resource sharing

### 3.3 Infrastructure and DevOps

**Containerization and Orchestration**
- Docker for containerization of all services
- Docker Compose for local development environment
- Kubernetes for production orchestration and scaling

**Cloud Platform**
- Amazon Web Services (AWS) as primary cloud provider
- AWS EKS for managed Kubernetes service
- AWS RDS for managed PostgreSQL instances
- AWS ElastiCache for managed Redis clusters

**CI/CD Pipeline**
- GitHub Actions for continuous integration and deployment
- Automated testing and code quality checks
- Blue-green deployment strategy for zero-downtime updates
- Infrastructure as Code using Terraform

**Monitoring and Logging**
- Prometheus for metrics collection and monitoring
- Grafana for visualization and alerting
- ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging
- AWS CloudWatch for cloud-native monitoring

## 4. Database Design

The database design follows domain-driven design principles with clear separation between different business contexts while maintaining data consistency and integrity.

### 4.1 PostgreSQL Schema Design

**Users and Authentication**
```sql
-- Users table for authentication and basic profile
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst',
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations table for multi-tenancy
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Deal Management**
```sql
-- Deals table for core deal information
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- M&A, IPO, Debt, etc.
    status VARCHAR(50) NOT NULL DEFAULT 'prospecting',
    target_company VARCHAR(255),
    deal_size DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    probability INTEGER CHECK (probability >= 0 AND probability <= 100),
    expected_close_date DATE,
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deal team assignments
CREATE TABLE deal_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) NOT NULL, -- lead, analyst, associate, etc.
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(deal_id, user_id)
);
```

**Financial Models**
```sql
-- Financial models with version control
CREATE TABLE financial_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id),
    name VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    model_data JSONB NOT NULL,
    assumptions JSONB DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model scenarios for sensitivity analysis
CREATE TABLE model_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES financial_models(id),
    name VARCHAR(255) NOT NULL,
    parameters JSONB NOT NULL,
    results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 MongoDB Collections Design

**Document Storage**
```javascript
// documents collection for due diligence files
{
  _id: ObjectId,
  dealId: UUID,
  fileName: String,
  fileType: String,
  fileSize: Number,
  s3Key: String,
  uploadedBy: UUID,
  uploadedAt: Date,
  category: String, // financial, legal, operational, etc.
  subcategory: String,
  aiAnalysis: {
    processed: Boolean,
    riskScore: Number,
    keyFindings: [String],
    flags: [{
      type: String,
      severity: String,
      description: String,
      confidence: Number
    }],
    extractedData: Object
  },
  metadata: Object,
  tags: [String]
}
```

**AI Training Data**
```javascript
// ai_models collection for ML model metadata
{
  _id: ObjectId,
  modelType: String, // prospect_scoring, risk_assessment, etc.
  version: String,
  trainingData: {
    datasetSize: Number,
    features: [String],
    accuracy: Number,
    lastTrained: Date
  },
  modelPath: String,
  isActive: Boolean,
  performance: {
    precision: Number,
    recall: Number,
    f1Score: Number
  },
  createdAt: Date,
  updatedAt: Date
}
```

### 4.3 Redis Data Structures

**Session Management**
```
Key: session:{sessionId}
Type: Hash
Fields: {
  userId: UUID,
  organizationId: UUID,
  role: String,
  lastActivity: Timestamp,
  ipAddress: String
}
TTL: 24 hours
```

**Real-time Notifications**
```
Key: notifications:{userId}
Type: List
Value: JSON objects containing notification data
TTL: 30 days
```

**Caching Strategy**
```
Key: deal:{dealId}:summary
Type: String (JSON)
Value: Cached deal summary data
TTL: 1 hour

Key: user:{userId}:permissions
Type: Set
Value: User permission strings
TTL: 4 hours
```

## 5. API Design and Specifications

The API design follows RESTful principles with clear resource modeling and consistent response formats. All APIs are documented using OpenAPI 3.0 specification for automatic client generation and testing.

### 5.1 API Architecture Principles

**Resource-Oriented Design**
- URLs represent resources, not actions
- HTTP methods indicate operations (GET, POST, PUT, DELETE)
- Consistent naming conventions using plural nouns
- Hierarchical resource relationships reflected in URL structure

**Response Format Standardization**
```json
{
  "success": true,
  "data": {
    // Resource data or array of resources
  },
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "totalPages": 8
    },
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "errors": [] // Only present when success is false
}
```

**Error Handling**
```json
{
  "success": false,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input data",
      "field": "email",
      "details": "Email format is invalid"
    }
  ],
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req_123456789"
  }
}
```

### 5.2 Core API Endpoints

**Authentication and User Management**
```
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
GET /api/v1/users/profile
PUT /api/v1/users/profile
GET /api/v1/users/{userId}
```

**Deal Management**
```
GET /api/v1/deals
POST /api/v1/deals
GET /api/v1/deals/{dealId}
PUT /api/v1/deals/{dealId}
DELETE /api/v1/deals/{dealId}
GET /api/v1/deals/{dealId}/team
POST /api/v1/deals/{dealId}/team
DELETE /api/v1/deals/{dealId}/team/{userId}
```

**Prospect AI**
```
GET /api/v1/prospects
POST /api/v1/prospects/search
GET /api/v1/prospects/{prospectId}/score
POST /api/v1/prospects/{prospectId}/analyze
GET /api/v1/market-intelligence
```

**Due Diligence**
```
GET /api/v1/deals/{dealId}/documents
POST /api/v1/deals/{dealId}/documents/upload
GET /api/v1/documents/{documentId}
GET /api/v1/documents/{documentId}/analysis
POST /api/v1/documents/{documentId}/analyze
```

**Financial Modeling**
```
GET /api/v1/deals/{dealId}/models
POST /api/v1/deals/{dealId}/models
GET /api/v1/models/{modelId}
PUT /api/v1/models/{modelId}
GET /api/v1/models/{modelId}/scenarios
POST /api/v1/models/{modelId}/scenarios
```

### 5.3 WebSocket Events

**Real-time Collaboration**
```javascript
// Model collaboration events
{
  event: 'model:cell_updated',
  data: {
    modelId: 'uuid',
    cellId: 'A1',
    value: 1000000,
    userId: 'uuid',
    timestamp: '2024-01-15T10:30:00Z'
  }
}

// Document analysis completion
{
  event: 'document:analysis_complete',
  data: {
    documentId: 'uuid',
    dealId: 'uuid',
    riskScore: 0.75,
    flags: [...],
    timestamp: '2024-01-15T10:30:00Z'
  }
}

// Deal status updates
{
  event: 'deal:status_changed',
  data: {
    dealId: 'uuid',
    oldStatus: 'due_diligence',
    newStatus: 'negotiation',
    changedBy: 'uuid',
    timestamp: '2024-01-15T10:30:00Z'
  }
}
```

## 6. Security Architecture

Security is paramount in investment banking applications due to the sensitive nature of financial data and regulatory requirements. The security architecture implements defense-in-depth principles with multiple layers of protection.

### 6.1 Authentication and Authorization

**Multi-Factor Authentication (MFA)**
- TOTP (Time-based One-Time Password) support
- SMS-based verification as fallback
- Hardware security key support (FIDO2/WebAuthn)
- Biometric authentication for mobile applications

**Role-Based Access Control (RBAC)**
```python
# Permission matrix example
PERMISSIONS = {
    'analyst': [
        'deals:read',
        'models:create',
        'models:edit_own',
        'documents:read',
        'documents:upload'
    ],
    'associate': [
        'deals:read',
        'deals:edit',
        'models:create',
        'models:edit_all',
        'documents:read',
        'documents:upload',
        'documents:analyze'
    ],
    'vp': [
        'deals:create',
        'deals:edit',
        'deals:delete',
        'team:manage',
        'models:approve',
        'compliance:review'
    ],
    'md': [
        'deals:all',
        'team:all',
        'organization:manage',
        'analytics:all'
    ]
}
```

**JWT Token Management**
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days)
- Token rotation on refresh
- Secure token storage with httpOnly cookies

### 6.2 Data Protection

**Encryption Standards**
- AES-256 encryption for data at rest
- TLS 1.3 for data in transit
- End-to-end encryption for sensitive documents
- Database-level encryption for PII fields

**Data Classification**
```python
DATA_CLASSIFICATION = {
    'public': {
        'encryption': False,
        'access_logging': False,
        'retention_days': 365
    },
    'internal': {
        'encryption': True,
        'access_logging': True,
        'retention_days': 2555  # 7 years
    },
    'confidential': {
        'encryption': True,
        'access_logging': True,
        'retention_days': 2555,
        'approval_required': True
    },
    'restricted': {
        'encryption': True,
        'access_logging': True,
        'retention_days': 2555,
        'approval_required': True,
        'mfa_required': True
    }
}
```

### 6.3 Compliance and Auditing

**Audit Trail Requirements**
- All user actions logged with timestamps
- Data access and modification tracking
- Failed authentication attempt monitoring
- Compliance report generation

**Regulatory Compliance**
- SOX (Sarbanes-Oxley) compliance for financial data
- GDPR compliance for EU users
- SOC 2 Type II certification
- ISO 27001 security management

## 7. Scalability and Performance

The architecture is designed to handle growth in users, data volume, and transaction throughput while maintaining responsive performance.

### 7.1 Horizontal Scaling Strategy

**Microservices Scaling**
- Independent scaling of services based on demand
- Auto-scaling groups with CPU and memory thresholds
- Load balancing with health checks
- Circuit breaker pattern for fault tolerance

**Database Scaling**
- Read replicas for PostgreSQL to distribute read load
- MongoDB sharding for document storage
- Redis clustering for cache distribution
- Connection pooling to optimize database connections

### 7.2 Caching Strategy

**Multi-Level Caching**
```python
# Cache hierarchy
CACHE_LEVELS = {
    'browser': {
        'type': 'client_side',
        'ttl': '1 hour',
        'data': ['static_assets', 'user_preferences']
    },
    'cdn': {
        'type': 'edge_cache',
        'ttl': '24 hours',
        'data': ['images', 'documents', 'static_content']
    },
    'application': {
        'type': 'redis',
        'ttl': '1 hour',
        'data': ['api_responses', 'computed_data']
    },
    'database': {
        'type': 'query_cache',
        'ttl': '15 minutes',
        'data': ['frequent_queries', 'aggregations']
    }
}
```

### 7.3 Performance Optimization

**Frontend Optimization**
- Code splitting and lazy loading
- Image optimization and WebP format
- Service worker for offline functionality
- Bundle size optimization with tree shaking

**Backend Optimization**
- Database query optimization with proper indexing
- Async processing for heavy computations
- Connection pooling and keep-alive
- Compression for API responses

## 8. AI and Machine Learning Integration

The AI components are designed to be modular and easily trainable, with clear interfaces for model deployment and monitoring.

### 8.1 AI Service Architecture

**Model Serving Infrastructure**
- TensorFlow Serving for production model deployment
- Model versioning and A/B testing capabilities
- GPU acceleration for compute-intensive models
- Batch and real-time inference endpoints

**Training Pipeline**
```python
# ML Pipeline stages
ML_PIPELINE = {
    'data_ingestion': {
        'sources': ['deals', 'documents', 'market_data'],
        'frequency': 'daily',
        'validation': True
    },
    'feature_engineering': {
        'transformations': ['normalization', 'encoding', 'aggregation'],
        'feature_store': 'feast'
    },
    'model_training': {
        'algorithms': ['random_forest', 'neural_networks', 'gradient_boosting'],
        'validation': 'cross_validation',
        'hyperparameter_tuning': True
    },
    'model_evaluation': {
        'metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
        'threshold': 0.85,
        'bias_detection': True
    },
    'deployment': {
        'strategy': 'blue_green',
        'monitoring': True,
        'rollback': 'automatic'
    }
}
```

### 8.2 AI Model Specifications

**Prospect Scoring Model**
- Input: Company financial data, market conditions, industry trends
- Output: Deal probability score (0-1) with confidence interval
- Algorithm: Gradient boosting with feature importance
- Retraining: Monthly with new deal outcomes

**Document Risk Assessment**
- Input: Document text, metadata, deal context
- Output: Risk categories and severity scores
- Algorithm: BERT-based transformer with fine-tuning
- Retraining: Quarterly with expert feedback

**Market Intelligence**
- Input: News articles, financial reports, market data
- Output: Trend analysis and opportunity identification
- Algorithm: NLP pipeline with sentiment analysis
- Retraining: Weekly with new market data

## 9. Deployment and DevOps

The deployment strategy emphasizes automation, reliability, and rapid recovery while maintaining security and compliance requirements.

### 9.1 Infrastructure as Code

**Terraform Configuration**
```hcl
# Example EKS cluster configuration
resource "aws_eks_cluster" "dealverse" {
  name     = "dealverse-${var.environment}"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.allowed_cidrs
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_service_policy,
  ]
}
```

### 9.2 CI/CD Pipeline

**GitHub Actions Workflow**
```yaml
name: Deploy DealVerse OS
on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app tests/
      - name: Security scan
        run: bandit -r app/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t dealverse:${{ github.sha }} .
      - name: Push to registry
        run: docker push dealverse:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: kubectl apply -f k8s/
```

### 9.3 Monitoring and Alerting

**Prometheus Metrics**
```yaml
# Custom metrics for business logic
dealverse_deals_total{status="active"} 150
dealverse_deals_total{status="closed"} 45
dealverse_api_requests_total{endpoint="/api/v1/deals",method="GET"} 1250
dealverse_model_inference_duration_seconds{model="prospect_scoring"} 0.125
dealverse_document_processing_queue_size 23
```

**Alert Rules**
```yaml
groups:
  - name: dealverse.rules
    rules:
      - alert: HighErrorRate
        expr: rate(dealverse_api_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
          
      - alert: DatabaseConnectionFailure
        expr: dealverse_db_connections_failed_total > 5
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Database connection failures
```

## 10. Development Guidelines for AI Coding Agents

This section provides specific guidance for AI coding agents to ensure consistent, maintainable, and secure code generation.

### 10.1 Code Structure and Organization

**Project Structure**
```
dealverse-os/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── utils/
│   │   └── __init__.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── infrastructure/
│   ├── terraform/
│   ├── kubernetes/
│   └── docker-compose.yml
└── docs/
```

### 10.2 Coding Standards

**Python Backend Standards**
```python
# Example service class structure
from typing import List, Optional
from dataclasses import dataclass
from app.models import Deal
from app.utils.exceptions import ValidationError

@dataclass
class DealCreateRequest:
    name: str
    type: str
    target_company: str
    deal_size: Optional[float] = None

class DealService:
    def __init__(self, db_session, user_context):
        self.db = db_session
        self.user = user_context
    
    def create_deal(self, request: DealCreateRequest) -> Deal:
        """Create a new deal with validation and authorization."""
        self._validate_create_request(request)
        self._check_create_permissions()
        
        deal = Deal(
            name=request.name,
            type=request.type,
            target_company=request.target_company,
            deal_size=request.deal_size,
            organization_id=self.user.organization_id,
            created_by=self.user.id
        )
        
        self.db.add(deal)
        self.db.commit()
        return deal
    
    def _validate_create_request(self, request: DealCreateRequest):
        if not request.name or len(request.name) < 3:
            raise ValidationError("Deal name must be at least 3 characters")
        # Additional validation logic
    
    def _check_create_permissions(self):
        if not self.user.has_permission('deals:create'):
            raise PermissionError("Insufficient permissions")
```

**React Frontend Standards**
```typescript
// Example component structure
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from 'react-query';
import { Deal, DealCreateRequest } from '../types/deal';
import { dealService } from '../services/dealService';

interface DealListProps {
  organizationId: string;
}

export const DealList: React.FC<DealListProps> = ({ organizationId }) => {
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
  
  const { data: deals, isLoading, error } = useQuery(
    ['deals', organizationId],
    () => dealService.getDeals(organizationId),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );
  
  const createDealMutation = useMutation(
    (request: DealCreateRequest) => dealService.createDeal(request),
    {
      onSuccess: () => {
        // Invalidate and refetch deals
        queryClient.invalidateQueries(['deals', organizationId]);
      },
    }
  );
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="deal-list">
      {deals?.map(deal => (
        <DealCard
          key={deal.id}
          deal={deal}
          onSelect={setSelectedDeal}
          isSelected={selectedDeal?.id === deal.id}
        />
      ))}
    </div>
  );
};
`
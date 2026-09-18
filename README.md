# PackagePro — Dynamic Tour Packages 🌍

PackagePro is a production-grade, event-driven travel platform that allows users to create dynamic, highly personalized tour packages. 

Unlike conventional travel booking platforms, PackagePro features an **Autonomous Event-Driven Trip Agent** that dynamically responds to real-world disruptions (e.g., attraction closures, weather changes) by deterministically finding and validating alternative itinerary items in real-time, all while preserving the user's budget, schedule, and preferences.

This repository serves as a showcase of modern software engineering practices, prioritizing maintainability, scalability, clean architecture, and deterministic AI validation over rapid prototyping.

---

## 🎯 Core Capabilities

1. **Dynamic Tour Package Builder**: Customize destinations, durations, guides, and activities.
2. **Deterministic Pricing Engine**: Strict decoupling of pricing logic from AI. All prices are calculated securely and deterministically via backend services.
3. **Local Tour Guide System**: First-class domain representation of guides with specializations, real-time availability, and language capabilities.
4. **Autonomous AI Trip Agent**: An event-driven background service (LangGraph + Kafka) that detects itinerary disruptions, semantically searches for replacements via `pgvector`, validates them against user constraints, and proposes seamless updates.
5. **Adaptive Itineraries**: Granular constraints (e.g., `preserve_budget`, `replacement_allowed`) on every itinerary item.

---

## 🏗️ System Architecture

The application follows a highly decoupled, service-oriented architecture. The frontend is cleanly separated from the FastAPI backend, and heavy AI/Agent workloads are offloaded to background workers via Kafka and Celery.

```mermaid
flowchart TD
    %% Frontend Layer
    Client[Next.js App Router Client]
    
    %% API Gateway & Services
    subgraph FastAPI Backend
        API[API Gateway]
        TS[Trip Service]
        PS[Package Service]
        US[User Service]
    end
    
    %% Deterministic Engines
    subgraph Deterministic Engines
        PE[Pricing Engine]
        AS[Availability Service]
        Val[Validation Layer]
    end
    
    %% Event & Agent System
    subgraph Event & Agent System
        ExtEvent[External Disruption Event]
        Kafka[Apache Kafka Topic]
        Celery[Celery Worker]
        LangGraph[LangGraph AI Agent]
    end
    
    %% Data Layer
    subgraph Data Layer
        DB[(PostgreSQL + pgvector)]
        Redis[(Redis Cache / PubSub)]
    end

    %% Flow
    Client <-->|REST / SSE| API
    API --> TS & PS & US
    TS --> PE & AS
    
    ExtEvent -->|Webhook| API
    API -->|Publish| Kafka
    Kafka -->|Consume| Celery
    Celery --> LangGraph
    
    LangGraph -->|1. Context Retrieval| DB
    LangGraph -->|2. Propose Action| Val
    Val -->|3. Validate Constraint| AS & PE
    Val -->|4. Apply Update| DB
    Val -->|5. Notify via PubSub| Redis
    Redis -->|Server-Sent Events| Client
```

---

## 💾 Domain Model (ER Diagram)

The database acts as the single source of truth. We use PostgreSQL with the `pgvector` extension for semantic search (RAG) when the AI agent hunts for alternative activities.

```mermaid
erDiagram
    USERS ||--o{ TRIPS : creates
    USERS {
        uuid id PK
        string email
        string role
        jsonb preferences
    }
    
    DESTINATIONS ||--o{ ACTIVITIES : has
    DESTINATIONS ||--o{ GUIDES : has
    DESTINATIONS {
        uuid id PK
        string name
        string country
        vector embedding
    }
    
    ACTIVITIES {
        uuid id PK
        uuid destination_id FK
        string type
        numeric base_price
        vector embedding
    }

    GUIDES {
        uuid id PK
        uuid destination_id FK
        string name
        jsonb specializations
        numeric base_price_per_day
    }
    
    TRIPS ||--o{ ITINERARY_ITEMS : contains
    TRIPS {
        uuid id PK
        uuid user_id FK
        date start_date
        date end_date
        numeric total_price
    }
    
    ITINERARY_ITEMS {
        uuid id PK
        uuid trip_id FK
        string component_type
        uuid component_id
        jsonb agent_constraints
        string status
    }
    
    AGENT_EVENTS ||--o{ AGENT_ACTIONS : triggers
    AGENT_EVENTS {
        uuid id PK
        string event_type
        jsonb payload
    }
    
    AGENT_ACTIONS {
        uuid id PK
        uuid event_id FK
        uuid trip_id FK
        jsonb proposed_changes
        string status
    }
```

---

## 🤖 The Autonomous Event-Driven Agent Workflow

One of the strict safety rules of this project is that **the AI must NEVER have unrestricted authority over the database**. 

```mermaid
sequenceDiagram
    participant E as Event Source
    participant K as Kafka
    participant A as LangGraph Agent
    participant V as Validation Layer
    participant DB as PostgreSQL
    participant UI as Next.js Client

    E->>K: Emit 'MUSEUM_CLOSED' Event
    K->>A: Consume Event
    A->>DB: Retrieve User Preferences & Itinerary
    A->>DB: pgvector semantic search for alternatives
    A->>A: Generate proposed itinerary diff
    A->>V: Submit Proposed Action
    
    Note over V: Deterministic Validation
    V->>V: Check time constraints
    V->>V: Check budget constraints
    V->>V: Check availability
    
    alt is valid
        V->>DB: Execute Action & Update Price
        V->>UI: SSE: Push Notification "Trip Updated"
    else is invalid
        V-->>A: Reject Action (Feedback Loop)
        A->>A: Regenerate new proposal
    end
```

---

## 🛠️ Technology Stack & Justification

### Frontend
* **Next.js (App Router) & React**: Server-side rendering for SEO (curated packages) and highly interactive client components for the dynamic trip builder.
* **Tailwind CSS & shadcn/ui**: For a premium, accessible, and highly customizable UI system.
* **TanStack Query & Zustand**: For handling complex server-state synchronization and client-side builder state.
* **Framer Motion**: For fluid micro-interactions, especially when communicating AI agent activity.

### Backend
* **Python & FastAPI**: Chosen for its native asynchronous support, Pydantic data validation, and seamless integration with the Python AI ecosystem.
* **SQLAlchemy 2.0 & Alembic**: Robust ORM and migration management.
* **Apache Kafka & Celery**: For decoupled, highly scalable event streaming and background task processing.
* **Redis**: Used as a caching layer, for distributed locking, and as a PubSub broker for real-time Server-Sent Events (SSE).

### Data & AI
* **PostgreSQL + pgvector**: A unified data layer preventing the need for a separate vector database. Handles both relational constraints and semantic similarity search.
* **LangGraph**: Orchestrates the multi-step AI reasoning loops (Context -> Search -> Plan -> Submit), allowing cyclic feedback from the deterministic Validation Layer.

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### 1. Start the Infrastructure
Spin up PostgreSQL (with pgvector), Redis, Zookeeper, and Kafka.
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations and seed data
alembic upgrade head
export PYTHONPATH=.
python app/db/seed.py

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Quality Assurance & Observability

- **Unit Testing**: Strict `pytest` coverage for the deterministic `PricingEngine` and `ValidationLayer`.
- **E2E Testing**: Playwright for critical user flows (e.g., custom package builder -> price calculation -> checkout).
- **Audit Trails**: Every action proposed by the LangGraph agent is durably recorded in the `agent_actions` table, creating a transparent, auditable history of AI decision-making.

---
*Built as a Final Year Project to demonstrate scalable, production-grade architectural design.*

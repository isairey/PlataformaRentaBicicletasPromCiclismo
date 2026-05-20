# Architectural Decision: Technology Stack & Development Practices

Date: March 3rd, 2026

## Decision

For the bike-sharing system to be implemented. The technology stack is defined as follows:

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend Services | Python + Flask | REST API microservices |
| Frontend | TypeScript + React | Static web client |
| Databases | MySQL | Relational data persistence |
| Maps | Leaflet | Interactive bike and station mapping |
| Authentication | Firebase + JWT | Stateless token-based authentication |
| Message Broker | RabbitMQ | Asynchronous inter-service communication |
| Orchestration | Kubernetes (EKS) | Container orchestration and scaling |

This decision is scoped to programming languages, frameworks, libraries, protocols, and development practices known by the team.

## Impacts & Implications

Dependencies introduced:

- All backend services depend on Python and Flask. Any service that deviates from this stack introduces inconsistency in tooling, testing, and deployment pipelines.
- The frontend depends on the REST API contract exposed by Flask services. Breaking changes to API endpoints directly impact the React client.
- Services that require it must be capable of accessing MySQL services at any given time. Schema migrations must be coordinated across services to avoid breaking changes.
- JWT validation logic must be consistent across all services that protect endpoints. A discrepancy in token validation (e.g., different secret keys or expiration handling) will cause authentication failures.
- RabbitMQ is a shared dependency for all services that publish or consume asynchronous events. If the broker is unavailable, rental, return, and map update flows degrade.

Organizational implications:

- All team members must have experience working with Python and TypeScript. A developer working primarily in one layer must still be able to read and understand code in the other.
- API contracts between services must be documented and versioned. Uncoordinated changes to REST endpoints will break consumers silently.
- JWT secrets must be managed externally (via Kubernetes secrets, as defined in AD-Cloud) and never hardcoded in source files.
- Database migrations must go through a controlled process. Direct schema changes in production without a migration script are not acceptable.

Risk analysis:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API contract broken between the service and the frontend | Medium | High | Define and document OpenAPI specs per service, validate on CI |
| JWT secret exposed in source control | Low | High | Inject secrets at runtime via Kubernetes secrets. |
| MySQL schema drift between environments | Medium | Medium | Use a migration tool (e.g., Alembic or Flask-Migrate) and apply migrations on deploy |
| Leaflet map data latency is affecting the user experience | Low | Low | Cache station and bike data on the client and refresh on an interval |

Skills required:

- Python: Flask, REST API design, Gunicorn, unit testing with pytest
- TypeScript: React, component design, API integration, state management
- MySQL: schema design, indexing, transactions, migration tooling
- RabbitMQ: exchange and queue configuration, publisher/consumer patterns
- Kubernetes: Deployment manifests, Services, Ingress, ConfigMaps, Secrets

## Problem & Constraints

### Description

Background: The bike-sharing system requires a set of software technologies capable of supporting the functional and non-functional requirements defined for the platform. The team evaluated multiple options across each layer of the stack, considering factors such as team familiarity, community support, licensing, performance characteristics, and alignment with the system's domain model. This document records the decisions made and the rationale behind each one.

Goal: Define a coherent, maintainable, and scalable technology stack that enables the development team to build, test, and deploy the bike-sharing platform efficiently while satisfying the system's functional and non-functional requirements.

Objectives:

Refer to the Functional and non functional requirements document

Short-Term Benefits: The selected stack gives the team immediate access to a well-documented, widely used set of tools. Flask and React have large ecosystems and abundant reference material, reducing the time spent on tooling issues and allowing the team to focus on domain logic from the start.

Long-Term Benefits: The stack is composed of technologies with strong industry adoption. Skills acquired during this project are directly transferable to professional environments. The use of TypeScript, microservices, and Kubernetes establishes engineering practices that scale beyond the academic context.

### Context

The project is developed by a small team of software engineering postgraduate students. All team members have working knowledge of Python and JavaScript/TypeScript. The system's domain model, consisting of users, bikes, stations, rentals, routes, and events, is inherently relational. The platform requires real-time map rendering, asynchronous event handling, and secure, authenticated access. No prior codebase exists that constrains the technology choices.

### Scope

This decision covers all technology choices at the application layer: programming languages, frameworks, libraries, protocols, and development practices. It does not cover:

- Cloud infrastructure, managed services, or deployment environment configuration.
- Database hosting configuration

Responsibility for the decisions in this document lies with the full design and development team.

### Constraints

Business:

- All technologies must be open source or available under a license that permits use in an academic project without cost.
- The team must be able to build, run, and test the full stack on local development machines without depending on paid services.

Architecture:

- The system must follow a microservices model. A single monolithic backend application is not acceptable.
- The frontend must be a decoupled static application served independently from the backend services.
- Inter-service communication that does not require an immediate response must be handled asynchronously via the message broker, not via synchronous HTTP calls. Instead the development team should follow a request-reply model.

Technology:

- REST over HTTP is the required protocol for client-to-service communication. GraphQL and gRPC are out of scope for this phase.
- Authentication must use JWT.

Assumptions:

- The team will acquire sufficient proficiency in TypeScript and React to deliver a functional frontend within the project timeline.
- Flask's synchronous request handling is sufficient for the expected concurrency at this scale. Async frameworks are not required.
- Leaflet's default tile provider (OpenStreetMap) is sufficient for the geographic scope of Medellín. No paid map API is required.

## Solutions Analysis

### Solution Architecture

The backend is composed of five Flask microservices, each responsible for a distinct bounded context: authentication, rental management, bike management, geolocation, and community events and routes. Each service exposes a versioned REST API and runs as an independent containerized workload on Kubernetes.

The React frontend is a statically compiled TypeScript application. It communicates with backend services via HTTP REST calls through a Kubernetes Ingress controller, renders bike coordinate data on a Leaflet map, and authenticates users through a JWT flow managed by the Auth service. The compiled static bundle is served from AWS S3. The frontend presents three distinct view contexts: unauthenticated users (login, registration), authenticated users (map, rental flow, community routes, and events), and administrators (bike management, community content management).

JWT tokens are issued by the Auth service upon successful login via Firebase. All other services validate the token on each request using a shared secret injected at runtime via Kubernetes Secrets. No service stores session state.

RabbitMQ handles all asynchronous flows. The bike service publishes create and delete events, which are consumed by the geolocation service to maintain its coordinate records in sync. The rental service publishes started and completed events: the bike service consumes these to keep availability status current, and the geolocation service consumes rental completed events to update a bike's last known position after a return.

MySQL provides the persistence layer for the Auth, Rental, Bike, and Events/Routes services. The Geolocation service owns a separate MySQL instance exclusively storing coordinate data indexed by bike ID. Schema migrations are managed with a migration tool and applied as part of the deployment process.

### Solutions Comparative Analysis

#### Backend Language and Framework

| Criteria | Python + Flask | Java + Spring Boot | Node.js + Express |
|----------|----------------|--------------------|-------------------|
| Team familiarity | High | Low | Medium |
| REST API support | Strong, via Flask-RESTful or native routing | Strong, mature ecosystem | Strong |
| Lightweight microservice fit | High (minimal boilerplate) | Low (heavy configuration) | High |
| Community and documentation | Large | Very large | Large |
| Performance (moderate load) | Sufficient | High | High |
| Licensing | Open source | Open source | Open source |
| Decision | Selected | Not selected | Not selected |

#### Frontend Language and Framework

| Criteria | TypeScript + React | JavaScript + React | Vue.js |
|----------|--------------------|--------------------|--------|
| Type safety | Yes (static typing enforced) | No (runtime errors possible) | Optional (via TypeScript) |
| Team familiarity | High | High | Low |
| Component reusability | High | High | High |
| Ecosystem and tooling | Very large | Very large | Large |
| Industry adoption | Very high | Very high | Moderate |
| Decision | Selected | Not selected | Not selected |

#### Database

| Criteria | MySQL | PostgreSQL | MongoDB |
|----------|-------|------------|---------|
| Relational model support | Yes | Yes | No (document model) |
| Team familiarity | High | Medium | Medium |
| Licensing | Open source | Open source | Open source |
| Managed AWS service | RDS for MySQL | RDS for PostgreSQL | DocumentDB |
| Decision | Selected | Not selected | Not selected |

#### Map Library

| Criteria | Leaflet | Google Maps JS API | Mapbox GL JS |
|----------|---------|--------------------|--------------|
| Open source | Yes | No | Partially (SDK open source, tiles require API key) |
| API key required | No (uses OpenStreetMap) | Yes (paid) | Yes (free tier, then paid) |
| React integration | Simple (react-leaflet) | Moderate | Moderate |
| Licensing cost | Free | Pay-per-use | Free tier, then paid |
| Decision | Selected | Not selected | Not selected |

#### Authentication Mechanism

| Criteria | JWT (stateless) | Session-based (server-side) | OAuth2 (delegated) |
|----------|-----------------|-----------------------------|--------------------|
| Stateless | Yes | No | Depends on implementation |
| Horizontal scaling compatibility | Yes (no shared session store needed) | No (requires shared session store) | Yes |
| Implementation complexity with Flask | Low | Low | High |
| Fits the microservices model | Yes | No | Yes |
| Decision | Selected | Not selected | Not selected |

### Rationale

Python with Flask was selected as the backend framework because it aligns with the team's strongest language competency, requires minimal boilerplate for REST API development, and is well-suited for a five-service microservices model where each service is small and focused. Flask's simplicity reduces time-to-delivery without sacrificing the ability to add structure as services grow.

TypeScript with React was selected for the frontend because it satisfies the type safety requirement while maintaining the team's existing React knowledge. The choice of TypeScript over plain JavaScript is a deliberate engineering decision: in a team setting, static types reduce the cost of integration errors between the frontend and the REST APIs of five independent services.

MySQL was selected because the domain model is relational by nature. Users have rentals, rental reference bikes, bikes have availability states driven by rental events, and community routes and events are managed entities with their own relational structure. These relationships require referential integrity and transactional consistency. The Geolocation service uses a dedicated MySQL instance rather than a shared one, both to own its data independently and to avoid cross-service schema coupling. PostgreSQL is an equivalent alternative and was not dismissed on technical grounds, only on familiarity.

Leaflet was selected because it is the only map library among the evaluated options that requires no API key, no account registration, and incurs no usage cost, satisfying the zero-licensing constraint directly. It renders bike coordinate data served by the Geolocation service without any dependency on third-party map providers.

JWT was selected as the authentication mechanism because it is stateless, which is a hard requirement for horizontal scaling of backend services. The Auth service issues tokens via Firebase, and all other services validate them independently at runtime using a shared secret injected via Kubernetes secrets. No service stores session state.

RabbitMQ was selected for asynchronous communication to decouple the services that produce state changes from those that react to them. The bike service publishes creation and deletion events consumed by the geolocation service. The rental service publishes rental lifecycle events consumed by both the bike service and the geolocation service. Synchronous HTTP calls between services for these flows would create cascading failure points and increase response latency for the end user. The AMQP protocol ensures compatibility with standard client libraries, preserving flexibility if any service is rewritten.

Kubernetes was selected as the orchestration platform because it enables horizontal pod autoscaling, rolling deployments with zero downtime, and automatic pod recovery, directly satisfying the requirements. Bare Docker Compose deployments were dismissed because they do not support these operational capabilities at any meaningful scale.

## Change History

| Version | Comments | Date |
|---------|----------|------|
| 1.0 | Initial architectural decision | 2026-03-03 |
# Architectural Decision: Cloud Infrastructure & Deployment

Date: March 3rd, 2026

## Decision

For the public bike-sharing system to be implemented. The cloud infrastructure will be hosted on Amazon Web Services (AWS), complemented by two external managed services. The full set of components is:

| Component | Provider | Purpose |
|-----------|----------|---------|
| RDS | AWS | Relational data persistence |
| EKS | AWS | Managed Kubernetes cluster orchestration |
| S3 | AWS | Static frontend hosting |
| RabbitMQ | External | Asynchronous message broker |
| Firebase Authentication | External (Google) | User identity and authentication |

This decision is scoped exclusively to cloud infrastructure. Framework choices, programming languages, internal software architecture, and development practices are addressed in a separate document.

## Impacts & Implications

Dependencies introduced:

- The system has a hard dependency on Firebase Authentication for all user identity operations. Any breaking change in Firebase directly affects login and registration flows.
- Asynchronous inter-service communication depends entirely on RabbitMQ. Services that rely on message queuing (e.g., bike availability updates, ride event processing) will fail or degrade if the broker is unavailable.
- The free tiers of both RabbitMQ and Firebase are assumed to be sufficient for the projected load of an initial deployment. Exceeding these limits requires a re-evaluation of the budget and range.

Organizational implications:

- The team must maintain AWS IAM roles and policies. Misconfigured permissions are a common source of production incidents.
- Even though the team is learning actively, Kubernetes (EKS) has a steep operational learning curve. The team must be capable of managing deployments, services, ingress controllers, and horizontal pod autoscaling.
- Secrets stored in the Kubernetes secrets. They must never be committed to version control. A clear secret management procedure must be documented and followed.

Risk analysis:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Free tier limits exceeded under demo load | Medium | High | Monitor usage from day one; define upgrade thresholds |
| Firebase breaking change or deprecation | Low | High | Abstract authentication behind an internal interface to allow provider swap |
| RabbitMQ connection saturation on free tier | Medium | Medium | Limit concurrent consumers; implement dead-letter queues |

Skills required:

- AWS core services: IAM, EKS, RDS, S3
- Kubernetes: deployment manifests, services, ingress, autoscaling
- Docker: image building and registry management
- RabbitMQ: queue/exchange configuration, consumer management
- Firebase: SDK integration, authentication rule configuration

## Problem & Constraints

### Description

Background: Multiple urban mobility studies conducted in the Medellín metropolitan area identify a gap in last-mile and intermediate-distance transportation. Cycling adoption has increased among young adults and adults, driven by infrastructure investments such as the ciclovías network and cultural campaigns promoting sustainable transport. The city currently lacks a unified, technology-enabled public bike-sharing system. This architectural decision addresses the cloud infrastructure required to support such a system.

Goal: Provide a robust, scalable, and secure cloud-based infrastructure that supports a physical bike-sharing network in the Medellín metropolitan area, enabling citizens to locate, reserve, unlock, and return bicycles through a digital platform.

Objectives:

Refer to the Functional and non functional requirements document

Short-Term Benefits: Upon deployment, the project will have a production-ready cloud environment with managed database persistence, container orchestration, secure secret management, and authenticated API access.

Long-Term Benefits: The use of Kubernetes via EKS abstracts the infrastructure from the underlying cloud provider, enabling future migration if cost or compliance requirements change. The architecture supports independent scaling of individual services, reducing waste and cost at scale.

### Context

The project is developed in an academic context with no prior system in production that could be affected. The development team is a small group of software engineering postgraduate students with working knowledge of cloud services, containerization, backend, and frontend development.

### Scope

This decision covers all cloud infrastructure components: compute, storage, networking, secret management, authentication, and messaging. It does not cover:

- Application-level architecture (microservices design, API contracts, database schemas)
- Frontend framework adapted for browsers
- Development environment setup

Responsibility for the decisions in this document lies with the full design and development team.

### Constraints

Business:

- The project has no allocated budget beyond the AWS Free Tier and the free tiers of external services. All infrastructure choices must operate within these tiers for the educational deployment phase.

Architecture:

- The system must support the independent deployment and scaling of individual services. A monolithic deployment model is not acceptable.
- The frontend must be decoupled from the backend and served independently.
- No prior architectural decisions constrain this document. This is the first AD in the project.

Technology:

- Kubernetes is required as the container orchestration platform to meet the portability and scalability of NFRs.
- The authentication system must support OAuth2/OpenID Connect-compatible flows to remain portable.
- The message broker must support AMQP protocol to remain compatible with standard consumer libraries.

Assumptions:

- Free tier quotas for RabbitMQ (CloudAMQP Lemur) and Firebase (Spark) are sufficient for the expected academic-scale load.
- The team has or will acquire sufficient knowledge to operate EKS clusters and Kubernetes workloads.
- AWS Free Tier covers RDS (db.t3.micro, 20GB), EKS control plane, and S3 storage within the expected usage bounds.
- Internet connectivity and a domain name are available for the deployment environment.
- No SLAs are imposed by external stakeholders for this phase.

## Solutions Analysis

### Solution Architecture

The chosen architecture deploys all backend services as containerized workloads on an AWS EKS cluster. Each microservice runs as an independent Kubernetes deployment with its own service definition. An ingress controller (e.g., AWS ALB ingress controller or NGINX) routes external HTTP traffic to the appropriate service.

The relational database (AWS RDS) runs outside the cluster as a managed service, connected via a private VPC subnet. Application credentials and environment-specific configuration are injected at runtime using Kubernetes secrets.

The React frontend is built as a static asset bundle and deployed to an S3 bucket configured for static website hosting, optionally fronted by CloudFront for CDN distribution.

Firebase Authentication handles user identity. The backend validates Firebase-issued JWT tokens on each authenticated request without storing credentials locally.

RabbitMQ (CloudAMQP) is provisioned as a managed external service. Services publish and consume messages using standard AMQP client libraries.

### Solutions Comparative Analysis

#### Cloud Provider Comparison

| Criteria | AWS | Google Cloud Platform (GCP) | Microsoft Azure |
|----------|-----|-----------------------------|-----------------|
| Managed Kubernetes | EKS (mature, widely documented) | GKE (best-in-class Kubernetes origin) | AKS (solid, tighter Azure AD integration) |
| Free tier | Generous; covers RDS, S3, EKS (control plane free) | Limited; GKE Autopilot has per-pod billing | The free tier less generous for compute |
| Team familiarity | High | Low | Low |
| Ecosystem breadth | Largest service catalog | Strong data/ML tooling | Strong enterprise/AD integration |
| Decision | Selected | Not selected | Not selected |

#### Authentication: Firebase vs. Auth0 vs. Self-hosted (Keycloak)

| Criteria | Firebase Auth | Auth0 | Keycloak (self-hosted) |
|----------|---------------|-------|------------------------|
| Free tier | 10K MAU (Spark plan) | 7,500 MAU | Free (infrastructure cost only) |
| Setup complexity | Low | Low | High |
| JWT/OAuth2 support | Yes | Yes | Yes |
| Operational overhead | None (managed) | None (managed) | High (self-managed) |
| Vendor lock-in risk | Medium | Medium | Low |
| Decision | Selected | Not selected | Not selected |

#### Message Broker: RabbitMQ vs. AWS SQS/SNS vs. Apache Kafka

| Criteria | RabbitMQ (CloudAMQP) | AWS SQS/SNS | Apache Kafka |
|----------|----------------------|-------------|--------------|
| Free tier | Yes (CloudAMQP Lemur) | Yes (1M requests/month) | No managed free tier |
| Protocol | AMQP (standard) | Proprietary AWS SDK | Kafka protocol |
| Cloud lock-in | None | High (AWS-specific) | None |
| Operational complexity | Low (managed) | Very low | Very high |
| Team familiarity | High | Low | Low |
| Decision | Selected | Not selected | Not selected |

### Rationale

AWS was selected as the primary cloud provider based on three factors: team familiarity, the breadth of its free tier (which covers all required managed services within expected usage), and the maturity of its EKS offering. GCP and Azure were evaluated and dismissed due to lower team familiarity and less favorable free-tier conditions for this specific set of services.

EKS was chosen over a simpler deployment model (e.g., EC2 instances, AWS App Runner, or ECS with Fargate) because it directly satisfies some of the functional and non-functional requirements. Kubernetes is provider-agnostic at the workload level; migrating from EKS to GKE or AKS would require only infrastructure reconfiguration. A simpler compute model would reduce operational complexity but would bind the architecture more tightly to AWS-specific tooling.

RDS was chosen over a self-managed database on EC2 because it eliminates the overhead of manual backup management, patching, and failover configuration. Concerns that are not the focus of this project.

S3 for frontend hosting was selected as the simplest, most cost-effective option for serving static assets, with no ongoing compute cost and high availability by default.

Firebase Authentication and RabbitMQ were selected as external services to avoid the operational cost of self-hosting an identity provider or a message broker. Both provide managed services with free tiers adequate for this phase. The primary risk, free tier limits, is acknowledged and accepted for the educational deployment context.

## Change History

| Version | Comments | Date |
|---------|----------|------|
| 1.0 | Initial architectural decision | 2026-03-03 |
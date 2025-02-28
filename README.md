# My Learning
---

## Resources

### Redis
- https://www.dragonflydb.io/guides/redis-best-practices
- https://medium.com/@sunny_81705/redis-master-slave-architecture-e730403cb495
- https://medium.com/@chaewonkong/redis-sentinel-vs-redis-cluster-a-comparative-overview-8c2561d3168f



### Rate Limiting
- https://medium.com/fluxninjahq/why-adaptive-rate-limiting-is-a-game-changer-79f130e6ec71

### WebSocket
- https://ably.com/topic/websockets
- https://www.designgurus.io/answers/detail/how-to-understand-websockets-and-real-time-communication-for-interviews
- https://medium.com/nerd-for-tech/scaling-websockets-horizontally-a-simple-guide-for-beginners-bf8b06c042f7

#### Conflict Resolution & Synchronization 
- Operational Transformations (OT) and  Conflict-Free Replicated Data Types (CRDTs)

&nbsp;

## AWS Deployment Environment Summary for Backend Engineers

This document summarizes key AWS services and concepts relevant for backend deployments, particularly microservices architectures.

**Core AWS Services for Backend Deployment:**

*   **EC2 (Elastic Compute Cloud): Virtual Servers**
    *   **What it is:** Rentable virtual servers in the cloud.
    *   **Backend Relevance:** Foundation for running applications, provides flexibility and control. Can be used directly or as worker nodes for container orchestration.
    *   **Key Concepts:** Instance Types (optimized for different workloads), AMIs (pre-configured OS images), Security Groups (virtual firewalls), Auto Scaling (dynamic scaling of instances).

*   **ECS & EKS (Elastic Container Service & Kubernetes Service): Container Orchestration**
    *   **What they are:** Services for running and managing Docker containers. EKS is managed Kubernetes.
    *   **Backend Relevance:**  Essential for deploying and scaling microservices using containers. Kubernetes (EKS) is industry standard for orchestration.
    *   **Key Concepts:** Docker (containerization), Kubernetes core concepts (Pods, Deployments, Services, Namespaces), EKS Clusters (managed Kubernetes), Fargate (serverless compute for containers).

*   **S3 (Simple Storage Service): Object Storage**
    *   **What it is:** Scalable, durable, and cost-effective object storage for files and data.
    *   **Backend Relevance:** Storing static assets, backups, data lake foundation.
    *   **Key Concepts:** Buckets (storage containers), Objects (files), Storage Classes (different tiers for cost optimization based on access frequency), Versioning, Access Control (IAM policies).

*   **RDS (Relational Database Service): Managed Relational Databases**
    *   **What it is:** Managed relational databases (Postgres, MySQL, etc.).
    *   **Backend Relevance:** Persistent data storage for applications. Postgres is specifically mentioned in the job description. Reduces operational overhead of database management.
    *   **Key Concepts:** Database Engines (Postgres focus), Instance Classes, Storage Types, Backups & Recovery, Multi-AZ Deployments (High Availability), Security (Security Groups, Encryption).

*   **SQS (Simple Queue Service): Message Queue**
    *   **What it is:** Fully managed message queuing service for asynchronous task processing and decoupling services.
    *   **Backend Relevance:** Implementing asynchronous tasks (background jobs), improving application responsiveness, decoupling microservices.
    *   **Key Concepts:** Queues, Messages, Producers & Consumers, Standard vs. FIFO Queues, Visibility Timeout, Dead-Letter Queues.

*   **VPC (Virtual Private Cloud): Virtual Networking**
    *   **What it is:**  Allows creation of isolated private networks within AWS for security and control.
    *   **Backend Relevance:**  Isolating backend infrastructure, network segmentation (public vs. private subnets), security.
    *   **Key Concepts:** Subnets (public and private), Route Tables, Internet Gateways, NAT Gateways, Security Groups, Network ACLs.

*   **IAM (Identity and Access Management): Security and Permissions**
    *   **What it is:** Service for managing access to AWS resources securely.
    *   **Backend Relevance:**  Implementing principle of least privilege, securing AWS infrastructure, service-to-service authentication.
    *   **Key Concepts:** Users, Groups, Roles (for granting permissions to services), Policies (JSON documents defining permissions).

**Basic Microservices Architecture on AWS with EKS (Example):**

```
Internet <-> Ingress Controller (API Gateway) [Public Subnet] -> EKS Worker Nodes (Microservices as Pods/Containers) [Private Subnet] <-> RDS Postgres (Database) [Private Subnet], SQS (Message Queue) [Private Subnet], S3 (Object Storage)
                                                                                                  ^
                                                                                                  |
                                                                             Monitoring & Logging Services
                                                                             (CloudWatch, Prometheus, Grafana, ELK - Hybrid Deployment)
```

*   **Ingress Controller (API Gateway):**  Entry point in a Public Subnet for external traffic.
*   **EKS Worker Nodes (Microservices):** Core application logic running as containers in Pods within Private Subnets.
*   **RDS Postgres, SQS, S3:** Backend services in Private Subnets for data persistence, asynchronous tasks, and object storage.
*   **Monitoring & Logging:**  Hybrid deployment, with collection agents inside EKS and backend storage/visualization often outside or in a dedicated monitoring infrastructure.

**Key Architectural Considerations for AWS Deployments (Interview Focus):**

*   **Scalability:** Design for horizontal scaling using Auto Scaling, EKS scaling, load balancing.
*   **Reliability & High Availability:** Multi-AZ deployments, fault tolerance.
*   **Security:** VPCs, Subnets, Security Groups, IAM, Encryption.
*   **Performance:** Instance type selection, database optimization, caching.
*   **Cost Optimization:** Right-sizing resources, storage class selection, reserved instances.
*   **Monitoring & Observability:** Comprehensive monitoring and logging for application and infrastructure health.

**Monitoring & Logging Stacks (Common Examples):**

*   **Metrics:** Exporters (in EKS) + Prometheus (backend) + Grafana (visualization)
*   **Logs:** Fluentd/Fluent Bit (in EKS) + Loki (backend) + Grafana (visualization)  OR  CloudWatch Logs (AWS Managed) OR ELK Stack (Elasticsearch, Logstash, Kibana - often outside EKS for production).

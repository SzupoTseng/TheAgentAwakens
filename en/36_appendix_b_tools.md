# Appendix B · Open-Source Tools Quick Reference

> These are the open-source tools that recur across all 300 scenarios in this book, grouped by function, each with a one-line note on "what it is / what role it plays in the book." The parentheses describe the situation in which the Lobster most often calls on it across the Hundred Battlefields. This list is itself a microcosm of the modern SRE / FA toolbox.

## Observability
| Tool | One-Line Take |
|------|--------------|
| **Prometheus** | The source of truth for time-series metrics; in this book it's the thing most often "crushed under its own weight" (cardinality explosion) and most often the alert trigger source |
| **Grafana** | Turns metrics into dashboards humans can read; the "visual topology maps" the Lobster pushes mostly live here |
| **Loki / Tempo / Jaeger** | The three ledgers of logs (Loki) and traces (Tempo/Jaeger); the workhorses for blind root-cause analysis across microservices and for trace comparison |
| **OpenTelemetry** | The unified collection standard for metrics/logs/traces; the common language for cross-language instrumentation |
| **Thanos / Cortex** | The horizontal-scaling layer that adds long-term storage and a global view to Prometheus |

## Orchestration, Release, and Autoscaling
| Tool | One-Line Take |
|------|--------------|
| **Kubernetes (K8s)** | The operating system of container orchestration; the bedrock of nearly every cloud scenario |
| **Argo Rollouts** | The canary / blue-green release controller; the target the Lobster operates when it slams the brakes on a release showing "trace-level anomalies" |
| **KEDA** | Event-driven autoscaling; the executor for FinOps "after-hours" scale-down |
| **Argo CD / Flux** | GitOps deployment; the key that makes "Git is the single source of truth" hold true |

## Networking and Service Mesh
| Tool | One-Line Take |
|------|--------------|
| **Istio / Linkerd / Envoy** | Service mesh and sidecar proxies; the execution layer for traffic tagging, mTLS, and rate limiting |
| **Cilium** | eBPF-based network and security policy; pushes a NetworkPolicy in seconds to isolate a malicious Pod |
| **FRRouting (FRR) / BIRD / ExaBGP** | Open-source BGP routing engines; the weapon the Lobster wields to launch a "defensive reverse announcement" and reclaim traffic |
| **RPKI / RIPE NCC API** | Cryptographic validation of route origins; the compliance foundation for countering BGP hijacking |
| **Cloudflare** | Edge scrubbing and Anycast scheduling; the traffic safe harbor during natural disasters / DDoS |

## Security and Supply Chain
| Tool | One-Line Take |
|------|--------------|
| **Falco** | eBPF-based runtime threat detection; the first whistleblower for reverse shells and ransomware behavior |
| **Wazuh** | Host intrusion detection and log auditing; the source of the ransomware "entropy spike" alert |
| **Trivy** | Container and dependency vulnerability scanning; the scanner for a fleet-wide blind sweep when a CVE breaks |
| **OPA Gatekeeper / Kyverno** | Policy as Code for K8s; intercepts non-compliant services that try to "sneak into production" |
| **HashiCorp Vault** | Centralized custody and rotation of secrets and credentials; cuts off a leaked key in seconds |
| **cert-manager** | Certificate issuance and renewal inside K8s; the gatekeeper that keeps mTLS / HTTPS from expiring |

## Storage and Data
| Tool | One-Line Take |
|------|--------------|
| **Ceph / MinIO / Rook** | Distributed object / block storage; in this book, the frequent victim of "space suddenly dropping to zero" |
| **Longhorn** | K8s-native distributed block storage; the target when releasing a stuck volume |
| **PostgreSQL / MySQL / ProxySQL** | Relational databases and read-write splitting proxies; the main battleground for deadlocks and replication lag |
| **Redis** | In-memory cache and distributed lock; the protagonist of the double-write disaster triggered by clock drift |
| **etcd** | The brain of K8s (cluster state store); the most lethal single point during a split-brain |
| **Elasticsearch / Logstash / Fluent Bit** | Log indexing and pipelines; the injection point for GDPR sensitive-data redaction |

## Messaging, Compute, and Resilience
| Tool | One-Line Take |
|------|--------------|
| **Kafka** | The distributed messaging backbone; the core of cross-cloud outage self-healing and of shaving the peaks off log floods |
| **Spark / Flink** | Big-data batch / stream compute; the birthplace of data skew (the straggler) |
| **Resilience4j / Sentinel** | Circuit-breaker and rate-limiting frameworks; the code-level implementation of "graceful degradation" |

## IaC, Chaos, and Backup
| Tool | One-Line Take |
|------|--------------|
| **Terraform / Pulumi / Ansible** | Infrastructure as Code (IaC); the target format for auto-remediation PRs against configuration drift |
| **Chaos Mesh / Litmus** | Chaos engineering injection frameworks; the target the Lobster aborts during an "emergency brake" |
| **Velero** | K8s cluster backup and restore; the safety net for post-disaster rebuilds |
| **Harbor** | Private container image registry; the backup mirror source when Docker Hub rate-limits you |

> 🔍 A Reminder for the Hands-On Crowd
> Not a single tool on this list is "Lobster-exclusive"—they're all mature open-source systems you're **using right now, or should have been using long ago**. The Agent's value isn't to replace them, but to be the commander who **knows how to call the right tool, at the right moment, and wire up the right people**. Stock your toolbox first, and only then does the Agent have something to command.

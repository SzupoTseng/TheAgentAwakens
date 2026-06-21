# Chapter 12 · Resilience and Chaos: The System's Airbag

## Scenario 71 · The Emergency Brake When a Chaos Engineering Safeguard Runs Wild
**Background**: The payments cluster runs a GameDay in production every Wednesday, using Chaos Mesh to inject network-loss, pod-kill, and IO-delay faults to validate circuit breaking and graceful degradation.
**Problem**: That Wednesday at 14:07, a NetworkChaos rule's selector was written as `app: payment-*` instead of `app: payment-canary`, instantly hitting all 1,200 pods with 60% packet loss. p99 spiked from 80ms to 9.4s, transaction success rate fell to 31%—an experiment meant to exercise only 5% of traffic was now dragging down the entire production environment, bleeding roughly ¥4.2M per minute.
**Skills Required**: Kubernetes label selector debugging, blast radius assessment, chaos experiment rollback, SLO error budget interpretation.
**Open-Source Tools**: Chaos Mesh, Prometheus, kube-state-metrics, Argo Rollouts.
**Agent Capabilities Used**: Within 11 seconds, the Lobster (OpenClaw) detected—via a Prometheus webhook—the dual signal "success-rate slope < -5%/min while a chaos CRD is active," and immediately judged it an experiment overflow. It first posted the list of affected pods and the estimated financial loss to the SRE group; 0.8 seconds later a local script slammed the brakes with `kubectl delete networkchaos payment-loss-w3 --grace-period=0`, then used the Multi-Channel Gateway to fan the incident card out to Slack, PagerDuty, and DingTalk simultaneously, attaching the selector diff screenshot and rollback commands.
**Without the Agent**: The on-call engineer would first have to recognize, amid a wall of 504 noise, that "this is something we injected ourselves," dig through the Chaos Mesh dashboard to find which rule was responsible, then kill it by hand—just the step of "realizing the blast radius is wrong" eats up 8 minutes on average.
**Payoff**: MTTR dropped from 13 minutes to 23 seconds; the loss from a single overflow fell from ¥54M to roughly ¥1.6M.

> 💡 A Word to the Wise
> "The dignity of chaos engineering lies not in how big a fault you dare inject, but in how quickly and calmly you can take it back."

> 🔍 Advanced Commentary — Where the Road Leads
> This case points toward the Lobster's future as an "Experiment Guardian": the Agent doesn't merely fight fires—before an experiment is even applied, it uses a dry-run to estimate how many targets the selector will hit, and refuses to sign off if the experiment oversteps. The real engineering challenge lies at the trust boundary—when the Agent has the authority to veto chaos rules submitted by humans, you must make its "blast radius model" explainable and auditable, or it turns from an airbag into a black-box gatekeeper no one dares touch.

## Scenario 72 · Automatic Circuit Breaking of an Upstream Dependency During a Wave of 504 Gateway Timeouts
**Background**: The e-commerce homepage aggregates 17 backend microservices behind Envoy sidecars. The recommendation service (reco) is one of them—non-core, yet permanently sitting on the critical path.
**Problem**: During an evening flash sale at 20:31, a slow query in reco exhausted its own connection pool, driving p99 to 12s. The upstream aggregation layer had no timeout configured, so threads piled up blocked on reco, backing up layer by layer. Within 30 seconds the frontend erupted in a wave of 504s; homepage availability collapsed from 99.95% to 76%, and the CDN edge was reaping nearly 40,000 failed connections per second.
**Skills Required**: Dependency topology analysis, circuit breaker parameter tuning, timeout budget allocation, fallback content design.
**Open-Source Tools**: Envoy, Resilience4j, Jaeger, Grafana.
**Agent Capabilities Used**: From the span flame graph of a Jaeger trace, the Lobster recognized that "all the 504s are stuck on the reco hop, and reco is non-core." It invoked the off-the-shelf "dependency-isolation" skill plugin from ClawHub, used the local `envoy` admin API to change reco's outlier detection to `consecutive_5xx: 3` and enable active circuit breaking, and simultaneously switched the homepage's reco block to a static popular-items cache. It broadcast to the group: "reco has been circuit-broken, the homepage now falls back to cache, the core transaction chain is unaffected," along with a before/after p99 comparison chart.
**Without the Agent**: A human would first have to pinpoint "who is dragging things down" among 17 services, then convince themselves that "reco can be sacrificed," and finally hand-edit the Envoy config and reload—during a flash sale, every extra minute of hesitation means hundreds of thousands of lost orders.
**Payoff**: Homepage availability returned to 99.9% within 12 seconds; the core ordering chain had zero interruption, recovering roughly ¥21M in GMV.

> 💡 A Word to the Wise
> "In a distributed system, learning to gracefully give up a non-core dependency takes more courage and wisdom than desperately trying to save it."

> 🔍 Advanced Commentary — Where the Road Leads
> This case pushes the Lobster toward "tiered dependency autonomy": the Agent decides in real time, from traces, which dependencies can be dropped and which must be preserved. The engineering snag in practice is that "criticality" is not a static label—reco is droppable during a flash sale, but if it feeds anti-fraud risk-control features, dropping it opens a back door. Future Agents will need a "dependency importance map" that shifts dynamically with business context, and deciding who owns and maintains that map will become a new battlefield in organizational governance.

## Scenario 73 · Intelligent Stack Tracing and Unblocking of Thread Starvation
**Background**: The order service runs on the JVM with a fixed-size business thread pool of 200, plus a shared ForkJoinPool for batch reconciliation.
**Problem**: Someone wrote a synchronous HTTP call inside a reconciliation task, blocking every work-stealing thread in the ForkJoinPool on a socket read. Downstream requests began queuing; queue depth grew to 18,000 over 3 minutes, yet CPU sat at just 11%—a textbook case of thread starvation, "the machine is idle but the system is dead." QPS avalanched from 6,000 to 280.
**Skills Required**: JVM thread state interpretation, lock contention and blocking-point localization, thread pool isolation (Bulkhead) design, jstack flame graph analysis.
**Open-Source Tools**: async-profiler, Arthas, jstack, Grafana Pyroscope.
**Agent Capabilities Used**: After detecting the starvation fingerprint "low CPU + queue explosion + throughput collapse," the Lobster locally ran Arthas `thread -b` to find the blocking chain, then captured a 30-second wall-clock flame graph with async-profiler, automatically flagging in red that "synchronous HTTP hidden inside the ForkJoinPool." It posted the file:line of the top blocking stack to the group and recommended "isolate reconciliation onto a dedicated bounded pool," while using the Multi-Channel Gateway to @-mention the module owner with a link to a one-click isolation-config PR.
**Without the Agent**: On-call only sees "the service got slow," with CPU and memory all green—it's all too easy to misdiagnose it as a downstream issue and restart fruitlessly. To actually catch that one blocking line of code, even a veteran comparing jstacks by hand often needs more than 20 minutes.
**Payoff**: Root-cause localization shrank from 25 minutes on average to 70 seconds; after isolation went live, starvation incidents of this class dropped to zero.

> 💡 A Word to the Wise
> "The most dangerous failures aren't the ones where the CPU is glowing red, but the ones where the machine is perfectly at ease while the system can't move an inch—starvation never cries out that it's hungry."

> 🔍 Advanced Commentary — Where the Road Leads
> This road leads to a "thread pool governance advisor": the Agent observes each pool's blocking patterns over time and proactively recommends isolation boundaries and capacity. The engineering challenge is that it must distinguish "transient blocking" from "structural starvation"—a misjudgment would have it wielding the knife amid normal momentary jitter. More forward-looking still: when the Agent can submit isolation PRs of its own, the review boundary of CI/CD must be upgraded—who reviews an AI-generated patch that directly alters the concurrency model?

## Scenario 74 · Automatic Heap Dump and Safe Restart for a Memory Leak
**Background**: The reporting service runs large batch exports in the early hours each day, with 8 permanent pods and a 6GB heap ceiling.
**Problem**: After one release, old gen grew a steady 4% per hour, Full GC frequency rose from twice a day to once every 9 minutes, with each STW pause lasting 1.3 seconds. For three nights running, a pod was OOMKilled in the early morning, leaving the day's reports with gaps—yet everything looked normal during the day, the leak silently devoured by the night shift.
**Skills Required**: GC log analysis, judging the right moment to capture a heap dump, locating leak-suspect objects (dominator tree), graceful restart and traffic draining.
**Open-Source Tools**: Eclipse MAT, jmap, VisualVM, Prometheus JMX Exporter.
**Agent Capabilities Used**: The Lobster built a linear-regression baseline of old gen for each pod and triggered when "the rebound slope is positive for 6 consecutive windows and approaching 85% heap." Before the OOM, it locally ran `jmap -dump:live` to grab a heap, uploaded it to object storage, and used MAT in batch mode to auto-parse the dominator tree, posting the largest retained-set object into the group ("a cache Map holding 2.1M unexpired entries"). A sub-agent then drained the pod from the LB, waited for in-flight requests to drain, and gracefully restarted—with zero report gaps throughout.
**Without the Agent**: The night shift typically wakes up only at the OOMKilled alert, by which point the JVM is already dead and the scene (the heap) has evaporated with it—leaving a corpse of a container with no autopsy report. To reproduce it, you'd have to stand guard for several overnight shifts, running jmap by hand.
**Payoff**: The leak went from "takes three nights to pinpoint" to "evidence preserved on the first rebound"; nighttime report gaps dropped to zero, and MTTR fell from 8 hours to 4 minutes.

> 💡 A Word to the Wise
> "An OOM kills not just the process, but the crime scene itself—only those who can leave behind a heap dump before the crash are entitled to talk about root cause."

> 🔍 Advanced Commentary — Where the Road Leads
> This case points toward "pre-mortem forensics": the Agent learns to automatically seal the scene in the final moment before a system dies. The challenge at scale is cost—heap dumps easily run to several GB, and grabbing them all automatically would blow up storage and IO; the Agent must learn to capture "on the right pod, at the right moment, exactly once." Further on, once it can autonomously decide to drain traffic and restart, it steps onto the red line of "self-healing authority": a single misjudged graceful restart, at peak hour, can also be an act of self-harm.

## Scenario 75 · Intercepting a Double-Write Disaster from Clock Drift in a Redis Distributed Lock
**Background**: Inventory deduction uses a Redis distributed lock (SET NX PX) for mutual exclusion, with a lock TTL of 3 seconds and one application node in each of three AZs.
**Problem**: One application node lost NTP connectivity, and its system clock drifted 4.2 seconds relative to the others. It believed its lock was still valid when in fact it had long expired, and another node had already grabbed the same lock—two nodes deducting the same SKU at once produced 3,700 oversells within 6 minutes, drove inventory negative, and lit up financial reconciliation in red.
**Skills Required**: Distributed lock correctness analysis, clock synchronization (NTP/chrony) investigation, fencing token mechanism design, double-write conflict detection.
**Open-Source Tools**: Redis, Redisson, chrony, Prometheus node_exporter.
**Agent Capabilities Used**: The Lobster cross-compared each node's `node_timex_offset_seconds` from node_exporter and flagged any node drifting >1s as a "lock-untrustworthy node." At the same time, it detected from the inventory event stream the double-write fingerprint "the same SKU deducted by two holders during the lock-overlap window," and immediately ran a local script to cordon the drifting node's deduction traffic, force it to re-sync via chrony, and post the oversell details and affected order numbers to the group, using the Multi-Channel Gateway to alert both the inventory and finance groups to stem the loss.
**Without the Agent**: Clock drift is one of the most insidious failures—log timestamps all look "normal," so engineers tend to first suspect code logic, taking a long detour before it occurs to them to run `chronyc tracking`. By the time they trace it, the oversold orders have long since shipped.
**Payoff**: Double-writes went from "discovered only at reconciliation" to "intercepted within 6 seconds"; the loss per oversell incident dropped from ¥1.8M to under ¥30K, and the lock was migrated to use a fencing token.

> 💡 A Word to the Wise
> "In a distributed system, the thing that should least be trusted is precisely the one every machine takes for granted—time."

> 🔍 Advanced Commentary — Where the Road Leads
> This road leads to an "Invariant Guard": the Agent no longer merely watches metrics, but continuously verifies business-level invariants—"a single lock must not have two holders," "inventory must not go negative." The hard bone in practice is the formal expression of invariants and their low-cost verification; at 100K QPS, performing a double-write check on every deduction is itself a tug-of-war between performance and correctness. Deeper still: when the Agent can cordon a node that is "lying about time," it is in fact exercising a new kind of power—adjudicating which machine's worldview is untrustworthy.

## Scenario 76 · Cache-Rebuild Rate Limiting and Singleflight Against the Thundering Herd
**Background**: The product detail page relies on a Redis cache to handle 95% of read traffic, with the cache TTL for hot SKUs uniformly set to 300 seconds.
**Problem**: A batch of best-selling SKUs had their caches expire collectively in the same second, and instantly tens of thousands of requests punched through to MySQL to rebuild the same data at once. The DB connection pool filled within 2 seconds, slow queries piled up, CPU hit 98%, and detail-page-wide p99 spiked from 40ms to 7s—a classic cache avalanche compounded by the thundering herd.
**Skills Required**: Cache invalidation strategy design, singleflight merging, TTL jitter, database overload protection.
**Open-Source Tools**: Redis, groupcache, Sentinel, Vitess.
**Agent Capabilities Used**: From the fingerprint "DB connection saturation + a flood of misses on the same cache key," the Lobster judged it a thundering herd and immediately pushed a local Sentinel rule to limit concurrency on the "cache rebuild" resource (admitting only 1 rebuild request per key), then invoked ClawHub's "cache-jitter" skill to add ±10% random jitter to subsequent TTLs, scattering the next collective expiry. It broadcast to the group how many penetrating requests it had intercepted and the DB QPS decline curve, and recommended switching hot keys to logical expiry + asynchronous rebuild.
**Without the Agent**: Seeing the DB glowing red, on-call's first instinct is often to scale up the DB—but under a thundering herd, scaling up is futile; the only real fix is "merged rebuild," and a human's odds of writing the correct singleflight config in the heat of the moment are extremely low.
**Payoff**: Rebuild requests penetrating to the DB merged from tens of thousands down to single digits; detail-page p99 returned to 50ms within 8 seconds, and DB CPU fell from 98% back to 30%.

> 💡 A Word to the Wise
> "What a cache releases at the instant of expiry isn't tens of thousands of requests, but tens of thousands of blades striking the database at once—your job is to make them queue, not to scale up the chopping block."

> 🔍 Advanced Commentary — Where the Road Leads
> This case leads the Lobster toward "invalidation traffic shaping": the Agent actively manages the temporal distribution of cache expiry, so the system is never left collectively exposed in the same second. The engineering challenge is that it must understand the business's hotspot distribution and consistency tolerance—applying logical expiry to inventory may serve stale values, a trade of correctness for availability. When a future Agent makes this trade-off for you, it must lay the business decision "how stale is tolerable" out in the open, rather than quietly signing on the boss's behalf.

## Scenario 77 · Backoff-Jitter Injection and Backpressure Against a Retry Storm
**Background**: From the mobile app to the gateway to the backend, each of the three layers was configured with "automatically retry 3 times on failure"—seemingly robust.
**Problem**: A single 1.5-second jitter in the auth service triggered client retries; the gateway retried too; the backend retried as well—multiplied across three layers, one original failure was amplified into 27× the traffic. Just as the auth service was about to recover, its own retry traffic killed it again, forming a self-exciting oscillation: QPS swung violently between 200 and 9,000 every 30 seconds, never converging.
**Skills Required**: Retry amplification factor calculation, exponential backoff with jitter, token-bucket backpressure, retry budgets.
**Open-Source Tools**: Envoy, gRPC, Resilience4j, Linkerd.
**Agent Capabilities Used**: From the traffic's periodic self-exciting oscillation waveform (FFT identified a 30-second period), the Lobster judged it a retry storm. It locally adjusted Envoy's retry budget to "retry traffic must not exceed 20% of normal traffic" and injected full-jitter backoff, while enabling queue-depth-based backpressure on the auth service's upstream. It plotted in the group the amplification factor converging from 27× to 1.3×, and @-mentioned all three layer owners with the architectural recommendation that "retries should be done once, only at the outermost layer."
**Without the Agent**: During the oscillation, each illusion of "it's almost recovered" misleads humans into stopping, only to be killed by the next wave; realizing that "it's our own retries trampling each other" usually only dawns when someone draws the timing diagram during the postmortem.
**Payoff**: The self-exciting oscillation converged within 90 seconds; auth service availability returned from 76% to 99.9%, and a unified end-to-end retry budget was put in place.

> 💡 A Word to the Wise
> "A retry is a remedy for single-point failure, but a poison for systemic overload—the only difference is whether anyone tallied up the total dose across these layers of remedy."

> 🔍 Advanced Commentary — Where the Road Leads
> This road leads to "end-to-end retry governance": the Agent looks down on the whole call chain and manages the retry configs scattered across layers as a single shared budget. The difficulty lies in the completeness of observability—it must assemble the full topology to compute the amplification factor accurately, yet in reality a few services always fail to report. The more forward-looking question is coordination authority: when the Agent demands "retries only at the outermost layer," it is in fact pushing an architectural constraint across multiple teams—which requires not just technical authority, but the organization's trust to grant it "cross-domain adjudication."

## Scenario 78 · Automatic Traffic Drain and Capacity Rebalancing for an Availability-Zone-Level Failure
**Background**: The service is deployed symmetrically across three AZs, each normally carrying 33% of traffic, with each AZ provisioned at 50% headroom to absorb a single-zone failure.
**Problem**: The network fabric of one cloud provider's AZ-b developed a grey failure—not a full outage, but 18% of cross-zone packets silently dropped. Because health checks occasionally succeeded, AZ-b was judged "healthy," traffic kept flowing in, yet users hit intermittent errors and p99 showed regional jitter—a traditional health check simply cannot detect this "half-dead" state.
**Skills Required**: Grey failure identification, AZ-level traffic shifting, capacity rebalancing calculation, cross-zone consistency impact assessment.
**Open-Source Tools**: Istio, Prometheus, Thanos, Cluster Autoscaler.
**Agent Capabilities Used**: The Lobster doesn't trust binary health checks; using active probes plus client-perspective success-rate percentiles, it discovered the grey fingerprint "any request that passes through AZ-b has a systematically 6-percentage-point lower success rate." It first calculated whether the remaining two zones could absorb the full load (headroom sufficient), then locally pushed Istio to drop AZ-b's weight from 33% to 0, simultaneously triggering pre-scaling of the autoscalers in the other two zones, broadcasting drain progress and capacity watermarks to the group throughout, and recommending opening a ticket with the cloud provider with packet-loss evidence.
**Without the Agent**: Grey failures are the ultimate nightmare of SRE—monitoring all green, users complaining. Humans often suspect their own code first, and by the time they manually compare per-zone success-rate percentiles to pinpoint AZ-b, half an hour has passed—plus they still face the decision pressure of "shifting an entire AZ away."
**Payoff**: Grey failure identification dropped from 35 minutes to 90 seconds; the regional jitter was eliminated, the user-side error rate returned to baseline, and because pre-scaling was in place, the zone shift caused zero jitter.
> 💡 A Word to the Wise
> "The most tormenting failure is never black or white, but that swath of grey 'sometimes still works'—it fools every health check, only never the patience of users."

> 🔍 Advanced Commentary — Where the Road Leads
> This case is exactly the "grey zone" main battlefield this book repeatedly pays homage to: the Lobster's road is to evolve from "liveness probing" to "truth probing"—replacing binary health checks with statistical percentiles from the user's perspective. The hardest part in practice is the authority boundary for a high-leverage action like "shifting away an entire AZ": judge right and you're a hero, judge wrong and you drag a good zone down too. Future Agents must be able to output decisions with confidence levels and, at low confidence, automatically degrade to "please have a human review" rather than charging ahead blindly.

## Scenario 79 · Automatic Scaling and Poison-Pill Isolation for a Consumer-Lag Avalanche
**Background**: Order events flow through Kafka, with 12 consumers processing in parallel downstream, 48 partitions, and lag normally held at the thousands.
**Problem**: A malformed "poison pill" message caused a consumer to throw on deserialization and retry infinitely, jamming that partition while the remaining messages backed up behind it. Lag exploded from 3,000 to 2.7M within 20 minutes, with the slope still increasing—downstream shipping and notifications all delayed, on the verge of breaching the Kafka retention period and permanently losing orders.
**Skills Required**: Consumer group health analysis, poison-pill isolation (DLQ), elastic scaling decisions, backlog catch-up rate estimation.
**Open-Source Tools**: Apache Kafka, Burrow, KEDA, Kafdump.
**Agent Capabilities Used**: From Burrow, the Lobster spotted the poison-pill fingerprint "lag exploding but concentrated in a single partition, whose commit offset isn't advancing." It first locally routed the jammed message into a dead-letter queue (DLQ) by rule to unblock the partition, then used KEDA to compute from "catch-up rate = consumption rate − production rate" that it needed to scale to 22 consumers to clear the backlog within the retention period, auto-scaled, and plotted the lag-prediction convergence curve in the group (ETA 18 minutes), while pasting the raw poison-pill message into the dev group for bug fixing.
**Without the Agent**: On-call, seeing lag soar, usually just blindly adds consumers—but without unblocking the poison pill, no number of consumers helps; that partition stays jammed. And fishing that one malformed message out of a 2.7M backlog by manually grepping logs is like searching for a needle in a haystack.
**Payoff**: Unblocking the partition + precise scaling cleared the backlog within 18 minutes with zero lost orders; the poison pill was automatically archived as a regression test case for downstream parsing.

> 💡 A Word to the Wise
> "A single malformed message can choke an entire pipeline—not because it's so toxic, but because no one gave the queue a throat that can spit the poison pill back out."

> 🔍 Advanced Commentary — Where the Road Leads
> This road leads to "lag autonomy": the Agent strings "unblock—scale—estimate ETA" into a closed loop, working backward from the deadline of the retention period to the compute it needs. The engineering difficulty lies in the prediction accuracy of the catch-up rate—the production rate fluctuates, scaling has cold-start latency, and a wrong ETA means lost orders. Further on, when the Agent can autonomously toss a message into the DLQ, it is deciding for the business "which data may be left unprocessed for now"—and what if the message it judged "poison" is actually a legitimate new-version format? The trustworthiness of the isolation rules will be the Achilles' heel of this road.

## Scenario 80 · Automatic Orchestration and a Resilience Scorecard for an End-to-End Chaos Drill (GameDay)
**Background**: A once-per-quarter end-to-end GameDay must inject 30+ kinds of faults in sequence in a production-like environment, validating SLOs and degradation playbooks—previously driven manually by a 200-line runbook.
**Problem**: Last quarter's GameDay caused an incident due to chaotic manual coordination—the 14th experiment (injecting a DB primary-replica failover) was mistakenly started while the 9th experiment (cache invalidation) had not yet recovered. The two faults stacked beyond the designed blast radius, the environment crashed outright, the entire drill was voided, the full day of effort by 40 people came to nothing, and no one could say "which resilience defenses actually held."
**Skills Required**: Chaos experiment orchestration (DAG), steady-state hypothesis validation, experiment dependency and precondition management, resilience measurement and scoring.
**Open-Source Tools**: Litmus, Chaos Toolkit, Argo Workflows, Prometheus.
**Agent Capabilities Used**: The Lobster built the 30+ experiments into a DAG with preconditions; before each injection it automatically verified "the system has returned to steady state (all SLOs green and no residual faults)" before clearing the next one, eliminating stacking. It scored each experiment in real time: did the defense trigger, MTTR, did the blast radius overstep. When the drill ended it auto-generated a "resilience scorecard," pushed it to every channel, and @-mentioned the owners of services that failed validation. Throughout, sub-agents watched steady state in parallel while the main Agent controlled the pace—humans only had to type "continue" or "abort" in the group.
**Without the Agent**: Driving the runbook by hand is slow and error-prone; just confirming "did the previous fault really recover" forces the coordinator to repeatedly poll each team, and one mistaken start wastes the whole day; afterward, reconstructing which defenses held relies on memory, rendering the scorecard a sham.
**Payoff**: GameDay went from "run 12 in a day, and it might still crash" to "run 30+ in half a day, with zero stacking incidents"; the resilience scorecard made the effectiveness of each defense quantifiable and trackable for the first time.

> 💡 A Word to the Wise
> "The value of a drill lies not in how many faults you injected, but in whether, before each injection, you truly confirmed the system was standing firm—resilience is built up by a chain of 'steady-state confirmations.'"

> 🔍 Advanced Commentary — Where the Road Leads
> This is the chapter's coda: the Lobster's ultimate road is to move from "firefighter" to "orchestrator and referee of resilience"—it not only responds to chaos, but proactively manufactures controlled chaos to temper the system. The deepest engineering proposition surfaces here: when the Agent designs the experiments, executes the injections, and scores the results, it is simultaneously athlete and referee, and this "self-grading" chain must have an external human audit gate. The real watershed of the future is not whether the Agent can run GameDay automatically, but whether the organization dares to hand it part of the task of "defining what resilience even means."

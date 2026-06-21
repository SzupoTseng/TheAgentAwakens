# Part 1 · Two Philosophies

# Chapter 1 · Abandon the Lobster, Raise the Horse: A Generational Shift in Open-Source Agents

## Two Animals, Two Faiths

If you've been hanging around open-source AI circles lately, you've probably found it hard to avoid these two names: **OpenClaw (the Lobster 🦞)** and **Hermes Agent (Hermes 🐴)**. They are the two hottest frameworks in the open-source AI agent space right now, and what they represent are two **fundamentally different design philosophies for AI assistants**.

Put them side by side and the differences jump right out:

| Dimension | 🦞 OpenClaw (the Lobster) | 🐴 Hermes Agent (Hermes) |
|------|------------------|------------------------|
| Core Belief | **Breadth-first**: the more it can connect to, the better | **Depth-first**: emphasis on autonomous learning and long-term memory |
| Communication Platforms | Supports up to **24+** messaging-app groups | Supports **6** major platforms such as Telegram and Discord |
| Skill System | Hand-written; the community provides **13,000+** ready-made skills (ClawHub) | The AI **writes skills automatically** based on your workflow |
| Memory | Primarily single-session (Stateless); easily forgets context | Long-term memory; the more you use it, the better it knows you |
| Cost | Has to re-feed context every time, so **Token costs run higher** | Optimizes the problem-solving flow; measured to save up to **90%** on Token fees |
| Security | Has had multiple vulnerabilities exposed; ClawHub carries a risk of malicious code | Relatively secure architecture; emphasis on sandboxing and permission control |

This table is essentially the entire rationale behind those four words: "abandon the Lobster, raise the Horse."

## The Lobster's Rise: A Golden Age of Connectors

Let's be fair first: the Lobster's explosive popularity was no accident.

Back when "AI agent" was still a new term, OpenClaw got one crucial thing right—**it pushed the act of "connecting" to its absolute limit**. At its core is a powerful "Control Plane" that can wire together a huge number of communication platforms at once, and then, through the community skill library ClawHub, hook up all kinds of web services in a flash.

For someone just looking to dip a toe in, the experience felt almost like magic: you say a single sentence to it on Telegram, and it can go drive your LINE, fire off a Slack message, or pull a note from a WeChat group. It's like an octopus with twenty-some arms, each arm gripping one of the services you use every day.

**Breadth is the Lobster's entire charm.**

## The Abandonment Wave: When Breadth Hits the Wall of Reality

But the magic fades fast. As more and more people "raised" the Lobster into their daily workflows, two walls rose up to meet them:

- **The first wall—amnesia.** Every conversation with the Lobster is like its first day alive: yesterday you taught it "my project lives in this directory, I like to use this deployment flow," and today it asks you all over again with a blank look on its face. For someone who only plays with it occasionally, this is a minor annoyance; but for someone who relies on it to get work done every day, it means **re-feeding the context every single time**—and every time you feed context, you're burning Tokens, real money down the drain.
- **The second wall—crashes and poison.** The bigger the ecosystem grows, the messier the community plugins on ClawHub become. Plugins started getting caught smuggling in malware; combine that with frequent system updates, and an update would often break the user's own environment and spit out serious bugs.

And so the mood online shifted. Headlines like "Stop fixing the Lobster" and "Ditch your Lobster" began flooding feeds, and that half-joking slogan in the community grew louder and louder—

> 💡 A Word to the Wise
> **The essence of "raising the Lobster" is inviting into your home an octopus of staggering breadth that also suffers from amnesia.**
> It can connect you to every service in the world, yet it can't remember what you said yesterday. Once the thrill of novelty fades and the Token bill arrives, what people want is no longer "how much it can connect to," but "can it get cheaper and understand me better the more I use it?"

## Hermes Strikes Back: A Long-Term Assistant That Evolves Itself

Hermes Agent's selling point is precisely those two painful walls the Lobster ran into.

Built by Nous Research, its official line—"The agent that grows with you"—isn't a slogan but an architecture: when it completes a complex task for you, **it automatically distills the entire solution process and organizes it into a skill document**. The next time you face a similar task, it simply invokes that skill—no need to explain it all over again. This is exactly why measurements show savings of up to ninety percent on Tokens—because **repeated context only needs to be "learned" once**.

Even more striking: it can spin up independent "sub-agents (Sub-Agents)" for you, each with its own conversational context, its own terminal, and its own Python RPC scripts, all running different workflows in parallel for you. One horse can split into a whole team.

It can run local models (such as Gemma and Llama) and also supports cloud APIs (OpenAI, Claude, OpenRouter)—and on this point it actually stands at the same starting line as the Lobster: both can run locally, both can run in the cloud. The difference was never about "whether it can run a model," but about **whether it remembers once the run is done**.

## So, Which One Should You Raise?

Don't rush to pick a side. Over the next two chapters, this book will take apart the Lobster's "breadth" and Hermes's "depth" in fine detail, then put them head-to-head in the ring with a six-dimension table.

But first, hold on to one starting point for the judgment:

- If your need is **breadth**—you want to wire up many platforms at once, you want ready-made skills you can grab and use, you want an "all-in-one adapter"—the Lobster's ecosystem still has no equal.
- If your need is **depth**—you want a long-term butler who's with you every day, remembers your habits, and gets cheaper the more you use it—then that "abandon the Lobster, raise the Horse" wave is blowing your way.

In the next chapter, we'll first step into the Lobster's world and see exactly how those twenty-some arms manage to grab the chaotic digital world and hold it all in one grip.

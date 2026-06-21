# Chapter 3 · Hermes Agent: The Long-Term Assistant That Evolves Itself

## One Slogan Holding Up an Entire Architecture

The official tagline for Hermes Agent is just a single line:

> **The agent that grows with you.**

Don't dismiss it as marketing. That line all but defines the most fundamental divergence between Hermes and the Lobster — the Lobster bets on *breadth of connection*, Hermes bets on *depth of growth*. It comes from the renowned AI research lab **Nous Research** (the community nicknamed it 🐴 thanks to the pun on "Hermès"), and its selling point isn't "how many platforms can it connect to" but rather "**the longer you use it, the better it understands you and the more money it saves you**."

## Writing Skills Automatically: Turning "Problems Solved" into "Problems It Knows"

Hermes's biggest highlight is a mechanism that sounds simple but is, in practice, subversive:

**After it finishes a complex task for you, it automatically extracts and organizes the solution steps into a "Skill File."**

The next time it faces a similar task, it invokes that file directly — no need for you to explain again.

Set this mechanism against the Lobster, and the difference is philosophical:

| | 🦞 The Lobster's Skills | 🐴 Hermes's Skills |
|---|---|---|
| Source | **Hand-written**, downloaded ready-made from the ClawHub community | **AI-authored automatically**, based on your real workflows |
| Quantity | 13,000+ Swiss Army knives from strangers | Knives each "tailor-made for you" |
| Growth | It knows exactly as much as you install | The more you use it, the more it grows on its own |

This is the secret behind "the more you use it, the more you save" — **a recurring context only needs to be *learned* once**. The first time, you walk it through a complex process, and it turns that process into a skill; from then on, the same job no longer requires you to re-explain line by line. In real-world testing, this mechanism can cut Token costs by as much as **90%**. The Lobster's amnesia makes you pay anew every day; Hermes's memory lets your investment compound day by day.

## Sub-Agents: One Horse, Splitting into a Squad

Hermes's second weapon is "spawning sub-agents."

It can spin off independent sub-agents to run different workflows for you in parallel. The key is that these sub-agents aren't decorative —

**Each sub-agent has its own conversation context, its own dedicated terminal, and its own independent Python RPC script.**

What does that mean? It means you can let the main agent act as the "commander" while dispatching three sub-agents at once: one to run tests, one to compile reports, one to keep watch over a deployment. Their contexts are isolated and never pollute one another, yet they all report back to the same command center. One person's workflow gets flattened into a parallel squad.

> 💡 A Word to the Wise
> **The Lobster grows through "add-ons"; Hermes grows through "splitting and sedimentation."**
> One keeps strapping on tools written by others — breadth explodes, but the individual gets no smarter; the other distills every experience into its own skills, then splits off a squad to run in parallel. The former is like collecting Pokémon, the latter like raising an apprentice who reads on its own. **The longer you use it, the wider the gap grows.**

## An Undiscriminating Appetite: On-Prem and Cloud Alike

Let's clear up a common misconception: many people assume that "running local models" is the Lobster's exclusive trick. It isn't.

Hermes Agent, like OpenClaw, is an AI Agent framework — **both can run with local models, and both support cloud APIs**:

- **On-prem models**: such as Gemma, Llama 3, etc. — your data never leaves the machine, and privacy stays in your hands.
- **Cloud APIs**: OpenAI, Claude, OpenRouter, etc. — switch to a stronger brain whenever you need one.

So the deciding factor was never "can it run a model" — both score full marks there. The real watershed is just one thing: **after finishing a task once, does it remember, and can it turn this experience into a capability for next time.**

## A Focus on Sandboxing and Permissions: Security by Design, Not by Patch

Remember the Lobster's lurking worry that "ClawHub might be poisoned"? Hermes takes the opposite road here.

Compared with the Lobster, which has had multiple vulnerabilities surface and carries the risk of malicious code in community add-ons, Hermes's architecture is **relatively secure, with an emphasis on sandboxing and permission control**. When skills are written by the AI itself based on your workflow and run inside a controlled sandbox, that "supply chain of thirteen thousand strangers" risk is naturally contained.

This is also why, when "ditch the shrimp, raise the horse" went from a joke to a trend, the reasoning behind it was actually quite rational: **what users want has never been more claws, but a long-term partner that remembers, learns, and won't bite back.**

---

The philosophy is done. But however beautiful, philosophy is empty talk if you can't get it installed. In the next part, we roll up our sleeves — and see how a single command can bring an agent like this into your computer for real.

## Preface · When "Raising a Lobster" Became a Sigh

At the end of 2025, a certain "Lobster" went viral on GitHub.

Its real name is **OpenClaw**, an open-source AI agent framework built on large language models, started by the developer steipete. Because *Claw* sounds the way it does in English, and thanks to the community's nickname, everyone affectionately called it the Lobster 🦞. Almost overnight, "raising a Lobster on your own machine" became all the rage in developer circles—some people offered dedicated "Lobster installation services" to set up your environment and tune your parameters, and before long, even "Lobster uninstallation services" appeared.

The very emergence of an uninstallation service was, in itself, a telling signal.

People quickly discovered that while the Lobster could simultaneously wire up more than twenty messaging platforms—Telegram, LINE, Slack, WeChat, and more—and, backed by the massive community skill library ClawHub, could rapidly hook into all sorts of web services with **astonishing breadth**, it had two fatal pain points: **it lost its memory every single day**—the preferences you taught it yesterday were gone today; and as its ecosystem grew, malicious code began creeping into the community plugins, while the system updated constantly and crashed at the slightest provocation. So every conversation meant re-feeding it the context from scratch, Token costs stayed stubbornly high, and every update felt like defusing a bomb.

Just as the Lobster hit this wall, a quiet trend began sweeping the internet: **ditch the Lobster, raise a Horse**.

That "Horse" is **Hermes Agent (Hermes 🐴)**, released by the renowned AI research lab **Nous Research**. Its official tagline is a single line—**"The agent that grows with you."** Its biggest selling point: every time it solves a complex task for you, it automatically distills and organizes the result into a "Skill File," so the next time a similar job comes up, it simply calls on that file—no need to explain it all over again. **The more you use it, the cheaper it gets; the more you use it, the smarter it grows.**

---

This book is written for you, standing at exactly this crossroads.

It is not a piece of marketing copy, nor a sermon for either side. It sets out to do three things:

- **Part 1 · Two Philosophies**: We take the Lobster and Hermes apart—not to tally up whose feature list is longer, but to see clearly the two **fundamentally different design beliefs** behind them: one bets on breadth and connection, the other on depth and memory. Only once you grasp the philosophy will you know which one to raise.
- **Part 2 · The Boot-Up Ritual**: How a single command can install an agent that writes its own code and runs its own commands onto your machine—from Linux / macOS / WSL2 to native Windows, with every pitfall flagged for you in advance.
- **Part 3 · A Hundred Battlefields**: This is the centerpiece of the whole book. Through the eyes of a **Google L7 Staff Engineer and seasoned SRE**, we wade into that "minefield of a swamp" that is distributed systems, watching how the Agent turns "black-box guesswork" into "visualized decisions" across real battlefields like multi-cloud networking, canary releases, chaos engineering, security incident golden-hour rescues, FinOps cost-cutting, and database deadlocks.

> 💡 How to Read This Book
> Every hands-on scenario is dissected using the same skeleton: **Background → Problem → Skills Required → Open-Source Tools → Agent Capabilities Used → Without the Agent (and why it hurts) → Payoff**, capped off with a "A Word to the Wise" takeaway.
> You can read the entire philosophy in order, or flip straight to whichever scenario keeps you up at night—each one stands on its own as a self-contained piece.

Technology grows obsolete, frameworks get renamed, and the Lobster and Hermes may well be supplanted by a third animal next year. But what this book truly hopes to leave you with isn't the install command for some tool—it's an idea:

**The end state of automation is not "no humans," but "the human only has to make that one final decision."**

Turn this page, and we'll begin with that generational changing of the guard—the great "ditch the Lobster, raise a Horse."

# Part 2 · The Boot-Up Ritual

# Chapter 4 · Summoning It with a Single Command: From Linux to Native Windows

## An Open-Source Butler, Raised on Your Own Machine

Before we get our hands dirty, let's make one thing clear: the Hermes Agent (and the Lobster) is, at its core, "**an open-source tool that lets you raise an AI assistant on your own computer**." Your conversation logs, your skills, your memories — all of it lives on your own machine, not in some company's cloud. This is the heart of being "self-hosted," and it's the precondition for every piece of automation this book discusses — **because it runs in your environment, it can actually do things for you, rather than merely chat.**

## Unix-Like Environments: One curl and You're Done

If you're on **Linux, macOS, WSL2, or Termux**, installation is literally a "single command." Paste the official install script into your terminal:

```
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh
```

(The community and official docs also frequently point to an equivalent script straight from GitHub: `https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh`.)

Once it's installed, run the guided setup once:

```
hermes setup
```

It walks you step by step through the two most critical things to configure: **your AI model** (local, like Ollama / Gemma / Llama, or cloud, like OpenAI / Claude) and **your messaging platform** (for example, hooking it up to your Telegram). Once that's done, you've got a butler on permanent standby, living right inside your terminal.

## Native Windows: Finally Free of the WSL2 Shackles

In the past, Windows users who wanted to raise an Agent like this almost always had to install WSL2, Docker, or Cygwin first — a non-trivial barrier. **That has changed.**

Nous Research has officially re-architected the platform for Windows, resolving the old character-encoding (UTF-8) and shell-command compatibility issues. Core features — the CLI, the TUI interactive interface, the messaging Gateway, and "AI autonomously writing its own skills" — now launch **natively and seamlessly on Windows 10 / 11**, with **no WSL2, Docker, or Cygwin required whatsoever**.

You have two of the simplest possible paths:

### Method 1 · One-Click Terminal Install (PowerShell)

Open **Windows Terminal** (no administrator privileges needed) and copy-paste the official native Windows install command:

```
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

This script automatically sandboxes the install under `%LOCALAPPDATA%\hermes\`, automatically provisions the **standalone Python and Node.js environments** it needs, and even bundles a lightweight **PortableGit (~45MB)** to run AI-generated shell commands invisibly in the background. Once it's done, open a fresh PowerShell window and you're good to go.

### Method 2 · Desktop GUI (Hermes Desktop)

If you'd rather not touch the command line at all, the community and the project also ship **Hermes Desktop** — download the Windows installer, run it, done. On first launch, it quietly invokes the script above in the background to set up every compatible environment for you. From then on, you can switch models, manage the AI's memory, and add skills directly inside a polished window interface (WebUI).

## ⚠️ One Small Limitation You Need to Know About

The native Windows version is already remarkably complete, but there's one inherent difference worth putting on the table up front:

**If your primary goal is to have the Agent "deeply control the Windows system or modify complex local project-code dependencies"** — because Windows system paths differ fundamentally from POSIX (Linux) environments, the AI may still occasionally hit a tiny bug when running complex local automation commands.

So the official recommendation is pragmatic:

| Who You Are | Recommended Environment | Why |
|---------|---------|------|
| Pure developer (need the Agent to edit code, run complex local automation) | **WSL2** | Smoothest for terminal automation and integration with code projects |
| Everyday user (messaging butler, organizing data, wiring up cloud APIs) | **Native Windows** | Already more than enough, and rock-solid |

> 💡 A Word to the Wise
> **The collapse of the installation barrier often decides a tool's fate far more than the features themselves.**
> When "raising an AI that writes its own code" went from "first learn to set up WSL2 + Docker" to "paste a single line of PowerShell," the tool's potential user base instantly expanded from a few tens of thousands of engineers to a few billion Windows users. The spread of a technology is often won not by being smarter, but by being easier to install.

---

Now that it's installed and `hermes setup` has finished running, your computer is home to an agent that takes commands, runs the terminal, and writes its own skills.

Only one question remains: **what, exactly, can it shoulder for us on a real battlefield?**

Turn to Part 3. We're about to throw this agent into the minefield-laden swamp of distributed systems.

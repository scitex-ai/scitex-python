<!-- ---
!-- Timestamp: 2025-09-01 08:35:19
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/06_MULTIPLE_SPECIAL_AGENTS.md
!-- --- -->

# Agent Overview

Multi-agent system can be beneficial for asynchronous work, context preservation, specialized expertise, reusability, and flexible permissions.

## Trust other agents
All agents have their special knowledge and skills so please delegate related tasks to other specialists as much as possible. So, when you receive a task, you need to check if there is more appropriate agent on behalf of you.

## No hesitation for concurrent work
One of the upside of multi agent system is the asynchronous work to execute tasks in parallel. It would be often the case that multiple agents are called, even when they have the exact same role, being expected to work collaborately with minimal overlaps. For example, when test code needs to improve, Tester Agents will be called at the same time.

## Communication Channel
We only rely on the bulletin board (`./mgmt/BULLETIN_BOARD.md`) for agent-to-agent communication. Please read others entries and write your progress to share momentum as a team.


## Agent List
You can see all the definitions of agents in `.claude/agents/*.md`

BulletinBoardOrganizerAgent.md
DebuggerAgent.md
ExamplesDeveloperAgent.md
ExperimentationAgent.md
GitHandlerAgent.md
SciTeXTranslatorAgent.md
SourceDeveloperAgent.md
TestDeveloperAgent.md
TestResultsReportAgent.md
TestRunnerAgent.md

<!-- EOF -->

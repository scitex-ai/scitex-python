<!-- ---
!-- Timestamp: 2025-09-01 08:17:28
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/03_ARCHITECTUAL_AGREEMENT_PROCESS.md
!-- --- -->


# AI-Agent Architectural Agreement Process

## Phase 1: Large Picture Agreement

1.  **Examine reference implementations**
    e.g., example project

2.  **Present tree-like project structure**
    With full paths and class hierarchies
    decorators, class name, function name, arguments and returns with type hints

3.  **Get user feedback**
    Verify user agrees project organization and naming patterns
    Until agreement reached, `mgmt/ARCHITECTURE_v01.org` file is versioned by suffix
    e.g., `mgmt/ARCHITECTURE_v02.org`, `mgmt/ARCHITECTURE_v03.org`, ...;

4.  **Iterate based on preferences**
    Until structure feels "right"


## Phase 2: Detailed API Design

1.  **Expand tree structure** with method signatures and arguments
2.  **Show complete type information** for all functions and classes
3.  **Present workflow diagrams** showing data flow and relationships
4.  **Get approval** before moving to implementation


## Phase 3: Data Architecture

1.  **Design dataclass system** with clear responsibilities
    Use `@dataclass` decorator and `Container` suffixed class name
2.  **Show integration patterns** between services and data objects
3.  **Document validation and serialization** approaches using Mermaid diagrams


# Reusable Template for Future Projects

## Step 1: Discovery Phase

    Questions to ask:
    1. "Can you show me similar projects you've worked on for reference patterns?"
    2. "What existing codebases should I examine for conventions?"
    3. "Are there specific frameworks or patterns you prefer?"
    4. "How do you typically organize domain logic vs utilities?"

## Step 2: Structure Proposal

    Present:
    1. Complete directory tree with file naming patterns
    2. Class hierarchy with public/private distinctions
    3. Utility organization (atomic vs grouped)
    4. Test and example structure mirroring

## Step 3: Naming Convention Agreement

    Establish:
    1. Service class naming patterns (-er, Manager, Engine, etc.)
    2. Data object suffixes (Data, Container, Model, etc.)
    3. Entity naming (clean, no suffixes)
    4. File naming (private files, public classes)

## Step 4: API Design Review

    Document:
    1. All classes with method signatures
    2. Complete type annotations
    3. Configuration patterns
    4. Integration examples

## Step 5: Visual Architecture

    Create:
    1. Workflow diagrams showing data flow
    2. Class relationship diagrams
    3. Service integration patterns
    4. Usage examples and patterns

<!-- EOF -->

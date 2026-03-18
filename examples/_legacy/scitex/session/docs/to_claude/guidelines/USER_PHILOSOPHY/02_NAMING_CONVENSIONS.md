<!-- ---
!-- Timestamp: 2025-09-01 08:15:57
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/USER_PHILOSOPHY/02_NAMING_CONVENSIONS.md
!-- --- -->

# Naming Conventions

## 1. Explicit is better than implicit

-   `mcp_server.py` instead of `server.py` - more specific
-   `ChromaVectorDBManager` instead of generic `VectorStore`

## 2. Methods and functions written in verb_objects format

-   Clean MCP tool names: `search`, `get_topics`, `get_database_overview`, `get_file_content`


## 3. Classes

-   **One class per file**:
    `_MarkdownChunker.py includes solely `class MarkdownChunker(...)`, with `main()` and main guard
    `$ python -m package.domain._ClassName.py` will explain the usage

-   **File names for Private Classes**:
    Starting with underscore (`_MarkdownChunker.py`)

-   **File names for Public Classes**:
    Starting without underscore (`MarkdownChunker.py`)

-   **Class Names**:
    Always PascalCase (e.g., `class MarkdownChunker(...)`)

-   **Four types of Classes**
    1.  **Abstract bases**
        File name with `_Base` and class (`_BaseCar.py` → `class BaseCar`)

    2.  **Entity**
        Simple noun (e.g., Car)

    3.  **Business Logic**
        Often has suffix `-er` (e.g., CarMaintainer, CarDesigner)

    4.  **Data Container**
        File name with underscore and suffix with `Container`
        (e.g., `_CarSpecsContainer.py` includes @dataclass class CarSpecsContainer(...))

-   **Methods**
    Methods must be in the `verb_objects` format

-   **Decorators**
    Use decorators such as @dataclass, @classmethod, @staticmethod, @abstractmethod, @property


## 4. Functions

-   **One function per file**
    `_get_file_type.py` includes solely `def get_file_type(...)`, with `main()` and main guard
    `$ python -m package.domain._function_file.py` will explain the usage

-   **\*Grouped by domain**
    e.g., `file_utils/_get_file_type.py`, `text_utils/_clean_text.py`

-   **File names starting with underscore**
    e.g., `_get_file_type.py`, `_clean_text.py`, etc.

## 4. Source-Test agreement

-   **One-to-one mapping**
    Each source file maps to the corresponding test file

    **Mapping step**:
    Step 1. src -> tests
    Step 2. filename.py -> test_filename.py

    Example 1:
    src:   `/path/to/src/package/domain/filename.py`
    tests: `/path/to/tests/package/domain/test_filename.py`

    Note that when source file starts from underscore, use **double underscore** (test_ + _filename.py)

    Example 2:
    src:   `/path/to/src/package/domain/_filename.py`
    tests: `/path/to/tests/package/domain/test__filename.py`

## 4. Split Type Definitions

-   **Separate enum files**: `_DocumentType.py`, `_ChunkingStrategy.py`, etc.
-   **Utility functions**: `_DocumentTypeUtils.py` for related functions

<!-- EOF -->

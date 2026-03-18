# Project Name

semantic-graph

# Purpose

A sophisticated semantic search engine package that migrates and enhances the complete document MCP server functionality into a clean, pip-installable Python package. The system provides comprehensive document understanding, chunking, vector search, and knowledge graph capabilities.

# Migration Context

This project migrates sophisticated functionality from ~doc~-mcp-server/ which contains a complete document MCP server implementation with:

-   Multi-format document chunking (Markdown, Python, Shell, Text)
-   ChromaDB vector database integration
-   Knowledge graph construction and querying
-   Multiple search strategies (semantic, keyword, hybrid)
-   Comprehensive type system with dataclasses
-   Advanced utilities for caching, file operations, and text processing

# Key Features

## Core Search Engine

-   Multi-strategy search: semantic, keyword, hybrid, and knowledge graph-based
-   ChromaDB vector database integration with optimized indexing
-   Configurable similarity thresholds and result ranking

## Document Processing & Chunking

-   Multi-format support: Markdown, Python, Shell scripts, plain text
-   Specialized chunkers with format-aware parsing (BaseChunker, MarkdownChunker, PythonChunker, ShellChunker, TextChunker)
-   Configurable chunk size and overlap strategies
-   Metadata extraction and preservation (ChunkMetadata with document paths, types, relationships)

## Knowledge Graph Integration

-   Entity relationship mapping from document content
-   Graph-based search and discovery
-   Semantic relationship analysis
-   Cross-document connection identification

## MCP Server Capabilities

-   Full MCP protocol implementation for document management
-   Resource-based document access
-   Tool-based search and indexing operations
-   Claude Code integration support
-   FastMCP 2.0 compliance

## Advanced Utilities

-   Intelligent caching system with TTL management
-   File system utilities with recursive processing
-   Text preprocessing and normalization
-   Performance monitoring and optimization

# Architecture Migration Strategy

Migrating from ~doc~-mcp-server structure to semantic-graph while:

-   Preserving all existing capabilities and performance
-   Following established naming conventions (underscore prefixes, verb~object~ methods)
-   Maintaining comprehensive test coverage
-   Supporting both library and MCP server usage modes
-   Ensuring clean domain separation (chunkers/, db/, search/, graph/, config/)
-   Integrating PriorityConfig for centralized configuration management with precedence resolution

# Target Users

-   Developers building document search applications
-   Research teams requiring semantic document retrieval
-   Organizations implementing knowledge management systems
-   AI application developers needing document understanding
-   Claude Code users wanting document MCP server functionality

# Success Criteria

-   Complete migration of ~doc~-mcp-server functionality with zero capability loss
-   Clean package architecture following user philosophy patterns
-   Comprehensive test suite with \>90% coverage maintained
-   Performance parity or improvement over original implementation
-   Seamless MCP server integration with Claude Code
-   Clear API documentation and usage examples

## Migration Phases

1.  \[PENDING\] Architecture agreement and directory structure design
2.  \[PENDING\] Core types and configuration migration
3.  \[PENDING\] Chunking system migration with all specialized chunkers
4.  \[PENDING\] Database layer migration (ChromaVectorDBManager)
5.  \[PENDING\] Search engine and knowledge graph migration
6.  \[PENDING\] MCP server implementation migration
7.  \[PENDING\] Utilities and helper functions migration
8.  \[PENDING\] Comprehensive test suite migration and validation
9.  \[PENDING\] CLI interface and usage examples
10. \[PENDING\] Documentation and deployment preparation

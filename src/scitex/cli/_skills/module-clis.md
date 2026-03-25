---
name: cli-module-clis
description: Quick reference for every module-specific scitex CLI subcommand — audio speak, audit, container build/status, dataset search, notification send, repro gen-id, tunnel setup/remove/status, web summarize.
---

# Module-Specific CLIs

## audio

```bash
scitex audio speak "Hello from SciTeX"
scitex audio speak "Hello" --engine google
```

## audit

```bash
scitex audit .
scitex audit . --checks python deps
```

## container

```bash
scitex container build environment.def
scitex container status
scitex container list-versions
scitex container switch-version v1.1
```

## dataset

```bash
scitex dataset search "EEG epilepsy"
scitex dataset fetch --source openneuro --max 20
scitex dataset db build
scitex dataset db search "alzheimer"
```

## notification

```bash
scitex notification send "Training complete"
scitex notification send "GPU alert" --urgency critical
scitex notification sms "Pipeline done"
scitex notification backends
```

## repro

```bash
scitex repro gen-id
scitex repro gen-timestamp
```

## tunnel

```bash
scitex tunnel setup --port 8888 --bastion user@host --key ~/.ssh/id_rsa
scitex tunnel status
scitex tunnel remove --port 8888
```

## web

```bash
scitex web summarize https://arxiv.org/abs/2301.12345
scitex web search-pubmed "EEG deep learning" --max 10
```

## security

```bash
scitex security check-github-alerts
scitex security check-github-alerts --save
```

## social

```bash
scitex social post "New preprint out!" --platform twitter
scitex social status
```

## stats

```bash
scitex stats run-test ttest-ind data1.csv data2.csv
scitex stats recommend --data data.csv
```

## template

```bash
scitex template list
scitex template clone python-scitex ./my_new_project
```

## writer

```bash
scitex writer compile manuscript/
scitex writer figures add figure1.png --caption "Results"
```

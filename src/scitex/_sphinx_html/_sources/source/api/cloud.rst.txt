Cloud Module (``stx.cloud``)
============================

Cloud platform integration for the SciTeX ecosystem. Provides
programmatic access to remote execution, file storage, job management,
and repository operations.

Overview
--------

The cloud module connects local SciTeX workflows to the cloud platform,
enabling remote computation, shared storage, and collaborative
features. All operations are available through Python API, CLI, and
MCP tools.

Quick Start
-----------

.. code-block:: python

   import scitex as stx

   # Check cloud connection
   status = stx.cloud.status()

   # Submit a job
   job_id = stx.cloud.jobs.submit(script="train.py", resources={"gpu": 1})

   # Check job status
   stx.cloud.jobs.status(job_id)

Key Features
------------

Job Management
^^^^^^^^^^^^^^

Submit, monitor, and retrieve results from remote compute jobs.

.. code-block:: python

   # Submit a job
   job_id = stx.cloud.jobs.submit(
       script="train.py",
       resources={"gpu": 1, "memory": "16G"},
   )

   # Poll status
   status = stx.cloud.jobs.status(job_id)

   # List all jobs
   stx.cloud.jobs.list()

   # Cancel a running job
   stx.cloud.jobs.cancel(job_id)

File Storage
^^^^^^^^^^^^

Upload and download files to/from cloud storage.

.. code-block:: python

   # Upload a file
   stx.cloud.files.upload("local_data.h5", remote="data/experiment.h5")

   # Download a file
   stx.cloud.files.download("data/experiment.h5", local="./downloaded.h5")

   # List remote files
   stx.cloud.files.list("data/")

Data API
^^^^^^^^

CRUD operations on structured data stored in the cloud.

.. code-block:: python

   # Create a record
   stx.cloud.data.create(collection="results", data={"accuracy": 0.95})

   # Search records
   results = stx.cloud.data.search(collection="results", query={"accuracy": {"$gt": 0.9}})

   # List collections
   stx.cloud.data.list()

Repository Operations
^^^^^^^^^^^^^^^^^^^^^

Manage git repositories through the cloud API.

.. code-block:: python

   stx.cloud.repo.list()
   stx.cloud.repo.status("my-project")
   stx.cloud.repo.push("my-project")

CLI Access
----------

.. code-block:: bash

   # Job management
   scitex cloud jobs submit train.py --gpu 1
   scitex cloud jobs status JOB_ID
   scitex cloud jobs list

   # File operations
   scitex cloud files upload data.h5
   scitex cloud files list

   # Status
   scitex cloud status

API Reference
-------------

.. automodule:: scitex.cloud
   :members:
   :no-undoc-members:
   :show-inheritance:

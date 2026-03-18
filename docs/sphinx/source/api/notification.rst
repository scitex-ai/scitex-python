Notification Module (``stx.notification``)
===============================

Multi-backend notification system for alerting researchers when
long-running tasks complete, errors occur, or results are ready.

.. note::

   ``stx.notification`` delegates to the standalone
   `scitex-notification <https://github.com/ywatanabe1989/scitex-notification>`_
   package. Install with: ``pip install scitex-notification``.

Supported Backends
------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Backend
     - Description
   * - ``desktop``
     - Native desktop notifications (Linux ``notify-send``, macOS, Windows)
   * - ``email``
     - Email via SMTP
   * - ``slack``
     - Slack messages via webhook or Bot API
   * - ``webhook``
     - Generic HTTP POST to any URL

Quick Start
-----------

.. code-block:: python

   import scitex as stx

   # Send a notification (uses default backend)
   stx.notification.send("Training complete! Accuracy: 95.2%")

   # Send to a specific backend
   stx.notification.send("Job finished", backend="slack")

   # List available backends
   stx.notification.list_backends()

Key Functions
-------------

``send(message, backend=None, **kwargs)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Send a notification through one or more backends.

.. code-block:: python

   # Simple message
   stx.notification.send("Experiment finished successfully.")

   # With title
   stx.notification.send("95.2% accuracy achieved", title="Training Complete")

   # To a specific backend
   stx.notification.send("Results ready", backend="email")

``config(**kwargs)``
^^^^^^^^^^^^^^^^^^^^

Configure notification backends. Settings persist across sessions.

.. code-block:: python

   # Configure Slack
   stx.notification.config(
       slack_webhook="https://hooks.slack.com/services/...",
   )

   # Configure email
   stx.notification.config(
       email_to="researcher@university.edu",
       email_from="scitex@lab.org",
       smtp_host="smtp.university.edu",
   )

``list_backends()``
^^^^^^^^^^^^^^^^^^^

List available and configured backends.

.. code-block:: python

   backends = stx.notification.list_backends()
   # [{'name': 'desktop', 'available': True, 'configured': True},
   #  {'name': 'slack', 'available': True, 'configured': False}, ...]

Integration with ``@stx.session``
----------------------------------

Enable automatic notifications when a session completes:

.. code-block:: python

   import scitex as stx

   @stx.session(notify=True)
   def main(CONFIG=stx.INJECTED):
       """Long-running experiment."""
       result = train_model()
       return 0    # Sends "Session FINISHED_SUCCESS" notification

   if __name__ == "__main__":
       main()

CLI Access
----------

.. code-block:: bash

   # Send a notification
   scitex notify send "Job complete"

   # Check backend status
   scitex notify backends

   # Configure a backend
   scitex notify config --slack-webhook "https://..."

API Reference
-------------

.. automodule:: scitex.notification
   :members:
   :no-undoc-members:
   :show-inheritance:

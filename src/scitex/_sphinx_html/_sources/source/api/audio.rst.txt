Audio Module (``stx.audio``)
============================

Text-to-speech synthesis and audio file playback. Supports multiple
TTS backends with automatic fallback.

Quick Start
-----------

.. code-block:: python

   import scitex as stx

   # Text-to-speech
   stx.audio.speak("Analysis complete. 42 significant results found.")

   # Play an audio file
   stx.audio.play("notification.wav")

Key Functions
-------------

``speak(text, backend=None, **kwargs)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert text to speech and play it through the default audio output.
If no backend is specified, the first available backend is used.

.. code-block:: python

   # Use default backend
   stx.audio.speak("Hello from SciTeX")

   # Specify a backend
   stx.audio.speak("Hello", backend="espeak")

``play(path)``
^^^^^^^^^^^^^^

Play an audio file (WAV, MP3, etc.).

.. code-block:: python

   stx.audio.play("alert.wav")
   stx.audio.play("recording.mp3")

``list_backends()``
^^^^^^^^^^^^^^^^^^^

List available TTS backends on the current system.

.. code-block:: python

   backends = stx.audio.list_backends()
   # e.g., ['espeak', 'festival', 'pyttsx3']

Use Cases
---------

Audible notifications are useful for long-running experiments:

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(CONFIG=stx.INJECTED):
       result = train_model()  # Takes hours
       stx.audio.speak(f"Training done. Accuracy: {result.accuracy:.1%}")
       return 0

API Reference
-------------

.. automodule:: scitex.audio
   :members:
   :no-undoc-members:
   :show-inheritance:

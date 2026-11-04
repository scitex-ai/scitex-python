# Packaged documentation prototype

This separate source prototype builds real Sphinx HTML during normal Hatch
PEP517 sdist and wheel builds. The wheel contains `scitex/_sphinx_html/`; the
sdist carries the same bundle under `src/` and the original Sphinx sources.
The wheel build from an sdist regenerates the bundle rather than accepting
copied HTML. Generated HTML remains ignored and is never tracked in Git.

The shared build/publisher provisioning helper creates a new owned environment
for each stage; it never executes credentials or uploads in local qualification.
The custom Hatch hook uses `require-runtime-dependencies` to obtain the
project's canonical runtime requirements. Its documentation tools are explicit
build requirements. The native producer obtains both targets' requirements
from Hatch's public PEP517 API, normally installs them into an exclusive build
environment, and builds source → sdist → wheel through the normal frontend.
No independent copy of the runtime dependency list or self `[all]` edge exists.

The release verifier recognizes exactly this producer/configuration shape.
It reconstructs selected ordinary source from immutable Git blobs and invokes
the Git-bound producer again in a clean directory. The generated files must
match both archives byte for byte; an artifact-provided manifest or digest is
never an authority for accepting documentation. The receipt binds the producer
digest, exact source-input inventory, installed toolchain RECORD-verified canonical bytes, Python/stdlib
identity, trusted invocation and actual output size. The installed toolchain
must be unchanged before/after replay. Only installer-generated Python
shebang paths may normalize, after resolving their interpreter to the exact
qualified executable; entrypoint bodies and code/data remain exact. CPU
constraints/affinity are separate observations, stable within a replay, never
a substitute for exact regenerated HTML. Existing whole ordinary source,
RECORD, archive membership, containment, link, file-size and expansion checks
remain mandatory. The current native producer explicitly requires derived docs and a v2 proof;
historical v1 primitives remain independently testable without granting them
current production admission. The admitted release SIF identity remains required; local
prototype evidence alone does not establish qualification in that SIF.

This is a static documentation build. Existing mocked imports remain mocked,
notebooks never execute, and the plot directive never evaluates examples.
After fixed local platform/font discovery, the Python audit guard refuses outbound
network, child execution and reads outside its source, runtime and private
scratch roots; runtime CPU-cgroup reads are observed separately. Private
scratch is the only writable root. Refusals fail the build even through normal
Sphinx warning handlers; this is a trusted-code build guard, not an OS sandbox. External intersphinx
inventories are disabled for this offline bundle. Ordinary Sphinx warnings
remain visible, matching the existing build policy: successful rendering is
not complete runtime/API verification. Release comes from the source
`pyproject.toml`; there is no stale version fallback or installed-version guess.

Local initial full-runtime measurement: 846 files / 148,882,760 expanded bytes,
largest member 979,547 bytes. This predates final proof and is a measurement,
not a release receipt. The existing budgets are unchanged. Final evidence must
include an independent clean rebuild, source → sdist → wheel equality,
tamper/source-mismatch/path rejection controls, and real installed discovery
and HTTP serving from a clean directory with no checkout import path.

This prototype is not pushed, released or installed into any live runtime.
The historical frozen metadata fixture is bound to actual commit 644558f8,
with its genuine Hatch 1.27 headers verified byte for byte. Its 97 unchanged
assertions exercise legacy primitives against the current helper. They are
separate from current v2 producer qualification. Preserve the original 2061
baseline and inaccurate-f34-comment evidence.

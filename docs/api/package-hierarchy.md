# Umbrella hierarchy declarations

`scitex.hierarchy` owns the SciTeX root (`0`), four layers and the umbrella's
package slot (`package:scitex`, `1.1` beneath Main). Each other package owns its
own declaration. The umbrella does not copy the full package inventory.

```python
from scitex.hierarchy import get_hierarchy_declarations

rows = get_hierarchy_declarations()
assert [row["index"] for row in rows] == ["0", "1", "1.1", "2", "3", "4"]
```

The result is a tuple of independent JSON-shaped dictionaries. Editing a
returned dictionary does not alter later calls. Plain declaration access does
not import SDK code, discover installed providers, assign slots to unknown
packages or start services. Taxonomy is distinct from dependencies, installed
presence, project scope, access and live availability.

The umbrella declares its provider as installed metadata:

```toml
[project.entry-points."scitex_dev.hierarchy"]
scitex = "scitex.hierarchy:get_hierarchy_nodes"
```

`get_hierarchy_nodes()` explicitly constructs the same six declarations as the
SDK's `HierarchyNode` records. It imports the SDK contract only when called.
It requires that actual capability; a version string alone cannot prove it
exists. If SDK or its hierarchy module is missing, it raises an actionable
`RuntimeError` pointing to the plain declaration accessor. Failures in other
SDK dependencies propagate; the provider does not replace them with a success.
No new hard dependency or version pin is introduced by this declaration.

With a hierarchy-capable SDK, an explicit integration can combine these trusted
umbrella records with the SDK's own leaf record and call the shared validator.
The resulting SDK breadcrumb is SciTeX / Applications / SciTeX SDK. The SDK owns
node/tree validation; the umbrella implements no second validator. Automatic
provider admission/loading, other leaf enrollment, Docs ordering, global
search, hosted breadcrumbs and public/runtime adoption remain separate work.

Implementation:
[`scitex.hierarchy`](../../src/scitex/hierarchy.py).
Behavior checks:
[`test_hierarchy.py`](../../tests/scitex/test_hierarchy.py).
The factory test exercises the capability present in its actual environment;
plain declarations remain testable when the SDK contract is absent. A passing
source check does not qualify the umbrella's entire dependency cohort or a
fresh installed artifact. Existing package and native qualification holds are
not changed by this feature.

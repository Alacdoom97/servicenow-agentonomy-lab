# Interface text and encoding fix

The server now reads HTML as UTF-8 explicitly. Decorative separator dots, arrows, long dashes, and bullet characters have been replaced by plain text. The portable snapshot was regenerated; the generator also reads/writes UTF-8 explicitly.

## Apply

1. Stop the server with Ctrl+C.
2. Extract this ZIP outside your repository.
3. Copy each file below to the matching location in your existing repository, replacing existing files where prompted. Merge the folders; preserve other files.

- lab/server.py
- visual/index.html
- visual/offline-snapshot.html
- scripts/build_snapshot.py
- tests/test_encoding.py (new)

4. Run from the repository root:

```powershell
py -3 -W error::ResourceWarning -m unittest discover -s tests -v
py -3 -m lab serve
```

Expected: 30 tests pass, ending with OK. The new regression simulates a Windows-style cp1252 default and confirms that HTML still reads and serves as UTF-8. Verified on Linux/Python 3.12.14; your browser refresh confirms the rendered appearance on Windows.

5. Open http://127.0.0.1:8765 and press Ctrl+F5. Run INC-LAB-001 again. Check the incident label, knowledge suggestions, trace, and impact/urgency choices.
6. In GitHub Desktop, commit the changed files with summary `Fix interface text encoding`, then Push origin.

This patch preserves your earlier database cleanup fix. It does not require deleting your mock database or resetting approved incidents.

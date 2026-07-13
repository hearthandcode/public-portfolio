import importlib.util
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "contextpack.py"
SPEC = importlib.util.spec_from_file_location("contextpack", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load ContextPack module from {MODULE_PATH}")
contextpack = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = contextpack
SPEC.loader.exec_module(contextpack)


class ContextPackTests(unittest.TestCase):
    def write_manifest(self, root: Path, **overrides):
        data = {
            "manifest_version": "1.0",
            "source_root": "source",
            "runtime_root": ".exocore-contextpacks",
            "include": ["README.md", "architecture/*.md"],
            "exclude": ["**/AGENTS.md", ".hermes.md"],
            "chunk_max_chars": 120,
            "default_pack_budget_chars": 500,
            "qdrant": {"url": "http://127.0.0.1:6335", "collection": "exocore_test_contextpack"},
        }
        data.update(overrides)
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(data), encoding="utf-8")
        return manifest_path

    def test_manifest_selects_allowlisted_markdown_and_excludes_agent_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            (source / "architecture").mkdir(parents=True)
            (source / "README.md").write_text("# Home\n", encoding="utf-8")
            (source / "architecture" / "01-ADR.md").write_text("# ADR\n", encoding="utf-8")
            (source / "architecture" / "AGENTS.md").write_text("do not index\n", encoding="utf-8")
            (source / "other.md").write_text("not allowlisted\n", encoding="utf-8")
            manifest = contextpack.load_manifest(self.write_manifest(root))
            selected = [path.relative_to(source).as_posix() for path in contextpack.list_manifest_sources(manifest)]
            self.assertEqual(selected, ["README.md", "architecture/01-ADR.md"])

    def test_chunks_preserve_heading_and_source_line_range(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            document_path = source / "README.md"
            document_path.write_text(
                "---\ntitle: Example\nkind: reference\nstatus: draft\nverified: false\n---\n# First\nalpha beta\n## Second\ngamma delta\n",
                encoding="utf-8",
            )
            manifest = contextpack.load_manifest(self.write_manifest(root))
            document = contextpack.load_document(source, document_path)
            chunks = contextpack.chunk_document(document, 120)
            self.assertEqual([chunk.heading for chunk in chunks], ["First", "Second"])
            self.assertEqual((chunks[0].line_start, chunks[0].line_end), (7, 8))
            self.assertIn("gamma delta", chunks[1].text)
            self.assertFalse(document.verified)
            self.assertEqual(manifest["source_root_path"], source.resolve())

    def test_lexical_vector_is_normalized_and_deterministic(self):
        first = contextpack.lexical_vector("record projection policy receipt")
        second = contextpack.lexical_vector("record projection policy receipt")
        self.assertEqual(first, second)
        self.assertAlmostEqual(math.sqrt(sum(value * value for value in first)), 1.0)
        self.assertEqual(contextpack.lexical_vector(""), [0.0] * contextpack.VECTOR_DIMENSIONS)

    def test_non_loopback_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source").mkdir()
            manifest_path = self.write_manifest(root, qdrant={"url": "http://10.0.0.9:6333", "collection": "exocore_test_contextpack"})
            with self.assertRaises(contextpack.ContextPackError):
                contextpack.load_manifest(manifest_path)

    def test_verify_pack_detects_source_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            document = source / "README.md"
            document.write_text("# Before\n", encoding="utf-8")
            manifest = contextpack.load_manifest(self.write_manifest(root))
            provenance = root / "pack.manifest.json"
            provenance.write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "source_path": "README.md",
                                "source_sha256": contextpack.sha256_text("# Before\n"),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertTrue(contextpack.verify_pack(manifest, provenance)["ok"])
            document.write_text("# After\n", encoding="utf-8")
            result = contextpack.verify_pack(manifest, provenance)
            self.assertFalse(result["ok"])
            self.assertEqual(result["failures"], ["hash changed: README.md"])


if __name__ == "__main__":
    unittest.main()

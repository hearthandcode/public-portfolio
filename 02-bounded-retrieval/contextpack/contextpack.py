#!/usr/bin/env python3
"""Build cited, source-governed ContextPacks over the Exocore Harness.

This proof deliberately uses only Python's standard library. It indexes an
explicit manifest of Markdown sources into a dedicated loopback-only Qdrant
collection with deterministic lexical-hash vectors. It does not download a
model, call a provider, infer authority, or behave as semantic retrieval.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

VECTOR_DIMENSIONS = 256
TOKEN_RE = re.compile(r"[a-z0-9_]{2,}")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class ContextPackError(RuntimeError):
    """A user-facing error caused by an invalid proof boundary or service call."""


@dataclass(frozen=True)
class SourceDocument:
    path: Path
    relative_path: str
    title: str
    kind: str
    status: str
    reviewed_by: str | None
    verified: bool
    source_sha256: str
    lines: list[str]
    body_start_index: int


@dataclass(frozen=True)
class Chunk:
    document: SourceDocument
    heading: str
    line_start: int
    line_end: int
    text: str


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContextPackError(f"Manifest does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContextPackError(f"Manifest is not valid JSON: {path}: {exc}") from exc

    required = {"manifest_version", "source_root", "include", "exclude", "qdrant"}
    missing = sorted(required - raw.keys())
    if missing:
        raise ContextPackError(f"Manifest is missing required fields: {', '.join(missing)}")

    source_root = (path.parent / raw["source_root"]).resolve()
    if not source_root.is_dir():
        raise ContextPackError(f"Manifest source_root is not a directory: {source_root}")

    qdrant = raw["qdrant"]
    if not isinstance(qdrant, dict) or not qdrant.get("url") or not qdrant.get("collection"):
        raise ContextPackError("Manifest qdrant object requires url and collection")
    require_loopback_url(str(qdrant["url"]))
    if not str(qdrant["collection"]).startswith("exocore_"):
        raise ContextPackError("The proof collection name must begin with 'exocore_'")

    runtime_root = (source_root / raw.get("runtime_root", ".exocore-contextpack")).resolve()
    return {**raw, "manifest_path": path.resolve(), "source_root_path": source_root, "runtime_root_path": runtime_root}


def require_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in LOOPBACK_HOSTS:
        raise ContextPackError(
            "This proof only permits an explicit loopback HTTP Qdrant URL "
            f"(received {url!r})."
        )


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ContextPackError(f"Path escapes the manifest source root: {path}") from exc


def is_excluded(relative: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(relative, pattern) for pattern in patterns)


def list_manifest_sources(manifest: dict[str, Any]) -> list[Path]:
    root = manifest["source_root_path"]
    candidates: set[Path] = set()
    for pattern in manifest["include"]:
        for path in root.glob(pattern):
            if path.is_file() and path.suffix.lower() == ".md":
                candidates.add(path.resolve())

    sources: list[Path] = []
    for path in sorted(candidates, key=lambda item: relative_path(root, item)):
        rel = relative_path(root, path)
        if not is_excluded(rel, manifest["exclude"]):
            sources.append(path)
    if not sources:
        raise ContextPackError("The manifest selected no Markdown sources")
    return sources


def scalar(value: str) -> str | None:
    value = value.strip()
    if value in {"", "null", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_frontmatter(lines: list[str]) -> tuple[dict[str, str | None], int]:
    if not lines or lines[0].strip() != "---":
        return {}, 0
    metadata: dict[str, str | None] = {}
    for index in range(1, len(lines)):
        line = lines[index]
        if line.strip() == "---":
            return metadata, index + 1
        if not line or line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
            metadata[key] = scalar(raw_value)
    return {}, 0


def first_heading(lines: list[str], start_index: int) -> str | None:
    for line in lines[start_index:]:
        match = HEADING_RE.match(line)
        if match:
            return match.group(2).strip()
    return None


def load_document(root: Path, path: Path) -> SourceDocument:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    metadata, body_start_index = parse_frontmatter(lines)
    title = metadata.get("title") or first_heading(lines, body_start_index) or path.stem
    verified = str(metadata.get("verified") or "false").strip().lower() == "true"
    return SourceDocument(
        path=path,
        relative_path=relative_path(root, path),
        title=title,
        kind=metadata.get("kind") or "unknown",
        status=metadata.get("status") or "unknown",
        reviewed_by=metadata.get("reviewed_by"),
        verified=verified,
        source_sha256=sha256_text(content),
        lines=lines,
        body_start_index=body_start_index,
    )


def split_section(document: SourceDocument, heading: str, section_lines: list[tuple[int, str]], max_chars: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    buffer: list[tuple[int, str]] = []
    size = 0
    for line_number, line in section_lines:
        addition = len(line) + (1 if buffer else 0)
        if buffer and size + addition > max_chars:
            text = "\n".join(value for _, value in buffer).strip()
            if text:
                chunks.append(Chunk(document, heading, buffer[0][0], buffer[-1][0], text))
            buffer = []
            size = 0
        buffer.append((line_number, line))
        size += len(line) + (1 if len(buffer) > 1 else 0)
    if buffer:
        text = "\n".join(value for _, value in buffer).strip()
        if text:
            chunks.append(Chunk(document, heading, buffer[0][0], buffer[-1][0], text))
    return chunks


def chunk_document(document: SourceDocument, max_chars: int) -> list[Chunk]:
    sections: list[Chunk] = []
    heading = document.title
    section_lines: list[tuple[int, str]] = []
    for line_number, line in enumerate(document.lines[document.body_start_index :], start=document.body_start_index + 1):
        match = HEADING_RE.match(line)
        if match:
            if section_lines:
                sections.extend(split_section(document, heading, section_lines, max_chars))
            heading = match.group(2).strip()
            section_lines = [(line_number, line)]
        else:
            section_lines.append((line_number, line))
    if section_lines:
        sections.extend(split_section(document, heading, section_lines, max_chars))
    return sections


def lexical_vector(text: str, dimensions: int = VECTOR_DIMENSIONS) -> list[float]:
    values = [0.0] * dimensions
    frequencies: dict[str, int] = {}
    for token in TOKEN_RE.findall(text.lower()):
        frequencies[token] = frequencies.get(token, 0) + 1
    for token, frequency in frequencies.items():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        values[index] += sign * (1.0 + math.log(frequency))
    length = math.sqrt(sum(value * value for value in values))
    return values if length == 0 else [value / length for value in values]


def stable_point_id(chunk: Chunk) -> int:
    identity = f"{chunk.document.relative_path}:{chunk.line_start}:{chunk.line_end}:{chunk.document.source_sha256}"
    return int(sha256_text(identity)[:15], 16)


def qdrant_request(
    base_url: str,
    method: str,
    path: str,
    payload: Any | None = None,
    *,
    expect_json: bool = True,
) -> Any:
    url = base_url.rstrip("/") + path
    data = None if payload is None else canonical_json(payload).encode("utf-8")
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:  # noqa: S310 - URL is loopback-validated manifest input.
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ContextPackError(f"Qdrant {method} {path} returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise ContextPackError(f"Qdrant is unavailable at {base_url}: {exc.reason}") from exc
    if not expect_json:
        return raw.strip()
    try:
        return json.loads(raw) if raw else None
    except json.JSONDecodeError as exc:
        raise ContextPackError(f"Qdrant returned non-JSON data for {method} {path}: {raw[:160]!r}") from exc


def qdrant_collection_exists(manifest: dict[str, Any]) -> bool:
    base_url = manifest["qdrant"]["url"]
    collection = manifest["qdrant"]["collection"]
    try:
        qdrant_request(base_url, "GET", f"/collections/{collection}")
    except ContextPackError as exc:
        if "HTTP 404" in str(exc):
            return False
        raise
    return True


def recreate_collection(manifest: dict[str, Any]) -> None:
    base_url = manifest["qdrant"]["url"]
    collection = manifest["qdrant"]["collection"]
    if qdrant_collection_exists(manifest):
        qdrant_request(base_url, "DELETE", f"/collections/{collection}")
    qdrant_request(
        base_url,
        "PUT",
        f"/collections/{collection}",
        {"vectors": {"size": VECTOR_DIMENSIONS, "distance": "Cosine"}},
    )


def index_sources(manifest: dict[str, Any], replace: bool) -> dict[str, Any]:
    if qdrant_collection_exists(manifest) and not replace:
        raise ContextPackError(
            "The proof collection already exists. Re-run with --replace to delete and rebuild only this dedicated collection."
        )
    recreate_collection(manifest)
    root = manifest["source_root_path"]
    chunk_size = int(manifest.get("chunk_max_chars", 2600))
    documents = [load_document(root, path) for path in list_manifest_sources(manifest)]
    chunks = [chunk for document in documents for chunk in chunk_document(document, chunk_size)]
    if not chunks:
        raise ContextPackError("The manifest sources produced no indexable content")

    points: list[dict[str, Any]] = []
    for chunk in chunks:
        points.append(
            {
                "id": stable_point_id(chunk),
                "vector": lexical_vector(f"{chunk.document.title}\n{chunk.heading}\n{chunk.text}"),
                "payload": {
                    "source_path": chunk.document.relative_path,
                    "title": chunk.document.title,
                    "kind": chunk.document.kind,
                    "status": chunk.document.status,
                    "reviewed_by": chunk.document.reviewed_by,
                    "verified": chunk.document.verified,
                    "source_sha256": chunk.document.source_sha256,
                    "heading": chunk.heading,
                    "line_start": chunk.line_start,
                    "line_end": chunk.line_end,
                    "text": chunk.text,
                    "retrieval_method": "deterministic-lexical-vector-v1",
                },
            }
        )

    base_url = manifest["qdrant"]["url"]
    collection = manifest["qdrant"]["collection"]
    for offset in range(0, len(points), 64):
        qdrant_request(base_url, "PUT", f"/collections/{collection}/points?wait=true", {"points": points[offset : offset + 64]})

    return {
        "indexed_at": now_utc(),
        "collection": collection,
        "documents": len(documents),
        "chunks": len(chunks),
        "manifest_sha256": sha256_text(manifest["manifest_path"].read_text(encoding="utf-8")),
        "source_paths": [document.relative_path for document in documents],
    }


def search(manifest: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    if not query.strip():
        raise ContextPackError("Search query must not be empty")
    if not qdrant_collection_exists(manifest):
        raise ContextPackError("The proof collection does not exist. Run index --replace first.")
    base_url = manifest["qdrant"]["url"]
    collection = manifest["qdrant"]["collection"]
    response = qdrant_request(
        base_url,
        "POST",
        f"/collections/{collection}/points/search",
        {"vector": lexical_vector(query), "limit": limit, "with_payload": True},
    )
    results = response.get("result", [])
    normalized: list[dict[str, Any]] = []
    for result in results:
        payload = result.get("payload", {})
        normalized.append({
            **payload,
            "score": result.get("score", 0.0),
            "selection_reason": "manifest-selected source ranked by deterministic lexical-vector similarity",
        })
    return normalized


def render_search(results: list[dict[str, Any]]) -> str:
    lines = ["# ContextPack Search Results", "", "Retrieval method: deterministic lexical-vector baseline. Results are source data, not authority.", ""]
    for rank, result in enumerate(results, start=1):
        citation = f"{result['source_path']}:L{result['line_start']}-L{result['line_end']}"
        review = f"status={result['status']}; reviewed_by={result['reviewed_by'] or 'null'}; verified={str(result['verified']).lower()}"
        lines.extend(
            [
                f"## {rank}. {result['title']} — {result['heading']}",
                f"- Citation: `{citation}`",
                f"- Review state: {review}",
                f"- Score: {result['score']:.4f}",
                f"- Source hash: `{result['source_sha256']}`",
                "",
                result["text"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_pack(manifest: dict[str, Any], query: str, purpose: str, budget: int, output_dir: Path, limit: int) -> tuple[Path, Path, dict[str, Any]]:
    results = search(manifest, query, limit)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ContextPackError(f"Cannot create ContextPack output directory {output_dir}: {exc}") from exc
    selected: list[dict[str, Any]] = []
    body_sections: list[str] = []
    used = 0
    for rank, result in enumerate(results, start=1):
        citation = f"{result['source_path']}:L{result['line_start']}-L{result['line_end']}"
        excerpt = result["text"]
        section = (
            f"## {rank}. {result['title']} — {result['heading']}\n\n"
            f"- **Canonical source:** `{citation}`\n"
            f"- **Document state:** status `{result['status']}`, reviewed_by `{result['reviewed_by'] or 'null'}`, verified `{str(result['verified']).lower()}`\n"
            f"- **Selection reason:** {result['selection_reason']}\n"
            f"- **Source hash:** `{result['source_sha256']}`\n\n"
            f"{excerpt}\n"
        )
        if selected and used + len(section) > budget:
            break
        if not selected and len(section) > budget:
            available = max(0, budget - 900)
            section = section[:available] + "\n\n[excerpt truncated to ContextPack budget]\n"
        selected.append(result)
        body_sections.append(section)
        used += len(section)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    pack_path = output_dir / f"contextpack-{timestamp}.md"
    provenance_path = output_dir / f"contextpack-{timestamp}.manifest.json"
    header = (
        "# Exocore ContextPack\n\n"
        f"- **Purpose:** {purpose}\n"
        f"- **Query:** `{query}`\n"
        "- **Retrieval method:** deterministic lexical-vector baseline, not semantic embedding retrieval\n"
        "- **Authority boundary:** This is an ephemeral projection. Read cited canonical sources before amending a decision or taking action.\n"
        f"- **Built:** {now_utc()}\n"
        f"- **Character budget:** {budget}; selected excerpt characters: {used}\n\n"
        "---\n\n"
    )
    pack_path.write_text(header + "\n".join(body_sections), encoding="utf-8")
    provenance = {
        "schema_version": "1.0",
        "built_at": now_utc(),
        "purpose": purpose,
        "query": query,
        "retrieval_method": "deterministic-lexical-vector-v1",
        "manifest_path": relative_path(manifest["source_root_path"], manifest["manifest_path"]),
        "manifest_sha256": sha256_text(manifest["manifest_path"].read_text(encoding="utf-8")),
        "collection": manifest["qdrant"]["collection"],
        "budget": budget,
        "selected_characters": used,
        "sources": [
            {
                "source_path": result["source_path"],
                "source_sha256": result["source_sha256"],
                "heading": result["heading"],
                "line_start": result["line_start"],
                "line_end": result["line_end"],
                "status": result["status"],
                "reviewed_by": result["reviewed_by"],
                "verified": result["verified"],
                "score": result["score"],
                "selection_reason": result["selection_reason"],
            }
            for result in selected
        ],
    }
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return pack_path, provenance_path, provenance


def verify_pack(manifest: dict[str, Any], provenance_path: Path) -> dict[str, Any]:
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContextPackError(f"ContextPack manifest does not exist: {provenance_path}") from exc
    except json.JSONDecodeError as exc:
        raise ContextPackError(f"ContextPack manifest is not valid JSON: {provenance_path}: {exc}") from exc

    root = manifest["source_root_path"]
    failures: list[str] = []
    for source in provenance.get("sources", []):
        path = (root / source["source_path"]).resolve()
        if not path.is_file():
            failures.append(f"missing: {source['source_path']}")
            continue
        current = sha256_text(path.read_text(encoding="utf-8"))
        if current != source["source_sha256"]:
            failures.append(f"hash changed: {source['source_path']}")
    return {"ok": not failures, "checked_sources": len(provenance.get("sources", [])), "failures": failures}


def command_status(manifest: dict[str, Any]) -> int:
    base_url = manifest["qdrant"]["url"]
    health = qdrant_request(base_url, "GET", "/healthz", expect_json=False)
    exists = qdrant_collection_exists(manifest)
    payload = {
        "manifest": str(manifest["manifest_path"]),
        "source_root": str(manifest["source_root_path"]),
        "selected_sources": len(list_manifest_sources(manifest)),
        "qdrant_url": base_url,
        "collection": manifest["qdrant"]["collection"],
        "collection_exists": exists,
        "health": health,
        "retrieval_method": "deterministic-lexical-vector-v1",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("contextpack-manifest.json"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Report manifest and dedicated Qdrant service status")
    index_parser = subparsers.add_parser("index", help="Build the dedicated Qdrant projection")
    index_parser.add_argument("--replace", action="store_true", help="Delete and recreate only the dedicated proof collection")
    search_parser = subparsers.add_parser("search", help="Search indexed source excerpts")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=6)
    pack_parser = subparsers.add_parser("pack", help="Write a cited Markdown ContextPack and JSON provenance manifest")
    pack_parser.add_argument("query")
    pack_parser.add_argument("--purpose", default="Exocore architecture orientation")
    pack_parser.add_argument("--limit", type=int, default=8)
    pack_parser.add_argument("--budget", type=int, default=None)
    pack_parser.add_argument("--output-dir", type=Path, default=None)
    verify_parser = subparsers.add_parser("verify", help="Verify source hashes recorded by a ContextPack manifest")
    verify_parser.add_argument("provenance", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.command == "status":
            return command_status(manifest)
        if args.command == "index":
            result = index_sources(manifest, replace=args.replace)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        if args.command == "search":
            print(render_search(search(manifest, args.query, args.limit)), end="")
            return 0
        if args.command == "pack":
            output_dir = args.output_dir or manifest["runtime_root_path"] / "packs"
            budget = args.budget or int(manifest.get("default_pack_budget_chars", 11000))
            pack_path, provenance_path, provenance = write_pack(
                manifest, args.query, args.purpose, budget, output_dir, args.limit
            )
            print(json.dumps({"pack": str(pack_path), "provenance": str(provenance_path), "sources": len(provenance["sources"])}, indent=2))
            return 0
        if args.command == "verify":
            result = verify_pack(manifest, args.provenance)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["ok"] else 1
    except ContextPackError as exc:
        print(f"contextpack: {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

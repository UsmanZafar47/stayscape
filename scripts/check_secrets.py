"""Conservative pre-push check: report locations/categories, never secret values.

This supplements review; no pattern scanner can prove that a repo contains no secrets.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', 'node_modules', 'dist', 'build', '.python', '__pycache__', '.uv-cache', '.npm-cache', '.asset-cache', 'fastembed-cache', '.pytest_cache', '.ruff_cache', 'test-results', 'playwright-report', '.venv', '.venv-m2', 'venv', '.idea', '.vscode'}
# Only recognized placeholders are ignored, not arbitrary strings containing "example".
PLACEHOLDERS = {'', 'YOUR_API_KEY', 'YOUR_TOKEN', 'YOUR_PASSWORD', 'REPLACE_ME', 'PASSWORD', 'USER', 'test', 'test-key', 'unused'}
PATTERNS = [
    ('private key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('provider token', re.compile(r'\b(?:sk-[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{30,}|AKIA[A-Z0-9]{16})\b')),
    ('credential URL', re.compile(r'[a-z][a-z0-9+.-]*://[^\s/:]+:([^\s/@]+)@', re.I)),
]
ASSIGNMENT = re.compile(r'''(?i)\b(?:[a-z_]*(?:api_key|access_token|auth_token|secret_key|secret_access_key|password)|token)["']?\s*[=:]\s*["']([^"'\r\n]*)["']''')
ENV_ASSIGNMENT = re.compile(r'(?i)^\s*[A-Z_]*(?:API_KEY|TOKEN|SECRET|SECRET_ACCESS_KEY|PASSWORD)\s*=\s*([^\s#]*)')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def scan(name, data):
    if b'\0' in data:
        return []
    text = data.decode('utf-8', errors='replace')
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        if name == 'git-history' and line[:1] in {'+', '-'}:
            line = line[1:]
        # Comments can leak real tokens, so only placeholder values are exempt.
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(line):
                if kind == 'credential URL' and match.group(1) in PLACEHOLDERS:
                    continue
                findings.append(f'{name}:{number}: {kind}')
        for pattern in [ASSIGNMENT, ENV_ASSIGNMENT]:
            match = pattern.search(line)
            if match and match.group(1).strip() not in PLACEHOLDERS:
                findings.append(f'{name}:{number}: possible credential assignment')
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true', help='scan exact Git index contents')
    parser.add_argument('--history', action='store_true', help='also scan all reachable Git history patches')
    args = parser.parse_args()
    findings, env_files, checked = [], [], 0
    if args.staged:
        names = git('ls-files', '-z').decode().split('\0')
        files = [(name, git('show', ':' + name)) for name in names if name]
    else:
        files = []
        for folder, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.venv')]
            for name in names:
                path = Path(folder) / name
                # Generated bulk data cannot be published; skip it but scan actual env files.
                if path.suffix.lower() in {'.png', '.jpg', '.glb', '.zip', '.db', '.sqlite', '.pyc', '.onnx', '.pdf', '.lock'}:
                    continue
                if path.stat().st_size > 5_000_000:
                    continue
                files.append((path.relative_to(ROOT).as_posix(), path.read_bytes()))
    for name, data in files:
        basename = Path(name).name
        if (basename == '.env' or basename.startswith('.env.')) and basename != '.env.example':
            env_files.append(name)
            if args.staged:
                findings.append(f'{name}: environment file must not be committed')
        findings.extend(scan(name, data))
        checked += 1
    if args.history:
        # Patch scanning catches values that were committed then removed; line numbers refer to patches.
        findings.extend(scan('git-history', git('log', '--all', '-p', '--format=', '--no-ext-diff')))
    print(f'Checked {checked} text files. Local environment files: {len(env_files)}.')
    for name in env_files:
        print('Environment file (contents redacted):', name)
    for finding in sorted(set(findings)):
        print(finding)
    print('FAIL: review the locations above.' if findings else 'PASS: no matching secret patterns found. Review staged files before publishing.')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Validate Phase 0 artifact integrity, not application behavior or model accuracy."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ['PRODUCT_REQUIREMENTS', 'REA_RESEARCH_REPORT', 'OPEN_SOURCE_CAPABILITY_MATRIX',
        'ENGINEERING_ARCHITECTURE', 'DATABASE_SCHEMA', 'API_CONTRACTS', 'AI_MATCHING_SPEC',
        'AGE_GAP_RECOGNITION_RESEARCH', 'MODEL_EVALUATION_PLAN', 'SECURITY_THREAT_MODEL',
        'CHILD_SAFEGUARDING_POLICY', 'PRIVACY_AND_RETENTION', 'UI_UX_SPECIFICATION',
        'TEST_STRATEGY', 'IMPLEMENTATION_PHASES', 'DEPLOYMENT_OPERATIONS']
checks = []


def check(condition, description):
    if not condition:
        raise AssertionError(description)
    checks.append(description)


def read_json(path):
    return json.loads((ROOT / path).read_text())


for name in DOCS:
    check((ROOT / 'docs' / (name + '.md')).is_file(), 'Required document: ' + name)

evidence = read_json('docs/research/source-evidence.json')
lock = read_json('docs/research/repository-lock.json')
check(len(lock['repositories']) == 14, 'All 14 required repositories pinned')
for repo in lock['repositories']:
    original = next(r for r in evidence['repositories'] if r['repository'] == repo['repository'])
    check(bool(re.fullmatch('[a-f0-9]{40}', repo['sha'])) and repo['sha'] == original['sha'],
          'Commit pin: ' + repo['repository'])
    for item in repo['files']:
        source = next(f for f in original['files'] if f['path'] == item['path'])
        check(hashlib.sha256(source['content'].encode()).hexdigest() == item['utf8_sha256'],
              'Fetched-text integrity: ' + repo['repository'] + '/' + item['path'])
        check('/' + repo['sha'] + '/' in item['url'], 'Immutable source URL: ' + item['path'])

for repo, source_path, snapshot in [
    ('raigaurav26/FindTrace', 'index.html', 'findtrace/index.html'),
    ('immich-app/immich', 'server/src/controllers/face.controller.ts',
     'immich-selected/server/src/controllers/face.controller.ts'),
    ('immich-app/immich', 'server/src/repositories/machine-learning.repository.ts',
     'immich-selected/server/src/repositories/machine-learning.repository.ts')]:
    row = next(r for r in evidence['repositories'] if r['repository'] == repo)
    text = next(f for f in row['files'] if f['path'] == source_path)['content']
    check((ROOT / 'docs/research/targets' / snapshot).read_bytes() == text.encode(),
          'Byte-exact snapshot: ' + snapshot)

html = (ROOT / 'docs/research/targets/findtrace/index.html').read_text()
provenance = read_json('docs/research/targets/findtrace-extracted/extraction-provenance.json')
check(hashlib.sha256(html.encode()).hexdigest() == provenance['original_sha256'],
      'Extraction original hash')
bodies = [m for m in re.finditer(r'<script\b([^>]*)>([\s\S]*?)</script>', html, re.I)
          if 'src=' not in m.group(1) and m.group(2).strip()]
for row, body in zip(provenance['scripts'], bodies, strict=True):
    data = (ROOT / 'docs/research/targets/findtrace-extracted' / row['derived_file']).read_bytes()
    check(data == body.group(2).encode() and hashlib.sha256(data).hexdigest() == row['sha256'],
          'Exact inline body and hash')
    check(row['original_start_line'] == html[:body.start(2)].count('\n') + 1,
          'Inline extraction line mapping')

for name in ['findtrace', 'findtrace-extracted', 'immich-selected']:
    prefix = 'docs/research/rea/' + name + '-analysis'
    check((ROOT / (prefix + '.exit.txt')).read_text().strip() == '0', 'REA exit zero: ' + name)
    result = read_json(prefix + '.json')
    check(result['evidence_id'] in (ROOT / 'docs/REA_RESEARCH_REPORT.md').read_text(),
          'REA evidence identity documented: ' + name)
    check(result['normalized_result']['statistics']['parse_failures'] == 0,
          'REA no parse failures within supplied scope: ' + name)
check(read_json('docs/research/rea/findtrace-analysis.json')['normalized_result']['graph']['coverage']['status'] == 'partial',
      'HTML inline-analysis limitation preserved')
check(read_json('docs/research/rea/codex-doctor-summary.json')['healthy'] is True,
      'Scoped Codex registration diagnostic healthy')

api = read_json('docs/contracts/openapi.json')
check(api['openapi'] == '3.1.0' and api['security'], 'OpenAPI outline version and default security')


def walk(value):
    if isinstance(value, dict):
        if '$ref' in value:
            parts = value['$ref'].split('/')[1:]
            current = api
            for part in parts:
                current = current[part]
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)


walk(api)
check(True, 'All local OpenAPI references resolve (structural check only)')
event = read_json('docs/contracts/event-envelope.schema.json')
check(event['additionalProperties'] is False and set(event['required']) == set(event['properties']),
      'Closed required-fields event envelope')
check('embedding' not in event['properties'] and 'contact' not in event['properties'],
      'No biometric/contact payload field in event envelope')

for path in [ROOT / 'README.md', *list((ROOT / 'docs').rglob('*.md'))]:
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if link.startswith(('https:', 'http:', '#', 'mailto:')):
            continue
        target = link.split('#')[0].strip('<>')
        if target:
            check((path.parent / target).exists(), 'Local link: ' + str(path.relative_to(ROOT)) + ' -> ' + target)
check((ROOT / 'docs/ENGINEERING_ARCHITECTURE.md').read_text().count('sequenceDiagram') == 4,
      'Four required workflow sequence diagrams present')
package = read_json('tools/rea/package.json')
check(package['dependencies']['rea-agents'] == '6.7.0', 'Direct research dependency exactly pinned')
check(read_json('tools/rea/package-lock.json')['packages']['node_modules/rea-agents']['version'] == '6.7.0',
      'Research lock matches exact REA version')
print(json.dumps({'status': 'passed', 'checks': len(checks), 'required_documents': len(DOCS),
                  'repositories': len(lock['repositories']), 'source_files': sum(len(r['files']) for r in lock['repositories']),
                  'limitations': ['Artifact checks only; no application tests',
                                 'OpenAPI checks are structural, not full standards validation',
                                 'Source hash checks do not verify upstream licensing entitlement',
                                 'REA coverage limitations remain; no runtime or accuracy claim']}, indent=2))

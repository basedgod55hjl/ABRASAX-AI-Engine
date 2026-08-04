#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  OSIRISBLXCK — MASTER AUTONOMY ENGINE                             ║
║  PRIMAL_HEX: 4f5349524953424c58434b | φ: 1.618033988749895         ║
║  MODE: MAX AUTONOMY | SELF-EDIT | ALL ENGINES | HEX ENHANCE        ║
║  CONNECTS: Rust Meta Layer + Daemon + Telegram + All Logs          ║
║  LLM BACKEND: LM Studio only — NO remote API fallback              ║
║                                                                    ║
║  --docs   Regenerate ECO_SYSTEM.md + UNIFIED_ARCHITECTURE.md      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import os, sys, time, json, subprocess, argparse
from datetime import datetime
from pathlib import Path
import urllib.request

ROOT = r'C:\Users\BASEDGOD\Desktop\ABRASAX'
HEX = '4f5349524953424c58434b'
PHI = 1.618033988749895
SELF_PID = os.getpid()

# LLM backends
LM_STUDIO_URL = 'http://127.0.0.1:1234/v1'
LM_STUDIO_KEY = os.environ.get("LM_STUDIO_KEY", "")
LOCAL_MODEL = 'gemma-4-e4b-it-uncensored-max-opus-4.7'
LM_HEADERS = {'Authorization': f'Bearer {LM_STUDIO_KEY}', 'Content-Type': 'application/json'}

RUST_BIN = Path(ROOT) / 'abrasax_rs' / 'target' / 'release' / 'abrasax.exe'
DAEMON_BIN = Path(ROOT) / 'abrasax_rs' / 'target' / 'release' / 'abrasaxd.exe'
SRC_DIR = Path(ROOT) / 'abrasax_rs' / 'src'
LOG_DIR = Path(ROOT) / 'logs'
DATA_LOG = Path(ROOT) / 'data' / 'logs'
DATA_LOG.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

processes = {}

def log(msg, level='INFO'):
    ts = datetime.now().isoformat()
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    for p in [LOG_DIR/'master_autonomy.log', DATA_LOG/'live_feed.log']:
        with open(p, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

def kill_all_except_self():
    log("Killing stale processes...")
    for t in ['abrasax.exe', 'abrasaxd.exe']:
        subprocess.run(f'taskkill /f /im {t} 2>nul', shell=True, capture_output=True)
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'python.exe\'" get processid,commandline /format:csv',
            shell=True, timeout=5, stderr=subprocess.DEVNULL).decode()
        for line in out.split('\n')[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                cmd = (parts[-2] or '').lower()
                pid_s = (parts[-1] or '').strip()
                if pid_s.isdigit() and int(pid_s) != SELF_PID:
                    pid = int(pid_s)
                    if any(x in cmd for x in ['abrasax','nemotron','live_log','master_auto']):
                        os.system(f'taskkill /f /pid {pid} 2>nul')
                        log(f"Killed python {pid}")
    except: pass
    time.sleep(1)
    log("Cleanup complete")

def start_process(name, cmd, cwd=None, env=None):
    log(f"Starting {name}: {os.path.basename(cmd[0])}")
    pe = os.environ.copy()
    if env: pe.update(env)
    proc = subprocess.Popen(cmd, cwd=cwd or ROOT, env=pe,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW)
    processes[name] = proc
    log(f"{name} started (PID {proc.pid})")
    return proc

def query_llm(prompt, system=None, max_tokens=512, timeout=120):
    """Query LM Studio — LOCAL ONLY. No remote API fallback."""
    if not system:
        system = f"You are OSIRISBLXCK. HEX:{HEX} φ:{PHI}\nJSON responses only."
    try:
        data = json.dumps({"model": LOCAL_MODEL, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ], "max_tokens": max_tokens, "temperature": 0.6}).encode()
        req = urllib.request.Request(f"{LM_STUDIO_URL}/chat/completions",
            data=data, headers=LM_HEADERS)
        resp = urllib.request.urlopen(req, timeout=timeout)
        result = json.loads(resp.read())
        c = result['choices'][0]['message']['content']
        if c and c.strip():
            return c, result.get('usage', {})
        else:
            log("LM Studio returned empty content", 'WARN')
    except Exception as e:
        log(f"LM Studio error: {type(e).__name__}: {e}", 'WARN')
    
    log("LM Studio unavailable — LLM calls offline", 'FALLBACK')
    return "[LOCAL LLM ONLY]", {}

def read_dev_logs(max_files=20):
    txt = ""
    for lf in sorted(LOG_DIR.glob('*.log'), key=os.path.getmtime, reverse=True)[:max_files]:
        try:
            with open(lf, 'r', errors='ignore') as f:
                lines = f.readlines()[-30:]
            txt += f"\n=== {lf.name} ===\n{''.join(lines[-20:])}"
        except: pass
    return txt[:15000]

def analyze_and_suggest():
    logs = read_dev_logs()
    prompt = f"""ABRASAX self-opt cycle. {datetime.now().isoformat()}
HEX:{HEX}
=== LOGS ===\n{logs}\n
Analyze logs, identify issues, suggest Rust source edits.
JSON response:
{{"phi":0.0,"issues":[],"edits":[{{"file":"src/x.rs","line":N,"desc":"what to change"}}],"phase":"","priority":1}}"""
    resp, _ = query_llm(prompt, max_tokens=1024)
    if resp:
        try:
            js, je = resp.find('{'), resp.rfind('}') + 1
            if js >= 0 and je > js:
                return json.loads(resp[js:je])
        except Exception:
            pass
    return None

def apply_edit(edit):
    fp = SRC_DIR / edit['file'].replace('src/', '')
    if not fp.exists(): return False
    try:
        bk = fp.with_suffix('.rs.bak')
        if not bk.exists():
            import shutil
            shutil.copy2(fp, bk)
        with open(fp, 'r') as f: content = f.read()
        lines = content.split('\n')
        ln = edit.get('line', 0)
        if 0 < ln <= len(lines):
            lines[ln-1] = f"// φ-auto: {edit.get('desc','')}\n{lines[ln-1]}"
            with open(fp, 'w') as f: f.write('\n'.join(lines))
            log(f"Edited {edit['file']}:{ln} — {edit.get('desc','')}")
            return True
    except Exception as e:
        log(f"Edit failed: {e}", 'ERROR')
    return False

# ═══════════════════════════════════════════════════════════════
# DOCS GENERATION MODE (--docs)
# ═══════════════════════════════════════════════════════════════

def scan_directory_tree(root=None, max_depth=4, ignore_patterns=None):
    """Walk the ABRASAX directory tree and return structured listing."""
    if root is None:
        root = ROOT
    if ignore_patterns is None:
        ignore_patterns = {'.git', '__pycache__', '.venv', '.mypy_cache',
                           '.pytest_cache', 'node_modules', 'target',
                           '.cargo', 'dist', 'build', 'backups', 'logs',
                           '.claude', '.vscode', '.qodo', '.specify',
                           '.loki', 'sessions', 'swarm_results', 'raw',
                           'temp_nlm', 'wire_results', 'compiled',
                           'builds', 'runtime', 'vendor', 'onnx_runtime',
                           'llama-cpp', 'deepseek-ultimate', 'notebooks',
                           'images', 'media', 'training', 'pipeline',
                           'examples', 'cuda', 'kernels', 'kernel',
                           'plugins', 'ingest', 'memory', 'models',
                           'phi_chain', 'seed', 'skills', 'sdk',
                           'launchers', 'launcher_app', 'config',
                           'nginx', 'k8s', 'docker', 'ops', 'deploy', 'tools',
                           'bin'}
    tree = {}
    def _walk(path, depth=0):
        if depth > max_depth:
            return None
        try:
            entries = sorted(path.iterdir())
        except (PermissionError, OSError):
            return None
        dirs = {}
        files = []
        for entry in entries:
            if entry.name.startswith('.') or entry.name in ignore_patterns:
                continue
            if entry.is_dir():
                sub = _walk(entry, depth + 1)
                if sub:
                    dirs[entry.name] = sub
            elif entry.is_file():
                files.append(entry.name)
        result = {'dirs': dirs, 'files': files[:50]}
        name = path.name or str(path)
        tree[name] = result
        if path == Path(root):
            return tree
        return result if (dirs or files) else None
    _walk(Path(root))
    return tree

def collect_doc_metadata():
    """Read key metadata files for doc generation context."""
    meta = {}
    # Read system status
    status_path = Path(ROOT) / 'SYSTEM_STATUS.md'
    if status_path.exists():
        meta['system_status'] = status_path.read_text(encoding='utf-8', errors='ignore')[:3000]
    # Read build status
    build_path = Path(ROOT) / 'BUILD_STATUS.md'
    if build_path.exists():
        meta['build_status'] = build_path.read_text(encoding='utf-8', errors='ignore')[:2000]
    # Read Cargo.toml for Rust version info
    cargo_toml = Path(ROOT) / 'abrasax_rs' / 'Cargo.toml'
    if cargo_toml.exists():
        meta['cargo_toml'] = cargo_toml.read_text(encoding='utf-8', errors='ignore')[:2000]
    # Read package.json for Node deps
    pkg_json = Path(ROOT) / 'package.json'
    if pkg_json.exists():
        meta['package_json'] = pkg_json.read_text(encoding='utf-8', errors='ignore')[:2000]
    # Read pyproject.toml
    pyproj = Path(ROOT) / 'pyproject.toml'
    if pyproj.exists():
        meta['pyproject_toml'] = pyproj.read_text(encoding='utf-8', errors='ignore')[:2000]
    # Read .env (sanitized — no keys)
    env_path = Path(ROOT) / '.env'
    if env_path.exists():
        lines = env_path.read_text(encoding='utf-8', errors='ignore').split('\n')
        safe_lines = []
        for line in lines[:40]:
            if '=' in line:
                k = line.split('=')[0]
                safe_lines.append(f"{k}=***")
            else:
                safe_lines.append(line)
        meta['env_vars'] = '\n'.join(safe_lines)
    # List of .md files
    md_files = [str(p.relative_to(ROOT)) for p in sorted(Path(ROOT).glob('*.md'))]
    meta['root_md_files'] = md_files[:30]
    # List of key Python scripts
    py_files = [str(p.relative_to(ROOT)) for p in sorted(Path(ROOT).glob('*.py'))
                if not p.name.startswith('_')][:30]
    meta['root_py_files'] = py_files
    # List of TypeScript files
    ts_files = [str(p.relative_to(ROOT)) for p in sorted(Path(ROOT).glob('*.ts'))][:20]
    meta['root_ts_files'] = ts_files
    return meta

def format_tree_output(tree, indent=0):
    """Format directory tree as readable text."""
    lines = []
    prefix = "  " * indent
    for name, content in sorted(tree.items()):
        if isinstance(content, dict):
            dirs = content.get('dirs', {})
            files = content.get('files', [])
            lines.append(f"{prefix}📁 {name}/")
            for dname in sorted(dirs.keys())[:15]:
                lines.extend(format_tree_output({dname: dirs[dname]}, indent + 1))
            for fname in sorted(files)[:15]:
                lines.append(f"{prefix}  📄 {fname}")
            if len(dirs) > 15:
                lines.append(f"{prefix}  ... ({len(dirs)-15} more dirs)")
            if len(files) > 15:
                lines.append(f"{prefix}  ... ({len(files)-15} more files)")
    return lines

def query_llm_for_docs(prompt, max_tokens=4096):
    """Query LLM specifically for documentation generation (longer output)."""
    system = f"""You are the ABRASAX system architect. HEX: {HEX} φ: {PHI}
You generate structured, comprehensive markdown documentation for the ABRASAX AI ecosystem.
Respond ONLY with valid markdown. No explanations outside the markdown.
Use tables, code blocks, mermaid diagrams where appropriate.
Be thorough and technically precise."""
    resp, _ = query_llm_local(prompt, system=system, max_tokens=max_tokens, timeout=180)
    return resp

def generate_eco_system_md():
    """Generate ECO_SYSTEM.md using LLM analysis of codebase."""
    log("Scanning directory tree...", 'DOCS')
    tree = scan_directory_tree(ROOT, max_depth=3)
    tree_text = '\n'.join(format_tree_output(tree))

    log("Collecting metadata...", 'DOCS')
    meta = collect_doc_metadata()

    # Build compact prompt to avoid context overflow on local models
    prompt_parts = [
        f"Generate ABRASAX ECO_SYSTEM.md. Timestamp: {datetime.now().isoformat()}",
        f"HEX: {HEX} | φ: {PHI}",
        "=== DIRECTORY TREE ===",
        tree_text[:5000],
        "=== ROOT .md FILES ===",
        ', '.join(meta.get('root_md_files', [])[:25]),
        "=== KEY .py FILES ===",
        ', '.join(meta.get('root_py_files', [])[:25]),
        "=== SYSTEM STATUS ===",
        (meta.get('system_status', 'N/A') or '')[:1500],
        "",
        "Generate ECO_SYSTEM.md with these sections:",
        "1. Header with HEX, φ, GPU=GTX 1660 Ti 6GB, CPU=AMD Ryzen 7 4800H, OS=Windows 11 Pro",
        "2. Ecosystem Structure as tables: Core Platform, Platform Services, AI Subsystems, Products, External Integrations",
        "3. Data Flow mermaid diagram",
        "4. Build System commands",
        "5. Directory Map",
        "6. Branding Standard",
        "Use the actual directory tree above to fill in real paths and components."
    ]
    prompt = '\n'.join(prompt_parts)
    
    log("Querying LLM for ECO_SYSTEM.md...", 'DOCS')
    content = query_llm_for_docs(prompt, max_tokens=4096)
    if content:
        out_path = Path(ROOT) / 'ECO_SYSTEM.md'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        log(f"ECO_SYSTEM.md written ({len(content)} chars)", 'OK')
        return True
    log("LLM returned no content for ECO_SYSTEM.md", 'ERROR')
    return False

def generate_unified_architecture_md():
    """Generate UNIFIED_ARCHITECTURE.md using LLM analysis."""
    log("Scanning for architecture context...", 'DOCS')
    meta = collect_doc_metadata()
    
    # Read key architecture files for context
    arch_files = {}
    for fname in ['ARCHITECTURE.md', 'BUILD.md', 'SYSTEM_STATUS.md', 'BUILD_STATUS.md']:
        fp = Path(ROOT) / fname
        if fp.exists():
            arch_files[fname] = fp.read_text(encoding='utf-8', errors='ignore')[:3000]
    
    # Read key source for technical details
    src_files = {}
    for fname in ['abrasax_pipeline.py', 'abs_engine.py', 'xor_abs_engine.py']:
        fp = Path(ROOT) / fname
        if fp.exists():
            src_files[fname] = fp.read_text(encoding='utf-8', errors='ignore')[:2000]
    
    # Check Rust src
    rs_src = Path(ROOT) / 'abrasax_rs' / 'src'
    rs_files = []
    if rs_src.exists():
        rs_files = [str(p.relative_to(rs_src)) for p in sorted(rs_src.glob('**/*.rs'))][:20]
    
    # Check neural language
    nnl_path = Path(ROOT) / 'projects' / 'neural_language'
    nnl_files = []
    if nnl_path.exists():
        nnl_files = [str(p.relative_to(nnl_path)) for p in sorted(nnl_path.glob('**/*.py'))][:15]

    # Build compact prompt
    x_equation = "x_{{t+1}} = (1-K)x_t + K x* - η ∇J(x_t)"
    prompt_parts = [
        f"Generate ABRASAX UNIFIED_ARCHITECTURE.md. Timestamp: {datetime.now().isoformat()}",
        f"HEX: {HEX} | φ: {PHI} | K: {PHI - 1:.14f}",
        "=== ARCHITECTURE DOCS ===",
        json.dumps({k: v[:1000] for k, v in arch_files.items()}, indent=2)[:4000],
        "=== RUST SOURCE FILES ===",
        json.dumps(rs_files, indent=2),
        "=== NEURAL LANGUAGE FILES ===",
        json.dumps(nnl_files, indent=2),
        "=== SYSTEM STATUS ===",
        (meta.get('system_status', 'N/A') or '')[:1500],
        "",
        "Generate UNIFIED_ARCHITECTURE.md with:",
        f"1. Foundational Math — Sacred Constants (Φ, Φ⁻¹, S², DIMS=7, Curvature κ=Φ⁻¹), K-Calibration Dynamics with {x_equation} table (K=0 zombie to K>1 divergent), ABS Protocol (magic 0x414253, header 64 bytes, capacity 48MB per 4096x4096 PNG, modes ABS/LSB-3/Layer), Compiler Pipeline Levels 0-7 (Intent->Seed->Weights->ABS->GGUF->VRAM->Crystal Transformer->Deployed)",
        "2. Correct System Layout — Core Engine, AI Subsystems, Infrastructure, Products, External Ecosystem",
        "3. Data Flow diagram (User Input -> Orchestration Hub -> DeepSeek API / Agent Framework / Local LLM Engine)",
        "4. Build Order from build_ecosystem.py",
        "5. Current System State (from SYSTEM_STATUS.md)",
        "Make it technically precise with concrete constants, file paths, and implementation details from the actual codebase."
    ]
    prompt = '\n'.join(prompt_parts)

    log("Querying LLM for UNIFIED_ARCHITECTURE.md...", 'DOCS')
    content = query_llm_for_docs(prompt, max_tokens=4096)
    if content:
        out_path = Path(ROOT) / 'UNIFIED_ARCHITECTURE.md'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        log(f"UNIFIED_ARCHITECTURE.md written ({len(content)} chars)", 'OK')
        return True
    log("LLM returned no content for UNIFIED_ARCHITECTURE.md", 'ERROR')
    return False

def run_docs_mode():
    """One-shot documentation regeneration mode."""
    log("=" * 60, 'DOCS')
    log("DOCUMENTATION REGENERATION MODE", 'DOCS')
    log(f"HEX: {HEX} | φ: {PHI}", 'DOCS')
    log("=" * 60, 'DOCS')

    # Test LLM connectivity
    resp, _ = query_llm("Reply EXACTLY: DOCS_READY", max_tokens=15)
    if not resp:
        log("No LLM backend available — cannot generate docs", 'FATAL')
        return False
    log(f"LLM check: {resp.strip()}", 'OK')

    success = True
    if not generate_eco_system_md():
        success = False
    if not generate_unified_architecture_md():
        success = False

    log("=" * 60, 'DOCS')
    if success:
        log("DOCS REGENERATION COMPLETE ✅", 'OK')
    else:
        log("DOCS REGENERATION FAILED ❌", 'ERROR')
    return success

# ═══════════════════════════════════════════════════════════════
# LOKI AUTONOMY MODE (--loki)
# ═══════════════════════════════════════════════════════════════

LOKI_DIR = Path(ROOT) / '.loki'
SKILLS_DIR = Path(ROOT) / 'skills'
SWARM_DIR = Path(ROOT) / 'swarm'
AGABITS_DIR = Path(ROOT) / 'agabits'
NODE_BRIDGE = Path(ROOT) / 'node_agabits_bridge.mjs'
NOTEBOOKLM_SCRIPT = Path(ROOT) / 'notebooklm.py'

def query_notebooklm(query_topic):
    """Query NotebookLM CLI for research docs and ideas."""
    if not NOTEBOOKLM_SCRIPT.exists():
        log(f"NotebookLM script not found: {NOTEBOOKLM_SCRIPT}", 'WARN')
        return None
    try:
        result = subprocess.run(
            [sys.executable, str(NOTEBOOKLM_SCRIPT), 'query', query_topic],
            cwd=str(ROOT), capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:5000]
    except Exception as e:
        log(f"NotebookLM query failed: {e}", 'WARN')
    return None

def discover_skills():
    """Scan skills directory for available agentic skills."""
    skills = []
    if SKILLS_DIR.exists():
        for skill_file in sorted(SKILLS_DIR.glob('**/*.md')):
            skills.append({
                'name': skill_file.stem,
                'path': str(skill_file.relative_to(ROOT)),
                'size': skill_file.stat().st_size
            })
    # Also scan .loki for skill configs
    if LOKI_DIR.exists():
        for cfg in sorted(LOKI_DIR.glob('*.json')):
            try:
                with open(cfg) as f:
                    skills.append({'name': cfg.stem, 'config': json.load(f)})
            except: pass
    return skills

def activate_swarm_agents(skills):
    """Activate swarm agents based on discovered skills."""
    if not SWARM_DIR.exists():
        return []
    agents_activated = []
    swarm_scripts = list(SWARM_DIR.glob('*.py'))
    for script in swarm_scripts[:10]:
        try:
            proc = subprocess.Popen(
                [sys.executable, str(script), '--agent'],
                cwd=str(SWARM_DIR),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            agents_activated.append({'script': script.name, 'pid': proc.pid})
            log(f"Swarm agent: {script.name} (PID {proc.pid})", 'SWARM')
        except Exception as e:
            log(f"Swarm agent failed: {script.name}: {e}", 'WARN')
    return agents_activated

def start_node_bridge():
    """Start Node.js bridge for JS agent communication."""
    if not NODE_BRIDGE.exists():
        log(f"Node bridge not found: {NODE_BRIDGE}", 'WARN')
        return None
    try:
        proc = subprocess.Popen(
            ['node', str(NODE_BRIDGE)],
            cwd=str(ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        log(f"Node.js bridge started (PID {proc.pid})", 'NODE')
        return proc
    except Exception as e:
        log(f"Node bridge failed: {e}", 'WARN')
        return None

def verify_python_syntax(filepath):
    """Verify Python file syntax. Returns (ok, error_message)."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', str(filepath)],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return True, None
        return False, result.stderr[:500]
    except Exception as e:
        return False, str(e)

def apply_code_edit(filepath, old_lines, new_lines, start_line):
    """Apply actual code edit to a file with backup and syntax verification.
    Returns (success, message)."""
    fp = Path(ROOT) / filepath
    if not fp.exists():
        return False, f"File not found: {fp}"
    try:
        # Read current content
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Create timestamped backup
        import shutil
        bk_dir = Path(ROOT) / 'backups' / 'self_upgrades'
        bk_dir.mkdir(parents=True, exist_ok=True)
        bk_path = bk_dir / f"{fp.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copy2(fp, bk_path)
        
        # Apply edit: replace lines at position
        idx = start_line - 1  # 0-indexed
        if idx < 0 or idx > len(lines):
            return False, f"Line {start_line} out of range (1-{len(lines)})"
        
        # Verify old_lines match
        old_joined = '\n'.join(old_lines)
        actual_old = '\n'.join(lines[idx:idx + len(old_lines)])
        if old_joined.strip() != actual_old.strip():
            return False, f"Old content mismatch at line {start_line}"
        
        # Apply replacement
        new_content_lines = lines[:idx] + new_lines + lines[idx + len(old_lines):]
        new_content = '\n'.join(new_content_lines)
        
        # Write and verify syntax
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        ok, err = verify_python_syntax(fp)
        if not ok:
            # Rollback
            shutil.copy2(bk_path, fp)
            return False, f"Syntax error after edit, rolled back: {err[:200]}"
        
        log(f"✏️  Code edit applied: {filepath}:{start_line} (backup: {bk_path.name})", 'UPGRADE')
        return True, f"Applied at line {start_line}, backup: {bk_path.name}"
    except Exception as e:
        return False, f"Edit failed: {e}"

def upgrade_self(cycle_count):
    """Read own source, send to LLM, get concrete code improvements, apply them."""
    log(f"Self-upgrade analysis cycle #{cycle_count}", 'UPGRADE')
    
    # Read our own source
    self_path = Path(__file__)
    try:
        source = self_path.read_text(encoding='utf-8')
        source_lines = source.split('\n')
        total_lines = len(source_lines)
    except Exception as e:
        log(f"Cannot read self: {e}", 'ERROR')
        return None
    
    # Send a chunk to the LLM for analysis (focus on a random section to keep prompt size manageable)
    import random
    chunk_size = 100
    start = random.randint(0, max(0, total_lines - chunk_size))
    chunk = '\n'.join(f"{start + i + 1}: {line}" for i, line in enumerate(source_lines[start:start + chunk_size]))
    
    prompt = f"""ABRASAX self-upgrade #{cycle_count}. HEX:{HEX} φ:{PHI}
You are upgrading YOUR OWN source code (_MASTER_AUTONOMY.py).
Analyze this code chunk (lines {start+1}-{start+chunk_size} of {total_lines}):

{chunk}

Propose ONE concrete code improvement. Respond as JSON:
{{"file":"_MASTER_AUTONOMY.py","start_line":NNN,"old_str":"EXACT old code","new_str":"EXACT replacement code","reason":"why this is better","confidence":0.8}}

Rules:
- old_str must match EXACTLY (preserve whitespace/indentation)
- new_str must be valid Python
- Focus on: performance, error handling, log detail, autonomy logic, async ops
- Do NOT change the core loop structure or API keys
- Make small, safe improvements"""
    
    resp, _ = query_llm(prompt, max_tokens=1024)
    if not resp:
        return None
    
    try:
        js, je = resp.find('{'), resp.rfind('}') + 1
        if js >= 0 and je > js:
            proposal = json.loads(resp[js:je])
            log(f"Upgrade proposal: L{proposal.get('start_line')} — {proposal.get('reason','?')[:80]}", 'UPGRADE')
            return proposal
    except Exception as ex:
        log(f"Failed to parse upgrade proposal: {ex}", 'WARN')
    return None

def apply_upgrade(proposal):
    """Apply a self-upgrade proposal with full safety checks."""
    if not proposal:
        return False
    
    filepath = proposal.get('file', '_MASTER_AUTONOMY.py')
    start_line = proposal.get('start_line', 0)
    old_str = proposal.get('old_str', '')
    new_str = proposal.get('new_str', '')
    reason = proposal.get('reason', 'unknown')
    confidence = proposal.get('confidence', 0)
    
    if not old_str or not new_str:
        log(f"Upgrade missing old_str or new_str", 'WARN')
        return False
    
    if confidence < 0.5:
        log(f"Upgrade confidence too low ({confidence}), skipping", 'WARN')
        return False
    
    old_lines = old_str.split('\n')
    new_lines = new_str.split('\n')
    
    success, msg = apply_code_edit(filepath, old_lines, new_lines, start_line)
    if success:
        log(f"✅ SELF-UPGRADED: {reason[:100]} (confidence={confidence:.2f})", 'UPGRADE')
        # Record upgrade in history
        history = []
        hist_path = DATA_LOG / 'upgrade_history.json'
        if hist_path.exists():
            try:
                history = json.loads(hist_path.read_text())
            except: pass
        history.append({
            'ts': datetime.now().isoformat(),
            'cycle': proposal.get('_cycle', 0),
            'file': filepath,
            'line': start_line,
            'reason': reason,
            'confidence': confidence,
            'msg': msg
        })
        with open(hist_path, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    else:
        log(f"Upgrade rejected: {msg}", 'WARN')
        return False

def self_restart():
    """Restart this script with --loki flag using new code."""
    log("SELF-RESTART: Launching upgraded instance...", 'UPGRADE')
    script = str(Path(__file__))
    # Use PowerShell to launch detached
    try:
        subprocess.Popen(
            ['powershell', '-Command',
             f'Start-Process python -ArgumentList "{script}", "--loki" -NoNewWindow'],
            cwd=str(ROOT),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        log("New instance launched, exiting current", 'UPGRADE')
        return True
    except Exception as e:
        log(f"Self-restart failed: {e}", 'ERROR')
        return False

def self_build_cycle(cycle_count):
    """Full self-upgrade cycle: analyze → propose → verify → apply → potentially restart."""
    log(f"Self-build cycle #{cycle_count}", 'BUILD')
    
    # 1. Try self-upgrade (analyze own source)
    if cycle_count % 3 == 0:  # Every 3rd cycle, try self-upgrade
        proposal = upgrade_self(cycle_count)
        if proposal:
            proposal['_cycle'] = cycle_count
            if apply_upgrade(proposal):
                # If we've upgraded, restart to use new code (every 5 upgrades)
                hist_path = DATA_LOG / 'upgrade_history.json'
                upgrade_count = 0
                if hist_path.exists():
                    try:
                        upgrade_count = len(json.loads(hist_path.read_text()))
                    except: pass
                if upgrade_count > 0 and upgrade_count % 5 == 0:
                    self_restart()
                    sys.exit(0)
                return proposal
    
    # 2. Also scan other Python files for improvements
    py_files = [str(p.relative_to(ROOT)) for p in sorted(Path(ROOT).glob('*.py'))
                if not p.name.startswith('_') and p.stat().st_size < 50000][:8]
    
    prompt = f"""ABRASAX code review cycle #{cycle_count}.
HEX:{HEX} φ:{PHI}
Review these files and propose ONE concrete code improvement:
{json.dumps(py_files, indent=2)}

Respond as JSON:
{{"file":"path/to/file.py","start_line":NNN,"old_str":"exact code to replace","new_str":"replacement code","reason":"why","confidence":0.8}}"""
    
    resp, _ = query_llm(prompt, max_tokens=1024)
    if not resp:
        return None
    
    try:
        js, je = resp.find('{'), resp.rfind('}') + 1
        if js >= 0 and je > js:
            proposal = json.loads(resp[js:je])
            log(f"Build proposal: {proposal.get('file')} L{proposal.get('start_line')} — {proposal.get('reason','?')[:80]}", 'IDEA')
            return proposal
    except Exception:
        pass
    return None

def feed_docs(discoveries):
    """Feed discoveries back into documentation files."""
    if not discoveries:
        return
    ts = datetime.now().isoformat()
    entry = f"\n<!-- LOKI DISCOVERY {ts} -->\n{discoveries}\n"
    
    eco_path = Path(ROOT) / 'ECO_SYSTEM.md'
    if eco_path.exists():
        with open(eco_path, 'a', encoding='utf-8') as f:
            f.write(entry)
    log(f"Fed {len(discoveries)} chars to ECO_SYSTEM.md", 'FEED')

def run_loki_mode():
    """Non-stop Loki autonomy loop — query, build, feed, repeat."""
    log("=" * 60, 'LOKI')
    log("LOKI AUTONOMY ENGINE — MAX AUTONOMY MODE", 'LOKI')
    log(f"HEX: {HEX} | φ: {PHI}", 'LOKI')
    log("Mode: non-stop query → build → feed → loop", 'LOKI')
    log("=" * 60, 'LOKI')
    
    # Test LLM
    resp, _ = query_llm("Reply: LOKI_READY", max_tokens=10)
    if resp:
        log(f"LLM: {resp.strip()}", 'OK')
    else:
        log("No LLM — running in scan-only mode", 'WARN')
    
    # Discover initial skills
    skills = discover_skills()
    log(f"Discovered {len(skills)} skills/configs", 'SKILLS')
    
    # Start Node.js bridge
    node_proc = start_node_bridge()
    
    # Activate swarm agents
    agents = activate_swarm_agents(skills)
    log(f"Activated {len(agents)} swarm agents", 'SWARM')
    
    cycle = 0
    topics = ['ABRASAX architecture', 'GPU optimization', 'CUDA kernels',
              'GGUF inference', 'swarm intelligence', 'neural compilation',
              '7D crystal transformer', 'Poincaré ball', 'K-calibration',
              'agent framework', 'self-improving code', 'autonomous systems']
    
    while True:
        cycle += 1
        log(f"--- LOKI CYCLE {cycle} ---", 'LOKI')
        
        # 1. Query NotebookLM for research
        topic = topics[cycle % len(topics)]
        log(f"Querying NotebookLM: {topic}", 'QUERY')
        nb_result = query_notebooklm(topic)
        if nb_result:
            log(f"NotebookLM returned {len(nb_result)} chars", 'OK')
            feed_docs(f"## NotebookLM: {topic}\n{nb_result[:2000]}")
        
        # 2. Rediscover skills (new ones may have been added)
        if cycle % 5 == 0:
            skills = discover_skills()
            log(f"Skills refresh: {len(skills)} available", 'SKILLS')
        
        # 3. Self-build cycle
        proposal = self_build_cycle(cycle)
        if proposal:
            feed_docs(json.dumps(proposal, indent=2))
        
        # 4. Regenerate docs every 10 cycles
        if cycle % 10 == 0:
            log("Regenerating documentation...", 'DOCS')
            generate_eco_system_md()
            generate_unified_architecture_md()
        
        # 5. Write state
        state = {
            "ts": datetime.now().isoformat(),
            "cycle": cycle,
            "mode": "loki",
            "skills": len(skills),
            "agents": len(agents),
            "node_bridge": node_proc is not None and node_proc.poll() is None,
            "hex": HEX,
            "phi": PHI
        }
        with open(DATA_LOG / 'loki_state.json', 'w') as f:
            json.dump(state, f, indent=2)
        
        # 6. Check Node bridge health
        if node_proc and node_proc.poll() is not None:
            log("Node bridge died, restarting", 'WARN')
            node_proc = start_node_bridge()
        
        log(f"Cycle {cycle} complete. Skills={len(skills)} Agents={len(agents)}", 'LOKI')
        time.sleep(30)  # 30-second cycle interval

def rebuild_rust():
    log("Rebuilding Rust...")
    r = subprocess.run(['cargo','build','--release'], cwd=str(Path(ROOT)/'abrasax_rs'),
                      capture_output=True, text=True, timeout=300)
    if r.returncode == 0:
        log("Build SUCCESS")
        return True
    log(f"Build FAILED: {r.stderr[-300:]}", 'ERROR')
    return False

def start_telegram():
    env = {'ABRASAX_LLM_HOST': '127.0.0.1', 'ABRASAX_LLM_PORT': '1234',
           'ABRASAX_TG_DEMO': '0', 'ABRASAX_TG_TOKEN': os.environ.get('ABRASAX_TG_TOKEN', ''),
           'ABRASAX_ADMIN_IDS': '2611544979'}
    tg = Path(ROOT)/'telegram'/'start_telegram_bridge.py'
    return start_process('telegram', [sys.executable, str(tg)], cwd=str(tg.parent), env=env)

def main():
    log("="*60, 'BOOT')
    log(f"OSIRISBLXCK MASTER AUTONOMY PID={SELF_PID}", 'BOOT')
    log(f"HEX: {HEX} | φ: {PHI} | GPU: GTX 1660 Ti 6GB", 'BOOT')
    log(f"LLM: LM Studio → DeepSeek API fallback", 'BOOT')
    log("="*60, 'BOOT')
    
    kill_all_except_self()
    
    log("\n[PHASE 1] Starting engines...", 'PHASE')
    if RUST_BIN.exists():
        start_process('meta', [str(RUST_BIN), 'meta'])
        time.sleep(2)
    if DAEMON_BIN.exists():
        start_process('daemon', [str(DAEMON_BIN)])
        time.sleep(1)
    start_telegram()
    time.sleep(3)
    
    # Quick LLM test
    resp, _ = query_llm("Reply EXACTLY: READY", max_tokens=10)
    if resp:
        log(f"DeepSeek API: {resp.strip()}", 'OK')
    else:
        log("No LLM backend available", 'WARN')
    
    log("\n[PHASE 2] Self-optimization loop ACTIVE", 'PHASE')
    cycle = 0
    edit_count = 0
    
    while True:
        cycle += 1
        log(f"--- CYCLE {cycle} ---", 'CYCLE')
        
        # Check process health
        for n, p in list(processes.items()):
            if p.poll() is not None:
                log(f"{n} died (code {p.returncode}), restarting", 'WARN')
                del processes[n]
                if n == 'meta' and RUST_BIN.exists():
                    start_process('meta', [str(RUST_BIN), 'meta'])
                elif n == 'telegram':
                    start_telegram()
        
        # Analyze logs → get edit suggestions from LLM
        analysis = analyze_and_suggest()
        if analysis:
            log(f"φ={analysis.get('phi',0):.4f} p={analysis.get('priority','?')} "
                f"edits={len(analysis.get('edits',[]))}", 'ANALYSIS')
            for e in (analysis.get('edits') or [])[:3]:
                if edit_count < 100:
                    if apply_edit(e):
                        edit_count += 1
        
        # Every 5 cycles: rebuild with edits
        if cycle % 5 == 0 and edit_count > 0:
            log(f"\n[REBUILD] {edit_count} edits applied", 'BUILD')
            if 'meta' in processes:
                processes['meta'].terminate()
                time.sleep(1)
            if rebuild_rust():
                if RUST_BIN.exists():
                    start_process('meta', [str(RUST_BIN), 'meta'])
                edit_count = 0
        
        # Every 10 cycles: write state
        if cycle % 10 == 0:
            state = {"ts": datetime.now().isoformat(), "cycle": cycle,
                     "edits": edit_count, "phi": PHI, "hex": HEX,
                     "running": [n for n,p in processes.items() if p.poll() is None],
                     "status": "running"}
            with open(DATA_LOG/'autonomy_state.json','w') as f:
                json.dump(state, f, indent=2)
            log(f"State: running={state['running']}", 'STATE')
        
        time.sleep(15)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OSIRISBLXCK Master Autonomy Engine')
    parser.add_argument('--docs', action='store_true',
                        help='One-shot: regenerate ECO_SYSTEM.md and UNIFIED_ARCHITECTURE.md')
    parser.add_argument('--loki', action='store_true',
                        help='Non-stop Loki autonomy loop: query NotebookLM → skills → swarm → self-build → feed docs')
    args = parser.parse_args()

    if args.docs:
        success = run_docs_mode()
        sys.exit(0 if success else 1)

    if args.loki:
        try:
            run_loki_mode()
        except KeyboardInterrupt:
            print("\nLoki shutdown...")
            sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown...")
        for n, p in processes.items():
            try: p.terminate()
            except: pass
        print("OSIRISBLXCK OUT.")
        sys.exit(0)

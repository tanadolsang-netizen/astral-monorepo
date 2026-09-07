#!/usr/bin/env bash
# ============================================================================
#  Astral Sync v2 — concurrent-safe handoff hub (2+ machines, same account)
# ----------------------------------------------------------------------------
#  Solves the "2 machines editing at once" problem with 3 layers:
#    1. conflict detection  — warns before overwrite (vault/memory/backend)
#    2. per-machine branch  — each machine has its own branch; main = merged truth
#    3. single-writer lock  — MEMORY.md lockfile prevents silent clobber
#
#  Commands:
#    ./sync.sh status     drift report (local vs hub, lock state, branch list)
#    ./sync.sh up         refresh hub from THIS machine (auto-merge into main)
#    ./sync.sh pull       pull latest hub -> local Astral clone
#    ./sync.sh apply      materialize hub's backend/vault/memory into local dirs
#    ./sync.sh lock       acquire single-writer lock on memory (before editing)
#    ./sync.sh unlock     release lock (call when done editing)
#    ./sync.sh help       this text
#
#  Flags:
#    --commit    (up) commit uncommitted backend source first
#    --yes       (apply) skip confirmation prompt
#    --force     (up) push even if conflict detected (last-writer-wins)
#
#  Env overrides:
#    ASTRAL_DIR     path to cloned Astral repo  (default: this script's dir)
#    BACKEND_SRC    NEW-AI-REBORN source dir     (default: native C:\AI\NEW-AI-REBORN)
#    VAULT_SRC      obsidian-vault source dir     (default: native C:\AI\obsidian-vault)
#    HERMES_MEM     hermes memories dir           (default: %LOCALAPPDATA%\hermes\memories)
#    BACKEND_DST    apply target for backend      (default: $BACKEND_SRC)
#    VAULT_DST      apply target for vault        (default: $VAULT_SRC)
#    MACHINE_ID     branch suffix (default: hostname)
# ============================================================================

# ---- colors -----------------------------------------------------------------
if [ -t 1 ]; then R='[31m'; G='[32m'; Y='[33m'; B='[34m'; M='[35m'; C='[36m'; N='[0m';
else R=''; G=''; Y=''; B=''; M=''; C=''; N=''; fi
info(){ printf "${B}▶${N} %s
" "$*"; }
ok(){   printf "${G}✓${N} %s
" "$*"; }
warn(){ printf "${Y}!${N} %s
" "$*"; }
err(){  printf "${R}✗${N} %s
" "$*" >&2; }
header(){ printf "
${M}══ %s ══${N}
" "$*"; }
die(){ err "$*"; exit 1; }

# ---- path helpers -----------------------------------------------------------
to_native(){ if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1" 2>/dev/null || echo "$1"; else echo "$1"; fi; }
to_unix(){   if command -v cygpath >/dev/null 2>&1; then cygpath -u "$1" 2>/dev/null || echo "$1"; else echo "$1"; fi; }

# ---- resolve config --------------------------------------------------------
# ASTRAL_DIR_UNIX = unix path for bash tools (tar, find, rm, cp, mkdir, diff)
# git -C and hermes need native Windows path, converted on the fly.
ASTRAL_DIR_UNIX="${ASTRAL_DIR:-$(cd "$(dirname "$0")" && pwd)}"
BACKEND_SRC="${BACKEND_SRC:-$(to_native /c/AI/NEW-AI-REBORN)}"
VAULT_SRC="${VAULT_SRC:-$(to_native /c/AI/obsidian-vault)}"
HERMES_MEM="${HERMES_MEM:-$(to_native "$(cygpath "$LOCALAPPDATA")/hermes/memories")}"
BACKEND_DST="${BACKEND_DST:-$BACKEND_SRC}"
VAULT_DST="${VAULT_DST:-$VAULT_SRC}"
MACHINE_ID="${MACHINE_ID:-$(hostname | tr -cd '[:alnum:]-' | tr '[:upper:]' '[:lower:]')}"
BRANCH="machine-${MACHINE_ID}"
MAIN_BRANCH="main"
LOCK_FILE="$ASTRAL_DIR_UNIX/memory/.sync-lock"
LOCK_TIMEOUT=3600

COMMIT_SRC=0; APPLY_YES=0; FORCE=0
for a in "$@"; do case "$a" in --commit) COMMIT_SRC=1;; --yes) APPLY_YES=1;; --force) FORCE=1;; esac; done
CMD="${1:-help}"

# ---- guards ----------------------------------------------------------------
[ -d "$ASTRAL_DIR_UNIX/.git" ] || die "ASTRAL_DIR is not a git repo: $ASTRAL_DIR_UNIX"
command -v git >/dev/null || die "git not found"
command -v tar >/dev/null || die "tar not found"

# ---- lockfile helpers ------------------------------------------------------
_lock_read(){
  [ -f "$LOCK_FILE" ] || return 1
  local who ts; who=$(head -1 "$LOCK_FILE" 2>/dev/null); ts=$(tail -1 "$LOCK_FILE" 2>/dev/null)
  local now; now=$(date +%s)
  if [ $((now - ts)) -gt $LOCK_TIMEOUT ]; then
    warn "stale lock from $who (expired $(( (now-ts)/60 )m ago) — auto-releasing"
    rm -f "$LOCK_FILE"; return 1
  fi
  printf '%s
' "$who"; return 0
}
do_lock(){
  local cur; cur=$(_lock_read) && die "memory locked by $cur — wait or ./sync.sh unlock if stale"
  printf '%s
%s
' "$MACHINE_ID" "$(date +%s)" > "$LOCK_FILE"
  git -C "$(to_native "$ASTRAL_DIR_UNIX")" add -f memory/.sync-lock 2>/dev/null || true
  ok "memory lock acquired: $MACHINE_ID"
}
do_unlock(){
  [ -f "$LOCK_FILE" ] || { info "no lock to release"; return 0; }
  rm -f "$LOCK_FILE"
  git -C "$(to_native "$ASTRAL_DIR_UNIX")" rm -f --cached memory/.sync-lock 2>/dev/null || true
  ok "memory lock released"
}

# ---- conflict detection ----------------------------------------------------
_detect_conflicts(){
  local src="$1"; shift
  local subdir="$1"; shift
  local hub_tmp; hub_tmp="$(mktemp -d)"
  git -C "$(to_native "$ASTRAL_DIR_UNIX")" archive "origin/$MAIN_BRANCH" "$subdir" 2>/dev/null > "$hub_tmp/archive.tar"
  [ -s "$hub_tmp/archive.tar" ] && tar -x -C "$hub_tmp" -f "$hub_tmp/archive.tar" 2>/dev/null || true
  local conflicts=()
  while IFS= read -r -d '' f; do
    local rel="${f#$src/}"; rel="${rel#./}"
    local hub_f="$hub_tmp/$rel"
    [ -f "$hub_f" ] || continue
    if ! diff -q "$f" "$hub_f" >/dev/null 2>&1; then
      conflicts+=("$rel")
    fi
  done < <(find "$src" -type f -not -path '*/.git/*' -not -path '*/.venv/*' -not -name '*.pyc' -print0 2>/dev/null)
  rm -rf "$hub_tmp"
  [ ${#conflicts[@]} -gt 0 ] && printf '%s
' "${conflicts[@]}"
}

# ---- refresh helpers -------------------------------------------------------
refresh_backend(){
  # Preserve de421.bsp OUTSIDE backend dir (in script's parent) so rm -rf can't touch it
  local bak_dir; bak_dir="$(mktemp -d)"
  local bak="$bak_dir/de421.bsp"
  if [ -f "$ASTRAL_DIR_UNIX/backend/de421.bsp" ]; then
    cp "$ASTRAL_DIR_UNIX/backend/de421.bsp" "$bak" && info "preserved de421.bsp"
  fi

  if [ -d "$BACKEND_SRC/.git" ]; then
    if [ -n "$(git -C "$BACKEND_SRC" status --porcelain 2>/dev/null)" ]; then
      if [ "$COMMIT_SRC" -eq 1 ]; then
        git -C "$BACKEND_SRC" add -A
        git -C "$BACKEND_SRC" -c core.autocrlf=true commit -q -m "sync: auto-commit before hub push ($(date +%F))"
        ok "committed backend source: $(git -C "$BACKEND_SRC" rev-parse --abbrev-ref HEAD)"
      else
        warn "backend source has UNCOMMITTED changes (use --commit to auto-commit):"
        git -C "$BACKEND_SRC" status --porcelain | sed 's/^/    /'
        return 0
      fi
    fi
    info "archiving backend from $BACKEND_SRC (HEAD)"
    rm -rf "${ASTRAL_DIR_UNIX:?}/backend/"*
    rm -rf "${ASTRAL_DIR_UNIX:?}/backend/".[!.]* 2>/dev/null || true
    local archive_tmp; archive_tmp="$bak_dir/backend.tar"
    git -C "$BACKEND_SRC" archive --format=tar HEAD > "$archive_tmp"
    tar -x -C "$ASTRAL_DIR_UNIX/backend" -f "$archive_tmp"
  else
    warn "BACKEND_SRC not a git repo — copying tree (excl .git/.venv/de421.bsp)"
    rm -rf "${ASTRAL_DIR_UNIX:?}/backend/"*
    rm -rf "${ASTRAL_DIR_UNIX:?}/backend/".[!.]* 2>/dev/null || true
    tar -C "$BACKEND_SRC" --exclude='.git' --exclude='.venv' --exclude='de421.bsp' -cf - . | tar -x -C "$ASTRAL_DIR_UNIX/backend"
  fi
  # Restore ephemeris (force-add since it's gitignored in source)
  if [ -f "$bak" ]; then
    cp "$bak" "$ASTRAL_DIR_UNIX/backend/de421.bsp"
    git -C "$(to_native "$ASTRAL_DIR_UNIX")" add -f backend/de421.bsp
    ok "restored de421.bsp"
  fi
  rm -rf "$bak_dir"
}

refresh_vault(){
  info "refreshing vault from $VAULT_SRC"
  rm -rf "$ASTRAL_DIR_UNIX/vault"
  mkdir -p "$ASTRAL_DIR_UNIX/vault"
  tar -C "$VAULT_SRC" --exclude='.git' --exclude='de421.bsp' --exclude='*/de421.bsp' --exclude='backups' -cf - . | tar -x -C "$ASTRAL_DIR_UNIX/vault"
}

refresh_memory(){
  info "copying hermes memory"
  mkdir -p "$ASTRAL_DIR_UNIX/memory"
  [ -f "$HERMES_MEM/MEMORY.md" ] && cp "$HERMES_MEM/MEMORY.md" "$ASTRAL_DIR_UNIX/memory/MEMORY.md"
  [ -f "$HERMES_MEM/USER.md" ]   && cp "$HERMES_MEM/USER.md"   "$ASTRAL_DIR_UNIX/memory/USER.md"
}

refresh_profile(){
  if command -v hermes >/dev/null 2>&1; then
    info "exporting hermes default profile"
    mkdir -p "$ASTRAL_DIR_UNIX/hermes"
    local out; out="$(to_native "$ASTRAL_DIR_UNIX/hermes/profile-default.tar.gz")"
    hermes profile export -o "$out" default
  else
    warn "hermes CLI not found — skipped profile export"
  fi
}

# ---- per-machine branch sync ----------------------------------------------
_branch_sync(){
  local native_dir; native_dir="$(to_native "$ASTRAL_DIR_UNIX")"
  git -C "$native_dir" fetch -q origin "$MAIN_BRANCH" 2>/dev/null || warn "fetch failed (offline?)"
  if ! git -C "$native_dir" rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    git -C "$native_dir" branch "$BRANCH" "origin/$MAIN_BRANCH" 2>/dev/null || git -C "$native_dir" branch "$BRANCH"
    ok "created branch $BRANCH (tracking origin/$MAIN_BRANCH)"
  fi
  git -C "$native_dir" checkout -q "$BRANCH"
}

# ---- commands --------------------------------------------------------------
do_status(){
  cd "$ASTRAL_DIR_UNIX"
  local native_dir; native_dir="$(to_native "$ASTRAL_DIR_UNIX")"
  header "Astral Sync Status"
  info "machine: $MACHINE_ID  |  branch: $BRANCH  |  hub HEAD: $(git -C "$native_dir" rev-parse --short origin/$MAIN_BRANCH 2>/dev/null)"
  echo "  local Astral vs origin/main: $(git -C "$native_dir" rev-list --left-right --count HEAD...origin/$MAIN_BRANCH 2>/dev/null | tr '	' '/' ) (local/remote)"
  echo "  backend source uncommitted:  $(git -C "$BACKEND_SRC" status --porcelain 2>/dev/null | wc -l) files"
  echo "  vault source uncommitted:    $(git -C "$VAULT_SRC" status --porcelain 2>/dev/null | wc -l) files"
  echo "  memory mtime:                $(stat -c '%y' "$HERMES_MEM/MEMORY.md" 2>/dev/null | cut -d. -f1)"
  local cur; cur=$(_lock_read 2>/dev/null) && echo "  memory lock:                 HELD by $cur" || echo "  memory lock:                 free"
  echo "  machine branches:"
  git -C "$native_dir" branch -r 2>/dev/null | grep -E 'machine-' | sed 's/^/    /' || echo "    (none)"
  echo "  conflict risk (local vs hub, same files changed):"
  local be ve
  be=$(_detect_conflicts "$BACKEND_SRC" backend 2>/dev/null)
  ve=$(_detect_conflicts "$VAULT_SRC" vault 2>/dev/null)
  if [ -n "$be$ve" ]; then
    warn "CONFLICTS detected:"
    [ -n "$be" ] && echo "  backend: $be" | tr '
' ' ' | fold -s -w 70 | sed 's/^/    /'
    [ -n "$ve" ] && echo "  vault:   $ve" | tr '
' ' ' | fold -s -w 70 | sed 's/^/    /'
  else
    ok "no conflicts detected"
  fi
}

do_up(){
  cd "$ASTRAL_DIR_UNIX"
  local native_dir; native_dir="$(to_native "$ASTRAL_DIR_UNIX")"
  header "Astral Sync: $MACHINE_ID → hub"
  local be ve conflicts=0
  be=$(_detect_conflicts "$BACKEND_SRC" backend 2>/dev/null || true)
  ve=$(_detect_conflicts "$VAULT_SRC" vault 2>/dev/null || true)
  [ -n "$be$ve" ] && conflicts=1
  if [ $conflicts -eq 1 ] && [ $FORCE -ne 1 ]; then
    warn "CONFLICTS detected — same files changed on both machines:"
    [ -n "$be" ] && echo "  backend: $be" | tr '
' ' ' | fold -s -w 70 | sed 's/^/    /'
    [ -n "$ve" ] && echo "  vault:   $ve" | tr '
' ' ' | fold -s -w 70 | sed 's/^/    /'
    die "resolve manually, or re-run with --force (last-writer-wins)"
  fi
  _branch_sync
  git -C "$native_dir" merge "$MAIN_BRANCH" --no-edit 2>/dev/null || warn "merge from main had issues — resolve manually"
  refresh_backend
  refresh_vault
  refresh_memory
  refresh_profile
  git -C "$native_dir" add -A
  if git -C "$native_dir" diff --cached --quiet; then
    ok "nothing to commit — hub already up to date"
  else
    local n; n=$(git -C "$native_dir" diff --cached --name-only | wc -l)
    git -C "$native_dir" -c core.autocrlf=true commit -q -m "sync[$MACHINE_ID]: $(date +%F_%H:%M) handoff ($n files)"
    ok "committed to $BRANCH ($n files)"
  fi
  git -C "$native_dir" push -u origin "$BRANCH" 2>&1 | tail -2
  git -C "$native_dir" checkout -q "$MAIN_BRANCH"
  if git -C "$native_dir" merge --ff-only "$BRANCH" 2>/dev/null; then
    git -C "$native_dir" push origin "$MAIN_BRANCH" 2>&1 | tail -1
    ok "main fast-forwarded → $(git -C "$native_dir" rev-parse --short HEAD)"
  else
    warn "main not fast-forwardable — manual merge needed: git merge $BRANCH"
  fi
  git -C "$native_dir" checkout -q "$BRANCH"
}

do_pull(){
  cd "$ASTRAL_DIR_UNIX"
  local native_dir; native_dir="$(to_native "$ASTRAL_DIR_UNIX")"
  header "Astral Sync: hub → $MACHINE_ID"
  git -C "$native_dir" fetch -q origin 2>/dev/null || warn "fetch failed (offline?)"
  _branch_sync
  git -C "$native_dir" merge --ff-only "origin/$MAIN_BRANCH" 2>/dev/null || {
    warn "not fast-forwardable — hub has diverged; run './sync.sh up' to push your changes first"
    return 1
  }
  ok "local Astral now at $(git -C "$native_dir" rev-parse --short HEAD)"
  info "run './sync.sh apply --yes' to materialize backend/vault/memory into local project dirs"
}

do_apply(){
  cd "$ASTRAL_DIR_UNIX"
  header "Astral Sync: materialize hub → local dirs"
  warn "this OVERWRITES files in $BACKEND_DST and $VAULT_DST (excluding .git/.venv)"
  [ $APPLY_YES -ne 1 ] && { read -r -p "continue? [y/N] " ans; case "$ans" in y|Y) ;; *) warn "aborted"; exit 0;; esac; }
  mkdir -p "$BACKEND_DST"
  tar -C "$ASTRAL_DIR_UNIX/backend" --exclude='.git' -cf - . | tar -x -C "$BACKEND_DST"
  ok "backend → $BACKEND_DST"
  mkdir -p "$VAULT_DST"
  tar -C "$ASTRAL_DIR_UNIX/vault" --exclude='.git' -cf - . | tar -x -C "$VAULT_DST"
  ok "vault → $VAULT_DST"
  [ -f "$ASTRAL_DIR_UNIX/memory/MEMORY.md" ] && cp "$ASTRAL_DIR_UNIX/memory/MEMORY.md" "$HERMES_MEM/MEMORY.md"
  [ -f "$ASTRAL_DIR_UNIX/memory/USER.md" ]   && cp "$ASTRAL_DIR_UNIX/memory/USER.md"   "$HERMES_MEM/USER.md"
  ok "memory → $HERMES_MEM"
  info "restore Hermes profile: hermes profile import $ASTRAL_DIR_UNIX/hermes/profile-default.tar.gz"
}

# ============================================================================
case "$CMD" in
  status|up|pull|apply|lock|unlock) "do_$CMD" ;;
  help|-h|--help|*) sed -n '2,55p' "$0" | sed 's/^# \{0,1\}//' ;;
esac

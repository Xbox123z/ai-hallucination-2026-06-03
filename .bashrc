# ── Git Bash IME Fix: winpty wraps claude with proper Windows console ──
# Git Bash (MINGW64) loses CJK IME in raw mode. winpty provides full IME.
# Using explicit path to avoid recursion with the function name.
claude() {
    if [ $# -gt 0 ]; then
        winpty /c/Users/Administrator/.local/bin/claude -p "$*"
    else
        winpty /c/Users/Administrator/.local/bin/claude
    fi
}

# ── mistral → vibe (DeepSeek backend) ──
export DEEPSEEK_API_KEY='sk-718f309ebab346b5a29e4d40b035e32c'
mistral() {
    cd ~/mistral-workspace
    python -c "
import ctypes, os
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW('Mistral')
from vibe.cli.entrypoint import main
main()
" "$@"
}

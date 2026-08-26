from pathlib import Path

p = Path('src/SumatraPDF.cpp')
s = p.read_text(encoding='utf-8')
old = '''    // go fullscreen before the first paint so the user doesn't see the
    // intermediate maximized window (EnterFullScreen requires a visible
    // window, so it can't happen before ShowWindow above)
    if (WIN_STATE_FULLSCREEN == windowState) {
        EnterFullScreen(win);
    }
'''
new = '''    // Modern fork: every newly shown reader window starts in windowed
    // borderless reading mode. This preserves the current window rectangle
    // and taskbar instead of using true fullscreen.
    if (!win->isBorderlessWindow && !gPluginMode) {
        ToggleBorderlessWindow(win);
    }
'''
if old not in s:
    raise SystemExit('ShowMainWindow startup fullscreen block not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8', newline='')

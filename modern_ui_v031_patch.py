from pathlib import Path

p = Path("src/gui/win/TabsCtrl.cpp")
s = p.read_text(encoding="utf-8")
old = '''    // Edge-style tab card: leave a small gutter between tabs and round
    // the painted surface without changing hit-testing or drag geometry.
    Rect tabSurface = r;
    int gapX = DpiScale(2);
    int gapTop = DpiScale(3);
    tabSurface.x += gapX;
    tabSurface.dx = std::max(0, tabSurface.dx - (gapX * 2));
    tabSurface.y += gapTop;
    tabSurface.dy = std::max(0, tabSurface.dy - gapTop);
    gfx->FillRoundedRect(tabSurface, DpiScale(IsSelected() ? 11 : 9), tabBgCol);
'''
new = '''    // Browser-style tab silhouette. An active browser tab is not a floating
    // pill: only its top is rounded and its bottom joins the content surface.
    // Hovered/inactive tabs can remain fully rounded cards.
    Rect tabSurface = r;
    int gapX = DpiScale(2);
    int gapTop = DpiScale(3);
    tabSurface.x += gapX;
    tabSurface.dx = std::max(0, tabSurface.dx - (gapX * 2));
    tabSurface.y += gapTop;
    tabSurface.dy = std::max(0, tabSurface.dy - gapTop);
    if (IsSelected()) {
        int radius = DpiScale(9);
        gfx->FillRoundedRect(tabSurface, radius, tabBgCol);
        // Square the two lower corners so the selected tab visually flows into
        // the toolbar/content row instead of looking like a detached capsule.
        Rect lower = tabSurface;
        lower.y = std::max(tabSurface.y, tabSurface.Bottom() - radius);
        lower.dy = std::max(0, tabSurface.Bottom() - lower.y);
        gfx->FillRect(lower, tabBgCol);
    } else {
        gfx->FillRoundedRect(tabSurface, DpiScale(8), tabBgCol);
    }
'''
if old not in s:
    raise SystemExit("expected tab paint block not found")
p.write_text(s.replace(old, new, 1), encoding="utf-8", newline="")

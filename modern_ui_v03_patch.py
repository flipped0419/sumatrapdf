from pathlib import Path


def replace_once(path: str, old: str, new: str):
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit(f"expected text not found in {path}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8", newline="")


# Edge-like tab hierarchy: gray strip, selected tab on a light surface.
replace_once(
    "src/gui/win/TabsCtrl.cpp",
    """static Color TabTextColorForBackground(Color text, Color tabBg) {
    if (abs((int)GetLightness(text) - (int)GetLightness(tabBg)) >= 80) {
        return text;
    }
    return IsLightColor(tabBg) ? kColBlack : kColWhite;
}
""",
    """static Color TabTextColorForBackground(Color text, Color tabBg) {
    if (abs((int)GetLightness(text) - (int)GetLightness(tabBg)) >= 80) {
        return text;
    }
    return IsLightColor(tabBg) ? kColBlack : kColWhite;
}

// Edge uses a tinted tab strip with the selected tab sitting on a lighter
// document surface. Sumatra's Light theme otherwise gives both the host and
// selected tab the same white control color, hiding the rounded silhouette.
static Color ModernTabStripBg(Color selectedBg) {
    if (IsLightColor(selectedBg)) {
        return MkRgb(0xE9, 0xEA, 0xEC);
    }
    return AccentColor(selectedBg, 18);
}
""",
)

replace_once(
    "src/gui/win/TabsCtrl.cpp",
    """    if (isSelected) {
        return selected;
    }
    return AccentColor(selected, isUnderMouse ? 35 : 25);
}""",
    """    if (isSelected) {
        return selected;
    }
    Color strip = ModernTabStripBg(selected);
    if (isUnderMouse) {
        return IsLightColor(selected) ? MkRgb(0xF3, 0xF3, 0xF3) : AccentColor(selected, 28);
    }
    // Default unselected tabs blend into the strip, like Edge. Hovering creates
    // a subtle card, while the selected tab remains the bright document surface.
    return strip;
}""",
)

replace_once(
    "src/gui/win/TabsCtrl.cpp",
    """    Rect tabSurface = r;
    int gap = DpiScale(2);
    tabSurface.x += gap;
    tabSurface.dx = std::max(0, tabSurface.dx - (gap * 2));
    tabSurface.y += gap;
    tabSurface.dy = std::max(0, tabSurface.dy - gap);
    gfx->FillRoundedRect(tabSurface, DpiScale(IsSelected() ? 10 : 8), tabBgCol);""",
    """    Rect tabSurface = r;
    int gapX = DpiScale(2);
    int gapTop = DpiScale(3);
    tabSurface.x += gapX;
    tabSurface.dx = std::max(0, tabSurface.dx - (gapX * 2));
    tabSurface.y += gapTop;
    tabSurface.dy = std::max(0, tabSurface.dy - gapTop);
    gfx->FillRoundedRect(tabSurface, DpiScale(IsSelected() ? 11 : 9), tabBgCol);""",
)

# This indentation uniquely identifies the host WM_PAINT background, not the
# drag bitmap background elsewhere in the same file.
replace_once(
    "src/gui/win/TabsCtrl.cpp",
    "            Color bgCol = GetColor(kColTabBg);",
    "            Color bgCol = ModernTabStripBg(GetColor(kColTabBg));",
)

# Restore true fullscreen behavior and give windowed borderless its own toolbar mode.
replace_once(
    "src/Toolbar.cpp",
    """static int ToolbarModeForWindow(MainWindow* win) {
    if (win->isFullScreen) {
        int mode = FullscreenToolbarModeFromPrefs();
        // Modern fork: fullscreen doubles as a distraction-free reading mode.
        // Preserve an explicit pinned toolbar, otherwise reveal it only when
        // the pointer touches the top edge instead of hiding it permanently.
        return mode == kToolbarShow ? kToolbarShow : kToolbarOverlay;
    }
    return ToolbarModeFromPrefs();
}""",
    """static int ToolbarModeForWindow(MainWindow* win) {
    if (win->isBorderlessWindow) {
        // Windowed borderless reading keeps the window rect/taskbar, while the
        // main toolbar floats over the page and is revealed at the top edge.
        return kToolbarOverlay;
    }
    if (win->isFullScreen) {
        return FullscreenToolbarModeFromPrefs();
    }
    return ToolbarModeFromPrefs();
}""",
)

replace_once(
    "src/MainWindow.h",
    """    bool isFullScreen = false;
    // chrome-less always-on-top preview from Explorer Space (issue #2568)""",
    """    bool isFullScreen = false;
    // Windowed frameless reading mode. Unlike fullscreen this preserves the
    // current window size/position and keeps the Windows taskbar available.
    bool isBorderlessWindow = false;
    long borderlessWindowStyle = 0;
    // chrome-less always-on-top preview from Explorer Space (issue #2568)""",
)

replace_once(
    "src/SumatraPDF.h",
    "void ToggleFullScreen(MainWindow* win, bool presentation = false);",
    """void ToggleFullScreen(MainWindow* win, bool presentation = false);
void ToggleBorderlessWindow(MainWindow* win);""",
)

# Add at the command tail so existing command ids stay stable.
replace_once(
    "cmd/gen-commands.ts",
    """    \"CmdApplyRedactions\", \"Apply Redactions\",
    \"CmdNone\", \"Do nothing\",""",
    """    \"CmdApplyRedactions\", \"Apply Redactions\",
    \"CmdToggleBorderlessWindow\", \"Toggle Borderless Window\",
    \"CmdNone\", \"Do nothing\",""",
)

# F11 toggles the requested windowed mode. Existing Ctrl+Shift+L and F keep
# their actual fullscreen bindings.
replace_once(
    "src/Accelerators.cpp",
    "    {FVIRTKEY, VK_F11, CmdToggleFullscreen},",
    "    {FVIRTKEY, VK_F11, CmdToggleBorderlessWindow},",
)

# Borderless mode must not reserve either custom caption or a separate tab row.
replace_once(
    "src/SumatraPDF.cpp",
    """    bool showCaption = !win->presentation && !win->isFullScreen && win->tabsInTitlebar;
    bool showingMenuBar = IsShowingMenuBarRebar(win);
    bool showTabsBar = !win->presentation && !win->isFullScreen && !win->tabsInTitlebar && win->tabsVisible;""",
    """    bool showCaption =
        !win->presentation && !win->isFullScreen && !win->isBorderlessWindow && win->tabsInTitlebar;
    bool showingMenuBar = IsShowingMenuBarRebar(win);
    bool showTabsBar = !win->presentation && !win->isFullScreen && !win->isBorderlessWindow &&
                       !win->tabsInTitlebar && win->tabsVisible;""",
)

# Hide the DWM border while the resizable WS_THICKFRAME remains present.
replace_once(
    "src/SumatraPDF.cpp",
    "    if (IsZoomed(win->hwndFrame) || win->isFullScreen || win->presentation) {",
    "    if (IsZoomed(win->hwndFrame) || win->isFullScreen || win->isBorderlessWindow || win->presentation) {",
)

# Settings reload must not reattach the menubar while borderless.
replace_once(
    "src/SumatraPDF.cpp",
    "    if (!win->presentation && !win->isFullScreen && IsMenubarVisible()) {",
    "    if (!win->presentation && !win->isFullScreen && !win->isBorderlessWindow && IsMenubarVisible()) {",
)

replace_once(
    "src/Tabs.cpp",
    """void UpdateTabWidth(MainWindow* win) {
    int nTabs = win->TabCount();""",
    """void UpdateTabWidth(MainWindow* win) {
    if (win->isBorderlessWindow) {
        ShowTabBar(win, false);
        return;
    }
    int nTabs = win->TabCount();""",
)

# Windowed borderless implementation. It strips only WS_CAPTION, leaves
# WS_THICKFRAME for resizing, preserves the current outer rect, and restores the
# normal menu/tab/toolbar state on F11.
replace_once(
    "src/SumatraPDF.cpp",
    "void EnterFullScreen(MainWindow* win, bool presentation) {",
    """static void EnterBorderlessWindow(MainWindow* win) {
    if (!win || win->isBorderlessWindow || win->isFullScreen || win->presentation || gPluginMode) {
        return;
    }

    HWND hwnd = win->hwndFrame;
    win->borderlessWindowStyle = GetWindowLong(hwnd, GWL_STYLE);
    Rect rect = HwndWindowRect(hwnd);
    win->isBorderlessWindow = true;

    BeginFrameRedrawSuppression(win);
    SetMenu(hwnd, nullptr);
    DestroyMenuBarRebar(win);

    long ws = win->borderlessWindowStyle & ~WS_CAPTION;
    SetWindowLong(hwnd, GWL_STYLE, ws);
    if (!IsRunningOnWine()) {
        SetWindowRoundedCorners(hwnd, true);
    }
    SetWindowPos(hwnd, nullptr, rect.x, rect.y, rect.dx, rect.dy,
                 SWP_FRAMECHANGED | SWP_NOACTIVATE | SWP_NOZORDER);

    UpdateTabWidth(win);
    ShowOrHideToolbar(win);
    // Enter quietly. Existing top-edge tracking reveals the overlay on demand.
    win->toolbarOverlayShown = false;
    RelayoutFrame(win);
    PositionOverlayToolbar(win);
    UpdateWindowFrameBorderColor(win);
    EndFrameRedrawSuppression(win);
}

static void ExitBorderlessWindow(MainWindow* win) {
    if (!win || !win->isBorderlessWindow) {
        return;
    }

    HWND hwnd = win->hwndFrame;
    Rect rect = HwndWindowRect(hwnd);
    BeginFrameRedrawSuppression(win);
    win->isBorderlessWindow = false;

    SetWindowLong(hwnd, GWL_STYLE, win->borderlessWindowStyle);
    SetWindowPos(hwnd, nullptr, rect.x, rect.y, rect.dx, rect.dy,
                 SWP_FRAMECHANGED | SWP_NOACTIVATE | SWP_NOZORDER);
    if (!IsRunningOnWine()) {
        SetWindowRoundedCorners(hwnd, true);
    }

    RebuildMenuBarForWindow(win);
    UpdateTabWidth(win);
    ShowOrHideToolbar(win);
    RelayoutFrame(win);
    UpdateWindowFrameBorderColor(win);
    EndFrameRedrawSuppression(win);
}

void ToggleBorderlessWindow(MainWindow* win) {
    if (!win) {
        return;
    }
    if (win->isBorderlessWindow) {
        ExitBorderlessWindow(win);
    } else {
        EnterBorderlessWindow(win);
    }
}

void EnterFullScreen(MainWindow* win, bool presentation) {""",
)

replace_once(
    "src/SumatraPDF.cpp",
    """        case CmdToggleFullscreen:
            if (ShouldToggle(cmd, win->isFullScreen)) {
                ToggleFullScreen(win);
            }
            break;""",
    """        case CmdToggleFullscreen:
            if (ShouldToggle(cmd, win->isFullScreen)) {
                ToggleFullScreen(win);
            }
            break;

        case CmdToggleBorderlessWindow:
            if (ShouldToggle(cmd, win->isBorderlessWindow)) {
                ToggleBorderlessWindow(win);
            }
            break;""",
)

# A narrow top band is draggable while chrome is hidden. The first 5px remain
# the resize hit target; when the floating toolbar is visible its child HWND
# receives button input normally.
replace_once(
    "src/SumatraPDF.cpp",
    """            {
                Point pt{x, y};
                Rect rClient = HwndMapRectToWindow(HwndClientRect(hwnd), hwnd, HWND_DESKTOP);""",
    """            if (win->isBorderlessWindow && !IsZoomed(hwnd)) {
                int fromTop = y - wrc.y;
                int dragBand = DpiScale(22);
                if (fromTop > kFrameResizeHitTest && fromTop < dragBand) {
                    *callDef = false;
                    return HTCAPTION;
                }
            }

            {
                Point pt{x, y};
                Rect rClient = HwndMapRectToWindow(HwndClientRect(hwnd), hwnd, HWND_DESKTOP);""",
)

print("modern UI v0.3 source patch applied")

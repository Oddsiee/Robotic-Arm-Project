# Python/dashboard.py
#
# Dashboard UI v3 — Apple Human Interface inspired.
#
# Design language:
#   • iOS dark mode palette (#1C1C1E base, #2C2C2E cards, #3A3A3C elevated)
#   • San Francisco style: DUPLEX for headings, SIMPLEX for body
#   • Rounded corner cards with subtle shadows (simulated)
#   • Generous whitespace, thin separators, pill-shaped status badges
#   • Color-coded semantic accents (blue=info, green=ok, orange=warn, red=err)
#
# Layout:
#   ┌──────────────────────────────────────────────────────────────────┐
#   │  Robotic Arm                        ● ARMED           28.5 fps  │
#   ├────────────────────────────────────┬─────────────────────────────┤
#   │                                    │  ┌   ROI Preview  ┐        │
#   │                                    │  └────────────────┘        │
#   │         CAMERA FEED                │  ┌   Detection    ┐        │
#   │                                    │  │ ○ Color  BLACK │        │
#   │                                    │  │ ◉ 234, 156    │        │
#   │                                    │  │ ⟳ Locked      │        │
#   │                                    │  └────────────────┘        │
#   │                                    │  ┌   IK Solver    ┐        │
#   │                                    │  │ Base    85.3° │        │
#   │                                    │  │ Shldr  120.1° │        │
#   │                                    │  │ Elbow   45.7° │        │
#   │                                    │  └────────────────┘        │
#   │                                    │  ┌   Serial       ┐        │
#   │                                    │  │ ● Connected   │        │
#   │                                    │  │ → WH          │        │
#   │                                    │  └────────────────┘        │
#   ├────────────────────────────────────┴─────────────────────────────┤
#   │  14:32:01  Reference captured                                    │
#   │  14:32:03  Object BLACK locked — processing                      │
#   │  14:32:04  Sent WH 85.3° / 120.1° / 45.7°                       │
#   │  14:32:06  Arduino acknowledged                                  │
#   ├──────────────────────────────────────────────────────────────────┤
#   │  q Quit    r Set Ref    m Mask    p Print       Auto Mode · ON  │
#   └──────────────────────────────────────────────────────────────────┘

import cv2
import numpy as np
from collections import deque
from datetime import datetime

from config import WindowConfig, DashboardConfig


class Dashboard:
    """Apple HIG-inspired single-window compositor for main.py."""

    # ── Typography ────────────────────────────────────────────────
    # DUPLEX = rounder, more SF-like for headings
    # SIMPLEX = cleaner for body/mono text
    FONT_HEADING = cv2.FONT_HERSHEY_DUPLEX
    FONT_BODY    = cv2.FONT_HERSHEY_SIMPLEX

    # ── iOS Dark Mode Palette ─────────────────────────────────────
    BG_ROOT      = (28,  28,  30)   # #1C1C1E  system background
    BG_CARD      = (44,  44,  46)   # #2C2C2E  card / grouped bg
    BG_ELEVATED  = (58,  58,  60)   # #3A3A3C  elevated card
    BG_HEADER    = (32,  32,  34)   # #202022  slightly darker header
    BG_LOG       = (22,  22,  24)   # #161618  log section

    # iOS System Colors
    BLUE         = (10,  132, 255)  # #0A84FF  system blue
    GREEN        = (48,  209, 88)   # #30D158  system green
    ORANGE       = (255, 159, 10)   # #FF9F0A  system orange
    RED          = (255, 69,  58)   # #FF453A  system red
    PURPLE       = (191, 90,  242)  # #BF5AF2  system purple

    # iOS Labels (semantic)
    LABEL        = (242, 242, 247)  # primary label (near-white)
    SECONDARY    = (174, 174, 178)  # #AEAEB2  secondary label
    TERTIARY     = (99,  99,  102)  # #636366  tertiary label
    SEPARATOR    = (56,  56,  58)   # #38383A  thin separators

    # Semantic color registry
    LEVEL_COLORS = {
        "REF":  BLUE,
        "LOCK": GREEN,
        "SEND": ORANGE,
        "ACK":  GREEN,
        "ERR":  RED,
        "SKIP": ORANGE,
        "UI":   TERTIARY,
        "INFO": SECONDARY,
    }

    OBJECT_COLORS = {
        "BLACK":   (209, 209, 214),
        "WHITE":   (255, 255, 255),
        "UNKNOWN": (255, 159, 10),
    }

    # ── Constructor ───────────────────────────────────────────────
    def __init__(self):
        self.log_buffer = deque(maxlen=DashboardConfig.LOG_MAX_LINES)
        self.show_mask = False
        self._tick = 0          # frame counter for subtle animations

        self._state = {
            "armed":      False,
            "processing": False,
            "fps":        0.0,
            "selected":   None,
            "locked":     False,
            "remaining":  None,
            "angles":     None,
            "serial_ok":  True,
            "last_cmd":   "",
        }

    # ── Public API ────────────────────────────────────────────────
    def update_state(self, **kwargs):
        self._state.update(kwargs)

    def log(self, message, level="INFO"):
        message = str(message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        self.log_buffer.append((timestamp, level, message))

    def toggle_mask(self):
        self.show_mask = not self.show_mask
        self.log(f"Mask debug: {'ON' if self.show_mask else 'OFF'}", "UI")

    # ── Drawing Utilities ─────────────────────────────────────────

    def _resize_to_width(self, img, w):
        h = img.shape[0]
        if img.shape[1] == w:
            return img
        s = w / img.shape[1]
        return cv2.resize(img, (w, max(1, int(h * s))))

    def _rounded_rect(self, canvas, x, y, w, h, r, color, fill=True):
        """Draw a rounded rectangle. r=radius, fill=True for filled."""
        if r > min(w, h) // 2:
            r = min(w, h) // 2
        if r < 1:
            r = 1
        t = -1 if fill else 1
        # Main body
        cv2.rectangle(canvas, (x + r, y), (x + w - r, y + h), color, t)
        cv2.rectangle(canvas, (x, y + r), (x + w, y + h - r), color, t)
        # Four corner circles
        cv2.ellipse(canvas, (x + r, y + r), (r, r), 180, 0, 90, color, t)
        cv2.ellipse(canvas, (x + w - r - 1, y + r), (r, r), 270, 0, 90, color, t)
        cv2.ellipse(canvas, (x + r, y + h - r - 1), (r, r), 90, 0, 90, color, t)
        cv2.ellipse(canvas, (x + w - r - 1, y + h - r - 1), (r, r), 0, 0, 90, color, t)

    def _pill(self, canvas, x, y, w, h, color, fill=True):
        """Pill-shaped rounded rect (fully rounded ends)."""
        r = h // 2
        self._rounded_rect(canvas, x, y, w, h, r, color, fill)

    def _text(self, canvas, text, x, y, color, font=None, scale=0.5,
              thickness=1, align="left"):
        font = font or self.FONT_BODY
        if align == "right":
            (tw, _), _ = cv2.getTextSize(text, font, scale, thickness)
            x -= tw
        elif align == "center":
            (tw, _), _ = cv2.getTextSize(text, font, scale, thickness)
            x -= tw // 2
        cv2.putText(canvas, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

    def _text_size(self, text, font=None, scale=0.5, thickness=1):
        font = font or self.FONT_BODY
        return cv2.getTextSize(text, font, scale, thickness)[0]

    def _hline(self, canvas, y, color, x0=0, x1=None):
        if x1 is None:
            x1 = canvas.shape[1]
        cv2.line(canvas, (x0, y), (x1, y), color, 1)

    # ── Panel: Header ─────────────────────────────────────────────

    def _make_header(self, width):
        h = 44
        header = np.full((h, width, 3), self.BG_HEADER, dtype=np.uint8)

        # Title — DUPLEX, semibold feel
        self._text(header, "Robotic Arm", 16, 29, self.LABEL,
                   font=self.FONT_HEADING, scale=0.6, thickness=1)

        # FPS badge (right side, before status)
        fps = self._state["fps"]
        fps_str = f"{fps:.0f} fps"
        self._text(header, fps_str, width - 16, 29, self.TERTIARY,
                   scale=0.45, align="right")

        # Status pill (left of FPS)
        armed = self._state["armed"]
        processing = self._state["processing"]

        if processing:
            dot, label, dot_c = "⟳", "Processing", self.ORANGE
        elif armed:
            dot, label, dot_c = "●", "Armed", self.GREEN
        else:
            dot, label, dot_c = "●", "Idle", self.RED

        # Measure and position the pill
        pill_text = f" {dot}  {label}  "
        (tw, th), _ = cv2.getTextSize(pill_text, self.FONT_BODY, 0.42, 1)
        pill_w = tw + 12
        pill_h = 22
        pill_x = width - 16 - self._text_size(fps_str, scale=0.45)[0] - pill_w - 16
        pill_y = (h - pill_h) // 2

        self._pill(header, pill_x, pill_y, pill_w, pill_h, self.BG_ELEVATED, fill=True)
        self._text(header, f" {dot}  {label}  ", pill_x + 6, pill_y + 16,
                   dot_c, scale=0.42)

        # Bottom separator
        self._hline(header, h - 1, self.SEPARATOR)

        return header

    # ── Panel: Camera Feed ────────────────────────────────────────

    def _make_camera(self, frame, target_h):
        """Camera feed, resized & cropped to match right column height."""
        cw = DashboardConfig.CAMERA_DISPLAY_WIDTH
        img = self._resize_to_width(frame, cw)
        ih = img.shape[0]
        if ih < target_h:
            pad = np.full((target_h - ih, cw, 3), self.BG_ROOT, dtype=np.uint8)
            return np.vstack([img, pad])
        return img[:target_h] if ih > target_h else img

    # ── Panel: Sidebar Cards ──────────────────────────────────────

    def _card(self, title, rows, width, accent=None):
        """
        Build a single rounded card.

        Args:
            title: str header
            rows: list of (icon, label, value, value_color) tuples
            width: card width
            accent: optional accent color for left edge glow
        """
        inner_w = width - 24         # 12px padding each side
        row_h = 20
        pad_t, pad_b = 14, 12
        header_h = 18
        gap_title_body = 8

        n_rows = len(rows)
        body_h = n_rows * row_h
        card_h = pad_t + header_h + gap_title_body + body_h + pad_b

        card = np.full((card_h, width, 3), self.BG_CARD, dtype=np.uint8)

        # Draw filled rounded rect for the card body
        self._rounded_rect(card, 4, 4, width - 8, card_h - 8, 10,
                          self.BG_CARD, fill=True)

        # Left accent bar (if any)
        if accent:
            self._rounded_rect(card, 4, pad_t, 4, card_h - pad_t - pad_b, 2,
                              accent, fill=True)

        # Section title
        self._text(card, title.upper(), 16, pad_t + 13, self.TERTIARY,
                   scale=0.38, thickness=1)

        # Thin separator below title
        sep_y = pad_t + header_h + 4
        self._hline(card, sep_y, self.SEPARATOR, x0=16, x1=width - 16)

        # Data rows
        y = sep_y + gap_title_body + row_h - 4
        for icon, label, value, val_color in rows:
            # Icon + label (left)
            self._text(card, f"{icon}  {label}", 16, y, self.SECONDARY, scale=0.42)
            # Value (right)
            self._text(card, value, width - 16, y, val_color,
                       scale=0.42, align="right", thickness=1)
            y += row_h

        return card

    def _make_roi_preview(self, roi_frame, width):
        """ROI thumbnail with rounded corners & overlay label."""
        inner_w = width - 24
        roi = self._resize_to_width(roi_frame, inner_w)
        rh = roi.shape[0]
        pad_t, pad_b, label_h = 10, 8, 18

        panel_h = pad_t + label_h + rh + pad_b
        panel = np.full((panel_h, width, 3), self.BG_CARD, dtype=np.uint8)
        self._rounded_rect(panel, 4, 4, width - 8, panel_h - 8, 10,
                          self.BG_CARD, fill=True)

        self._text(panel, "CAMERA ROI", 16, pad_t + 13, self.TERTIARY,
                   scale=0.38)

        # Place ROI image (with subtle rounded border)
        img_y = pad_t + label_h + 4
        panel[img_y:img_y + rh, 12:12 + inner_w] = roi
        self._rounded_rect(panel, 11, img_y - 1, inner_w + 2, rh + 2, 6,
                          self.SEPARATOR, fill=False)

        return panel

    def _make_detection_card(self, width):
        selected = self._state.get("selected")
        locked   = self._state.get("locked", False)
        remaining = self._state.get("remaining")

        if selected is None:
            rows = [
                ("○", "Status", "No object", self.TERTIARY),
            ]
            accent = None
        else:
            clr = selected.get("color", "???")
            cx, cy = selected.get("centroid", (0, 0))
            val_c = self.OBJECT_COLORS.get(clr, self.LABEL)

            rows = [
                ("○", "Color",  clr,      val_c),
                ("◉", "Position", f"{cx}, {cy}", self.LABEL),
            ]

            if locked:
                rows.append(("⟳", "Lock", "Locked", self.GREEN))
                accent = self.GREEN
            elif remaining is not None:
                rows.append(("⟳", "Lock", f"{remaining:.1f}s", self.ORANGE))
                accent = self.ORANGE
            else:
                rows.append(("⟳", "Lock", "—", self.TERTIARY))
                accent = None

        return self._card("Detection", rows, width, accent)

    def _make_ik_card(self, width):
        angles = self._state.get("angles")

        if angles is None:
            rows = [("∠", "Status", "Idle", self.TERTIARY)]
            accent = None
        else:
            ba, sa, ea = angles
            rows = [
                ("∠", "Base",     f"{ba:.1f}°", self.LABEL),
                ("∠", "Shoulder", f"{sa:.1f}°", self.LABEL),
                ("∠", "Elbow",    f"{ea:.1f}°", self.LABEL),
            ]
            accent = self.BLUE

        return self._card("Inverse Kinematics", rows, width, accent)

    def _make_serial_card(self, width):
        serial_ok = self._state.get("serial_ok", True)
        last_cmd  = self._state.get("last_cmd", "")

        if serial_ok:
            status, s_color = "Connected", self.GREEN
            accent = self.GREEN
        else:
            status, s_color = "Disconnected", self.RED
            accent = self.RED

        cmd_display = last_cmd if last_cmd else "—"
        # Map color code to readable
        cmd_map = {"B": "BLACK", "W": "WHITE"}
        cmd_display = cmd_map.get(cmd_display, cmd_display)

        rows = [
            ("●", "Port",  status,      s_color),
            ("→", "Last",  cmd_display, self.LABEL),
        ]

        return self._card("Serial", rows, width, accent)

    def _make_mask_card(self, mask, width):
        inner_w = width - 24
        pad_t, pad_b, label_h = 10, 8, 18

        if mask is None:
            rh = 60
            img = np.full((rh, inner_w, 3), self.BG_CARD, dtype=np.uint8)
            self._text(img, "No mask data", inner_w // 2, rh // 2 + 5,
                       self.TERTIARY, scale=0.38, align="center")
        else:
            mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            img = self._resize_to_width(mask_bgr, inner_w)

        rh = img.shape[0]
        panel_h = pad_t + label_h + rh + pad_b
        panel = np.full((panel_h, width, 3), self.BG_CARD, dtype=np.uint8)
        self._rounded_rect(panel, 4, 4, width - 8, panel_h - 8, 10,
                          self.BG_CARD, fill=True)

        self._text(panel, "MASK DEBUG", 16, pad_t + 13, self.TERTIARY, scale=0.38)

        img_y = pad_t + label_h + 4
        panel[img_y:img_y + rh, 12:12 + inner_w] = img
        self._rounded_rect(panel, 11, img_y - 1, inner_w + 2, rh + 2, 6,
                          self.SEPARATOR, fill=False)

        return panel

    # ── Panel: Log ────────────────────────────────────────────────

    def _make_log(self, width):
        lh = DashboardConfig.LOG_LINE_HEIGHT
        n = DashboardConfig.LOG_MAX_LINES
        pad_t, pad_b = 12, 8
        header_h = 20

        total_h = header_h + pad_t + n * lh + pad_b
        panel = np.full((total_h, width, 3), self.BG_LOG, dtype=np.uint8)

        # Label + clear hint
        self._text(panel, "System Log", 16, 14, self.TERTIARY, scale=0.38)
        self._text(panel, f"{n} entries", width - 16, 14, self.TERTIARY,
                   scale=0.35, align="right")

        self._hline(panel, header_h - 1, self.SEPARATOR, x0=12, x1=width - 12)

        y = header_h + pad_t + lh - 4
        for ts, level, msg in self.log_buffer:
            # Timestamp — tertiary
            self._text(panel, ts, 16, y, self.TERTIARY, scale=0.35)

            # Level dot
            lc = self.LEVEL_COLORS.get(level, self.TERTIARY)
            self._text(panel, "●", 74, y, lc, scale=0.32)

            # Message — truncate to fit
            max_w = width - 180
            (tw, _), _ = cv2.getTextSize(msg, self.FONT_BODY, 0.38, 1)
            display = msg
            if tw > max_w:
                while tw > max_w and len(display) > 3:
                    display = display[:-1]
                    (tw, _), _ = cv2.getTextSize(display + "…", self.FONT_BODY, 0.38, 1)
                display += "…"

            self._text(panel, display, 92, y, self.SECONDARY, scale=0.38)

            y += lh

        return panel

    # ── Panel: Footer ─────────────────────────────────────────────

    def _make_footer(self, width):
        h = 28
        footer = np.full((h, width, 3), self.BG_HEADER, dtype=np.uint8)

        self._hline(footer, 0, self.SEPARATOR)

        # Keyboard shortcuts — SF-style key badges
        keys = [
            ("q", "Quit"),
            ("r", "Set Ref"),
            ("m", "Mask"),
            ("p", "Print"),
        ]
        x = 14
        for key, label in keys:
            # Key badge
            (kw, _), _ = cv2.getTextSize(key, self.FONT_BODY, 0.38, 1)
            badge_w = kw + 10
            badge_h = 18
            self._rounded_rect(footer, x, 5, badge_w, badge_h, 4, self.BG_ELEVATED, fill=True)
            self._text(footer, key, x + 5, 18, self.LABEL, scale=0.38)
            # Label
            self._text(footer, label, x + badge_w + 5, 18, self.TERTIARY, scale=0.35)
            x += badge_w + self._text_size(label, scale=0.35)[0] + 22

        # Auto-mode indicator (right side)
        armed = self._state.get("armed", False)
        mode_text = "Auto Mode  ·  ON" if armed else "Auto Mode  ·  OFF"
        mode_c = self.GREEN if armed else self.TERTIARY
        self._text(footer, mode_text, width - 14, 18, mode_c,
                   scale=0.38, align="right")

        return footer

    # ── Render ────────────────────────────────────────────────────

    def render(self, camera_frame, roi_frame, mask=None):
        """
        Compose the full Apple-style dashboard.

        Args:
            camera_frame: Full frame with all overlays pre-drawn.
            roi_frame: ROI crop with object overlays pre-drawn.
            mask: Optional debug mask (shown only when toggle ON).

        Returns:
            Composite ndarray for cv2.imshow().
        """
        self._tick += 1
        cw = DashboardConfig.CAMERA_DISPLAY_WIDTH
        sw = DashboardConfig.SIDE_PANEL_WIDTH
        total_w = cw + sw

        # 1. Header
        header = self._make_header(total_w)

        # 2. Sidebar (right column) — build first to know body height
        gap = 10
        sidebar_parts = []

        roi_card = self._make_roi_preview(roi_frame, sw)
        sidebar_parts.append(roi_card)

        det_card = self._make_detection_card(sw)
        sidebar_parts.append(det_card)

        ik_card = self._make_ik_card(sw)
        sidebar_parts.append(ik_card)

        ser_card = self._make_serial_card(sw)
        sidebar_parts.append(ser_card)

        if self.show_mask:
            mask_card = self._make_mask_card(mask, sw)
            sidebar_parts.append(mask_card)

        # Stack sidebar with gaps
        sidebar = sidebar_parts[0]
        for part in sidebar_parts[1:]:
            spacer = np.full((gap, sw, 3), self.BG_ROOT, dtype=np.uint8)
            sidebar = np.vstack([sidebar, spacer, part])

        body_h = sidebar.shape[0]

        # 3. Camera (left column) — match sidebar height
        camera_col = self._make_camera(camera_frame, body_h)

        # 4. Body row
        body = np.hstack([camera_col, sidebar])

        # 5. Log
        log = self._make_log(total_w)

        # 6. Footer
        footer = self._make_footer(total_w)

        # Assemble
        composite = np.vstack([header, body, log, footer])
        return composite

    def show(self, composite):
        cv2.imshow(WindowConfig.MAIN_WINDOW, composite)
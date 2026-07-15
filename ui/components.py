"""Reusable UI components: stat cards and a sortable device table."""
from __future__ import annotations

from typing import Callable, List, Optional, Tuple

import customtkinter as ctk

from scanner.device_info import Device


class StatCard(ctk.CTkFrame):
    """A compact metric card for the dashboard header."""

    def __init__(self, master, title: str, value: str = "-", **kwargs) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self._title = ctk.CTkLabel(
            self, text=title.upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#8b93a7",
        )
        self._title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))
        self._value = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=22, weight="bold"),
        )
        self._value.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

    def set_value(self, value: str) -> None:
        self._value.configure(text=value)


class DeviceTable(ctk.CTkFrame):
    """Sortable, filterable virtual table built on customtkinter widgets."""

    COLUMNS: List[Tuple[str, str, int]] = [
        ("ip", "IP Address", 140),
        ("mac", "MAC Address", 170),
        ("hostname", "Hostname", 220),
        ("vendor", "Vendor", 220),
        ("status", "Status", 90),
    ]

    def __init__(
        self,
        master,
        on_select: Optional[Callable[[Optional[Device]], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        self._devices: List[Device] = []
        self._filtered: List[Device] = []
        self._sort_key: str = "ip"
        self._sort_reverse: bool = False
        self._selected_index: Optional[int] = None
        self._row_widgets: List[ctk.CTkFrame] = []
        self._on_select = on_select

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._body = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self._body.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 1))
        for idx, (_, _, weight) in enumerate(self.COLUMNS):
            self._body.grid_columnconfigure(idx, weight=weight, uniform="cols")

        self._empty_label = ctk.CTkLabel(
            self._body,
            text="No devices yet. Click Scan to begin.",
            text_color="#8b93a7",
        )
        self._empty_label.grid(row=0, column=0, columnspan=len(self.COLUMNS), pady=40)

    # ---------- Header ----------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#1f2330")
        header.grid(row=0, column=0, sticky="ew")
        for idx, (key, label, weight) in enumerate(self.COLUMNS):
            header.grid_columnconfigure(idx, weight=weight, uniform="cols")
            btn = ctk.CTkButton(
                header,
                text=label + "  ↕",
                anchor="w",
                fg_color="transparent",
                text_color="#c7ccd9",
                hover_color="#2a2f3f",
                font=ctk.CTkFont(size=12, weight="bold"),
                height=36,
                command=lambda k=key: self.sort_by(k),
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(8 if idx == 0 else 0, 0))

    # ---------- Public API ----------
    def set_devices(self, devices: List[Device]) -> None:
        self._devices = list(devices)
        self.apply_filter("")

    def apply_filter(self, query: str) -> None:
        q = query.strip().lower()
        if not q:
            self._filtered = list(self._devices)
        else:
            self._filtered = [
                d for d in self._devices
                if q in d.ip.lower()
                or q in d.mac.lower()
                or q in d.hostname.lower()
                or q in d.vendor.lower()
            ]
        self._sort_apply()
        self._render()

    def sort_by(self, key: str) -> None:
        if self._sort_key == key:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_key = key
            self._sort_reverse = False
        self._sort_apply()
        self._render()

    def selected(self) -> Optional[Device]:
        if self._selected_index is None:
            return None
        if 0 <= self._selected_index < len(self._filtered):
            return self._filtered[self._selected_index]
        return None

    # ---------- Internals ----------
    def _sort_apply(self) -> None:
        def key_fn(dev: Device):
            val = getattr(dev, self._sort_key, "")
            if self._sort_key == "ip":
                try:
                    return tuple(int(p) for p in val.split("."))
                except ValueError:
                    return (0, 0, 0, 0)
            return (val or "").lower()

        self._filtered.sort(key=key_fn, reverse=self._sort_reverse)

    def _render(self) -> None:
        for w in self._row_widgets:
            w.destroy()
        self._row_widgets.clear()
        self._empty_label.grid_remove()
        self._selected_index = None
        if self._on_select:
            self._on_select(None)

        if not self._filtered:
            self._empty_label.grid()
            return

        for row_idx, device in enumerate(self._filtered):
            bg = "#181b25" if row_idx % 2 == 0 else "#1f2330"
            row = ctk.CTkFrame(self._body, fg_color=bg, corner_radius=6, height=34)
            row.grid(row=row_idx, column=0, columnspan=len(self.COLUMNS),
                     sticky="ew", padx=2, pady=1)
            for idx, (key, _, weight) in enumerate(self.COLUMNS):
                row.grid_columnconfigure(idx, weight=weight, uniform="cols")
                value = getattr(device, key, "")
                color = "#c7ccd9"
                if key == "status":
                    color = "#3ddc84" if value == "Active" else "#8b93a7"
                if key == "ip" and device.extra.get("role") == "gateway":
                    value = f"{value}  ⭑"
                lbl = ctk.CTkLabel(
                    row, text=value, anchor="w", text_color=color,
                    font=ctk.CTkFont(size=12),
                )
                lbl.grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=6)
                lbl.bind("<Button-1>", lambda _e, i=row_idx: self._select(i))
            row.bind("<Button-1>", lambda _e, i=row_idx: self._select(i))
            self._row_widgets.append(row)

    def _select(self, index: int) -> None:
        self._selected_index = index
        for i, row in enumerate(self._row_widgets):
            if i == index:
                row.configure(fg_color="#2f6feb")
            else:
                row.configure(fg_color="#181b25" if i % 2 == 0 else "#1f2330")
        if self._on_select:
            self._on_select(self.selected())

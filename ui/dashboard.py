"""Main dashboard window."""
from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from scanner import Device, NetworkScanner, ScanResult
from utils.exporter import Exporter
from utils.helpers import get_local_host_info, ping_host
from utils.logger import get_logger

from .components import DeviceTable, StatCard

logger = get_logger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Dashboard(ctk.CTk):
    """Top-level application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Network Scanner")
        self.geometry("1180x740")
        self.minsize(980, 620)
        self.configure(fg_color="#0f1117")

        self._scanner = NetworkScanner()
        self._result: Optional[ScanResult] = None
        self._selected: Optional[Device] = None
        self._scanning = False

        self._build_layout()
        self._refresh_host_info()

    # ---------- Layout ----------
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_stats()
        self._build_table()
        self._build_footer()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header, text="🛰  Network Scanner",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=2, sticky="e")

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_search())
        search = ctk.CTkEntry(
            actions, placeholder_text="Search IP, MAC, hostname, vendor...",
            width=280, textvariable=self._search_var,
        )
        search.grid(row=0, column=0, padx=(0, 10))

        self._scan_btn = ctk.CTkButton(
            actions, text="Scan", width=90, command=self.start_scan,
        )
        self._scan_btn.grid(row=0, column=1, padx=4)

        self._refresh_btn = ctk.CTkButton(
            actions, text="Refresh", width=90,
            fg_color="#2a2f3f", hover_color="#343a4f",
            command=self.start_scan,
        )
        self._refresh_btn.grid(row=0, column=2, padx=4)

        self._export_btn = ctk.CTkButton(
            actions, text="Export", width=90,
            fg_color="#2a2f3f", hover_color="#343a4f",
            command=self.export_results, state="disabled",
        )
        self._export_btn.grid(row=0, column=3, padx=4)

    def _build_stats(self) -> None:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=1, column=0, sticky="ew", padx=24, pady=(6, 12))
        for i in range(4):
            wrapper.grid_columnconfigure(i, weight=1, uniform="stats")

        self._card_devices = StatCard(wrapper, "Active Devices", "0", fg_color="#1a1f2e")
        self._card_devices.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._card_duration = StatCard(wrapper, "Scan Duration", "-", fg_color="#1a1f2e")
        self._card_duration.grid(row=0, column=1, sticky="ew", padx=8)

        self._card_subnet = StatCard(wrapper, "Subnet", "-", fg_color="#1a1f2e")
        self._card_subnet.grid(row=0, column=2, sticky="ew", padx=8)

        self._card_gateway = StatCard(wrapper, "Gateway", "-", fg_color="#1a1f2e")
        self._card_gateway.grid(row=0, column=3, sticky="ew", padx=(8, 0))

    def _build_table(self) -> None:
        container = ctk.CTkFrame(self, fg_color="#141824", corner_radius=14)
        container.grid(row=2, column=0, sticky="nsew", padx=24, pady=8)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(container, fg_color="transparent", height=44)
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        toolbar.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(
            toolbar, text="Discovered Devices",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self._ping_btn = ctk.CTkButton(
            toolbar, text="Ping", width=80, state="disabled",
            fg_color="#2a2f3f", hover_color="#343a4f",
            command=self.ping_selected,
        )
        self._ping_btn.grid(row=0, column=1, padx=(16, 4))

        self._copy_ip_btn = ctk.CTkButton(
            toolbar, text="Copy IP", width=90, state="disabled",
            fg_color="#2a2f3f", hover_color="#343a4f",
            command=lambda: self._copy(self._selected.ip if self._selected else ""),
        )
        self._copy_ip_btn.grid(row=0, column=2, padx=4)

        self._copy_mac_btn = ctk.CTkButton(
            toolbar, text="Copy MAC", width=100, state="disabled",
            fg_color="#2a2f3f", hover_color="#343a4f",
            command=lambda: self._copy(self._selected.mac if self._selected else ""),
        )
        self._copy_mac_btn.grid(row=0, column=3, padx=4)

        self._table = DeviceTable(container, on_select=self._on_row_select)
        self._table.grid(row=1, column=0, sticky="nsew", padx=10, pady=(4, 10))

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(4, 18))
        footer.grid_columnconfigure(1, weight=1)

        self._status_dot = ctk.CTkLabel(
            footer, text="●", text_color="#3ddc84",
            font=ctk.CTkFont(size=16),
        )
        self._status_dot.grid(row=0, column=0, padx=(0, 8))

        self._status_label = ctk.CTkLabel(
            footer, text="Ready.", text_color="#c7ccd9", anchor="w",
        )
        self._status_label.grid(row=0, column=1, sticky="ew")

        self._progress = ctk.CTkProgressBar(footer, width=260)
        self._progress.grid(row=0, column=2, sticky="e")
        self._progress.set(0)

    # ---------- Actions ----------
    def _refresh_host_info(self) -> None:
        host = get_local_host_info()
        self._card_subnet.set_value(host.subnet_cidr)
        self._card_gateway.set_value(host.gateway or "Unknown")
        self._status_label.configure(
            text=f"Local: {host.hostname} ({host.ip_address}) · {host.system}"
        )

    def start_scan(self) -> None:
        if self._scanning:
            return
        self._scanning = True
        self._scan_btn.configure(state="disabled", text="Scanning...")
        self._refresh_btn.configure(state="disabled")
        self._export_btn.configure(state="disabled")
        self._status_dot.configure(text_color="#f5a623")
        self._progress.set(0)
        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self) -> None:
        def progress(pct: float, msg: str) -> None:
            self.after(0, self._progress.set, pct)
            self.after(0, self._status_label.configure, {"text": msg})

        result = self._scanner.scan(progress_cb=progress)
        self.after(0, self._on_scan_done, result)

    def _on_scan_done(self, result: ScanResult) -> None:
        self._scanning = False
        self._scan_btn.configure(state="normal", text="Scan")
        self._refresh_btn.configure(state="normal")
        self._result = result

        if result.error:
            self._status_dot.configure(text_color="#ff5c5c")
            self._status_label.configure(text=f"Error: {result.error}")
            messagebox.showerror("Scan failed", result.error)
            return

        self._table.set_devices(result.devices)
        self._card_devices.set_value(str(result.total))
        self._card_duration.set_value(f"{result.duration_seconds:.2f}s")
        if result.host:
            self._card_subnet.set_value(result.host.subnet_cidr)
            self._card_gateway.set_value(result.host.gateway or "Unknown")
        self._status_dot.configure(text_color="#3ddc84")
        self._status_label.configure(
            text=f"Scan finished · {result.total} devices in {result.duration_seconds:.2f}s"
        )
        self._export_btn.configure(state="normal" if result.total else "disabled")

        try:
            path = Exporter.save_history(result.devices)
            logger.info("History saved to %s", path)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to save history: %s", exc)

    def export_results(self) -> None:
        if not self._result or not self._result.devices:
            return
        path = filedialog.asksaveasfilename(
            title="Export scan results",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json")],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".json"):
                Exporter.to_json(self._result.devices, path)
            else:
                Exporter.to_csv(self._result.devices, path)
            self._status_label.configure(text=f"Exported to {Path(path).name}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

    def _apply_search(self) -> None:
        self._table.apply_filter(self._search_var.get())

    def _on_row_select(self, device: Optional[Device]) -> None:
        self._selected = device
        state = "normal" if device else "disabled"
        for btn in (self._ping_btn, self._copy_ip_btn, self._copy_mac_btn):
            btn.configure(state=state)

    def ping_selected(self) -> None:
        if not self._selected:
            return
        ip = self._selected.ip
        self._status_label.configure(text=f"Pinging {ip}...")

        def _worker() -> None:
            reachable = ping_host(ip)
            self.after(
                0, self._status_label.configure,
                {"text": f"{ip} is {'reachable ✅' if reachable else 'not reachable ❌'}"},
            )

        threading.Thread(target=_worker, daemon=True).start()

    def _copy(self, text: str) -> None:
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self._status_label.configure(text=f"Copied: {text}")

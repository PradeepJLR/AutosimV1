import sys
import os
import re
import difflib
import traceback
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.table import Table
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton, QDialog, QCheckBox,
                             QLineEdit, QComboBox, QFileDialog, QListWidget,
                             QAbstractItemView, QLabel, QColorDialog, QGridLayout,
                             QMenu, QMessageBox, QFrame, QGroupBox, QFormLayout,
                             QStatusBar, QScrollArea, QSpinBox, QTableWidget,
                             QHeaderView, QStackedWidget, QTabWidget, QDoubleSpinBox,
                             QRadioButton, QSizePolicy, QInputDialog, QWidgetAction)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QAction, QFont, QFontDatabase, QPalette, QShortcut, QKeySequence
import mplcursors


# ==========================================
# GLOBAL EXCEPTION HANDLER
# ==========================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    tb_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"CRITICAL ERROR CAUGHT:\n{tb_string}")
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Fatal Application Error")
        msg.setText("An unexpected error occurred. The application caught the crash instead of closing.")
        msg.setDetailedText(tb_string)
        msg.exec()


sys.excepthook = global_exception_handler

# ==========================================
# GLOBAL STYLESHEET
# ==========================================
GLOBAL_STYLE = """
QWidget {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
    color: #1e293b;
}
QMainWindow, QDialog, QStackedWidget { background-color: #f1f5f9; }
QScrollArea { border: none; background-color: transparent; }
#topbar { background-color: #0f172a; border-bottom: 2px solid #1e293b; }
#topbar QWidget#brand_container { border-right: 1px solid #334155; margin-right: 10px; }
#topbar QLabel.brand_title { color: #38bdf8; font-size: 18px; font-weight: 800; padding-right: 15px; }
QComboBox.mode_switcher {
    background-color: #1e293b; color: #38bdf8; font-size: 11px; font-weight: 700;
    border: 1px solid #334155; border-radius: 3px; padding: 2px 5px; margin-right: 15px; margin-top: 2px;
}
QComboBox.mode_switcher::drop-down { border: none; }
#topbar QPushButton { background-color: transparent; color: #cbd5e1; padding: 8px 14px; border-radius: 4px; font-size: 13px; font-weight: 600; border: none; }
#topbar QPushButton:hover { background-color: #1e293b; color: #ffffff; }
#topbar QPushButton:pressed { background-color: #334155; }
QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 5px; padding: 8px 16px; font-weight: 600; }
QPushButton:hover { background-color: #1d4ed8; }
QPushButton:pressed { background-color: #1e40af; }
QPushButton#btn_rms { background-color: #64748b; color: white; margin-left: 10px; }
QPushButton#btn_rms:hover { background-color: #475569; }
QPushButton#btn_plot { background-color: #059669; color: white; margin-left: 10px; }
QPushButton#btn_plot:hover { background-color: #047857; }
QPushButton#btn_export { background-color: #0284c7; color: white; }
QPushButton#btn_export:hover { background-color: #0369a1; }
QPushButton#btn_cursor { background-color: #d97706; color: white; }
QPushButton#btn_cursor:hover { background-color: #b45309; }
QPushButton#btn_reset { background-color: #dc2626; color: white; }
QPushButton#btn_reset:hover { background-color: #b91c1c; }
QPushButton#btn_help { background-color: #475569; color: white; border-radius: 12px; padding: 4px 10px;}
QPushButton#btn_help:hover { background-color: #334155; }
QPushButton#gridButton { background-color: #64748b; font-size: 16px; font-weight: bold; padding: 4px; color: white;}
QPushButton#gridButton:checked { background-color: #0ea5e9; }
QPushButton#legendButton { background-color: #64748b; font-size: 14px; font-weight: bold; padding: 4px; color: white;}
QPushButton#legendButton:checked { background-color: #0ea5e9; }

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px 10px; color: #334155;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #38bdf8; background-color: #f0f9ff; }
QGroupBox { font-weight: 600; color: #475569; border: 1px solid #cbd5e1; border-radius: 6px; margin-top: 12px; padding-top: 15px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
QTableWidget { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; gridline-color: #e2e8f0; }
QHeaderView::section { background-color: #f1f5f9; padding: 6px; border: none; border-right: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1; font-weight: 600; color: #475569; }
QTabWidget::pane { border: 1px solid #cbd5e1; background-color: #ffffff; border-radius: 4px; }
QTabBar::tab { background-color: #e2e8f0; color: #475569; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #ffffff; border-bottom: 2px solid #2563eb; color: #2563eb; font-weight: bold;}
QStatusBar { background-color: #ffffff; color: #475569; border-top: 1px solid #e2e8f0; }
"""


def setup_matplotlib_style():
    plt.rcParams.update({
        'axes.edgecolor': '#cbd5e1', 'axes.linewidth': 1.2, 'axes.facecolor': '#ffffff',
        'grid.color': '#f1f5f9', 'grid.linestyle': '-', 'grid.linewidth': 1.5,
        'figure.facecolor': '#ffffff', 'font.family': 'sans-serif',
        'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica', 'sans-serif'],
        'legend.frameon': True,
        'legend.edgecolor': '#cbd5e1', 'legend.facecolor': '#ffffff',
    })


def calculate_grid(n_plots):
    if n_plots <= 0: return 1, 1
    if n_plots == 1: return 1, 1
    if n_plots == 2: return 1, 2
    if n_plots <= 4: return 2, 2
    if n_plots <= 6: return 2, 3
    if n_plots <= 9: return 3, 3
    if n_plots <= 12: return 3, 4
    n_cols = 4
    n_rows = (n_plots + n_cols - 1) // n_cols
    return n_rows, n_cols


def get_best_match(target, options):
    target_norm = str(target).lower().strip()
    options_norm = [str(o).lower().strip() for o in options]
    if target_norm in options_norm: return options[options_norm.index(target_norm)]
    best_match = "-- None --"
    best_score = 0
    target_tokens = set(target_norm.replace('_', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ').split())
    for idx, opt in enumerate(options_norm):
        score = difflib.SequenceMatcher(None, target_norm, opt).ratio()
        if target_norm in opt or opt in target_norm: score += 0.4
        opt_tokens = set(opt.replace('_', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ').split())
        if target_tokens & opt_tokens: score += 0.3
        if score > best_score:
            best_score = score
            best_match = options[idx]
    if best_score > 0.45: return best_match
    return "-- None --"


def load_dataframe(filepath, header="infer"):
    """Robustly load CSV, XLS, and XLSX files handling common encoding issues."""
    ext = filepath.lower()
    if ext.endswith('.csv'):
        try:
            return pd.read_csv(filepath, header=header, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(filepath, header=header, encoding='latin1')
    elif ext.endswith(('.xls', '.xlsx')):
        excel_header = 0 if header == "infer" else header
        return pd.read_excel(filepath, header=excel_header)
    else:
        raise ValueError("Unsupported file format. Please use CSV, XLS, or XLSX files.")


class NoScrollComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        event.ignore()


# ==========================================
# INTERACTIVE SUBPLOT ZOOM MANAGER
# ==========================================
class SubplotZoomManager:
    """
    Manages left-click hold-and-drag rectangular zooming within subplots.
    Resets zoom when pressing Escape or clicking (left or right) outside the zoomed subplot.
    """

    def __init__(self, canvas, status_bar=None, ignore_func=None):
        self.canvas = canvas
        self.status_bar = status_bar
        self.ignore_func = ignore_func
        self.orig_limits = {}  # ax -> (xlim, ylim)
        self.zoomed_axes = set()  # set of currently zoomed axes

        self.dragging = False
        self.active_ax = None
        self.x0 = None
        self.y0 = None
        self.px0 = None
        self.py0 = None
        self.last_xdata = None
        self.last_ydata = None
        self.rect_patch = None
        self.suppress_next_context_menu = False

        self.canvas.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_key = self.canvas.mpl_connect('key_press_event', self.on_key)

    def register_axes(self):
        """Record baseline limits right after subplots are generated."""
        self.orig_limits.clear()
        self.zoomed_axes.clear()
        self.cleanup_drag()
        for ax in self.canvas.figure.axes:
            self.orig_limits[ax] = (ax.get_xlim(), ax.get_ylim())

    def cleanup_drag(self):
        if self.rect_patch is not None:
            try:
                self.rect_patch.remove()
            except Exception:
                pass
            self.rect_patch = None
        self.dragging = False
        self.active_ax = None
        self.x0 = self.y0 = None
        self.px0 = self.py0 = None
        self.last_xdata = self.last_ydata = None

    def reset_axis_zoom(self, ax):
        if ax in self.orig_limits:
            xlim, ylim = self.orig_limits[ax]
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
        self.zoomed_axes.discard(ax)

    def reset_all_zooms(self):
        if not self.zoomed_axes and not self.dragging:
            return False
        self.cleanup_drag()
        for ax in list(self.zoomed_axes):
            self.reset_axis_zoom(ax)
        self.canvas.draw_idle()
        if self.status_bar:
            self.status_bar.showMessage("Zoom reset to default view.", 3000)
        return True

    def on_key(self, event):
        if event.key == 'escape':
            self.reset_all_zooms()

    def on_press(self, event):
        if self.ignore_func and self.ignore_func(event):
            return

        self.suppress_next_context_menu = False
        self.canvas.setFocus()

        # If any subplot is zoomed and the user clicks (left or right) outside that subplot, reset it
        if self.zoomed_axes and event.button in (1, 3):
            outside_zoomed = [ax for ax in list(self.zoomed_axes) if event.inaxes != ax]
            if outside_zoomed:
                for ax in outside_zoomed:
                    self.reset_axis_zoom(ax)
                self.canvas.draw_idle()
                if self.status_bar:
                    self.status_bar.showMessage("Zoom reset.", 3000)
                if event.button == 3:
                    self.suppress_next_context_menu = True
                if event.inaxes is None:
                    return

        # Left-click inside a subplot initiates rubberband zoom
        if event.button == 1 and event.inaxes is not None:
            if event.xdata is None or event.ydata is None:
                return
            self.active_ax = event.inaxes
            if self.active_ax not in self.orig_limits:
                self.orig_limits[self.active_ax] = (self.active_ax.get_xlim(), self.active_ax.get_ylim())

            self.dragging = True
            self.x0, self.y0 = event.xdata, event.ydata
            self.last_xdata, self.last_ydata = event.xdata, event.ydata
            self.px0, self.py0 = event.x, event.y

            self.rect_patch = Rectangle(
                (self.x0, self.y0), 0, 0,
                fill=True, facecolor='#38bdf8', alpha=0.22,
                edgecolor='#0284c7', linewidth=1.5, linestyle='--',
                zorder=1000
            )
            self.active_ax.add_patch(self.rect_patch)

    def on_motion(self, event):
        if not self.dragging or self.active_ax is None or self.rect_patch is None:
            return

        try:
            inv = self.active_ax.transData.inverted()
            xdata, ydata = inv.transform((event.x, event.y))
            xlim = self.active_ax.get_xlim()
            ylim = self.active_ax.get_ylim()
            xdata = float(np.clip(xdata, min(xlim), max(xlim)))
            ydata = float(np.clip(ydata, min(ylim), max(ylim)))
        except Exception:
            if event.inaxes == self.active_ax and event.xdata is not None and event.ydata is not None:
                xdata, ydata = event.xdata, event.ydata
            else:
                return

        self.last_xdata, self.last_ydata = xdata, ydata
        xmin = min(self.x0, xdata)
        ymin = min(self.y0, ydata)
        width = abs(xdata - self.x0)
        height = abs(ydata - self.y0)

        self.rect_patch.set_bounds(xmin, ymin, width, height)
        self.canvas.draw_idle()

    def on_release(self, event):
        if event.button != 1 or not self.dragging or self.active_ax is None:
            return

        ax = self.active_ax
        x0, y0 = self.x0, self.y0
        x1, y1 = self.last_xdata, self.last_ydata
        px0, py0 = self.px0, self.py0

        self.cleanup_drag()

        # Require a minimum drag distance of 8 pixels so normal clicks don't trigger micro-zooms
        if event.x is not None and event.y is not None and px0 is not None and py0 is not None:
            if abs(event.x - px0) < 8 or abs(event.y - py0) < 8:
                self.canvas.draw_idle()
                return

        if x0 is not None and x1 is not None and y0 is not None and y1 is not None:
            xmin, xmax = min(x0, x1), max(x0, x1)
            ymin, ymax = min(y0, y1), max(y0, y1)
            if xmax > xmin and ymax > ymin:
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                self.zoomed_axes.add(ax)
                if self.status_bar:
                    self.status_bar.showMessage(
                        "Subplot zoomed. Press 'Esc' or click outside this subplot to reset zoom.", 5000
                    )

        self.canvas.draw_idle()


# ==========================================
# COMMON DIALOGS
# ==========================================
class DefineFilesDialog(QDialog):
    def __init__(self, current_count=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Define Working Files")
        self.setMinimumWidth(300)
        self.selected_files = []
        self.current_count = current_count if current_count > 0 else 1
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Configuration")
        form = QFormLayout(group)
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 20)
        self.spin_box.setValue(self.current_count)
        form.addRow("Number of Data Files:", self.spin_box)
        layout.addWidget(group)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Next ➔")
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self.apply_selection)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def apply_selection(self):
        count = self.spin_box.value()
        self.selected_files = [f"Data File {i}" for i in range(1, count + 1)]
        self.accept()


class FileSelectionDialog(QDialog):
    def __init__(self, selected_files, prev_settings=None, prev_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Selection & Styling")
        self.setMinimumWidth(800)
        self.selected_files = selected_files
        self.file_settings = prev_settings.copy() if prev_settings else {}
        self.file_data = prev_data.copy() if prev_data else {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for file_name in self.selected_files:
            group = QGroupBox(file_name)
            grid = QGridLayout(group)

            grid.addWidget(QLabel("File Path:"), 0, 0)
            path_edit = QLineEdit()
            path_edit.setObjectName(f"path_{file_name}")
            if file_name in self.file_settings:
                path_edit.setText(self.file_settings[file_name]["path"])
            grid.addWidget(path_edit, 0, 1, 1, 4)

            browse_btn = QPushButton("Browse...")
            browse_btn.clicked.connect(lambda _, f=file_name: self.browse_file(f))
            grid.addWidget(browse_btn, 0, 5)

            enable_chk = QCheckBox("Enable")
            enable_chk.setObjectName(f"enable_{file_name}")
            enable_chk.setChecked(True)
            if file_name in self.file_settings and not self.file_settings[file_name].get("enabled", True):
                enable_chk.setChecked(False)
            grid.addWidget(enable_chk, 0, 6)

            grid.addWidget(QLabel("Legend Name:"), 1, 0)
            name_edit = QLineEdit()
            name_edit.setObjectName(f"name_{file_name}")
            if file_name in self.file_settings:
                name_edit.setText(self.file_settings[file_name]["name"])
            else:
                name_edit.setText(file_name)
            grid.addWidget(name_edit, 1, 1)

            grid.addWidget(QLabel("Line Width:"), 1, 2)
            width_combo = NoScrollComboBox()
            width_combo.addItems(["0.5", "1", "1.5", "2", "2.5", "3"])
            width_combo.setObjectName(f"width_{file_name}")
            if file_name in self.file_settings:
                width_combo.setCurrentText(str(self.file_settings[file_name]["width"]))
            grid.addWidget(width_combo, 1, 3)

            grid.addWidget(QLabel("Style:"), 1, 4)
            style_combo = NoScrollComboBox()
            style_combo.addItems(["Solid", "Dashed", "Dotted"])
            style_combo.setObjectName(f"style_{file_name}")
            if file_name in self.file_settings:
                style_combo.setCurrentText(self.file_settings[file_name]["style"])
            grid.addWidget(style_combo, 1, 5)

            color_btn = QPushButton("Pick Color")
            color_btn.setObjectName(f"color_{file_name}")
            color_btn.clicked.connect(lambda _, f=file_name: self.choose_color(f))
            if file_name in self.file_settings:
                color_btn.setStyleSheet(
                    f"background-color: {self.file_settings[file_name]['color']}; color: white; border: 1px solid #000;")
            else:
                color_btn.setStyleSheet("background-color: #000000; color: white;")
            grid.addWidget(color_btn, 1, 6)
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply & Continue")
        apply_btn.setMinimumWidth(120)
        apply_btn.clicked.connect(self.apply_settings)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def browse_file(self, file_name):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Data Files (*.csv *.xls *.xlsx)")
        if file_path:
            self.findChild(QLineEdit, f"path_{file_name}").setText(file_path)

    def choose_color(self, file_name):
        color = QColorDialog.getColor()
        if color.isValid():
            btn = self.findChild(QPushButton, f"color_{file_name}")
            btn.setStyleSheet(f"background-color: {color.name()}; color: white; border: 1px solid #000;")
            btn.setProperty("selected_color", color.name())

    def apply_settings(self):
        for file_name in self.selected_files:
            enabled = self.findChild(QCheckBox, f"enable_{file_name}").isChecked()
            path = self.findChild(QLineEdit, f"path_{file_name}").text()

            if not enabled:
                if file_name in self.file_data: del self.file_data[file_name]
                if file_name in self.file_settings: del self.file_settings[file_name]
                continue

            if path:
                old_path = self.file_settings.get(file_name, {}).get("path", "")
                if path != old_path or file_name not in self.file_data:
                    try:
                        df = load_dataframe(path)
                        self.file_data[file_name] = df
                    except Exception:
                        tb = traceback.format_exc()
                        QMessageBox.warning(self, "Read Error", f"Error reading file {path}:\n{tb}")
                        continue

                color_btn = self.findChild(QPushButton, f"color_{file_name}")
                color = color_btn.property("selected_color")
                if not color:
                    style = color_btn.styleSheet()
                    color = style.split('background-color:')[1].split(';')[
                        0].strip() if 'background-color:' in style else '#000000'

                self.file_settings[file_name] = {
                    "path": path, "color": color,
                    "width": float(self.findChild(NoScrollComboBox, f"width_{file_name}").currentText()),
                    "style": self.findChild(NoScrollComboBox, f"style_{file_name}").currentText(),
                    "name": self.findChild(QLineEdit, f"name_{file_name}").text() or file_name,
                    "enabled": enabled
                }

        self.accept()


class PCHFileSelectionDialog(QDialog):
    def __init__(self, selected_files, prev_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PCH File Selection & Styling")
        self.setMinimumWidth(800)
        self.selected_files = selected_files
        self.file_settings = prev_settings.copy() if prev_settings else {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for file_name in self.selected_files:
            group = QGroupBox(file_name)
            grid = QGridLayout(group)

            grid.addWidget(QLabel("File Path:"), 0, 0)
            path_edit = QLineEdit()
            path_edit.setObjectName(f"path_{file_name}")
            if file_name in self.file_settings:
                path_edit.setText(self.file_settings[file_name]["path"])
            grid.addWidget(path_edit, 0, 1, 1, 4)

            browse_btn = QPushButton("Browse...")
            browse_btn.clicked.connect(lambda _, f=file_name: self.browse_file(f))
            grid.addWidget(browse_btn, 0, 5)

            enable_chk = QCheckBox("Enable")
            enable_chk.setObjectName(f"enable_{file_name}")
            enable_chk.setChecked(True)
            if file_name in self.file_settings and not self.file_settings[file_name].get("enabled", True):
                enable_chk.setChecked(False)
            grid.addWidget(enable_chk, 0, 6)

            grid.addWidget(QLabel("Legend Name:"), 1, 0)
            name_edit = QLineEdit()
            name_edit.setObjectName(f"name_{file_name}")
            if file_name in self.file_settings:
                name_edit.setText(self.file_settings[file_name]["name"])
            else:
                name_edit.setText(file_name)
            grid.addWidget(name_edit, 1, 1)

            grid.addWidget(QLabel("Line Width:"), 1, 2)
            width_combo = NoScrollComboBox()
            width_combo.addItems(["0.5", "1", "1.5", "2", "2.5", "3"])
            width_combo.setObjectName(f"width_{file_name}")
            if file_name in self.file_settings:
                width_combo.setCurrentText(str(self.file_settings[file_name]["width"]))
            grid.addWidget(width_combo, 1, 3)

            grid.addWidget(QLabel("Style:"), 1, 4)
            style_combo = NoScrollComboBox()
            style_combo.addItems(["Solid", "Dashed", "Dotted"])
            style_combo.setObjectName(f"style_{file_name}")
            if file_name in self.file_settings:
                style_combo.setCurrentText(self.file_settings[file_name]["style"])
            grid.addWidget(style_combo, 1, 5)

            color_btn = QPushButton("Pick Color")
            color_btn.setObjectName(f"color_{file_name}")
            color_btn.clicked.connect(lambda _, f=file_name: self.choose_color(f))
            if file_name in self.file_settings:
                color_btn.setStyleSheet(
                    f"background-color: {self.file_settings[file_name]['color']}; color: white; border: 1px solid #000;")
            else:
                color_btn.setStyleSheet("background-color: #000000; color: white;")
            grid.addWidget(color_btn, 1, 6)
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply & Continue")
        apply_btn.setMinimumWidth(120)
        apply_btn.clicked.connect(self.apply_settings)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def browse_file(self, file_name):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PCH File", "", "PCH Files (*.pch)")
        if file_path:
            self.findChild(QLineEdit, f"path_{file_name}").setText(file_path)
            name_entry = self.findChild(QLineEdit, f"name_{file_name}")
            if not name_entry.text() or name_entry.text() == file_name:
                name_entry.setText(os.path.basename(file_path))

    def choose_color(self, file_name):
        color = QColorDialog.getColor()
        if color.isValid():
            btn = self.findChild(QPushButton, f"color_{file_name}")
            btn.setStyleSheet(f"background-color: {color.name()}; color: white; border: 1px solid #000;")
            btn.setProperty("selected_color", color.name())

    def apply_settings(self):
        for file_name in self.selected_files:
            enabled = self.findChild(QCheckBox, f"enable_{file_name}").isChecked()
            path = self.findChild(QLineEdit, f"path_{file_name}").text()

            if not enabled:
                if file_name in self.file_settings: del self.file_settings[file_name]
                continue

            if path:
                color_btn = self.findChild(QPushButton, f"color_{file_name}")
                color = color_btn.property("selected_color")
                if not color:
                    style = color_btn.styleSheet()
                    color = style.split('background-color:')[1].split(';')[
                        0].strip() if 'background-color:' in style else '#000000'

                self.file_settings[file_name] = {
                    "path": path, "color": color,
                    "width": float(self.findChild(NoScrollComboBox, f"width_{file_name}").currentText()),
                    "style": self.findChild(NoScrollComboBox, f"style_{file_name}").currentText(),
                    "name": self.findChild(QLineEdit, f"name_{file_name}").text() or file_name,
                    "enabled": enabled
                }

        self.accept()


class CurveMappingDialog(QDialog):
    def __init__(self, file_settings, file_data, saved_mappings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Map Curve Columns")
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        self.file_settings = file_settings
        self.file_data = file_data
        self.file_names = list(self.file_settings.keys())
        self.saved_mappings = saved_mappings if saved_mappings else []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        info = QLabel(
            "Select curves to plot. Missing columns in secondary files have been smart-matched where possible.")
        info.setStyleSheet("color: #64748b; font-style: italic; margin-bottom: 5px;")
        layout.addWidget(info)

        action_layout = QHBoxLayout()
        sel_all = QPushButton("Select All")
        sel_all.setStyleSheet("background-color: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1;")
        sel_all.clicked.connect(lambda: self.toggle_all(True))

        desel_all = QPushButton("Deselect All")
        desel_all.setStyleSheet("background-color: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1;")
        desel_all.clicked.connect(lambda: self.toggle_all(False))

        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel(" Match Legend: "))
        lbl_blue = QLabel("Exact Match")
        lbl_blue.setStyleSheet(
            "background-color: #e0f2fe; padding: 2px 6px; border-radius: 3px; border: 1px solid #7dd3fc;")
        lbl_amber = QLabel("Closest Match")
        lbl_amber.setStyleSheet(
            "background-color: #fef3c7; padding: 2px 6px; border-radius: 3px; border: 1px solid #fde047;")
        lbl_red = QLabel("No Match")
        lbl_red.setStyleSheet(
            "background-color: #fee2e2; padding: 2px 6px; border-radius: 3px; border: 1px solid #fca5a5;")

        legend_layout.addWidget(lbl_blue)
        legend_layout.addWidget(lbl_amber)
        legend_layout.addWidget(lbl_red)
        action_layout.addWidget(sel_all)
        action_layout.addWidget(desel_all)
        action_layout.addStretch()
        action_layout.addLayout(legend_layout)
        layout.addLayout(action_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2 + len(self.file_names))
        headers = ["Plot?", "Master Plot Title"] + [self.file_settings[fn]["name"] for fn in self.file_names]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        if not self.saved_mappings:
            self.generate_smart_mappings()
        else:
            self.update_existing_mappings_for_new_files()
        self.populate_table()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply & Generate Plots")
        apply_btn.setMinimumWidth(150)
        apply_btn.clicked.connect(self.apply_selection)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def update_existing_mappings_for_new_files(self):
        """Smart-matches newly added files into the existing saved mappings."""
        existing_files = set(self.saved_mappings[0]['map'].keys()) if self.saved_mappings else set()
        new_files = [fn for fn in self.file_names if fn not in existing_files]

        if not new_files:
            return

        # 1. Try to map new files to existing master titles
        for mapping in self.saved_mappings:
            master_title = mapping['title']
            for fn in new_files:
                cols = list(self.file_data[fn].columns[1:])
                match = get_best_match(master_title, cols)
                mapping['map'][fn] = match

        # 2. Add any remaining columns from the new files as new rows
        for fn in new_files:
            all_cols = set(self.file_data[fn].columns[1:])
            mapped_cols = {mapping['map'].get(fn) for mapping in self.saved_mappings}
            unmapped_cols = all_cols - mapped_cols

            for col in unmapped_cols:
                if col == "-- None --": continue
                row_map = {f: "-- None --" for f in self.file_names}
                row_map[fn] = col
                self.saved_mappings.append({'selected': False, 'title': col, 'map': row_map})

    def toggle_all(self, state):
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0).findChild(QCheckBox)
            if chk:
                chk.setChecked(state)

    def generate_smart_mappings(self):
        if not self.file_names: return
        unmapped_cols = {fn: list(self.file_data[fn].columns[1:]) for fn in self.file_names}
        base_fn = self.file_names[0]

        for col in list(unmapped_cols[base_fn]):
            row_map = {base_fn: col}
            unmapped_cols[base_fn].remove(col)
            for other_fn in self.file_names[1:]:
                match = get_best_match(col, unmapped_cols[other_fn])
                row_map[other_fn] = match
                if match != "-- None --":
                    unmapped_cols[other_fn].remove(match)
            self.saved_mappings.append({'selected': False, 'title': col, 'map': row_map})

        for fn in self.file_names[1:]:
            for col in list(unmapped_cols[fn]):
                row_map = {f: "-- None --" for f in self.file_names}
                row_map[fn] = col
                self.saved_mappings.append({'selected': False, 'title': col, 'map': row_map})

    def update_combo_color(self, combo, master_title):
        val = combo.currentText()
        base_style = "QComboBox QAbstractItemView { background-color: #ffffff; }"
        if val == "-- None --":
            combo.setStyleSheet(base_style + "QComboBox { background-color: #fee2e2; border: 1px solid #fca5a5; }")
        elif val.lower().strip() == master_title.lower().strip():
            combo.setStyleSheet(base_style + "QComboBox { background-color: #e0f2fe; border: 1px solid #7dd3fc; }")
        else:
            combo.setStyleSheet(base_style + "QComboBox { background-color: #fef3c7; border: 1px solid #fde047; }")

    def populate_table(self):
        self.table.setRowCount(len(self.saved_mappings))
        for row, mapping in enumerate(self.saved_mappings):
            chk = QCheckBox()
            chk.setChecked(mapping['selected'])
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, chk_widget)

            title_edit = QLineEdit(mapping['title'])
            self.table.setCellWidget(row, 1, title_edit)

            combos = []
            for col_idx, fn in enumerate(self.file_names, start=2):
                combo = NoScrollComboBox()
                options = ["-- None --"] + [str(c) for c in self.file_data[fn].columns[1:]]
                combo.addItems(options)
                if mapping['map'].get(fn, "-- None --") in options:
                    combo.setCurrentText(str(mapping['map'].get(fn, "-- None --")))
                self.table.setCellWidget(row, col_idx, combo)
                combos.append(combo)
                self.update_combo_color(combo, title_edit.text())
                combo.currentTextChanged.connect(
                    lambda text, c=combo, t=title_edit: self.update_combo_color(c, t.text()))
            title_edit.textChanged.connect(
                lambda text, cb_list=combos: [self.update_combo_color(c, text) for c in cb_list])

    def apply_selection(self):
        new_mappings = []
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0).findChild(QCheckBox)
            title = self.table.cellWidget(row, 1).text()
            row_map = {fn: self.table.cellWidget(row, col_idx).currentText() for col_idx, fn in
                       enumerate(self.file_names, start=2)}
            new_mappings.append({'selected': chk.isChecked(), 'title': title, 'map': row_map})
        self.saved_mappings = new_mappings
        self.accept()


class DynamicSettingsDialog(QDialog):
    def __init__(self, prev_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Axis Settings")
        self.setMinimumWidth(550)
        self.settings = prev_settings if prev_settings else {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        group_x = QGroupBox("X-Axis Configuration")
        form_x = QFormLayout(group_x)
        self.x_title = QLineEdit(self.settings.get("x_title", "Frequency"))
        self.x_min = QLineEdit(str(self.settings.get("x_min", "")) if self.settings.get("x_min") is not None else "")
        self.x_max = QLineEdit(str(self.settings.get("x_max", "")) if self.settings.get("x_max") is not None else "")
        self.x_ticks = QLineEdit(
            str(self.settings.get("x_ticks", "")) if self.settings.get("x_ticks") is not None else "")
        self.x_min.setPlaceholderText("Auto")
        self.x_max.setPlaceholderText("Auto")
        self.x_ticks.setPlaceholderText("Auto (e.g. 5, 10)")
        form_x.addRow("Title:", self.x_title)
        form_x.addRow("Min Limit:", self.x_min)
        form_x.addRow("Max Limit:", self.x_max)
        form_x.addRow("Max Ticks:", self.x_ticks)
        main_layout.addWidget(group_x)

        group_y = QGroupBox("Y-Axis Configuration")
        form_y = QFormLayout(group_y)
        self.y_title = QLineEdit(self.settings.get("y_title", "Acceleration m/sec²"))
        self.y_min = QLineEdit(str(self.settings.get("y_min", "")) if self.settings.get("y_min") is not None else "")
        self.y_max = QLineEdit(str(self.settings.get("y_max", "")) if self.settings.get("y_max") is not None else "")
        self.y_ticks = QLineEdit(
            str(self.settings.get("y_ticks", "")) if self.settings.get("y_ticks") is not None else "")
        self.y_min.setPlaceholderText("Auto")
        self.y_max.setPlaceholderText("Auto")
        self.y_ticks.setPlaceholderText("Auto (e.g. 5, 10)")
        self.y_log = QCheckBox("Use Logarithmic Scale for Y-Axis")
        self.y_log.setChecked(self.settings.get("y_log", False))
        form_y.addRow("Title:", self.y_title)
        form_y.addRow("Min Limit:", self.y_min)
        form_y.addRow("Max Limit:", self.y_max)
        form_y.addRow("Max Ticks:", self.y_ticks)
        form_y.addRow("", self.y_log)
        main_layout.addWidget(group_y)

        group_gen = QGroupBox("General Display")
        form_gen = QFormLayout(group_gen)

        font_layout = QHBoxLayout()
        self.font_type = NoScrollComboBox()
        self.font_type.addItems(["Segoe UI", "Arial", "Times New Roman", "Calibri"])
        self.font_type.setCurrentText(self.settings.get("font_type", "Segoe UI"))
        font_layout.addWidget(self.font_type)
        form_gen.addRow("Font Family:", font_layout)

        self.title_size = QSpinBox()
        self.title_size.setRange(6, 30)
        self.title_size.setValue(self.settings.get("title_size", 14))

        self.axis_size = QSpinBox()
        self.axis_size.setRange(6, 30)
        self.axis_size.setValue(self.settings.get("axis_size", 12))

        self.tick_size = QSpinBox()
        self.tick_size.setRange(6, 30)
        self.tick_size.setValue(self.settings.get("tick_size", 10))

        self.legend_size = QSpinBox()
        self.legend_size.setRange(6, 30)
        self.legend_size.setValue(self.settings.get("legend_size", 10))

        form_gen.addRow("Subplot Title Size:", self.title_size)
        form_gen.addRow("Axis Title Size:", self.axis_size)
        form_gen.addRow("Tick Label Size:", self.tick_size)
        form_gen.addRow("Legend Font Size:", self.legend_size)

        check_layout = QHBoxLayout()
        self.legend_on = QCheckBox("Show Legend")
        self.legend_on.setChecked(self.settings.get("legend_on", True))
        self.grid_on = QCheckBox("Show Grid")
        self.grid_on.setChecked(self.settings.get("grid_on", True))
        check_layout.addWidget(self.legend_on)
        check_layout.addWidget(self.grid_on)
        form_gen.addRow("Features:", check_layout)
        main_layout.addWidget(group_gen)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setMinimumWidth(120)
        apply_btn.clicked.connect(self.apply_settings)
        btn_layout.addWidget(apply_btn)
        main_layout.addLayout(btn_layout)

    def apply_settings(self):
        try:
            self.settings = {
                "x_title": self.x_title.text(),
                "x_min": float(self.x_min.text()) if self.x_min.text().strip() else None,
                "x_max": float(self.x_max.text()) if self.x_max.text().strip() else None,
                "x_ticks": int(self.x_ticks.text()) if self.x_ticks.text().strip() else None,
                "y_title": self.y_title.text(),
                "y_min": float(self.y_min.text()) if self.y_min.text().strip() else None,
                "y_max": float(self.y_max.text()) if self.y_max.text().strip() else None,
                "y_ticks": int(self.y_ticks.text()) if self.y_ticks.text().strip() else None,
                "font_type": self.font_type.currentText(),
                "title_size": self.title_size.value(),
                "axis_size": self.axis_size.value(),
                "tick_size": self.tick_size.value(),
                "legend_size": self.legend_size.value(),
                "y_log": self.y_log.isChecked(),
                "legend_on": self.legend_on.isChecked(),
                "grid_on": self.grid_on.isChecked()
            }
            self.accept()
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please ensure limits and ticks are numeric values.")


class RMSDialog(QDialog):
    def __init__(self, file_settings, file_data, mapped_curves, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RMS Analytics")
        self.setMinimumWidth(400)
        self.file_settings = file_settings
        self.file_data = file_data
        self.mapped_curves = mapped_curves
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("RMS Parameters")
        form = QFormLayout(group)
        self.rms_type = NoScrollComboBox()
        self.rms_type.addItems(["Vibration", "Sound"])
        form.addRow("Analysis Type:", self.rms_type)
        self.min_freq = QLineEdit()
        self.min_freq.setPlaceholderText("e.g. 20")
        form.addRow("Min Frequency (Hz):", self.min_freq)
        self.max_freq = QLineEdit()
        self.max_freq.setPlaceholderText("e.g. 20000")
        form.addRow("Max Frequency (Hz):", self.max_freq)
        self.freq_increment = QLineEdit()
        self.freq_increment.setPlaceholderText("e.g. 100")
        form.addRow("Frequency Increment (Hz):", self.freq_increment)
        layout.addWidget(group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        calc_btn = QPushButton("Calculate & Export")
        calc_btn.clicked.connect(self.calculate_rms)
        btn_layout.addWidget(calc_btn)
        layout.addLayout(btn_layout)

    def calculate_rms(self):
        try:
            min_freq = float(self.min_freq.text())
            max_freq = float(self.max_freq.text())
            increment = float(self.freq_increment.text())
            rms_type = self.rms_type.currentText()
        except ValueError:
            QMessageBox.critical(self, "Invalid Input",
                                 "Please enter valid numeric values for frequencies and increment.")
            return

        legend_names = [settings["name"] for settings in self.file_settings.values()]
        colors = [settings["color"] for settings in self.file_settings.values()]
        freq_cache = {fn: df.iloc[:, 0].values for fn, df in self.file_data.items()}

        rms_values = {plot_title: [] for plot_title in self.mapped_curves}
        intervals = []

        for start_freq in np.arange(min_freq, max_freq, increment):
            end_freq = start_freq + increment
            intervals.append(f"{int(start_freq)}-{int(end_freq)} Hz")
            for plot_title, mapping in self.mapped_curves.items():
                rms_value_list = []
                for file_idx, (file_name, settings) in enumerate(self.file_settings.items()):
                    if file_name in mapping and mapping[file_name] != "-- None --":
                        orig_col = mapping[file_name]
                        df = self.file_data[file_name]
                        if orig_col in df.columns:
                            frequencies = freq_cache[file_name]
                            mask = (frequencies >= start_freq) & (frequencies < end_freq)
                            amplitude_values = df[orig_col].values[mask]

                            if rms_type == "Vibration":
                                amplitude_values = amplitude_values / 9.80665 / 2 ** 1.63
                                rms_value = np.sqrt(np.sum(amplitude_values ** 2))
                            elif rms_type == "Sound":
                                power_ratios = [10 ** (val / 10) for val in amplitude_values]
                                avg_power = np.mean(power_ratios) if power_ratios else 0
                                rms_value = 10 * np.log10(avg_power) if avg_power > 0 else float('-inf')
                            rms_value_list.append((rms_value, file_idx))
                rms_values[plot_title].append(rms_value_list)

        self.generate_rms_tables(intervals, rms_values, list(self.mapped_curves.keys()), legend_names, colors, rms_type)
        self.accept()

    def generate_rms_tables(self, intervals, rms_values, plot_titles, legend_names, colors, rms_type):
        export_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not export_path:
            return

        rms_data_path = os.path.join(export_path, "RMS_Analytics")
        os.makedirs(rms_data_path, exist_ok=True)

        unit = "g" if rms_type == "Vibration" else "dB"
        for plot_title in plot_titles:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('off')
            table_data = [["Curves", "Frequency (Hz)", f"Spectrum to RMS ({unit})"]]
            for i, interval in enumerate(intervals):
                for rms_value, file_idx in rms_values[plot_title][i]:
                    table_data.append([legend_names[file_idx], interval, f"{rms_value:.4f}"])

            if len(table_data) <= 1:
                plt.close(fig)
                continue

            table = Table(ax, bbox=[0, 0, 1, 1])
            nrows, ncols = len(table_data), len(table_data[0])
            width, height = 1.0 / ncols, 1.0 / nrows

            for i in range(nrows):
                for j in range(ncols):
                    text = table_data[i][j]
                    if i == 0:
                        cell = table.add_cell(i, j, width, height, text=text, loc='center', facecolor='#0f172a',
                                              edgecolor='white')
                        cell.get_text().set_color('white')
                        cell.get_text().set_weight('bold')
                        cell.get_text().set_fontsize(11)
                    else:
                        if j == 0:
                            file_idx = legend_names.index(text)
                            color = colors[file_idx]
                            cell = table.add_cell(i, j, width, height, text=text, loc='center', facecolor=color,
                                                  edgecolor='white')
                            h = text.lstrip('#') if color.startswith('#') else '000000'
                            try:
                                b = (int(h[0:2], 16) * 0.299 + int(h[2:4], 16) * 0.587 + int(h[4:6], 16) * 0.114)
                                font_color = 'black' if b > 186 else 'white'
                            except Exception:
                                font_color = 'white'
                            cell.get_text().set_color(font_color)
                            cell.get_text().set_weight('bold')
                        else:
                            cell = table.add_cell(i, j, width, height, text=text, loc='center', facecolor='#f8fafc',
                                                  edgecolor='#e2e8f0')

            ax.add_table(table)
            plt.title(f"RMS Analytics ({unit}) - {plot_title}", fontsize=14, weight='bold', pad=15, color='#1e293b')
            safe_col = plot_title.replace(' ', '_').replace('/', '_').replace('[', '').replace(']', '')
            plt.savefig(os.path.join(rms_data_path, f"rms_table_{safe_col}.png"), bbox_inches='tight', pad_inches=0.1,
                        dpi=150)
            plt.close(fig)
        QMessageBox.information(self, "Success", f"RMS analytics exported successfully to:\n{rms_data_path}")


# ==========================================
# MODULE 1: PLOTTING STUDIO
# ==========================================
class PlottingStudio(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.file_settings = {}
        self.file_data = {}
        self.selected_files = []
        self.plot_settings = {}
        self.plot_lines = {}
        self.hidden_curves = set()
        self.cursor_enabled = True
        self.cursor = None
        self.pinned_annotations = []
        self.saved_mappings = []
        self.mapped_curves = {}
        self.custom_titles = {}
        self.ax_to_header = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(50)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(15, 0, 15, 0)
        topbar_layout.setSpacing(5)

        brand_container = QWidget()
        brand_container.setObjectName("brand_container")
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 6, 0, 6)
        brand_layout.setSpacing(0)
        brand_title = QLabel("Autosim")
        brand_title.setProperty("class", "brand_title")
        brand_layout.addWidget(brand_title)

        self.mode_switcher = NoScrollComboBox()
        self.mode_switcher.setProperty("class", "mode_switcher")
        self.mode_switcher.addItems(["Plotting", "Mobility", "Gear & Bearings"])
        self.mode_switcher.setCurrentText("Plotting")
        self.mode_switcher.currentTextChanged.connect(self.main_window.switch_mode)
        brand_layout.addWidget(self.mode_switcher)
        topbar_layout.addWidget(brand_container)

        actions = [
            ("📁 Define Files", self.show_define_files, "Start the file definition sequence"),
            ("🎨 Map Files & Style", self.show_file_selection, "Edit file mapping and styling"),
            ("📊 Select Curves", self.show_curve_columns, "Smart Match and Edit selected curves"),
            ("⚙️ Chart Settings", self.show_dynamic_settings, "Configure axes, limits, and fonts")
        ]
        for name, callback, tooltip in actions:
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            btn.setToolTip(tooltip)
            topbar_layout.addWidget(btn)

        save_session_btn = QPushButton("💾 Save Session")
        save_session_btn.clicked.connect(self.main_window.save_session)
        topbar_layout.addWidget(save_session_btn)

        load_session_btn = QPushButton("📂 Load Session")
        load_session_btn.clicked.connect(self.main_window.load_session)
        topbar_layout.addWidget(load_session_btn)

        topbar_layout.addStretch()

        rms_btn = QPushButton("📈 Calculate RMS")
        rms_btn.setObjectName("btn_rms")
        rms_btn.clicked.connect(self.show_rms_dialog)
        topbar_layout.addWidget(rms_btn)

        plot_btn = QPushButton("▶ Plot")
        plot_btn.setObjectName("btn_plot")
        plot_btn.clicked.connect(self.plot_data)
        topbar_layout.addWidget(plot_btn)

        export_btn = QPushButton("💾 Export")
        export_btn.setObjectName("btn_export")
        export_btn.clicked.connect(self.export_plots)
        topbar_layout.addWidget(export_btn)

        cursor_btn = QPushButton("🔍 Toggle Inspector")
        cursor_btn.setObjectName("btn_cursor")
        cursor_btn.clicked.connect(self.toggle_cursor)
        topbar_layout.addWidget(cursor_btn)

        reset_btn = QPushButton("⟲ Reset")
        reset_btn.setObjectName("btn_reset")
        reset_btn.clicked.connect(self.reset_gui)
        topbar_layout.addWidget(reset_btn)

        main_layout.addWidget(topbar)

        plot_area = QWidget()
        plot_area.setStyleSheet("background-color: #ffffff;")
        plot_layout = QVBoxLayout(plot_area)
        plot_layout.setContentsMargins(10, 10, 10, 10)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.show_context_menu)
        self.zoom_manager = SubplotZoomManager(self.canvas, self.main_window.statusBar,
                                               ignore_func=self.check_pin_annotation)
        plot_layout.addWidget(self.canvas)

        main_layout.addWidget(plot_area, stretch=1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.zoom_manager.reset_all_zooms()
        super().keyPressEvent(event)

    def check_pin_annotation(self, event):
        if hasattr(self, 'pinned_annotations'):
            for ann in list(self.pinned_annotations):
                if ann.contains(event)[0]:
                    if event.button == 3:
                        try:
                            ann.remove()
                        except Exception:
                            pass
                        self.pinned_annotations.remove(ann)
                        self.zoom_manager.suppress_next_context_menu = True
                        self.canvas.draw_idle()
                        if self.main_window.statusBar:
                            self.main_window.statusBar.showMessage("Pinned annotation removed.", 3000)
                        return True
                    return True  # Delegate left-click drag to the annotation

        if event.button == 1 and self.cursor_enabled and self.cursor and len(self.cursor.selections) > 0:
            sel = self.cursor.selections[0]
            ax = sel.artist.axes
            x, y = sel.target
            disp_pt = ax.transData.transform((x, y))
            dist = np.hypot(event.x - disp_pt[0], event.y - disp_pt[1])
            if dist < 20:
                color = sel.artist.get_color()
                text = sel.annotation.get_text()
                ann = ax.annotate(text, xy=(x, y), xytext=(30, 30), textcoords="offset points",
                                  bbox=dict(boxstyle="round,pad=0.5", fc="#ffffff", ec=color, lw=2, alpha=0.95),
                                  arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                                  fontsize=9)
                ann._draggable = ann.draggable(use_blit=True)
                self.pinned_annotations.append(ann)
                self.canvas.draw_idle()
                return True
        return False

    def toggle_cursor(self):
        self.cursor_enabled = not self.cursor_enabled
        self.main_window.statusBar.showMessage(f"Data inspector {'enabled' if self.cursor_enabled else 'disabled'}.")
        if self.file_data:
            self.plot_data()

    def show_error_message(self, message):
        self.main_window.statusBar.showMessage("Error: " + message.split('\n')[0], 5000)
        QMessageBox.critical(self, "Error", message)

    def show_context_menu(self, pos):
        if self.zoom_manager.suppress_next_context_menu:
            self.zoom_manager.suppress_next_context_menu = False
            return

        if not self.file_settings:
            return
        x, y = pos.x(), self.canvas.figure.bbox.height - pos.y()
        clicked_header = None
        clicked_ax = None
        for ax, header in self.ax_to_header.items():
            if ax.bbox.contains(x, y):
                clicked_header = header
                clicked_ax = ax
                break

        if self.zoom_manager.zoomed_axes and clicked_ax not in self.zoom_manager.zoomed_axes:
            self.zoom_manager.reset_all_zooms()
            return

        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; } QMenu::item { padding: 8px 25px; } QMenu::item:selected { background-color: #f1f5f9; color: #2563eb; font-weight: bold; }")

        if self.zoom_manager.zoomed_axes:
            reset_zoom_act = QAction("Reset Subplot Zoom (Esc)", self)
            reset_zoom_act.triggered.connect(self.zoom_manager.reset_all_zooms)
            menu.addAction(reset_zoom_act)
            menu.addSeparator()

        export_menu = menu.addMenu("Export Options")
        export_menu.addAction("Export Full Dashboard Image").triggered.connect(self.export_full_dashboard)
        export_menu.addAction("Export All Subplots Individually").triggered.connect(self.export_all_individual)
        if clicked_header:
            title = self.custom_titles.get(clicked_header, clicked_header)
            export_menu.addAction(f"Export '{title}' (Current Subplot)").triggered.connect(
                lambda _, h=clicked_header: self.export_single_subplot(h))
        menu.addSeparator()

        hide_menu = menu.addMenu("Hide/Show Curves")
        for file_name, settings in self.file_settings.items():
            chk = QCheckBox(settings["name"])
            chk.setChecked(file_name not in self.hidden_curves)
            chk.setStyleSheet("padding: 2px 10px; background-color: transparent;")
            chk.toggled.connect(lambda checked, fn=file_name: self.set_curve_visibility(fn, checked))
            widget_action = QWidgetAction(self)
            widget_action.setDefaultWidget(chk)
            hide_menu.addAction(widget_action)
        menu.addSeparator()

        axis_title_action = QAction("Global Axis Settings", self)
        axis_title_action.triggered.connect(self.show_dynamic_settings)
        menu.addAction(axis_title_action)

        if clicked_header:
            plot_title_action = QAction("Edit Plot Title (Current Subplot)", self)
            plot_title_action.triggered.connect(lambda _, h=clicked_header: self.edit_plot_title(h))
            menu.addAction(plot_title_action)
            menu.addSeparator()

        log_y_action = QAction("Log Y", self, checkable=True)
        log_y_action.setChecked(self.plot_settings.get("y_log", False))
        log_y_action.triggered.connect(self.toggle_log_y)
        menu.addAction(log_y_action)

        rms_action = QAction("Apply RMS (Rolling)", self, checkable=True)
        rms_action.setChecked(self.plot_settings.get("apply_rms", False))
        rms_action.triggered.connect(self.toggle_apply_rms)
        menu.addAction(rms_action)
        menu.addSeparator()

        curves_menu = menu.addMenu("Override Curve Color")
        for file_name, settings in self.file_settings.items():
            color_action = QAction(settings["name"], self)
            color_action.triggered.connect(lambda _, fn=file_name: self.change_curve_color(fn))
            curves_menu.addAction(color_action)

        legend_menu = menu.addMenu("Legend Position")
        positions = {"Top Right": "upper right", "Top Left": "upper left", "Bottom Right": "lower right",
                     "Bottom Left": "lower left", "Center": "center", "Top Center": "upper center",
                     "Bottom Center": "lower center"}
        for display_name, loc in positions.items():
            action = QAction(display_name, self)
            action.triggered.connect(lambda _, l=loc: self.set_legend_position(l))
            legend_menu.addAction(action)

        menu.exec(self.canvas.mapToGlobal(pos))

    def set_curve_visibility(self, file_name, is_visible):
        if is_visible:
            self.hidden_curves.discard(file_name)
        else:
            self.hidden_curves.add(file_name)
        self.plot_data()

    def edit_plot_title(self, header):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Plot Title")
        form = QFormLayout(dialog)
        title_edit = QLineEdit(self.custom_titles.get(header, header))
        form.addRow("Plot Title:", title_edit)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(dialog.accept)
        form.addRow("", apply_btn)
        if dialog.exec():
            self.custom_titles[header] = title_edit.text()
            self.plot_data()

    def toggle_log_y(self, checked):
        self.plot_settings["y_log"] = checked
        self.plot_data()

    def toggle_apply_rms(self, checked):
        self.plot_settings["apply_rms"] = checked
        self.plot_data()

    def change_curve_color(self, file_name):
        color = QColorDialog.getColor()
        if color.isValid():
            self.file_settings[file_name]["color"] = color.name()
            self.plot_data()

    def set_legend_position(self, position):
        self.plot_settings["legend_loc"] = position
        self.plot_data()

    def show_define_files(self):
        current_val = len(self.selected_files) if self.selected_files else 1
        dialog = DefineFilesDialog(current_count=current_val, parent=self)
        if dialog.exec():
            self.selected_files = dialog.selected_files
            self.show_file_selection(chained=True)

    def show_file_selection(self, chained=False):
        if not self.selected_files:
            return self.show_error_message("Please define working files first.")
        dialog = FileSelectionDialog(self.selected_files, self.file_settings, self.file_data, self)
        if dialog.exec():
            self.file_settings = dialog.file_settings
            self.file_data = dialog.file_data
            if chained:
                self.show_curve_columns(chained=True)
            else:
                self.plot_data()

    def show_curve_columns(self, chained=False):
        if not self.file_settings or not self.file_data:
            return self.show_error_message("Please map files in 'Map Files & Style' first.")
        dialog = CurveMappingDialog(self.file_settings, self.file_data, self.saved_mappings, self)
        if dialog.exec():
            self.saved_mappings = dialog.saved_mappings
            self.mapped_curves = {m['title']: m['map'] for m in self.saved_mappings if m['selected']}
            if chained:
                self.plot_data()

    def show_dynamic_settings(self):
        dialog = DynamicSettingsDialog(self.plot_settings, self)
        if dialog.exec():
            self.plot_settings = dialog.settings
            if self.file_data and self.mapped_curves:
                self.plot_data()

    def show_rms_dialog(self):
        if not self.file_settings or not self.mapped_curves:
            return self.show_error_message("Configure files and select curves before RMS analysis.")
        dialog = RMSDialog(self.file_settings, self.file_data, self.mapped_curves, self)
        dialog.exec()

    def on_cursor_add(self, sel):
        try:
            x, y = sel.target
            curve_label = sel.artist.get_label()
            curve_color = sel.artist.get_color()
            sel.annotation.set_text(f'Curve: {curve_label}\nFreq: {x:.2f} Hz\nAcc: {y:.2f} m/sec²')
            sel.annotation.get_bbox_patch().set(boxstyle="round,pad=0.5", fc="#ffffff", ec=curve_color, lw=2,
                                                alpha=0.95)
            sel.annotation.set_fontsize(9)
        except Exception:
            pass

    def plot_data(self):
        try:
            if not self.selected_files or not self.file_data or not self.mapped_curves:
                return

            if self.cursor:
                try:
                    self.cursor.remove()
                except Exception:
                    pass
                self.cursor = None

            for ann in getattr(self, 'pinned_annotations', []):
                try:
                    ann.remove()
                except Exception:
                    pass
            self.pinned_annotations.clear()

            self.figure.clear()
            self.plot_lines.clear()
            self.ax_to_header.clear()
            n_plots = len(self.mapped_curves)
            if n_plots == 0:
                return

            n_rows, n_cols = calculate_grid(n_plots)
            line_styles = {"solid": "-", "dashed": "--", "dotted": ":"}

            for i, (plot_title, mapping) in enumerate(self.mapped_curves.items(), 1):
                ax = self.figure.add_subplot(n_rows, n_cols, i)
                self.ax_to_header[ax] = plot_title

                for file_name, settings in self.file_settings.items():
                    if file_name in self.hidden_curves:
                        continue
                    if file_name in mapping and mapping[file_name] != "-- None --":
                        orig_col = mapping[file_name]
                        df = self.file_data.get(file_name)
                        if df is not None and orig_col in df.columns:
                            x_data = df.iloc[:, 0]
                            y_data = df[orig_col].copy()
                            if self.plot_settings.get("apply_rms", False):
                                try:
                                    y_data = np.sqrt((y_data ** 2).rolling(window=10, min_periods=1).mean())
                                except Exception:
                                    pass
                            line, = ax.plot(x_data, y_data, color=settings["color"], linewidth=settings["width"],
                                            linestyle=line_styles[settings["style"].lower()], label=settings["name"])
                            if settings["name"] not in self.plot_lines:
                                self.plot_lines[settings["name"]] = {}
                            self.plot_lines[settings["name"]][plot_title] = line

                ax.set_title(self.custom_titles.get(plot_title, plot_title), pad=10,
                             fontsize=self.plot_settings.get("title_size", 14))
                ax.set_xlabel(self.plot_settings.get("x_title", "Frequency"),
                              fontsize=self.plot_settings.get("axis_size", 12))
                ax.set_ylabel(self.plot_settings.get("y_title", "Acceleration m/sec²"),
                              fontsize=self.plot_settings.get("axis_size", 12))
                ax.tick_params(axis='both', labelsize=self.plot_settings.get("tick_size", 10))

                try:
                    if self.plot_settings.get("x_min") is not None:
                        ax.set_xlim(left=self.plot_settings["x_min"])
                    if self.plot_settings.get("x_max") is not None:
                        ax.set_xlim(right=self.plot_settings["x_max"])
                    if self.plot_settings.get("y_min") is not None:
                        ax.set_ylim(bottom=self.plot_settings["y_min"])
                    if self.plot_settings.get("y_max") is not None:
                        ax.set_ylim(top=self.plot_settings["y_max"])
                    if self.plot_settings.get("x_ticks") is not None:
                        ax.xaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["x_ticks"]))
                    if self.plot_settings.get("y_ticks") is not None:
                        ax.yaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["y_ticks"]))
                except Exception:
                    pass

                if "font_type" in self.plot_settings:
                    plt.rc('font', family=self.plot_settings["font_type"])
                if self.plot_settings.get("y_log", False):
                    ax.set_yscale('log')
                if self.plot_settings.get("legend_on", True):
                    ax.legend(loc=self.plot_settings.get("legend_loc", "best"), frameon=True, edgecolor='#cbd5e1',
                              fontsize=self.plot_settings.get("legend_size", 10))
                ax.grid(self.plot_settings.get("grid_on", True))

            try:
                self.figure.tight_layout(pad=2.0)
            except Exception:
                pass

            self.canvas.draw()
            self.zoom_manager.register_axes()

            if self.cursor_enabled:
                self.cursor = mplcursors.cursor(self.canvas.figure.axes, hover=True)
                self.cursor.connect("add", self.on_cursor_add)
            else:
                self.cursor = None

        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Plotting Error", f"Failed during plot generation:\n{tb}")

    def export_plots(self):
        if not self.mapped_curves:
            return self.show_error_message("No valid plots to export.")
        self.export_full_dashboard()

    def export_full_dashboard(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self.figure.savefig(os.path.join(folder, "Full_Dashboard_Plot.png"), dpi=200, bbox_inches='tight')
            QMessageBox.information(self, "Export Successful", f"Full Dashboard exported to:\n{folder}")

    def export_all_individual(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self._do_export_individuals(folder, list(self.mapped_curves.keys()))
            QMessageBox.information(self, "Export Successful", f"Individual subplots exported to:\n{folder}")

    def export_single_subplot(self, header):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self._do_export_individuals(folder, [header])
            title = self.custom_titles.get(header, header)
            QMessageBox.information(self, "Export Successful", f"'{title}' exported to:\n{folder}")

    def _do_export_individuals(self, folder, headers_to_export):
        line_styles = {"solid": "-", "dashed": "--", "dotted": ":"}
        for plot_title in headers_to_export:
            mapping = self.mapped_curves[plot_title]
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)

            for file_name, settings in self.file_settings.items():
                if file_name in self.hidden_curves:
                    continue
                if file_name in mapping and mapping[file_name] != "-- None --":
                    orig_col = mapping[file_name]
                    df = self.file_data.get(file_name)
                    if df is not None and orig_col in df.columns:
                        x_data = df.iloc[:, 0]
                        y_data = df[orig_col].copy()
                        if self.plot_settings.get("apply_rms", False):
                            try:
                                y_data = np.sqrt((y_data ** 2).rolling(window=10, min_periods=1).mean())
                            except Exception:
                                pass
                        ax.plot(x_data, y_data, color=settings["color"], linewidth=settings["width"],
                                linestyle=line_styles[settings["style"].lower()], label=settings["name"])

            title = self.custom_titles.get(plot_title, plot_title)
            ax.set_title(title, fontsize=self.plot_settings.get("title_size", 14))
            ax.set_xlabel(self.plot_settings.get("x_title", "Frequency"),
                          fontsize=self.plot_settings.get("axis_size", 12))
            ax.set_ylabel(self.plot_settings.get("y_title", "Acceleration m/sec²"),
                          fontsize=self.plot_settings.get("axis_size", 12))
            ax.tick_params(axis='both', labelsize=self.plot_settings.get("tick_size", 10))

            try:
                if self.plot_settings.get("x_min") is not None:
                    ax.set_xlim(left=self.plot_settings["x_min"])
                if self.plot_settings.get("x_max") is not None:
                    ax.set_xlim(right=self.plot_settings["x_max"])
                if self.plot_settings.get("y_min") is not None:
                    ax.set_ylim(bottom=self.plot_settings["y_min"])
                if self.plot_settings.get("y_max") is not None:
                    ax.set_ylim(top=self.plot_settings["y_max"])
                if self.plot_settings.get("x_ticks") is not None:
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["x_ticks"]))
                if self.plot_settings.get("y_ticks") is not None:
                    ax.yaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["y_ticks"]))
            except Exception:
                pass

            if "font_type" in self.plot_settings:
                plt.rc('font', family=self.plot_settings["font_type"])
            if self.plot_settings.get("y_log", False):
                ax.set_yscale('log')
            if self.plot_settings.get("legend_on", True):
                ax.legend(loc=self.plot_settings.get("legend_loc", "best"),
                          fontsize=self.plot_settings.get("legend_size", 10))
            ax.grid(self.plot_settings.get("grid_on", True))

            safe_title = title.replace(' ', '_').replace('/', '_').replace('[', '').replace(']', '').replace('\\', '_')
            filename = f"{safe_title}.png"
            fig.savefig(os.path.join(folder, filename), dpi=150, bbox_inches='tight')
            plt.close(fig)

    def reset_gui(self):
        reply = QMessageBox.question(self, 'Reset Workspace', 'Clear all Plotting data?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.file_settings.clear()
            self.file_data.clear()
            self.selected_files.clear()
            self.saved_mappings.clear()
            self.mapped_curves.clear()
            self.plot_settings.clear()
            self.custom_titles.clear()
            self.ax_to_header.clear()
            self.hidden_curves.clear()
            self.zoom_manager.register_axes()

            for ann in getattr(self, 'pinned_annotations', []):
                try:
                    ann.remove()
                except Exception:
                    pass
            self.pinned_annotations.clear()

            if self.cursor:
                try:
                    self.cursor.remove()
                except Exception:
                    pass
                self.cursor = None

            self.figure.clear()
            self.canvas.draw()


# ==========================================
# MODULE 2: MOBILITY STUDIO
# ==========================================
class MobilityNodesDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nodes, Directions & Data Source")
        self.setMinimumWidth(480)
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        left_group = QGroupBox("Detected Nodes")
        left_layout = QVBoxLayout(left_group)
        self.node_list = QListWidget()
        for node in self.settings.get("available_nodes", []):
            self.node_list.addItem(str(node))
        self.node_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for i in range(self.node_list.count()):
            if int(self.node_list.item(i).text()) in self.settings.get("nodes", []):
                self.node_list.item(i).setSelected(True)
        left_layout.addWidget(self.node_list)
        layout.addWidget(left_group)

        right_col = QVBoxLayout()

        # Dynamic Data Source Group (only shows checkboxes for data types present in the PCH files)
        source_group = QGroupBox("Data Source (Mobility from)")
        source_layout = QHBoxLayout(source_group)
        available_types = self.settings.get("available_data_types", [])
        selected_types = self.settings.get("selected_data_types", [])

        self.disp_check = None
        self.vel_check = None

        if "Displacement" in available_types:
            self.disp_check = QCheckBox("Displacement")
            # Default to checked if previously selected or if it's the only available option
            is_checked = ("Displacement" in selected_types) or (len(available_types) == 1)
            self.disp_check.setChecked(is_checked)
            source_layout.addWidget(self.disp_check)

        if "Velocity" in available_types:
            self.vel_check = QCheckBox("Velocity")
            is_checked = ("Velocity" in selected_types) or (len(available_types) == 1) or not selected_types
            self.vel_check.setChecked(is_checked)
            source_layout.addWidget(self.vel_check)

        right_col.addWidget(source_group)

        dir_group = QGroupBox("Translations")
        dir_layout = QHBoxLayout(dir_group)
        self.x_check = QCheckBox("X")
        self.x_check.setChecked(self.settings.get("x", True))
        self.y_check = QCheckBox("Y")
        self.y_check.setChecked(self.settings.get("y", True))
        self.z_check = QCheckBox("Z")
        self.z_check.setChecked(self.settings.get("z", True))
        dir_layout.addWidget(self.x_check)
        dir_layout.addWidget(self.y_check)
        dir_layout.addWidget(self.z_check)
        right_col.addWidget(dir_group)

        rot_group = QGroupBox("Rotations")
        rot_layout = QHBoxLayout(rot_group)
        self.rx_check = QCheckBox("Rx")
        self.rx_check.setChecked(self.settings.get("rx", False))
        self.ry_check = QCheckBox("Ry")
        self.ry_check.setChecked(self.settings.get("ry", False))
        self.rz_check = QCheckBox("Rz")
        self.rz_check.setChecked(self.settings.get("rz", False))
        rot_layout.addWidget(self.rx_check)
        rot_layout.addWidget(self.ry_check)
        rot_layout.addWidget(self.rz_check)
        right_col.addWidget(rot_group)

        right_col.addStretch()
        apply_btn = QPushButton("Apply & Generate Plots")
        apply_btn.clicked.connect(self.apply_selection)
        right_col.addWidget(apply_btn)
        layout.addLayout(right_col)

    def apply_selection(self):
        self.settings["nodes"] = [
            int(self.node_list.item(i).text())
            for i in range(self.node_list.count())
            if self.node_list.item(i).isSelected()
        ]

        selected_types = []
        if self.disp_check and self.disp_check.isChecked():
            selected_types.append("Displacement")
        if self.vel_check and self.vel_check.isChecked():
            selected_types.append("Velocity")
        self.settings["selected_data_types"] = selected_types

        self.settings["x"] = self.x_check.isChecked()
        self.settings["y"] = self.y_check.isChecked()
        self.settings["z"] = self.z_check.isChecked()
        self.settings["rx"] = self.rx_check.isChecked()
        self.settings["ry"] = self.ry_check.isChecked()
        self.settings["rz"] = self.rz_check.isChecked()

        if not self.settings["nodes"]:
            return QMessageBox.warning(self, "Warning", "Please select at least one node.")
        if not self.settings["selected_data_types"]:
            return QMessageBox.warning(self, "Warning", "Please select at least one data source.")
        has_trans = self.settings["x"] or self.settings["y"] or self.settings["z"]
        has_rot = self.settings["rx"] or self.settings["ry"] or self.settings["rz"]
        if not (has_trans or has_rot):
            return QMessageBox.warning(self, "Warning", "Please select at least one direction (Trans or Rot).")

        self.accept()


class MobilityStudio(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.selected_files = []
        self.file_settings = {}

        self.displacement_data = {}
        self.velocity_data = {}

        self.cursor_enabled = True
        self.cursor = None
        self.pinned_annotations = []
        self.hidden_curves = set()

        self.settings = {
            "x": True, "y": True, "z": True, "rx": False, "ry": False, "rz": False,
            "nodes": [], "available_nodes": [],
            "available_data_types": [],
            "selected_data_types": [],
            "target_stiffness_trans": 12500,
            "target_stiffness_rot": 12500
        }
        self.plot_settings = {"y_log": True, "x_title": "Frequency (Hz)", "y_title": "(m/s)/N", "show_stiffness": False,
                              "title_size": 14, "axis_size": 12, "tick_size": 10, "legend_size": 10}
        self.custom_titles = {}  # keyed by (node, 'Trans'|'Rot')
        self.ax_to_info = {}  # ax -> (node, 'Trans'|'Rot')

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(50)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(15, 0, 15, 0)
        topbar_layout.setSpacing(5)

        brand_container = QWidget()
        brand_container.setObjectName("brand_container")
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 6, 0, 6)
        brand_layout.setSpacing(0)
        brand_title = QLabel("Autosim")
        brand_title.setProperty("class", "brand_title")
        brand_layout.addWidget(brand_title)

        self.mode_switcher = NoScrollComboBox()
        self.mode_switcher.setProperty("class", "mode_switcher")
        self.mode_switcher.addItems(["Plotting", "Mobility", "Gear & Bearings"])
        self.mode_switcher.setCurrentText("Mobility")
        self.mode_switcher.currentTextChanged.connect(self.main_window.switch_mode)
        brand_layout.addWidget(self.mode_switcher)
        topbar_layout.addWidget(brand_container)

        actions = [
            ("📁 Define Files", self.show_define_files, "Start the file definition sequence"),
            ("🎨 Map Files & Style", self.show_file_selection, "Select PCH files and Styling"),
            ("🎯 Nodes", self.open_nodes_dialog, "Select nodes, directions, and data source")
        ]
        for name, callback, tooltip in actions:
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            btn.setToolTip(tooltip)
            topbar_layout.addWidget(btn)

        save_session_btn = QPushButton("💾 Save Session")
        save_session_btn.clicked.connect(self.main_window.save_session)
        topbar_layout.addWidget(save_session_btn)

        load_session_btn = QPushButton("📂 Load Session")
        load_session_btn.clicked.connect(self.main_window.load_session)
        topbar_layout.addWidget(load_session_btn)

        help_btn = QPushButton("?")
        help_btn.setObjectName("btn_help")
        help_btn.clicked.connect(self.show_guide)
        topbar_layout.addWidget(help_btn)

        topbar_layout.addStretch()

        plot_btn = QPushButton("▶ Plot")
        plot_btn.setObjectName("btn_plot")
        plot_btn.clicked.connect(self.plot_data)
        topbar_layout.addWidget(plot_btn)

        export_btn = QPushButton("💾 Export")
        export_btn.setObjectName("btn_export")
        export_btn.clicked.connect(self.export_plots)
        topbar_layout.addWidget(export_btn)

        cursor_btn = QPushButton("🔍 Toggle Inspector")
        cursor_btn.setObjectName("btn_cursor")
        cursor_btn.clicked.connect(self.toggle_cursor)
        topbar_layout.addWidget(cursor_btn)

        reset_btn = QPushButton("⟲ Reset")
        reset_btn.setObjectName("btn_reset")
        reset_btn.clicked.connect(self.reset)
        topbar_layout.addWidget(reset_btn)

        main_layout.addWidget(topbar)

        self.plot_frame = QFrame()
        self.plot_frame.setStyleSheet("background-color: #ffffff;")
        self.plot_frame_layout = QVBoxLayout(self.plot_frame)
        self.plot_frame_layout.setContentsMargins(10, 10, 10, 10)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.show_context_menu)
        self.zoom_manager = SubplotZoomManager(self.canvas, self.main_window.statusBar,
                                               ignore_func=self.check_pin_annotation)
        self.plot_frame_layout.addWidget(self.canvas)

        main_layout.addWidget(self.plot_frame, stretch=1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.zoom_manager.reset_all_zooms()
        super().keyPressEvent(event)

    def check_pin_annotation(self, event):
        if hasattr(self, 'pinned_annotations'):
            for ann in list(self.pinned_annotations):
                if ann.contains(event)[0]:
                    if event.button == 3:
                        try:
                            ann.remove()
                        except Exception:
                            pass
                        self.pinned_annotations.remove(ann)
                        self.zoom_manager.suppress_next_context_menu = True
                        self.canvas.draw_idle()
                        if self.main_window.statusBar:
                            self.main_window.statusBar.showMessage("Pinned annotation removed.", 3000)
                        return True
                    return True  # Delegate left-click drag to the annotation

        if event.button == 1 and self.cursor_enabled and self.cursor and len(self.cursor.selections) > 0:
            sel = self.cursor.selections[0]
            ax = sel.artist.axes
            x, y = sel.target
            disp_pt = ax.transData.transform((x, y))
            dist = np.hypot(event.x - disp_pt[0], event.y - disp_pt[1])
            if dist < 20:
                color = sel.artist.get_color()
                text = sel.annotation.get_text()
                ann = ax.annotate(text, xy=(x, y), xytext=(30, 30), textcoords="offset points",
                                  bbox=dict(boxstyle="round,pad=0.5", fc="#ffffff", ec=color, lw=2, alpha=0.95),
                                  arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                                  fontsize=9)
                ann._draggable = ann.draggable(use_blit=True)
                self.pinned_annotations.append(ann)
                self.canvas.draw_idle()
                return True
        return False

    def show_guide(self):
        guide_dialog = QDialog(self)
        guide_dialog.setWindowTitle("Quick Guide - Mobility Plotting")
        layout = QVBoxLayout(guide_dialog)
        guide_text = QLabel("""
            <h2>Quick Guide to Mobility Plotting</h2>
            <p>This tool helps you visualize mobility and displacement data from PCH files.</p>
            <p><b>How to Generate Plots:</b></p>
            <ul>
                <li><b>Define Files & Map:</b> Select any number of PCH files and assign custom names for the curves using the same flow as the Plotting studio.</li>
                <li><b>Nodes & Data Source:</b> Pick which nodes to plot, choose between <b>Velocity</b> ($VELOCITY) or <b>Displacement</b> ($DISPLACEMENTS) data, and select Translations (X, Y, Z) and Rotations (Rx, Ry, Rz).</li>
                <li><b>Interactive Zoom & Pins:</b> Left-click, hold, and drag to zoom in. <b>Left-click on a point</b> while hovering to drop a pinned, draggable label; <b>right-click a pinned label</b> to delete it! Press <b>Esc</b> to reset zoom.</li>
                <li><b>Right Click Options:</b> Context menu allows you to edit Plot Titles, Axis Limits, edit the Target Stiffness, and toggle between Mobility/Compliance and Dynamic Stiffness curves.</li>
                <li><b>Exporting:</b> Right-click any plot to export individual views.</li>
            </ul>
        """)
        guide_text.setWordWrap(True)
        layout.addWidget(guide_text)
        guide_dialog.setFixedWidth(400)
        guide_dialog.exec()

    def show_define_files(self):
        current_val = len(self.selected_files) if self.selected_files else 1
        dialog = DefineFilesDialog(current_count=current_val, parent=self)
        if dialog.exec():
            self.selected_files = dialog.selected_files
            self.show_file_selection()

    def show_file_selection(self):
        if not self.selected_files:
            return QMessageBox.warning(self, "Warning", "Please define working files first.")
        dialog = PCHFileSelectionDialog(self.selected_files, self.file_settings, self)
        if dialog.exec():
            self.file_settings = dialog.file_settings
            self.parse_all_pch()
            self.open_nodes_dialog()

    def open_nodes_dialog(self):
        if not self.displacement_data and not self.velocity_data:
            return QMessageBox.warning(self, "Warning", "Please process PCH files first.")
        dialog = MobilityNodesDialog(self.settings, self)
        if dialog.exec():
            self.plot_data()

    def parse_all_pch(self):
        self.displacement_data.clear()
        self.velocity_data.clear()
        for fn, settings in self.file_settings.items():
            if settings.get("enabled", True):
                path = settings.get("path")
                if path:
                    try:
                        with open(path, 'r') as file:
                            file_content = file.read()
                        disp, vel = self.parse_pch(file_content)
                        self.displacement_data[fn] = disp
                        self.velocity_data[fn] = vel
                    except Exception as e:
                        tb = traceback.format_exc()
                        QMessageBox.critical(self, "Error", f"Failed to load {path}:\n{tb}")
        self.list_nodes()

    def parse_pch(self, file_content):
        try:
            displacement_data = {}
            velocity_data = {}
            node_number = None
            active_dir = None
            velocity = False
            last_freq = None
            for line in file_content.split('\n'):
                if '$POINT ID' in line:
                    match = re.search(r'\d+', line)
                    if match:
                        node_number = int(match.group())
                elif '$LABEL' in line:
                    if '=' in line:
                        lbl = line.split('=')[1].strip().lower()
                        if re.search(r'(?:\b|_|-)(rx)(?:\b|_|-|$)', lbl):
                            active_dir = 'Rx'
                        elif re.search(r'(?:\b|_|-)(ry)(?:\b|_|-|$)', lbl):
                            active_dir = 'Ry'
                        elif re.search(r'(?:\b|_|-)(rz)(?:\b|_|-|$)', lbl):
                            active_dir = 'Rz'
                        elif re.search(r'(?:\b|_|-)(x)(?:\b|_|-|$)', lbl):
                            active_dir = 'X'
                        elif re.search(r'(?:\b|_|-)(y)(?:\b|_|-|$)', lbl):
                            active_dir = 'Y'
                        elif re.search(r'(?:\b|_|-)(z)(?:\b|_|-|$)', lbl):
                            active_dir = 'Z'
                        else:
                            if 'rx' in lbl:
                                active_dir = 'Rx'
                            elif 'ry' in lbl:
                                active_dir = 'Ry'
                            elif 'rz' in lbl:
                                active_dir = 'Rz'
                            elif 'x' in lbl:
                                active_dir = 'X'
                            elif 'y' in lbl:
                                active_dir = 'Y'
                            elif 'z' in lbl:
                                active_dir = 'Z'
                            else:
                                active_dir = None
                elif '$VELOCITY' in line:
                    velocity = True
                elif '$DISPLACEMENTS' in line:
                    velocity = False
                elif re.match(r'\s*\d+\.\d+E[+-]\d+\s+G', line):
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            f, x, y, z = float(parts[0]), float(parts[2]), float(parts[3]), float(parts[4])
                            last_freq = f
                            if node_number is not None and active_dir in ['X', 'Y', 'Z']:
                                target_dict = velocity_data if velocity else displacement_data
                                if node_number not in target_dict:
                                    target_dict[node_number] = {'X': [], 'Y': [], 'Z': [], 'Rx': [], 'Ry': [], 'Rz': []}
                                if active_dir == 'X':
                                    target_dict[node_number]['X'].append((f, x))
                                elif active_dir == 'Y':
                                    target_dict[node_number]['Y'].append((f, y))
                                elif active_dir == 'Z':
                                    target_dict[node_number]['Z'].append((f, z))
                        except ValueError:
                            pass
                elif line.startswith('-CONT-') and last_freq is not None:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            rx, ry, rz = float(parts[1]), float(parts[2]), float(parts[3])
                            if node_number is not None and active_dir in ['Rx', 'Ry', 'Rz']:
                                target_dict = velocity_data if velocity else displacement_data
                                if node_number not in target_dict:
                                    target_dict[node_number] = {'X': [], 'Y': [], 'Z': [], 'Rx': [], 'Ry': [], 'Rz': []}
                                if active_dir == 'Rx':
                                    target_dict[node_number]['Rx'].append((last_freq, rx))
                                elif active_dir == 'Ry':
                                    target_dict[node_number]['Ry'].append((last_freq, ry))
                                elif active_dir == 'Rz':
                                    target_dict[node_number]['Rz'].append((last_freq, rz))
                        except ValueError:
                            pass
                    last_freq = None
            return displacement_data, velocity_data
        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "PCH Parsing Error", f"Failed to parse PCH file:\n{tb}")
            return {}, {}

    def list_nodes(self):
        self.settings["available_nodes"] = []
        nodes = set()
        has_disp = False
        has_vel = False

        for data in self.displacement_data.values():
            if data:
                nodes.update(data.keys())
                has_disp = True

        for data in self.velocity_data.values():
            if data:
                nodes.update(data.keys())
                has_vel = True

        self.settings["available_nodes"] = sorted(nodes)

        avail_types = []
        if has_disp:
            avail_types.append("Displacement")
        if has_vel:
            avail_types.append("Velocity")
        self.settings["available_data_types"] = avail_types

        # Keep existing valid selections, or default to Velocity (or Displacement if only Disp exists)
        current_sel = [t for t in self.settings.get("selected_data_types", []) if t in avail_types]
        if not current_sel and avail_types:
            if "Velocity" in avail_types:
                current_sel = ["Velocity"]
            else:
                current_sel = [avail_types[0]]
        self.settings["selected_data_types"] = current_sel

    def toggle_cursor(self):
        self.cursor_enabled = not self.cursor_enabled
        self.main_window.statusBar.showMessage(
            f"Mobility Data inspector {'enabled' if self.cursor_enabled else 'disabled'}.")
        if self.settings["nodes"]:
            self.plot_data()

    def show_dynamic_settings(self):
        dialog = DynamicSettingsDialog(self.plot_settings, self)
        if dialog.exec():
            self.plot_settings = dialog.settings
            if self.settings["nodes"]:
                self.plot_data()

    def show_context_menu(self, pos):
        if self.zoom_manager.suppress_next_context_menu:
            self.zoom_manager.suppress_next_context_menu = False
            return

        if not self.settings["nodes"]:
            return
        x, y = pos.x(), self.canvas.figure.bbox.height - pos.y()
        clicked_info = None
        clicked_ax = None
        for ax, info in self.ax_to_info.items():
            if ax.bbox.contains(x, y):
                clicked_info = info
                clicked_ax = ax
                break

        if self.zoom_manager.zoomed_axes and clicked_ax not in self.zoom_manager.zoomed_axes:
            self.zoom_manager.reset_all_zooms()
            return

        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; } QMenu::item { padding: 8px 25px; } QMenu::item:selected { background-color: #f1f5f9; color: #2563eb; font-weight: bold; }")

        if self.zoom_manager.zoomed_axes:
            reset_zoom_act = QAction("Reset Subplot Zoom (Esc)", self)
            reset_zoom_act.triggered.connect(self.zoom_manager.reset_all_zooms)
            menu.addAction(reset_zoom_act)
            menu.addSeparator()

        export_menu = menu.addMenu("Export Options")
        export_menu.addAction("Export Full Dashboard Image").triggered.connect(self.export_full_dashboard)
        export_menu.addAction("Export All Subplots Individually").triggered.connect(self.export_all_individual)
        if clicked_info:
            title = self.custom_titles.get(clicked_info, f"Node {clicked_info[0]} ({clicked_info[1]})")
            export_menu.addAction(f"Export '{title}' (Current Subplot)").triggered.connect(
                lambda _, i=clicked_info: self.export_single_subplot(i))
        menu.addSeparator()

        hide_menu = menu.addMenu("Hide/Show Curves")
        for fname, settings in self.file_settings.items():
            if not settings.get("enabled", True): continue
            chk = QCheckBox(settings["name"])
            chk.setChecked(fname not in self.hidden_curves)
            chk.setStyleSheet("padding: 2px 10px; background-color: transparent;")
            chk.toggled.connect(lambda checked, fn=fname: self.set_curve_visibility(fn, checked))
            widget_action = QWidgetAction(self)
            widget_action.setDefaultWidget(chk)
            hide_menu.addAction(widget_action)
        menu.addSeparator()

        if clicked_info:
            ptype = clicked_info[1]
            target_action = QAction(f"Edit Target Curve Stiffness ({ptype})", self)
            target_action.triggered.connect(lambda _, p=ptype: self.edit_target_stiffness(p))
            menu.addAction(target_action)
            menu.addSeparator()

            plot_title_action = QAction("Edit Plot Title (Current Subplot)", self)
            plot_title_action.triggered.connect(lambda _, i=clicked_info: self.edit_plot_title(i))
            menu.addAction(plot_title_action)
            menu.addSeparator()

        stiff_action = QAction("Show Dynamic Stiffness Curves (Instead of Mobility)", self, checkable=True)
        stiff_action.setChecked(self.plot_settings.get("show_stiffness", False))
        stiff_action.triggered.connect(self.toggle_stiffness)
        menu.addAction(stiff_action)
        menu.addSeparator()

        axis_title_action = QAction("Global Axis Settings", self)
        axis_title_action.triggered.connect(self.show_dynamic_settings)
        menu.addAction(axis_title_action)

        log_y_action = QAction("Log Y", self, checkable=True)
        log_y_action.setChecked(self.plot_settings.get("y_log", True))
        log_y_action.triggered.connect(self.toggle_log_y)
        menu.addAction(log_y_action)

        legend_menu = menu.addMenu("Legend Position")
        positions = {"Top Right": "upper right", "Top Left": "upper left", "Bottom Right": "lower right",
                     "Bottom Left": "lower left", "Center": "center", "Top Center": "upper center",
                     "Bottom Center": "lower center"}
        for display_name, loc in positions.items():
            action = QAction(display_name, self)
            action.triggered.connect(lambda _, l=loc: self.set_legend_position(l))
            legend_menu.addAction(action)

        menu.exec(self.canvas.mapToGlobal(pos))

    def set_curve_visibility(self, file_name, is_visible):
        if is_visible:
            self.hidden_curves.discard(file_name)
        else:
            self.hidden_curves.add(file_name)
        self.plot_data()

    def edit_target_stiffness(self, ptype):
        setting_key = "target_stiffness_trans" if ptype == "Trans" else "target_stiffness_rot"
        current_val = float(self.settings.get(setting_key, 12500))
        val, ok = QInputDialog.getDouble(self, f"Target Stiffness ({ptype})",
                                         f"Enter Target Dynamic Stiffness ({ptype}):", current_val, 1, 10000000, 2)
        if ok:
            self.settings[setting_key] = val
            self.plot_data()
            self.main_window.statusBar.showMessage(f"Target stiffness for {ptype} updated to {val}")

    def toggle_stiffness(self, checked):
        self.plot_settings["show_stiffness"] = checked
        self.plot_data()

    def edit_plot_title(self, info_tuple):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Plot Title")
        form = QFormLayout(dialog)
        title_edit = QLineEdit(self.custom_titles.get(info_tuple, f"Node {info_tuple[0]} ({info_tuple[1]})"))
        form.addRow("Plot Title:", title_edit)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(dialog.accept)
        form.addRow("", apply_btn)
        if dialog.exec():
            self.custom_titles[info_tuple] = title_edit.text()
            self.plot_data()

    def toggle_log_y(self, checked):
        self.plot_settings["y_log"] = checked
        self.plot_data()

    def set_legend_position(self, position):
        self.plot_settings["legend_loc"] = position
        self.plot_data()

    def plot_mobility(self, ax, node, ptype):
        is_stiff = self.plot_settings.get("show_stiffness", False)
        selected_types = self.settings.get("selected_data_types", ["Velocity"])
        multi_type = len(selected_types) > 1

        def to_stiff(freqs, mob_vals):
            # mob_vals is already Mobility in (m/s)/N -> Dynamic Stiffness in N/mm
            return [(2 * np.pi * freq * 1e-3) / val if val != 0 else np.nan for freq, val in zip(freqs, mob_vals)]

        line_styles_map = {"solid": "-", "dashed": "--", "dotted": ":"}

        for fname, settings in self.file_settings.items():
            if fname in self.hidden_curves or not settings.get("enabled", True):
                continue

            name = settings["name"]
            color = settings["color"]
            base_style = line_styles_map.get(settings["style"].lower(), "-")
            width = settings["width"]

            for dtype in selected_types:
                source_dict = self.displacement_data if dtype == "Displacement" else self.velocity_data
                data = source_dict.get(fname, {})
                if not data or node not in data:
                    continue

                # Differentiate label and linestyle if user checks BOTH Displacement and Velocity to overlay them
                type_suffix = f" ({'Disp' if dtype == 'Displacement' else 'Vel'})" if multi_type else ""
                style = "--" if (multi_type and dtype == "Displacement" and base_style == "-") else base_style

                dir_pairs = [('X', 'x'), ('Y', 'y'), ('Z', 'z')] if ptype == 'Trans' else [('Rx', 'rx'), ('Ry', 'ry'), ('Rz', 'rz')]

                for dir_key, setting_key in dir_pairs:
                    if self.settings.get(setting_key) and data.get(node, {}).get(dir_key):
                        f, raw_vals = zip(*data[node][dir_key])

                        # 1. Convert raw PCH values to Mobility [(m/s)/N or (rad/s)/Nmm]
                        if dtype == "Displacement":
                            # Derivative in frequency domain: v = 2 * pi * f * u
                            mob_vals = [val * (2 * np.pi * freq) * 1e-3 for freq, val in zip(f, raw_vals)]
                        else:
                            mob_vals = [val * 1e-3 for val in raw_vals]

                        # 2. Convert to Dynamic Stiffness if toggled in right-click menu
                        y_vals = to_stiff(f, mob_vals) if is_stiff else mob_vals

                        ax.plot(f, y_vals, label=f'{name} {dir_key}{type_suffix}',
                                linestyle=style, color=color, linewidth=width)

        k_val = self.settings["target_stiffness_trans"] if ptype == 'Trans' else self.settings["target_stiffness_rot"]
        frequencies = np.arange(10, 4002, 2)
        if is_stiff:
            target_values = np.full_like(frequencies, k_val, dtype=float)
        else:
            target_values = (1.0 / k_val) * 2 * np.pi * frequencies * 1e-3

        ax.plot(frequencies, target_values, color='black', linestyle='-', label=f'Target ({k_val} N/mm)')

    def on_cursor_add(self, sel):
        try:
            x, y = sel.target
            curve_color = sel.artist.get_color()
            is_stiff = self.plot_settings.get("show_stiffness", False)
            if y != 0 and not np.isnan(y):
                k = y if is_stiff else ((1.0 / y) * 2 * np.pi * x * 1e-3)
                sel.annotation.set_text(f'Freq: {x:.2f} Hz\nK: {k:.2f} N/mm')
            else:
                sel.annotation.set_text(f'Freq: {x:.2f} Hz\nK: Undefined')
            sel.annotation.get_bbox_patch().set(boxstyle="round,pad=0.5", fc="#ffffff", ec=curve_color, lw=2,
                                                alpha=0.95)
            sel.annotation.set_fontsize(9)
        except Exception:
            pass

    def plot_data(self):
        try:
            if not self.settings["nodes"]:
                QMessageBox.critical(self, "Error", "Please select at least one node.")
                return

            if not self.settings.get("selected_data_types"):
                QMessageBox.critical(self, "Error",
                                     "Please select at least one data source (Displacement or Velocity).")
                return

            plot_trans = self.settings["x"] or self.settings["y"] or self.settings["z"]
            plot_rot = self.settings["rx"] or self.settings["ry"] or self.settings["rz"]
            if not (plot_trans or plot_rot):
                QMessageBox.critical(self, "Error", "Select at least one direction (Translation or Rotation).")
                return

            if self.cursor:
                try:
                    self.cursor.remove()
                except Exception:
                    pass
                self.cursor = None

            for ann in getattr(self, 'pinned_annotations', []):
                try:
                    ann.remove()
                except Exception:
                    pass
            self.pinned_annotations.clear()

            self.figure.clear()
            self.ax_to_info.clear()

            plots_to_make = []
            for node in self.settings["nodes"]:
                if plot_trans:
                    plots_to_make.append((node, 'Trans'))
                if plot_rot:
                    plots_to_make.append((node, 'Rot'))

            n_plots = len(plots_to_make)
            if n_plots == 0:
                return

            n_rows, n_cols = calculate_grid(n_plots)

            for i, info in enumerate(plots_to_make, 1):
                node, ptype = info
                ax = self.figure.add_subplot(n_rows, n_cols, i)
                self.ax_to_info[ax] = info

                self.plot_mobility(ax, node, ptype)

                custom_title = self.custom_titles.get(info, f"Node {node} ({ptype})")
                ax.set_title(custom_title, pad=10, fontsize=self.plot_settings.get("title_size", 14))

                default_y_title = "Dynamic Stiffness (N/mm)" if self.plot_settings.get("show_stiffness") else "(m/s)/N"
                user_y_title = self.plot_settings.get("y_title", default_y_title)
                if user_y_title in ("(m/s)/N", "Dynamic Stiffness (N/mm)"):
                    user_y_title = default_y_title

                ax.set_xlabel(self.plot_settings.get("x_title", "Frequency (Hz)"),
                              fontsize=self.plot_settings.get("axis_size", 12))
                ax.set_ylabel(user_y_title,
                              fontsize=self.plot_settings.get("axis_size", 12))
                ax.tick_params(axis='both', labelsize=self.plot_settings.get("tick_size", 10))

                try:
                    if self.plot_settings.get("x_min") is not None:
                        ax.set_xlim(left=self.plot_settings["x_min"])
                    if self.plot_settings.get("x_max") is not None:
                        ax.set_xlim(right=self.plot_settings["x_max"])
                    if self.plot_settings.get("y_min") is not None:
                        ax.set_ylim(bottom=self.plot_settings["y_min"])
                    if self.plot_settings.get("y_max") is not None:
                        ax.set_ylim(top=self.plot_settings["y_max"])
                    if self.plot_settings.get("x_ticks") is not None:
                        ax.xaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["x_ticks"]))
                    if self.plot_settings.get("y_ticks") is not None:
                        ax.yaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["y_ticks"]))
                except Exception:
                    pass

                if "font_type" in self.plot_settings:
                    plt.rc('font', family=self.plot_settings["font_type"])

                if self.plot_settings.get("y_log", True):
                    ax.set_yscale('log', nonpositive='clip')
                else:
                    ax.set_yscale('linear')

                if self.plot_settings.get("legend_on", True):
                    ax.legend(loc=self.plot_settings.get("legend_loc", "best"), frameon=True, edgecolor='#cbd5e1',
                              fontsize=self.plot_settings.get("legend_size", 10))
                ax.grid(self.plot_settings.get("grid_on", True))

            try:
                self.figure.tight_layout(pad=2.0)
            except Exception:
                pass

            self.canvas.draw()
            self.zoom_manager.register_axes()

            if self.cursor_enabled:
                self.cursor = mplcursors.cursor(self.canvas.figure.axes, hover=True)
                self.cursor.connect("add", self.on_cursor_add)
            else:
                self.cursor = None

        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Plotting Error", f"Failed during plot generation:\n{tb}")

    def export_plots(self):
        self.export_full_dashboard()

    def export_full_dashboard(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self.figure.savefig(os.path.join(folder, "Full_Dashboard_Mobility.png"), dpi=200, bbox_inches='tight')
            QMessageBox.information(self, "Export Successful", f"Full Dashboard exported to:\n{folder}")

    def export_all_individual(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            plots_to_make = []
            plot_trans = self.settings["x"] or self.settings["y"] or self.settings["z"]
            plot_rot = self.settings["rx"] or self.settings["ry"] or self.settings["rz"]
            for node in self.settings["nodes"]:
                if plot_trans:
                    plots_to_make.append((node, 'Trans'))
                if plot_rot:
                    plots_to_make.append((node, 'Rot'))
            self._do_export_individuals(folder, plots_to_make)
            QMessageBox.information(self, "Export Successful", f"Individual subplots exported to:\n{folder}")

    def export_single_subplot(self, info_tuple):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if folder:
            self._do_export_individuals(folder, [info_tuple])
            title = self.custom_titles.get(info_tuple, f"Node {info_tuple[0]} ({info_tuple[1]})")
            QMessageBox.information(self, "Export Successful", f"'{title}' exported to:\n{folder}")

    def _do_export_individuals(self, folder, infos_to_export):
        for info in infos_to_export:
            node, ptype = info
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            self.plot_mobility(ax, node, ptype)

            title = self.custom_titles.get(info, f"Node {node} ({ptype})")
            ax.set_title(title, fontsize=self.plot_settings.get("title_size", 14))

            default_y_title = "Dynamic Stiffness (N/mm)" if self.plot_settings.get("show_stiffness") else "(m/s)/N"
            user_y_title = self.plot_settings.get("y_title", default_y_title)
            if user_y_title in ("(m/s)/N", "Dynamic Stiffness (N/mm)"):
                user_y_title = default_y_title

            ax.set_xlabel(self.plot_settings.get("x_title", "Frequency (Hz)"),
                          fontsize=self.plot_settings.get("axis_size", 12))
            ax.set_ylabel(user_y_title,
                          fontsize=self.plot_settings.get("axis_size", 12))
            ax.tick_params(axis='both', labelsize=self.plot_settings.get("tick_size", 10))

            try:
                if self.plot_settings.get("x_min") is not None:
                    ax.set_xlim(left=self.plot_settings["x_min"])
                if self.plot_settings.get("x_max") is not None:
                    ax.set_xlim(right=self.plot_settings["x_max"])
                if self.plot_settings.get("y_min") is not None:
                    ax.set_ylim(bottom=self.plot_settings["y_min"])
                if self.plot_settings.get("y_max") is not None:
                    ax.set_ylim(top=self.plot_settings["y_max"])
                if self.plot_settings.get("x_ticks") is not None:
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["x_ticks"]))
                if self.plot_settings.get("y_ticks") is not None:
                    ax.yaxis.set_major_locator(ticker.MaxNLocator(self.plot_settings["y_ticks"]))
            except Exception:
                pass

            if "font_type" in self.plot_settings:
                plt.rc('font', family=self.plot_settings["font_type"])
            if self.plot_settings.get("y_log", True):
                ax.set_yscale('log', nonpositive='clip')
            else:
                ax.set_yscale('linear')
            if self.plot_settings.get("legend_on", True):
                ax.legend(loc=self.plot_settings.get("legend_loc", "best"),
                          fontsize=self.plot_settings.get("legend_size", 10))
            ax.grid(self.plot_settings.get("grid_on", True))

            safe_title = title.replace(' ', '_').replace('/', '_').replace('[', '').replace(']', '').replace('\\', '_')
            filename = f"{safe_title}.png"
            fig.savefig(os.path.join(folder, filename), dpi=150, bbox_inches='tight')
            plt.close(fig)

    def reset(self):
        reply = QMessageBox.question(self, 'Reset Workspace', 'Clear all Mobility data?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.selected_files.clear()
            self.file_settings.clear()
            self.displacement_data.clear()
            self.velocity_data.clear()
            self.settings.update({
                "x": True, "y": True, "z": True, "rx": False, "ry": False, "rz": False,
                "nodes": [], "available_nodes": [],
                "available_data_types": [], "selected_data_types": [],
                "target_stiffness_trans": 12500, "target_stiffness_rot": 12500
            })
            self.plot_settings = {
                "y_log": True, "x_title": "Frequency (Hz)", "y_title": "(m/s)/N",
                "show_stiffness": False, "title_size": 14, "axis_size": 12,
                "tick_size": 10, "legend_size": 10
            }
            self.custom_titles.clear()
            self.ax_to_info.clear()
            self.hidden_curves.clear()
            self.zoom_manager.register_axes()

            for ann in getattr(self, 'pinned_annotations', []):
                try:
                    ann.remove()
                except Exception:
                    pass
            self.pinned_annotations.clear()

            if self.cursor:
                try:
                    self.cursor.remove()
                except Exception:
                    pass
                self.cursor = None
            self.figure.clear()
            self.canvas.draw()


# ==========================================
# MODULE 3: GEAR & BEARINGS STUDIO
# ==========================================
class GBFileSelectionDialog(QDialog):
    def __init__(self, title, files_dict, custom_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.files = files_dict.copy()
        self.custom_names = custom_names
        self.layout = QVBoxLayout(self)
        self.setMinimumWidth(600)

        self.entries = {}
        self.name_entries = {}

        if not self.files:
            self.add_file_entry("File 1")
        else:
            for fname, fpath in self.files.items():
                self.add_file_entry(fname)

        add_btn = QPushButton("Add File")
        add_btn.clicked.connect(self.add_new_file)
        add_btn.setFixedWidth(80)
        self.layout.addWidget(add_btn)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #64748b;")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        ok_btn.setFixedWidth(80)
        cancel_btn.setFixedWidth(80)
        buttons.addStretch()
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        self.layout.addLayout(buttons)

    def add_file_entry(self, fname):
        hbox = QHBoxLayout()
        label = QLabel(fname)
        name_entry = QLineEdit(self.custom_names.get(fname, fname))
        entry = QLineEdit(self.files.get(fname, ""))
        entry.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(lambda: self.browse_file(fname, entry, name_entry))
        browse_btn.setFixedWidth(70)
        remove_btn = QPushButton("X")
        remove_btn.setStyleSheet("background-color: #ef4444; font-weight: bold;")
        remove_btn.clicked.connect(lambda: self.remove_file_entry(hbox, fname))
        remove_btn.setFixedWidth(30)
        hbox.addWidget(label)
        hbox.addWidget(name_entry)
        hbox.addWidget(entry)
        hbox.addWidget(browse_btn)
        hbox.addWidget(remove_btn)
        self.layout.insertLayout(self.layout.count() - 2, hbox)
        self.entries[fname] = entry
        self.name_entries[fname] = name_entry

    def add_new_file(self):
        existing_nums = [int(f.split()[1]) for f in self.entries.keys() if f.startswith("File ")]
        next_num = max(existing_nums, default=0) + 1
        self.add_file_entry(f"File {next_num}")

    def browse_file(self, fname, entry, name_entry):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, f"Select {fname}", "",
                                                       "Excel/CSV Files (*.xls *.xlsx *.csv)")
            if file_path:
                entry.setText(file_path)
                self.files[fname] = file_path
                if not name_entry.text() or name_entry.text() == fname:
                    name_entry.setText(os.path.basename(file_path))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to browse file: {str(e)}")

    def remove_file_entry(self, hbox, fname):
        for i in reversed(range(hbox.count())):
            widget = hbox.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.layout.removeItem(hbox)
        if fname in self.files:
            del self.files[fname]
        if fname in self.entries:
            del self.entries[fname]
        if fname in self.name_entries:
            del self.name_entries[fname]
        if fname in self.custom_names:
            del self.custom_names[fname]

    def get_custom_names(self):
        return {fname: self.name_entries[fname].text() for fname in self.name_entries}


class GearBearingsStudio(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.order_files = {}
        self.order_data = {}
        self.te_files = {}
        self.te_data = {}
        self.bearing_files = {}
        self.bearing_data = {}
        self.custom_names = {}
        self.bar_colors = {
            "File 1": "#0000FF", "File 2": "#FF0000", "File 3": "#00FF00", "File 4": "#808080",
            "File 5": "#FF00FF", "File 6": "#4B0082", "File 7": "#FFA500", "File 8": "#800080",
            "File 9": "#00FFFF", "File 10": "#A52A2A"
        }
        self.hidden_bars = set()

        self.forces_settings = {'Forces': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 0},
                                'Moments': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 0}}
        self.te_settings = {'Linear TE': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 4},
                            'Tilt TE': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 4}}
        self.bearing_settings = {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 0}

        self.forces_ax_to_title = {}
        self.te_ax_to_title = {}
        self.bearing_ax_to_title = {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Ribbon
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(50)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(15, 0, 15, 0)
        topbar_layout.setSpacing(5)

        brand_container = QWidget()
        brand_container.setObjectName("brand_container")
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 6, 0, 6)
        brand_layout.setSpacing(0)
        brand_title = QLabel("Autosim")
        brand_title.setProperty("class", "brand_title")
        brand_layout.addWidget(brand_title)

        self.mode_switcher = NoScrollComboBox()
        self.mode_switcher.setProperty("class", "mode_switcher")
        self.mode_switcher.addItems(["Plotting", "Mobility", "Gear & Bearings"])
        self.mode_switcher.setCurrentText("Gear & Bearings")
        self.mode_switcher.currentTextChanged.connect(self.main_window.switch_mode)
        brand_layout.addWidget(self.mode_switcher)
        topbar_layout.addWidget(brand_container)

        self.order_btn = QPushButton("📁 Order Files")
        self.te_btn = QPushButton("📁 TE Files")
        self.bearing_btn = QPushButton("📁 Bearing Files")
        for btn in [self.order_btn, self.te_btn, self.bearing_btn]:
            topbar_layout.addWidget(btn)

        self.order_btn.clicked.connect(
            lambda: self.show_file_dialog("Order Files", self.order_files, self.process_order_files,
                                          self.update_orders_checkboxes))
        self.te_btn.clicked.connect(
            lambda: self.show_file_dialog("TE Files", self.te_files, self.process_te_files, self.update_te_checkboxes))
        self.bearing_btn.clicked.connect(
            lambda: self.show_file_dialog("Bearing Files", self.bearing_files, self.process_bearing_files,
                                          self.update_bearing_checkboxes))

        topbar_layout.addStretch()

        save_session_btn = QPushButton("💾 Save Session")
        save_session_btn.clicked.connect(self.main_window.save_session)
        topbar_layout.addWidget(save_session_btn)

        load_session_btn = QPushButton("📂 Load Session")
        load_session_btn.clicked.connect(self.main_window.load_session)
        topbar_layout.addWidget(load_session_btn)

        help_btn = QPushButton("?")
        help_btn.setObjectName("btn_help")
        help_btn.clicked.connect(self.show_help)
        topbar_layout.addWidget(help_btn)

        reset_btn = QPushButton("⟲ Reset")
        reset_btn.setObjectName("btn_reset")
        reset_btn.clicked.connect(self.reset)
        topbar_layout.addWidget(reset_btn)

        main_layout.addWidget(topbar)

        # Workspace
        self.tabs = QTabWidget()
        self.forces_tab = QWidget()
        self.te_tab = QWidget()
        self.bearing_tab = QWidget()

        self.tabs.addTab(self.forces_tab, "Forces & Moments")
        self.tabs.addTab(self.te_tab, "Transmission Error")
        self.tabs.addTab(self.bearing_tab, "Bearing Stiffness")

        main_layout.addWidget(self.tabs)

        self.big_btn_style = "font-size: 14px; font-weight: bold; padding: 12px 10px; min-width: 160px;"

        self.setup_forces_tab()
        self.setup_te_tab()
        self.setup_bearing_tab()

    def show_file_dialog(self, title, files_dict, process_func, update_func):
        dialog = GBFileSelectionDialog(title, files_dict, self.custom_names, self)
        if dialog.exec():
            files_dict.clear()
            files_dict.update(dialog.files)
            self.custom_names.update(dialog.get_custom_names())
            process_func()
            update_func()
            self.main_window.statusBar.showMessage(f"{title} loaded successfully.")

    def process_order_files(self):
        self.order_data.clear()
        for fname, fpath in self.order_files.items():
            if fpath:
                try:
                    df = load_dataframe(fpath, header=None)
                    df = df.drop_duplicates(subset=[1], keep='first')
                    self.order_data[fname] = df
                except Exception:
                    tb = traceback.format_exc()
                    QMessageBox.warning(self, "Error", f"Failed to process {fname}:\n{tb}")

    def process_te_files(self):
        self.te_data.clear()
        for fname, fpath in self.te_files.items():
            if fpath:
                try:
                    df = load_dataframe(fpath, header=None)
                    te_values = {}
                    for stage, order_type in [("Primary", "Primary"), ("Secondary", "Secondary")]:
                        for harmonic in range(3):
                            harmonic_name = f"{stage[0]}{harmonic + 1}"
                            linear_te = self.get_te_values(df, "First Harmonic", order_type, harmonic)
                            tilt_te = self.get_te_values(df, "Tilt Transmission Error", order_type, harmonic)
                            te_values[f"{harmonic_name}_Linear"] = linear_te
                            te_values[f"{harmonic_name}_Tilt"] = tilt_te
                    self.te_data[fname] = te_values
                except Exception:
                    tb = traceback.format_exc()
                    QMessageBox.warning(self, "Error", f"Failed to process {fname}:\n{tb}")

    def process_bearing_files(self):
        self.bearing_data.clear()
        for fname, fpath in self.bearing_files.items():
            if fpath:
                try:
                    df = load_dataframe(fpath, header=None)
                    bearing_values = {}
                    for bearing in [f"B{i}" for i in range(1, 9)]:
                        for direction in ['X', 'Y', 'Z', 'Rx', 'Ry', 'Rz']:
                            cell = self.get_bearing_cell(bearing, direction)
                            if cell:
                                row, col = cell
                                if row < len(df) and col < len(df.columns):
                                    value = df.iloc[row, col]
                                    bearing_values[f"{bearing}_{direction}"] = float(value) / 1000 if not pd.isna(
                                        value) else 0
                                else:
                                    bearing_values[f"{bearing}_{direction}"] = 0
                    self.bearing_data[fname] = bearing_values
                except Exception:
                    tb = traceback.format_exc()
                    QMessageBox.warning(self, "Error", f"Failed to process {fname}:\n{tb}")

    def get_te_values(self, df, harmonic, order_type, order_index):
        cell_mappings = {
            "Primary_0": (23, 5), "Primary_1": (23, 7), "Primary_2": (23, 9),
            "Secondary_0": (24, 5), "Secondary_1": (24, 7), "Secondary_2": (24, 9),
            "Tilt_Primary_0": (26, 5), "Tilt_Primary_1": (26, 7), "Tilt_Primary_2": (26, 9),
            "Tilt_Secondary_0": (27, 5), "Tilt_Secondary_1": (27, 7), "Tilt_Secondary_2": (27, 9)
        }
        key = f"{order_type}_{order_index}" if harmonic == "First Harmonic" else f"Tilt_{order_type}_{order_index}"
        if key not in cell_mappings:
            return None
        row, col = cell_mappings[key]
        if row >= len(df) or col >= len(df.columns):
            return None
        value = df.iloc[row, col]
        return value if not pd.isna(value) else 0

    def get_bearing_cell(self, bearing, direction):
        bearing_map = {
            "B1": {"X": (4, 2), "Y": (5, 2), "Z": (6, 2), "Rx": (7, 2), "Ry": (8, 2), "Rz": (9, 2)},
            "B2": {"X": (4, 5), "Y": (5, 5), "Z": (6, 5), "Rx": (7, 5), "Ry": (8, 5), "Rz": (9, 5)},
            "B3": {"X": (4, 8), "Y": (5, 8), "Z": (6, 8), "Rx": (7, 8), "Ry": (8, 8), "Rz": (9, 8)},
            "B4": {"X": (4, 11), "Y": (5, 11), "Z": (6, 11), "Rx": (7, 11), "Ry": (8, 11), "Rz": (9, 11)},
            "B5": {"X": (14, 2), "Y": (15, 2), "Z": (16, 2), "Rx": (17, 2), "Ry": (18, 2), "Rz": (19, 2)},
            "B6": {"X": (14, 5), "Y": (15, 5), "Z": (16, 5), "Rx": (17, 5), "Ry": (18, 5), "Rz": (19, 5)},
            "B7": {"X": (14, 8), "Y": (15, 8), "Z": (16, 8), "Rx": (17, 8), "Ry": (18, 8), "Rz": (19, 8)},
            "B8": {"X": (14, 11), "Y": (15, 11), "Z": (16, 11), "Rx": (17, 11), "Ry": (18, 11), "Rz": (19, 11)}
        }
        return bearing_map.get(bearing, {}).get(direction, None)

    def update_orders_checkboxes(self):
        while self.orders_layout.count():
            child = self.orders_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.primary_orders.clear()
        self.secondary_orders.clear()

        primary_orders_set, secondary_orders_set = set(), set()
        for fname, df in self.order_data.items():
            primary_orders_set.update(df[df[0] == 2][1].unique())
            secondary_orders_set.update(df[df[0] == 1][1].unique())

        if primary_orders_set:
            label = QLabel("Primary")
            label.setStyleSheet("font-weight: bold; color: #003087;")
            self.orders_layout.addWidget(label)
            for order in sorted(primary_orders_set):
                order_str = f"{order:.2f}" if order % 1 != 0 else f"{int(order)}"
                rb = QRadioButton(order_str)
                rb.setChecked(False)
                rb.toggled.connect(self.plot_forces)
                self.orders_layout.addWidget(rb)
                self.primary_orders[order_str] = rb

        if secondary_orders_set:
            label = QLabel("Secondary")
            label.setStyleSheet("font-weight: bold; color: #003087;")
            self.orders_layout.addWidget(label)
            for order in sorted(secondary_orders_set):
                order_str = f"{order:.2f}" if order % 1 != 0 else f"{int(order)}"
                rb = QRadioButton(order_str)
                rb.setChecked(False)
                rb.toggled.connect(self.plot_forces)
                self.orders_layout.addWidget(rb)
                self.secondary_orders[order_str] = rb

    def update_te_checkboxes(self):
        pass

    def update_bearing_checkboxes(self):
        pass

    def setup_forces_tab(self):
        layout = QHBoxLayout(self.forces_tab)
        layout.setSpacing(5)
        plot_frame = QFrame()
        plot_layout = QVBoxLayout(plot_frame)
        plot_layout.setSpacing(2)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        self.forces_fig = plt.Figure(facecolor='#ffffff')
        self.forces_canvas = FigureCanvas(self.forces_fig)
        plot_layout.addWidget(self.forces_canvas, stretch=5)

        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.forces_font_combo = NoScrollComboBox()
        self.forces_font_combo.addItems(["Segoe UI", "Arial", "Times New Roman", "Calibri"])
        self.forces_font_combo.setCurrentText("Segoe UI")
        self.forces_font_combo.currentTextChanged.connect(self.plot_forces)

        self.forces_font_size = QDoubleSpinBox()
        self.forces_font_size.setRange(6, 20)
        self.forces_font_size.setValue(10)
        self.forces_font_size.valueChanged.connect(self.plot_forces)

        self.forces_grid_btn = QPushButton("⊞")
        self.forces_grid_btn.setObjectName("gridButton")
        self.forces_grid_btn.setCheckable(True)
        self.forces_grid_btn.setFixedSize(34, 34)
        self.forces_grid_btn.clicked.connect(self.plot_forces)

        self.forces_legend_btn = QPushButton("L")
        self.forces_legend_btn.setObjectName("legendButton")
        self.forces_legend_btn.setCheckable(True)
        self.forces_legend_btn.setFixedSize(34, 34)
        self.forces_legend_btn.clicked.connect(self.plot_forces)

        top_layout.addWidget(self.forces_font_combo)
        top_layout.addWidget(self.forces_font_size)
        top_layout.addStretch()
        top_layout.addWidget(self.forces_grid_btn)
        top_layout.addWidget(self.forces_legend_btn)
        plot_layout.addWidget(top_frame, stretch=0)
        layout.addWidget(plot_frame, stretch=5)

        right_frame = QFrame()
        right_frame.setFixedWidth(160)
        right_frame.setStyleSheet("QFrame {background-color: #f1f5f9; border-left: 1px solid #cbd5e1; padding: 5px;}")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(2)

        forces_group = QFrame()
        forces_layout = QVBoxLayout(forces_group)
        self.forces_checkboxes = {}
        for f in ['Fx', 'Fy', 'Fz']:
            cb = QCheckBox(f)
            cb.setChecked(True)
            forces_layout.addWidget(cb)
            self.forces_checkboxes[f] = cb

        moments_group = QFrame()
        moments_layout = QVBoxLayout(moments_group)
        self.moments_checkboxes = {}
        for m in ['Mx', 'My', 'Mz']:
            cb = QCheckBox(m)
            cb.setChecked(True)
            moments_layout.addWidget(cb)
            self.moments_checkboxes[m] = cb

        self.orders_group = QFrame()
        self.orders_layout = QVBoxLayout(self.orders_group)
        self.primary_orders = {}
        self.secondary_orders = {}

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 10)

        self.forces_plot_btn = QPushButton("Plot")
        self.forces_plot_btn.setStyleSheet(f"background-color: #059669; color: white; {self.big_btn_style}")
        self.forces_plot_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.forces_plot_btn.clicked.connect(self.plot_forces)

        self.forces_export_btn = QPushButton("Export")
        self.forces_export_btn.setStyleSheet(f"background-color: #0284c7; color: white; {self.big_btn_style}")
        self.forces_export_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.forces_export_btn.clicked.connect(lambda: self.export_plots("Forces_Moments"))

        button_layout.addWidget(self.forces_plot_btn)
        button_layout.addWidget(self.forces_export_btn)

        right_layout.addWidget(QLabel("Forces"))
        right_layout.addWidget(forces_group)
        right_layout.addWidget(QLabel("Moments"))
        right_layout.addWidget(moments_group)
        right_layout.addWidget(QLabel("Orders"))
        right_layout.addWidget(self.orders_group)
        right_layout.addStretch()
        right_layout.addWidget(button_frame)

        layout.addWidget(right_frame, stretch=1)
        self.forces_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.forces_canvas.customContextMenuRequested.connect(self.show_forces_context_menu)

    def setup_te_tab(self):
        layout = QHBoxLayout(self.te_tab)
        layout.setSpacing(5)
        plot_frame = QFrame()
        plot_layout = QVBoxLayout(plot_frame)
        plot_layout.setSpacing(2)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        self.te_fig = plt.Figure(facecolor='#ffffff')
        self.te_canvas = FigureCanvas(self.te_fig)
        plot_layout.addWidget(self.te_canvas, stretch=5)

        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.te_font_combo = NoScrollComboBox()
        self.te_font_combo.addItems(["Segoe UI", "Arial", "Times New Roman", "Calibri"])
        self.te_font_combo.setCurrentText("Segoe UI")
        self.te_font_combo.currentTextChanged.connect(self.plot_te)

        self.te_font_size = QDoubleSpinBox()
        self.te_font_size.setRange(6, 20)
        self.te_font_size.setValue(10)
        self.te_font_size.valueChanged.connect(self.plot_te)

        self.te_grid_btn = QPushButton("⊞")
        self.te_grid_btn.setObjectName("gridButton")
        self.te_grid_btn.setCheckable(True)
        self.te_grid_btn.setFixedSize(34, 34)
        self.te_grid_btn.clicked.connect(self.plot_te)

        self.te_legend_btn = QPushButton("L")
        self.te_legend_btn.setObjectName("legendButton")
        self.te_legend_btn.setCheckable(True)
        self.te_legend_btn.setFixedSize(34, 34)
        self.te_legend_btn.clicked.connect(self.plot_te)

        top_layout.addWidget(self.te_font_combo)
        top_layout.addWidget(self.te_font_size)
        top_layout.addStretch()
        top_layout.addWidget(self.te_grid_btn)
        top_layout.addWidget(self.te_legend_btn)
        plot_layout.addWidget(top_frame, stretch=0)
        layout.addWidget(plot_frame, stretch=5)

        right_frame = QFrame()
        right_frame.setFixedWidth(160)
        right_frame.setStyleSheet("QFrame {background-color: #f1f5f9; border-left: 1px solid #cbd5e1; padding: 5px;}")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(2)

        self.stage1_group = QFrame()
        self.stage1_layout = QVBoxLayout(self.stage1_group)
        self.stage1_radios = {}
        for h in ['P1', 'P2', 'P3']:
            rb = QRadioButton(h)
            rb.setChecked(False)
            self.stage1_layout.addWidget(rb)
            self.stage1_radios[h] = rb

        self.stage2_group = QFrame()
        self.stage2_layout = QVBoxLayout(self.stage2_group)
        self.stage2_radios = {}
        for h in ['S1', 'S2', 'S3']:
            rb = QRadioButton(h)
            rb.setChecked(False)
            self.stage2_layout.addWidget(rb)
            self.stage2_radios[h] = rb

        te_group = QFrame()
        te_layout = QVBoxLayout(te_group)
        self.te_checkboxes = {}
        for t in ['Linear TE', 'Tilt TE']:
            cb = QCheckBox(t)
            cb.setChecked(True)
            te_layout.addWidget(cb)
            self.te_checkboxes[t] = cb

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 10)

        self.te_plot_btn = QPushButton("Plot")
        self.te_plot_btn.setStyleSheet(f"background-color: #059669; color: white; {self.big_btn_style}")
        self.te_plot_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.te_plot_btn.clicked.connect(self.plot_te)

        self.te_export_btn = QPushButton("Export")
        self.te_export_btn.setStyleSheet(f"background-color: #0284c7; color: white; {self.big_btn_style}")
        self.te_export_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.te_export_btn.clicked.connect(lambda: self.export_plots("Transmission_Error"))

        button_layout.addWidget(self.te_plot_btn)
        button_layout.addWidget(self.te_export_btn)

        right_layout.addWidget(QLabel("1st Stage"))
        right_layout.addWidget(self.stage1_group)
        right_layout.addWidget(QLabel("2nd Stage"))
        right_layout.addWidget(self.stage2_group)
        right_layout.addWidget(QLabel("TE Types"))
        right_layout.addWidget(te_group)
        right_layout.addStretch()
        right_layout.addWidget(button_frame)

        layout.addWidget(right_frame, stretch=1)
        self.te_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.te_canvas.customContextMenuRequested.connect(self.show_te_context_menu)

    def setup_bearing_tab(self):
        layout = QHBoxLayout(self.bearing_tab)
        layout.setSpacing(5)
        plot_frame = QFrame()
        plot_layout = QVBoxLayout(plot_frame)
        plot_layout.setSpacing(2)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        self.bearing_fig = plt.Figure(facecolor='#ffffff')
        self.bearing_canvas = FigureCanvas(self.bearing_fig)
        plot_layout.addWidget(self.bearing_canvas, stretch=5)

        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.bearing_font_combo = NoScrollComboBox()
        self.bearing_font_combo.addItems(["Segoe UI", "Arial", "Times New Roman", "Calibri"])
        self.bearing_font_combo.setCurrentText("Segoe UI")
        self.bearing_font_combo.currentTextChanged.connect(self.plot_bearing)

        self.bearing_font_size = QDoubleSpinBox()
        self.bearing_font_size.setRange(6, 20)
        self.bearing_font_size.setValue(10)
        self.bearing_font_size.valueChanged.connect(self.plot_bearing)

        self.bearing_toggle_trans_rot = QPushButton("T")
        self.bearing_toggle_trans_rot.setCheckable(True)
        self.bearing_toggle_trans_rot.setStyleSheet("background-color: #2563eb; font-weight:bold; color: white;")
        self.bearing_toggle_trans_rot.setFixedSize(34, 34)
        self.bearing_toggle_trans_rot.clicked.connect(self.update_toggle_color)
        self.bearing_toggle_trans_rot.clicked.connect(self.plot_bearing)

        self.bearing_toggle_global = QPushButton("Y-Global")
        self.bearing_toggle_global.setCheckable(True)
        self.bearing_toggle_global.setStyleSheet(
            "background-color: #dc2626; font-size: 11px; font-weight:bold; color: white;")
        self.bearing_toggle_global.setMinimumWidth(80)
        self.bearing_toggle_global.setFixedHeight(34)
        self.bearing_toggle_global.clicked.connect(self.plot_bearing)

        self.bearing_grid_btn = QPushButton("⊞")
        self.bearing_grid_btn.setObjectName("gridButton")
        self.bearing_grid_btn.setCheckable(True)
        self.bearing_grid_btn.setFixedSize(34, 34)
        self.bearing_grid_btn.clicked.connect(self.plot_bearing)

        self.bearing_legend_btn = QPushButton("L")
        self.bearing_legend_btn.setObjectName("legendButton")
        self.bearing_legend_btn.setCheckable(True)
        self.bearing_legend_btn.setFixedSize(34, 34)
        self.bearing_legend_btn.clicked.connect(self.plot_bearing)

        top_layout.addWidget(self.bearing_font_combo)
        top_layout.addWidget(self.bearing_font_size)
        top_layout.addStretch()
        top_layout.addWidget(self.bearing_toggle_trans_rot)
        top_layout.addWidget(self.bearing_toggle_global)
        top_layout.addWidget(self.bearing_grid_btn)
        top_layout.addWidget(self.bearing_legend_btn)
        plot_layout.addWidget(top_frame, stretch=0)
        layout.addWidget(plot_frame, stretch=5)

        right_frame = QFrame()
        right_frame.setFixedWidth(160)
        right_frame.setStyleSheet("QFrame {background-color: #f1f5f9; border-left: 1px solid #cbd5e1; padding: 5px;}")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(2)

        self.bearing_group = QFrame()
        self.bearing_layout = QVBoxLayout(self.bearing_group)
        self.bearing_checkboxes = {}
        for i in range(1, 9):
            cb = QCheckBox(f"B{i}")
            cb.setChecked(True)
            self.bearing_layout.addWidget(cb)
            self.bearing_checkboxes[f"B{i}"] = cb

        self.trans_group = QFrame()
        self.trans_layout = QVBoxLayout(self.trans_group)
        self.trans_checkboxes = {}
        for d in ['X', 'Y', 'Z']:
            cb = QCheckBox(d)
            cb.setChecked(True)
            self.trans_layout.addWidget(cb)
            self.trans_checkboxes[d] = cb

        self.rot_group = QFrame()
        self.rot_layout = QVBoxLayout(self.rot_group)
        self.rot_checkboxes = {}
        for d in ['Rx', 'Ry', 'Rz']:
            cb = QCheckBox(d)
            cb.setChecked(True)
            self.rot_layout.addWidget(cb)
            self.rot_checkboxes[d] = cb

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 10)

        self.bearing_plot_btn = QPushButton("Plot")
        self.bearing_plot_btn.setStyleSheet(f"background-color: #059669; color: white; {self.big_btn_style}")
        self.bearing_plot_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bearing_plot_btn.clicked.connect(self.plot_bearing)

        self.bearing_export_btn = QPushButton("Export")
        self.bearing_export_btn.setStyleSheet(f"background-color: #0284c7; color: white; {self.big_btn_style}")
        self.bearing_export_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bearing_export_btn.clicked.connect(lambda: self.export_plots("Bearing_Stiffness"))

        button_layout.addWidget(self.bearing_plot_btn)
        button_layout.addWidget(self.bearing_export_btn)

        right_layout.addWidget(QLabel("Bearings"))
        right_layout.addWidget(self.bearing_group)
        right_layout.addWidget(QLabel("Translations"))
        right_layout.addWidget(self.trans_group)
        right_layout.addWidget(QLabel("Rotations"))
        right_layout.addWidget(self.rot_group)
        right_layout.addStretch()
        right_layout.addWidget(button_frame)

        layout.addWidget(right_frame, stretch=1)
        self.bearing_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bearing_canvas.customContextMenuRequested.connect(self.show_bearing_context_menu)

    def update_toggle_color(self):
        if self.bearing_toggle_trans_rot.isChecked():
            self.bearing_toggle_trans_rot.setText("R")
            self.bearing_toggle_trans_rot.setStyleSheet("background-color: #0369a1; font-weight:bold; color: white;")
        else:
            self.bearing_toggle_trans_rot.setText("T")
            self.bearing_toggle_trans_rot.setStyleSheet("background-color: #2563eb; font-weight:bold; color: white;")

    def plot_forces(self):
        try:
            self.forces_fig.clear()
            self.forces_ax_to_title.clear()
            ax1 = self.forces_fig.add_subplot(121)
            ax2 = self.forces_fig.add_subplot(122)
            self.forces_ax_to_title[ax1] = "Forces"
            self.forces_ax_to_title[ax2] = "Moments"

            selected_forces = [f for f in self.forces_checkboxes if self.forces_checkboxes[f].isChecked()]
            selected_moments = [m for m in self.moments_checkboxes if self.moments_checkboxes[m].isChecked()]
            selected_primary = [o for o in self.primary_orders if self.primary_orders[o].isChecked()]
            selected_secondary = [o for o in self.secondary_orders if self.secondary_orders[o].isChecked()]
            selected_orders = selected_primary + selected_secondary

            if not (selected_forces or selected_moments) or not selected_orders or not self.order_data:
                return

            force_cols = {'Fx': 2, 'Fy': 4, 'Fz': 6}
            moment_cols = {'Mx': 8, 'My': 10, 'Mz': 12}
            num_files = len([f for f in self.order_data if f not in self.hidden_bars])
            bar_width = 0.8 / num_files if num_files > 0 else 0.8

            all_force_values, all_moment_values = [], []

            for i, (fname, df) in enumerate(self.order_data.items()):
                if fname in self.hidden_bars:
                    continue
                custom_name = self.custom_names.get(fname, fname)
                color = self.bar_colors.get(fname, f'C{i}')
                df_orders = df[df[1].apply(lambda x: f"{x:.2f}" if x % 1 != 0 else f"{int(x)}").isin(selected_orders)]

                if not df_orders.empty:
                    if selected_forces:
                        x = np.arange(len(selected_forces))
                        force_values = [abs(df_orders[force_cols[f]].mean()) for f in selected_forces]
                        all_force_values.extend(force_values)
                        bars1 = ax1.bar(x + i * bar_width, force_values, bar_width, label=custom_name, color=color,
                                        zorder=2)
                        for bar in bars1:
                            h = bar.get_height()
                            ax1.text(bar.get_x() + bar.get_width() / 2, h,
                                     f'{h:.{self.forces_settings["Forces"]["decimals"]}f}', ha='center', va='bottom',
                                     fontsize=self.forces_font_size.value(), zorder=3)

                    if selected_moments:
                        x = np.arange(len(selected_moments))
                        moment_values = [abs(df_orders[moment_cols[m]].mean()) for m in selected_moments]
                        all_moment_values.extend(moment_values)
                        bars2 = ax2.bar(x + i * bar_width, moment_values, bar_width, label=custom_name, color=color,
                                        zorder=2)
                        for bar in bars2:
                            h = bar.get_height()
                            ax2.text(bar.get_x() + bar.get_width() / 2, h,
                                     f'{h:.{self.forces_settings["Moments"]["decimals"]}f}', ha='center', va='bottom',
                                     fontsize=self.forces_font_size.value(), zorder=3)

            force_max = max(all_force_values) * 1.1 if all_force_values else 10
            moment_max = max(all_moment_values) * 1.1 if all_moment_values else 10

            forces_settings = self.forces_settings['Forces']
            moments_settings = self.forces_settings['Moments']

            if selected_forces:
                ax1.set_title("Forces", fontfamily=self.forces_font_combo.currentText(),
                              fontsize=forces_settings['title_size'])
                ax1.set_ylabel("Force (N)", fontfamily=self.forces_font_combo.currentText(),
                               fontsize=self.forces_font_size.value())
                ax1.set_xticks(np.arange(len(selected_forces)) + bar_width * (num_files - 1) / 2)
                ax1.set_xticklabels(selected_forces, fontfamily=self.forces_font_combo.currentText(),
                                    fontsize=self.forces_font_size.value())
                y_max_f = forces_settings['y_max'] if forces_settings['y_max'] is not None else force_max
                ax1.set_ylim(0, y_max_f)
                ax1.set_yticks(np.linspace(0, y_max_f, forces_settings['y_levels']))
                ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                ax1.tick_params(axis='both', labelsize=self.forces_font_size.value())
                if self.forces_grid_btn.isChecked():
                    ax1.grid(True, zorder=1)
                if num_files > 1 and self.forces_legend_btn.isChecked():
                    ax1.legend()

            if selected_moments:
                ax2.set_title("Moments", fontfamily=self.forces_font_combo.currentText(),
                              fontsize=moments_settings['title_size'])
                ax2.set_ylabel("Moment (N-mm)", fontfamily=self.forces_font_combo.currentText(),
                               fontsize=self.forces_font_size.value())
                ax2.set_xticks(np.arange(len(selected_moments)) + bar_width * (num_files - 1) / 2)
                ax2.set_xticklabels(selected_moments, fontfamily=self.forces_font_combo.currentText(),
                                    fontsize=self.forces_font_size.value())
                y_max_m = moments_settings['y_max'] if moments_settings['y_max'] is not None else moment_max
                ax2.set_ylim(0, y_max_m)
                ax2.set_yticks(np.linspace(0, y_max_m, moments_settings['y_levels']))
                ax2.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                ax2.tick_params(axis='both', labelsize=self.forces_font_size.value())
                if self.forces_grid_btn.isChecked():
                    ax2.grid(True, zorder=1)
                if num_files > 1 and self.forces_legend_btn.isChecked():
                    ax2.legend()

            self.forces_fig.tight_layout(pad=1.5)
            self.forces_canvas.draw()
        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Plotting Error", f"Failed during plot generation:\n{tb}")

    def plot_te(self):
        try:
            self.te_fig.clear()
            self.te_ax_to_title.clear()
            ax1 = self.te_fig.add_subplot(121)
            ax2 = self.te_fig.add_subplot(122)
            self.te_ax_to_title[ax1] = "Linear TE"
            self.te_ax_to_title[ax2] = "Tilt TE"

            selected_stage1 = [h for h in self.stage1_radios if self.stage1_radios[h].isChecked()]
            selected_stage2 = [h for h in self.stage2_radios if self.stage2_radios[h].isChecked()]
            selected_harmonics = selected_stage1 + selected_stage2
            show_linear = self.te_checkboxes['Linear TE'].isChecked()
            show_tilt = self.te_checkboxes['Tilt TE'].isChecked()

            if not selected_harmonics or not self.te_data or not (show_linear or show_tilt):
                return

            num_files = len([f for f in self.te_data if f not in self.hidden_bars])
            bar_width = 0.8 / num_files if num_files > 0 else 0.8
            linear_values, tilt_values = [], []

            for i, fname in enumerate(self.te_data.keys()):
                if fname in self.hidden_bars:
                    continue
                custom_name = self.custom_names.get(fname, fname)
                color = self.bar_colors.get(fname, f'C{i}')

                for j, harmonic in enumerate(selected_harmonics):
                    linear_val = self.te_data[fname][f"{harmonic}_Linear"]
                    tilt_val = self.te_data[fname][f"{harmonic}_Tilt"]

                    if show_linear:
                        x = np.arange(len(selected_harmonics))
                        bars1 = ax1.bar(x[j] + i * bar_width, linear_val, bar_width,
                                        label=custom_name if j == 0 else "", color=color, zorder=2)
                        linear_values.append(linear_val)
                        for bar in bars1:
                            h = bar.get_height()
                            ax1.text(bar.get_x() + bar.get_width() / 2, h,
                                     f'{h:.{self.te_settings["Linear TE"]["decimals"]}f}', ha='center', va='bottom',
                                     fontsize=self.te_font_size.value(), zorder=3)

                    if show_tilt:
                        x = np.arange(len(selected_harmonics))
                        bars2 = ax2.bar(x[j] + i * bar_width, tilt_val, bar_width,
                                        label=custom_name if j == 0 else "", color=color, zorder=2)
                        tilt_values.append(tilt_val)
                        for bar in bars2:
                            h = bar.get_height()
                            ax2.text(bar.get_x() + bar.get_width() / 2, h,
                                     f'{h:.{self.te_settings["Tilt TE"]["decimals"]}f}', ha='center', va='bottom',
                                     fontsize=self.te_font_size.value(), zorder=3)

            linear_max = max(linear_values) * 1.3 if linear_values else 0.1
            tilt_max = max(tilt_values) * 1.3 if tilt_values else 0.1

            linear_settings = self.te_settings['Linear TE']
            tilt_settings = self.te_settings['Tilt TE']

            if show_linear:
                ax1.set_title("Linear TE", fontfamily=self.te_font_combo.currentText(),
                              fontsize=linear_settings['title_size'])
                ax1.set_ylabel("TE (μm)", fontfamily=self.te_font_combo.currentText(),
                               fontsize=self.te_font_size.value())
                ax1.set_xticks(np.arange(len(selected_harmonics)) + bar_width * (num_files - 1) / 2)
                ax1.set_xticklabels(selected_harmonics, fontfamily=self.te_font_combo.currentText(),
                                    fontsize=self.te_font_size.value())
                y_max_l = linear_settings['y_max'] if linear_settings['y_max'] is not None else linear_max
                ax1.set_ylim(0, y_max_l)
                ax1.set_yticks(np.linspace(0, y_max_l, linear_settings['y_levels']))
                ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
                ax1.tick_params(axis='both', labelsize=self.te_font_size.value())
                if self.te_grid_btn.isChecked():
                    ax1.grid(True, zorder=1)
                if num_files > 1 and self.te_legend_btn.isChecked():
                    ax1.legend()

            if show_tilt:
                ax2.set_title("Tilt TE", fontfamily=self.te_font_combo.currentText(),
                              fontsize=tilt_settings['title_size'])
                ax2.set_ylabel("TE (m-rad)", fontfamily=self.te_font_combo.currentText(),
                               fontsize=self.te_font_size.value())
                ax2.set_xticks(np.arange(len(selected_harmonics)) + bar_width * (num_files - 1) / 2)
                ax2.set_xticklabels(selected_harmonics, fontfamily=self.te_font_combo.currentText(),
                                    fontsize=self.te_font_size.value())
                y_max_t = tilt_settings['y_max'] if tilt_settings['y_max'] is not None else tilt_max
                ax2.set_ylim(0, y_max_t)
                ax2.set_yticks(np.linspace(0, y_max_t, tilt_settings['y_levels']))
                ax2.yaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
                ax2.tick_params(axis='both', labelsize=self.te_font_size.value())
                if self.te_grid_btn.isChecked():
                    ax2.grid(True, zorder=1)
                if num_files > 1 and self.te_legend_btn.isChecked():
                    ax2.legend()

            self.te_fig.tight_layout(pad=2.0)
            self.te_canvas.draw()
        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Plotting Error", f"Failed during plot generation:\n{tb}")

    def plot_bearing(self):
        try:
            self.bearing_fig.clear()
            self.bearing_ax_to_title.clear()
            selected_bearings = [b for b in self.bearing_checkboxes if self.bearing_checkboxes[b].isChecked()]
            is_trans = not self.bearing_toggle_trans_rot.isChecked()
            components = [t for t in self.trans_checkboxes if self.trans_checkboxes[t].isChecked()] if is_trans else [
                r for r in self.rot_checkboxes if self.rot_checkboxes[r].isChecked()]

            if not self.bearing_data or not selected_bearings or not components:
                return

            num_files = len([f for f in self.bearing_data if f not in self.hidden_bars])
            bar_width = 0.8 / num_files if num_files > 0 else 0.8
            global_max = 0
            axes = []

            for i, bearing in enumerate(selected_bearings):
                ax = self.bearing_fig.add_subplot(2, 4, i + 1)
                axes.append(ax)
                title = f"{bearing} {'Trans' if is_trans else 'Rot'}"
                self.bearing_ax_to_title[ax] = title
                ax.set_title(title, fontfamily=self.bearing_font_combo.currentText(),
                             fontsize=self.bearing_settings['title_size'])
                if self.bearing_grid_btn.isChecked():
                    ax.grid(True, zorder=1)

                all_values = []
                for j, (fname, data) in enumerate(self.bearing_data.items()):
                    if fname in self.hidden_bars:
                        continue
                    custom_name = self.custom_names.get(fname, fname)
                    color = self.bar_colors.get(fname, f'C{j}')
                    values = [data[f"{bearing}_{comp}"] for comp in components]
                    all_values.extend(values)
                    x = np.arange(len(components))
                    bars = ax.bar(x + j * bar_width, values, bar_width, label=custom_name if i == 0 else "",
                                  color=color, zorder=2)
                    for bar in bars:
                        h = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, h + (self.bearing_font_size.value() * 0.3),
                                f'{h:.{self.bearing_settings["decimals"]}f}', ha='center', va='bottom', rotation=90,
                                fontsize=self.bearing_font_size.value(), zorder=3)

                ax.set_xticks(np.arange(len(components)) + bar_width * (num_files - 1) / 2)
                ax.set_xticklabels(components, fontfamily=self.bearing_font_combo.currentText(),
                                   fontsize=self.bearing_font_size.value())
                local_max = max(all_values) * 1.2 if all_values else 10
                global_max = max(global_max, local_max)
                y_max_b = self.bearing_settings['y_max'] if self.bearing_settings['y_max'] is not None else local_max
                ax.set_ylim(0, y_max_b)
                ax.set_yticks(np.linspace(0, y_max_b, self.bearing_settings['y_levels']))
                ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
                ax.tick_params(axis='both', labelsize=self.bearing_font_size.value())
                if num_files > 1 and self.bearing_legend_btn.isChecked() and i == 0:
                    ax.legend()

            if self.bearing_toggle_global.isChecked():
                for ax in axes:
                    ax.set_ylim(0, self.bearing_settings['y_max'] if self.bearing_settings[
                                                                         'y_max'] is not None else global_max)
                    ax.set_yticks(np.linspace(0, ax.get_ylim()[1], self.bearing_settings['y_levels']))

            self.bearing_fig.supylabel(f"Stiffness ({'kN/mm' if is_trans else 'kNmm/rad'})",
                                       fontfamily=self.bearing_font_combo.currentText(),
                                       fontsize=self.bearing_font_size.value())
            self.bearing_fig.tight_layout(pad=1.5)
            self.bearing_canvas.draw()
        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Plotting Error", f"Failed during plot generation:\n{tb}")

    def show_forces_context_menu(self, pos):
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu {background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; color: #1e293b;} QMenu::item {padding: 6px 24px;} QMenu::item:selected {background-color: #f1f5f9; color: #2563eb; font-weight:bold;}")

        x, y = pos.x(), self.forces_canvas.figure.bbox.height - pos.y()
        clicked_title = None
        for ax, title in self.forces_ax_to_title.items():
            if ax.bbox.contains(x, y):
                clicked_title = title
                break

        e_menu = menu.addMenu("Export Options")
        e_menu.addAction("Export Full Dashboard Image").triggered.connect(
            lambda: self._export_gb_full(self.forces_fig, "Forces_Moments"))
        e_menu.addAction("Export All Subplots Individually").triggered.connect(
            lambda: self._export_gb_individuals("Forces_Moments", None))
        if clicked_title:
            e_menu.addAction(f"Export '{clicked_title}' (Current Subplot)").triggered.connect(
                lambda _, t=clicked_title: self._export_gb_individuals("Forces_Moments", [t]))
        menu.addSeparator()

        c_menu = menu.addMenu("Bar Colors")
        h_menu = menu.addMenu("Hide/Show Bars")
        s_menu = menu.addMenu("Plot Settings")
        for fname in self.order_files.keys():
            custom_name = self.custom_names.get(fname, fname)
            c_menu.addAction(custom_name).triggered.connect(
                lambda _, f=fname: self.change_bar_color(f, self.plot_forces))

            h_action = QAction(custom_name, self, checkable=True)
            h_action.setChecked(fname not in self.hidden_bars)
            h_action.triggered.connect(lambda checked, f=fname: self.toggle_bar_visibility(f, self.plot_forces))
            h_menu.addAction(h_action)

        for key, tab in [('Forces', s_menu.addMenu("Forces")), ('Moments', s_menu.addMenu("Moments"))]:
            tab.addAction("Y-Axis Max").triggered.connect(
                lambda _, k=key: self.set_y_max(k, self.forces_settings, self.plot_forces))
            tab.addAction("Y-Axis Levels").triggered.connect(
                lambda _, k=key: self.set_y_levels(k, self.forces_settings, self.plot_forces))
            tab.addAction("Title Font Size").triggered.connect(
                lambda _, k=key: self.set_title_size(k, self.forces_settings, self.plot_forces))
            dec_menu = tab.addMenu("Decimal Places")
            for d in [1, 2, 3, 4]:
                dec_menu.addAction(f"{d} Decimal{'s' if d > 1 else ''}").triggered.connect(
                    lambda _, d=d, k=key: self.set_decimals(k, self.forces_settings, d, self.plot_forces))
        menu.exec(self.forces_canvas.mapToGlobal(pos))

    def show_te_context_menu(self, pos):
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu {background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; color: #1e293b;} QMenu::item {padding: 6px 24px;} QMenu::item:selected {background-color: #f1f5f9; color: #2563eb; font-weight:bold;}")

        x, y = pos.x(), self.te_canvas.figure.bbox.height - pos.y()
        clicked_title = None
        for ax, title in self.te_ax_to_title.items():
            if ax.bbox.contains(x, y):
                clicked_title = title
                break

        e_menu = menu.addMenu("Export Options")
        e_menu.addAction("Export Full Dashboard Image").triggered.connect(
            lambda: self._export_gb_full(self.te_fig, "Transmission_Error"))
        e_menu.addAction("Export All Subplots Individually").triggered.connect(
            lambda: self._export_gb_individuals("Transmission_Error", None))
        if clicked_title:
            e_menu.addAction(f"Export '{clicked_title}' (Current Subplot)").triggered.connect(
                lambda _, t=clicked_title: self._export_gb_individuals("Transmission_Error", [t]))
        menu.addSeparator()

        c_menu = menu.addMenu("Bar Colors")
        h_menu = menu.addMenu("Hide/Show Bars")
        s_menu = menu.addMenu("Plot Settings")
        for fname in self.te_files.keys():
            custom_name = self.custom_names.get(fname, fname)
            c_menu.addAction(custom_name).triggered.connect(lambda _, f=fname: self.change_bar_color(f, self.plot_te))

            h_action = QAction(custom_name, self, checkable=True)
            h_action.setChecked(fname not in self.hidden_bars)
            h_action.triggered.connect(lambda checked, f=fname: self.toggle_bar_visibility(f, self.plot_te))
            h_menu.addAction(h_action)

        for key, tab in [('Linear TE', s_menu.addMenu("Linear TE")), ('Tilt TE', s_menu.addMenu("Tilt TE"))]:
            tab.addAction("Y-Axis Max").triggered.connect(
                lambda _, k=key: self.set_y_max(k, self.te_settings, self.plot_te))
            tab.addAction("Y-Axis Levels").triggered.connect(
                lambda _, k=key: self.set_y_levels(k, self.te_settings, self.plot_te))
            tab.addAction("Title Font Size").triggered.connect(
                lambda _, k=key: self.set_title_size(k, self.te_settings, self.plot_te))
            dec_menu = tab.addMenu("Decimal Places")
            for d in [1, 2, 3, 4]:
                dec_menu.addAction(f"{d} Decimal{'s' if d > 1 else ''}").triggered.connect(
                    lambda _, d=d, k=key: self.set_decimals(k, self.te_settings, d, self.plot_te))
        menu.exec(self.te_canvas.mapToGlobal(pos))

    def show_bearing_context_menu(self, pos):
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu {background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; color: #1e293b;} QMenu::item {padding: 6px 24px;} QMenu::item:selected {background-color: #f1f5f9; color: #2563eb; font-weight:bold;}")

        x, y = pos.x(), self.bearing_canvas.figure.bbox.height - pos.y()
        clicked_title = None
        for ax, title in self.bearing_ax_to_title.items():
            if ax.bbox.contains(x, y):
                clicked_title = title
                break

        e_menu = menu.addMenu("Export Options")
        e_menu.addAction("Export Full Dashboard Image").triggered.connect(
            lambda: self._export_gb_full(self.bearing_fig, "Bearing_Stiffness"))
        e_menu.addAction("Export All Subplots Individually").triggered.connect(
            lambda: self._export_gb_individuals("Bearing_Stiffness", None))
        if clicked_title:
            e_menu.addAction(f"Export '{clicked_title}' (Current Subplot)").triggered.connect(
                lambda _, t=clicked_title: self._export_gb_individuals("Bearing_Stiffness", [t]))
        menu.addSeparator()

        c_menu = menu.addMenu("Bar Colors")
        h_menu = menu.addMenu("Hide/Show Bars")
        s_menu = menu.addMenu("Plot Settings")
        for fname in self.bearing_files.keys():
            custom_name = self.custom_names.get(fname, fname)
            c_menu.addAction(custom_name).triggered.connect(
                lambda _, f=fname: self.change_bar_color(f, self.plot_bearing))

            h_action = QAction(custom_name, self, checkable=True)
            h_action.setChecked(fname not in self.hidden_bars)
            h_action.triggered.connect(lambda checked, f=fname: self.toggle_bar_visibility(f, self.plot_bearing))
            h_menu.addAction(h_action)

        s_menu.addAction("Y-Axis Max").triggered.connect(
            lambda: self.set_y_max(None, self.bearing_settings, self.plot_bearing))
        s_menu.addAction("Y-Axis Levels").triggered.connect(
            lambda: self.set_y_levels(None, self.bearing_settings, self.plot_bearing))
        s_menu.addAction("Title Font Size").triggered.connect(
            lambda: self.set_title_size(None, self.bearing_settings, self.plot_bearing))
        dec_menu = s_menu.addMenu("Decimal Places")
        for d in [1, 2, 3, 4]:
            dec_menu.addAction(f"{d} Decimal{'s' if d > 1 else ''}").triggered.connect(
                lambda _, d=d: self.set_decimals(None, self.bearing_settings, d, self.plot_bearing))
        menu.exec(self.bearing_canvas.mapToGlobal(pos))

    def set_y_max(self, subplot, settings, plot_func):
        key = subplot if subplot else None
        current_max = settings[key]['y_max'] if key and settings[key]['y_max'] is not None else settings[
            'y_max'] if 'y_max' in settings and settings['y_max'] is not None else 0
        y_max, ok = QInputDialog.getDouble(self, f"{subplot if subplot else 'Bearing'} Y-Axis Max",
                                           "Y Max (0 for auto):", current_max, 0, 10000, 4)
        if ok:
            if key:
                settings[key]['y_max'] = y_max if y_max != 0 else None
            else:
                settings['y_max'] = y_max if y_max != 0 else None
            plot_func()

    def set_y_levels(self, subplot, settings, plot_func):
        key = subplot if subplot else None
        current_levels = settings[key]['y_levels'] if key else settings['y_levels']
        levels, ok = QInputDialog.getInt(self, f"{subplot if subplot else 'Bearing'} Y-Axis Levels", "Number of ticks:",
                                         current_levels, 2, 20)
        if ok:
            if key:
                settings[key]['y_levels'] = levels
            else:
                settings['y_levels'] = levels
            plot_func()

    def set_title_size(self, subplot, settings, plot_func):
        key = subplot if subplot else None
        current_size = settings[key]['title_size'] if key else settings['title_size']
        size, ok = QInputDialog.getDouble(self, f"{subplot if subplot else 'Bearing'} Title Font Size", "Font Size:",
                                          current_size, 6, 20, 1)
        if ok:
            if key:
                settings[key]['title_size'] = size
            else:
                settings['title_size'] = size
            plot_func()

    def set_decimals(self, subplot, settings, decimals, plot_func):
        key = subplot if subplot else None
        if key:
            settings[key]['decimals'] = decimals
        else:
            settings['decimals'] = decimals
        plot_func()

    def change_bar_color(self, filename, plot_func):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_colors[filename] = color.name()
            plot_func()

    def toggle_bar_visibility(self, filename, plot_func):
        if filename in self.hidden_bars:
            self.hidden_bars.remove(filename)
        else:
            self.hidden_bars.add(filename)
        plot_func()

    def export_plots(self, tab_name):
        fig_map = {
            "Forces_Moments": self.forces_fig,
            "Transmission_Error": self.te_fig,
            "Bearing_Stiffness": self.bearing_fig
        }
        self._export_gb_full(fig_map.get(tab_name, self.forces_fig), tab_name)

    def _export_gb_full(self, figure, name):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Plots")
        if not folder:
            return
        figure.savefig(os.path.join(folder, f"Full_Dashboard_{name}.png"), dpi=200, bbox_inches='tight')
        QMessageBox.information(self, "Export Successful", f"Full dashboard exported to:\n{folder}")

    def _plot_forces_subplot(self, ax, components, title, ylabel, show_legend):
        num_files = len([f for f in self.order_data if f not in self.hidden_bars])
        bar_width = 0.8 / num_files if num_files > 0 else 0.8
        selected_orders = [o for o in self.primary_orders if self.primary_orders[o].isChecked()] + [
            o for o in self.secondary_orders if self.secondary_orders[o].isChecked()]
        cols = {'Fx': 2, 'Fy': 4, 'Fz': 6, 'Mx': 8, 'My': 10, 'Mz': 12}
        all_values = []
        for i, (fname, df) in enumerate(self.order_data.items()):
            if fname in self.hidden_bars:
                continue
            df_orders = df[df[1].apply(lambda x: f"{x:.2f}" if x % 1 != 0 else f"{int(x)}").isin(selected_orders)]
            if not df_orders.empty:
                x = np.arange(len(components))
                values = [abs(df_orders[cols[c]].mean()) for c in components]
                all_values.extend(values)
                bars = ax.bar(x + i * bar_width, values, bar_width, label=self.custom_names.get(fname, fname),
                              color=self.bar_colors.get(fname, f'C{i}'), zorder=2)
                for bar in bars:
                    h = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, h,
                            f'{h:.{self.forces_settings[title]["decimals"]}f}', ha='center', va='bottom',
                            fontsize=self.forces_font_size.value(), zorder=3)

        ax.set_title(title, fontfamily=self.forces_font_combo.currentText(),
                     fontsize=self.forces_settings[title]['title_size'])
        ax.set_ylabel(ylabel, fontfamily=self.forces_font_combo.currentText(), fontsize=self.forces_font_size.value())
        ax.set_xticks(np.arange(len(components)) + bar_width * (num_files - 1) / 2)
        ax.set_xticklabels(components, fontfamily=self.forces_font_combo.currentText(),
                           fontsize=self.forces_font_size.value())
        y_max = self.forces_settings[title]['y_max'] if self.forces_settings[title]['y_max'] is not None else (
            max(all_values) * 1.1 if all_values else 10)
        ax.set_ylim(0, y_max)
        ax.set_yticks(np.linspace(0, y_max, self.forces_settings[title]['y_levels']))
        ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        ax.tick_params(axis='both', labelsize=self.forces_font_size.value())
        if self.forces_grid_btn.isChecked():
            ax.grid(True, zorder=1)
        if num_files > 1 and show_legend:
            ax.legend()

    def _plot_te_subplot(self, ax, harmonics, title, ylabel, is_linear, show_legend):
        num_files = len([f for f in self.te_data if f not in self.hidden_bars])
        bar_width = 0.8 / num_files if num_files > 0 else 0.8
        all_values = []
        for i, fname in enumerate(self.te_data.keys()):
            if fname in self.hidden_bars:
                continue
            for j, harmonic in enumerate(harmonics):
                key = f"{harmonic}_Linear" if is_linear else f"{harmonic}_Tilt"
                val = self.te_data[fname][key]
                bars = ax.bar(np.arange(len(harmonics))[j] + i * bar_width, val, bar_width,
                              label=self.custom_names.get(fname, fname) if j == 0 else "",
                              color=self.bar_colors.get(fname, f'C{i}'), zorder=2)
                all_values.append(val)
                for bar in bars:
                    h = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, h,
                            f'{h:.{self.te_settings[title]["decimals"]}f}', ha='center', va='bottom',
                            fontsize=self.te_font_size.value(), zorder=3)

        ax.set_title(title, fontfamily=self.te_font_combo.currentText(), fontsize=self.te_settings[title]['title_size'])
        ax.set_ylabel(ylabel, fontfamily=self.te_font_combo.currentText(), fontsize=self.te_font_size.value())
        ax.set_xticks(np.arange(len(harmonics)) + bar_width * (num_files - 1) / 2)
        ax.set_xticklabels(harmonics, fontfamily=self.te_font_combo.currentText(), fontsize=self.te_font_size.value())
        y_max = self.te_settings[title]['y_max'] if self.te_settings[title]['y_max'] is not None else (
            max(all_values) * 1.3 if all_values else 0.1)
        ax.set_ylim(0, y_max)
        ax.set_yticks(np.linspace(0, y_max, self.te_settings[title]['y_levels']))
        ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
        ax.tick_params(axis='both', labelsize=self.te_font_size.value())
        if self.te_grid_btn.isChecked():
            ax.grid(True, zorder=1)
        if num_files > 1 and show_legend:
            ax.legend()

    def _plot_bearing_subplot(self, ax, bearing, components, is_trans, show_legend):
        num_files = len([f for f in self.bearing_data if f not in self.hidden_bars])
        bar_width = 0.8 / num_files if num_files > 0 else 0.8
        all_values = []
        for i, (fname, data) in enumerate(self.bearing_data.items()):
            if fname in self.hidden_bars:
                continue
            values = [data[f"{bearing}_{comp}"] for comp in components]
            all_values.extend(values)
            bars = ax.bar(np.arange(len(components)) + i * bar_width, values, bar_width,
                          label=self.custom_names.get(fname, fname), color=self.bar_colors.get(fname, f'C{i}'),
                          zorder=2)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h + (self.bearing_font_size.value() * 0.3),
                        f'{h:.{self.bearing_settings["decimals"]}f}', ha='center', va='bottom', rotation=90,
                        fontsize=self.bearing_font_size.value(), zorder=3)

        ax.set_title(f"{bearing} {'Trans' if is_trans else 'Rot'}", fontfamily=self.bearing_font_combo.currentText(),
                     fontsize=self.bearing_settings['title_size'])
        ax.set_xticks(np.arange(len(components)) + bar_width * (num_files - 1) / 2)
        ax.set_xticklabels(components, fontfamily=self.bearing_font_combo.currentText(),
                           fontsize=self.bearing_font_size.value())
        y_max = self.bearing_settings['y_max'] if self.bearing_settings['y_max'] is not None else (
            max(all_values) * 1.2 if all_values else 10)
        ax.set_ylim(0, y_max)
        ax.set_yticks(np.linspace(0, y_max, self.bearing_settings['y_levels']))
        ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        ax.tick_params(axis='both', labelsize=self.bearing_font_size.value())
        if self.bearing_grid_btn.isChecked():
            ax.grid(True, zorder=1)
        if num_files > 1 and show_legend:
            ax.legend()

    def _export_gb_individuals(self, tab_name, subset_titles=None):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Plots")
        if not folder:
            return
        try:
            if tab_name == "Forces_Moments":
                selected_forces = [f for f in self.forces_checkboxes if self.forces_checkboxes[f].isChecked()]
                selected_moments = [m for m in self.moments_checkboxes if self.moments_checkboxes[m].isChecked()]
                if (subset_titles is None or "Forces" in subset_titles) and selected_forces:
                    fig = plt.Figure(facecolor='#ffffff')
                    ax = fig.add_subplot(111)
                    self._plot_forces_subplot(ax, selected_forces, "Forces", "Force (N)",
                                              self.forces_legend_btn.isChecked())
                    fig.tight_layout(pad=1.5)
                    fig.savefig(os.path.join(folder, "Forces.png"), dpi=300, bbox_inches='tight')
                if (subset_titles is None or "Moments" in subset_titles) and selected_moments:
                    fig = plt.Figure(facecolor='#ffffff')
                    ax = fig.add_subplot(111)
                    self._plot_forces_subplot(ax, selected_moments, "Moments", "Moment (N-mm)",
                                              self.forces_legend_btn.isChecked())
                    fig.tight_layout(pad=1.5)
                    fig.savefig(os.path.join(folder, "Moments.png"), dpi=300, bbox_inches='tight')
                if subset_titles is None:
                    self._save_gb_legend(folder, self.order_data, "Forces_Moments_Legend.png")

            elif tab_name == "Transmission_Error":
                harms = [h for h in self.stage1_radios if self.stage1_radios[h].isChecked()] + [
                    h for h in self.stage2_radios if self.stage2_radios[h].isChecked()]
                if (subset_titles is None or "Linear TE" in subset_titles) and self.te_checkboxes[
                    'Linear TE'].isChecked() and harms:
                    fig = plt.Figure(facecolor='#ffffff')
                    ax = fig.add_subplot(111)
                    self._plot_te_subplot(ax, harms, "Linear TE", "TE (μm)", True, self.te_legend_btn.isChecked())
                    fig.tight_layout(pad=2.0)
                    fig.savefig(os.path.join(folder, "Linear_TE.png"), dpi=300, bbox_inches='tight')
                if (subset_titles is None or "Tilt TE" in subset_titles) and self.te_checkboxes[
                    'Tilt TE'].isChecked() and harms:
                    fig = plt.Figure(facecolor='#ffffff')
                    ax = fig.add_subplot(111)
                    self._plot_te_subplot(ax, harms, "Tilt TE", "TE (m-rad)", False, self.te_legend_btn.isChecked())
                    fig.tight_layout(pad=2.0)
                    fig.savefig(os.path.join(folder, "Tilt_TE.png"), dpi=300, bbox_inches='tight')
                if subset_titles is None:
                    self._save_gb_legend(folder, self.te_data, "Transmission_Error_Legend.png")

            elif tab_name == "Bearing_Stiffness":
                bearings = [b for b in self.bearing_checkboxes if self.bearing_checkboxes[b].isChecked()]
                is_trans = not self.bearing_toggle_trans_rot.isChecked()
                comps = [t for t in self.trans_checkboxes if self.trans_checkboxes[t].isChecked()] if is_trans else [
                    r for r in self.rot_checkboxes if self.rot_checkboxes[r].isChecked()]
                for bearing in bearings:
                    target_title = f"{bearing} {'Trans' if is_trans else 'Rot'}"
                    if subset_titles is None or target_title in subset_titles:
                        fig = plt.Figure(facecolor='#ffffff')
                        ax = fig.add_subplot(111)
                        self._plot_bearing_subplot(ax, bearing, comps, is_trans, self.bearing_legend_btn.isChecked())
                        fig.supylabel(f"Stiffness ({'kN/mm' if is_trans else 'kNmm/rad'})",
                                      fontfamily=self.bearing_font_combo.currentText(),
                                      fontsize=self.bearing_font_size.value())
                        fig.tight_layout(pad=1.5)
                        safe_title = target_title.replace(' ', '_').replace('/', '_')
                        fig.savefig(os.path.join(folder, f"{safe_title}.png"), dpi=300, bbox_inches='tight')
                if subset_titles is None:
                    self._save_gb_legend(folder, self.bearing_data, "Bearing_Stiffness_Legend.png")

            QMessageBox.information(self, "Export Success", f"Plots exported to:\n{folder}")
        except Exception:
            tb = traceback.format_exc()
            QMessageBox.warning(self, "Export Error", f"Failed to export plots:\n{tb}")

    def _save_gb_legend(self, folder, data_dict, filename):
        if not data_dict:
            return
        legend_fig = plt.Figure(figsize=(2, len(data_dict) * 0.3), facecolor='#ffffff')
        legend_fig.legend([plt.Rectangle((0, 0), 1, 1, facecolor=self.bar_colors.get(fname, f'C{i}')) for i, fname in
                           enumerate(data_dict.keys()) if fname not in self.hidden_bars],
                          [self.custom_names.get(fname, fname) for fname in data_dict.keys() if
                           fname not in self.hidden_bars], loc='center', frameon=False, prop={'size': 10})
        legend_fig.savefig(os.path.join(folder, filename), dpi=300, bbox_inches='tight', pad_inches=0.1)

    def reset(self):
        reply = QMessageBox.question(self, "Reset Confirmation",
                                     "Are you sure you want to reset all data and settings?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.order_files.clear()
            self.order_data.clear()
            self.te_files.clear()
            self.te_data.clear()
            self.bearing_files.clear()
            self.bearing_data.clear()
            self.custom_names.clear()
            self.hidden_bars.clear()
            for cb in self.forces_checkboxes.values():
                cb.setChecked(True)
            for cb in self.moments_checkboxes.values():
                cb.setChecked(True)
            for rb in self.primary_orders.values():
                rb.setChecked(False)
            for rb in self.secondary_orders.values():
                rb.setChecked(False)
            self.update_orders_checkboxes()
            for rb in self.stage1_radios.values():
                rb.setChecked(False)
            for rb in self.stage2_radios.values():
                rb.setChecked(False)
            for cb in self.te_checkboxes.values():
                cb.setChecked(True)
            for cb in self.bearing_checkboxes.values():
                cb.setChecked(True)
            for cb in self.trans_checkboxes.values():
                cb.setChecked(True)
            for cb in self.rot_checkboxes.values():
                cb.setChecked(True)
            self.forces_fig.clear()
            self.te_fig.clear()
            self.bearing_fig.clear()
            self.forces_canvas.draw()
            self.te_canvas.draw()
            self.bearing_canvas.draw()
            self.forces_settings = {'Forces': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 0},
                                    'Moments': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 0}}
            self.te_settings = {'Linear TE': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 4},
                                'Tilt TE': {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 4}}
            self.bearing_settings = {'y_max': None, 'y_levels': 5, 'title_size': 10, 'decimals': 0}

    def show_help(self):
        QMessageBox.information(self, "Help Guide",
                                """<h2>Gear & Bearings Tool</h2><p>Visualize Forces & Moments, Transmission Errors, and Bearing Stiffness.</p><ul><li><b>Load Data:</b> Use the top ribbon to load your CSV/XLS data files.</li><li><b>Plotting:</b> Check the desired parameters on the right side and hit Plot.</li><li><b>Context Menus:</b> Right click any plot to modify colors, Y-Axis limits, ticks, and decimal values, or export individual subplots.</li></ul>""")


# ==========================================
# MASTER APPLICATION WINDOW
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autosim Master Suite")
        setup_matplotlib_style()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Workspace ready.")

        # Initialize All 3 Modules
        self.plotting_module = PlottingStudio(self)
        self.mobility_module = MobilityStudio(self)
        self.gear_bearings_module = GearBearingsStudio(self)

        self.stacked_widget.addWidget(self.plotting_module)
        self.stacked_widget.addWidget(self.mobility_module)
        self.stacked_widget.addWidget(self.gear_bearings_module)

        # Global Escape shortcut to guarantee zoom reset regardless of widget focus
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.reset_active_zoom)

        screen = QApplication.primaryScreen()
        self.setGeometry(screen.availableGeometry())
        self.showMaximized()

    def reset_active_zoom(self):
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, "zoom_manager"):
            current_widget.zoom_manager.reset_all_zooms()

    def switch_mode(self, mode_name):
        module_map = {
            "Plotting": self.plotting_module,
            "Mobility": self.mobility_module,
            "Gear & Bearings": self.gear_bearings_module
        }

        target_widget = module_map.get(mode_name)
        if target_widget:
            self.stacked_widget.setCurrentWidget(target_widget)
            self.statusBar.showMessage(f"Switched to {mode_name} Mode.")

            for module in module_map.values():
                module.mode_switcher.blockSignals(True)
                module.mode_switcher.setCurrentText(mode_name)
                module.mode_switcher.blockSignals(False)

    def save_session(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Master Session", "", "JSON Files (*.json)")
        if not path: return

        try:
            state = {
                "plotting": {
                    "selected_files": self.plotting_module.selected_files,
                    "file_settings": self.plotting_module.file_settings,
                    "saved_mappings": self.plotting_module.saved_mappings,
                    "plot_settings": self.plotting_module.plot_settings,
                    "hidden_curves": list(self.plotting_module.hidden_curves),
                    "custom_titles": self.plotting_module.custom_titles,
                },
                "mobility": {
                    "selected_files": self.mobility_module.selected_files,
                    "file_settings": self.mobility_module.file_settings,
                    "settings": self.mobility_module.settings,
                    "plot_settings": self.mobility_module.plot_settings,
                    "hidden_curves": list(self.mobility_module.hidden_curves),
                    "custom_titles": {str(k): v for k, v in self.mobility_module.custom_titles.items()},
                },
                "gear_bearings": {
                    "order_files": self.gear_bearings_module.order_files,
                    "te_files": self.gear_bearings_module.te_files,
                    "bearing_files": self.gear_bearings_module.bearing_files,
                    "custom_names": self.gear_bearings_module.custom_names,
                    "bar_colors": self.gear_bearings_module.bar_colors,
                    "hidden_bars": list(self.gear_bearings_module.hidden_bars),
                    "forces_settings": self.gear_bearings_module.forces_settings,
                    "te_settings": self.gear_bearings_module.te_settings,
                    "bearing_settings": self.gear_bearings_module.bearing_settings,
                    "ui_state": {
                        "forces": {k: cb.isChecked() for k, cb in self.gear_bearings_module.forces_checkboxes.items()},
                        "moments": {k: cb.isChecked() for k, cb in
                                    self.gear_bearings_module.moments_checkboxes.items()},
                        "te_types": {k: cb.isChecked() for k, cb in self.gear_bearings_module.te_checkboxes.items()},
                        "bearings": {k: cb.isChecked() for k, cb in
                                     self.gear_bearings_module.bearing_checkboxes.items()},
                        "trans": {k: cb.isChecked() for k, cb in self.gear_bearings_module.trans_checkboxes.items()},
                        "rot": {k: cb.isChecked() for k, cb in self.gear_bearings_module.rot_checkboxes.items()},
                        "primary_orders": {k: rb.isChecked() for k, rb in
                                           self.gear_bearings_module.primary_orders.items()},
                        "secondary_orders": {k: rb.isChecked() for k, rb in
                                             self.gear_bearings_module.secondary_orders.items()},
                        "stage1": {k: rb.isChecked() for k, rb in self.gear_bearings_module.stage1_radios.items()},
                        "stage2": {k: rb.isChecked() for k, rb in self.gear_bearings_module.stage2_radios.items()},
                        "bearing_toggle_trans_rot": self.gear_bearings_module.bearing_toggle_trans_rot.isChecked(),
                        "bearing_toggle_global": self.gear_bearings_module.bearing_toggle_global.isChecked(),
                    }
                }
            }
            with open(path, 'w') as f:
                json.dump(state, f, indent=4)
            self.statusBar.showMessage(f"Master Session saved to {path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save session:\n{e}")

    def load_session(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Master Session", "", "JSON Files (*.json)")
        if not path: return

        try:
            with open(path, 'r') as f:
                state = json.load(f)

            # --- Restore Plotting ---
            p_state = state.get("plotting", {})
            self.plotting_module.selected_files = p_state.get("selected_files", [])
            self.plotting_module.file_settings = p_state.get("file_settings", {})
            self.plotting_module.saved_mappings = p_state.get("saved_mappings", [])
            self.plotting_module.plot_settings = p_state.get("plot_settings", {})
            self.plotting_module.hidden_curves = set(p_state.get("hidden_curves", []))
            self.plotting_module.custom_titles = p_state.get("custom_titles", {})

            self.plotting_module.file_data.clear()
            for fn, settings in self.plotting_module.file_settings.items():
                if settings.get("path") and os.path.exists(settings.get("path")):
                    self.plotting_module.file_data[fn] = load_dataframe(settings["path"])
            self.plotting_module.mapped_curves = {m['title']: m['map'] for m in self.plotting_module.saved_mappings if
                                                  m.get('selected', False)}
            self.plotting_module.plot_data()

            # --- Restore Mobility ---
            m_state = state.get("mobility", {})
            self.mobility_module.selected_files = m_state.get("selected_files", [])
            self.mobility_module.file_settings = m_state.get("file_settings", {})
            loaded_m_settings = m_state.get("settings", {})
            self.mobility_module.settings.update(loaded_m_settings)
            if "data_type" not in self.mobility_module.settings:
                self.mobility_module.settings["data_type"] = "Velocity"
            self.mobility_module.plot_settings = m_state.get("plot_settings", {})
            self.mobility_module.hidden_curves = set(m_state.get("hidden_curves", []))

            # Reconstruct numeric tuple keys for custom_titles
            m_titles_raw = m_state.get("custom_titles", {})
            self.mobility_module.custom_titles = {}
            for k, v in m_titles_raw.items():
                if isinstance(k, str) and k.startswith('(') and k.endswith(')'):
                    parts = k.strip('()').split(',')
                    self.mobility_module.custom_titles[(int(parts[0].strip()), parts[1].strip(" '\""))] = v
                else:
                    self.mobility_module.custom_titles[k] = v

            self.mobility_module.parse_all_pch()
            if self.mobility_module.settings.get("nodes"):
                self.mobility_module.plot_data()

            # --- Restore Gear & Bearings ---
            gb_state = state.get("gear_bearings", {})
            self.gear_bearings_module.order_files = gb_state.get("order_files", {})
            self.gear_bearings_module.te_files = gb_state.get("te_files", {})
            self.gear_bearings_module.bearing_files = gb_state.get("bearing_files", {})
            self.gear_bearings_module.custom_names = gb_state.get("custom_names", {})
            self.gear_bearings_module.bar_colors = gb_state.get("bar_colors", {})
            self.gear_bearings_module.hidden_bars = set(gb_state.get("hidden_bars", []))
            self.gear_bearings_module.forces_settings = gb_state.get("forces_settings",
                                                                     self.gear_bearings_module.forces_settings)
            self.gear_bearings_module.te_settings = gb_state.get("te_settings", self.gear_bearings_module.te_settings)
            self.gear_bearings_module.bearing_settings = gb_state.get("bearing_settings",
                                                                      self.gear_bearings_module.bearing_settings)

            # Process files to generate data & dynamic UI
            self.gear_bearings_module.process_order_files()
            self.gear_bearings_module.update_orders_checkboxes()
            self.gear_bearings_module.process_te_files()
            self.gear_bearings_module.process_bearing_files()

            # Restore exact UI state
            ui_state = gb_state.get("ui_state", {})

            for k, v in ui_state.get("forces", {}).items():
                if k in self.gear_bearings_module.forces_checkboxes: self.gear_bearings_module.forces_checkboxes[
                    k].setChecked(v)
            for k, v in ui_state.get("moments", {}).items():
                if k in self.gear_bearings_module.moments_checkboxes: self.gear_bearings_module.moments_checkboxes[
                    k].setChecked(v)
            for k, v in ui_state.get("te_types", {}).items():
                if k in self.gear_bearings_module.te_checkboxes: self.gear_bearings_module.te_checkboxes[k].setChecked(
                    v)
            for k, v in ui_state.get("bearings", {}).items():
                if k in self.gear_bearings_module.bearing_checkboxes: self.gear_bearings_module.bearing_checkboxes[
                    k].setChecked(v)
            for k, v in ui_state.get("trans", {}).items():
                if k in self.gear_bearings_module.trans_checkboxes: self.gear_bearings_module.trans_checkboxes[
                    k].setChecked(v)
            for k, v in ui_state.get("rot", {}).items():
                if k in self.gear_bearings_module.rot_checkboxes: self.gear_bearings_module.rot_checkboxes[
                    k].setChecked(v)
            for k, v in ui_state.get("primary_orders", {}).items():
                if k in self.gear_bearings_module.primary_orders: self.gear_bearings_module.primary_orders[
                    k].setChecked(v)
            for k, v in ui_state.get("secondary_orders", {}).items():
                if k in self.gear_bearings_module.secondary_orders: self.gear_bearings_module.secondary_orders[
                    k].setChecked(v)
            for k, v in ui_state.get("stage1", {}).items():
                if k in self.gear_bearings_module.stage1_radios: self.gear_bearings_module.stage1_radios[k].setChecked(
                    v)
            for k, v in ui_state.get("stage2", {}).items():
                if k in self.gear_bearings_module.stage2_radios: self.gear_bearings_module.stage2_radios[k].setChecked(
                    v)

            self.gear_bearings_module.bearing_toggle_trans_rot.setChecked(
                ui_state.get("bearing_toggle_trans_rot", False))
            self.gear_bearings_module.bearing_toggle_global.setChecked(ui_state.get("bearing_toggle_global", False))
            self.gear_bearings_module.update_toggle_color()

            # Re-plot all GB Tabs
            self.gear_bearings_module.plot_forces()
            self.gear_bearings_module.plot_te()
            self.gear_bearings_module.plot_bearing()

            self.statusBar.showMessage(f"Master Session loaded from {path}", 5000)
        except Exception as e:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Error", f"Failed to load session:\n{tb}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
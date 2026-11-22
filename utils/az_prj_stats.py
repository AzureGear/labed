"""SAMA project grouping health checks and global_id frequency statistics."""

from __future__ import annotations

import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from utils import helper
from utils.sama_project_handler import DatasetSAMAHandler

_log = logging.getLogger(__name__)

# Above this many image groups, skip per-group bar/box/violin plots (unreadable).
_MANY_GROUPS_PLOT_THRESHOLD = 22


def group_images(
    image_names: Iterable[str],
    pattern: str | None = None,
) -> tuple[dict[str, list[str]], list[str]]:
    """Group image keys by prefix pattern; names that do not match go to *ungrouped*."""
    pattern = pattern or helper.PATTERNS.get("double_underscore")
    groups: dict[str, list[str]] = defaultdict(list)
    ungrouped: list[str] = []
    prefix_re = re.compile(pattern)

    for name in sorted(image_names):
        m = prefix_re.match(name)
        if m:
            key = f"{m.group(1)}_{m.group(2)}"
            groups[key].append(name)
        else:
            ungrouped.append(name)

    return groups, ungrouped


def _ordered_group_keys(keys: Iterable[str]) -> list[str]:
    ks = list(keys)
    rest = sorted(k for k in ks if k != "__ungrouped__")
    tail = [k for k in ks if k == "__ungrouped__"]
    return rest + tail


class ProjectGroupsStats:
    """Load a SAMA JSON, inspect image naming / groups, and analyse *global_id* frequencies."""

    def __init__(
        self,
        json_path: str | Path,
        *,
        pattern: str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.json_path = Path(json_path)
        self._pattern = pattern or helper.PATTERNS.get("double_underscore")
        self._log = logger or _log
        self._handler = DatasetSAMAHandler()
        self._handler.load(str(self.json_path))

    @property
    def data(self) -> dict[str, Any]:
        return self._handler.data

    @property
    def sama(self) -> DatasetSAMAHandler:
        return self._handler

    def grouped_images(self) -> tuple[dict[str, list[str]], list[str]]:
        return group_images(self.data["images"].keys(), self._pattern)

    @staticmethod
    def filename_issues(filename: str) -> list[str]:
        """Return human-readable filename / naming convention issues."""
        issues: list[str] = []
        if " " in filename:
            issues.append("пробел в имени")
        stem = Path(filename).stem
        parts = stem.split("_")
        after_prefix = "_".join(parts[2:])
        if not re.match(r"\s*\d{4}", after_prefix):
            issues.append("после префикса не год")
        return issues

    def check_issues(self) -> None:
        """Log ungrouped image names and per-file naming issues inside each group."""
        groups, ungrouped = self.grouped_images()
        if ungrouped:
            self._log.info("\n-- не распознан префикс --")
            for name in ungrouped:
                self._log.info("  ✗ %s", name)

        for group_key in sorted(groups):
            imgs = groups[group_key]
            flagged = [(n, self.filename_issues(n)) for n in imgs if self.filename_issues(n)]
            marker = f"  [{len(flagged)} с ошибкой]" if flagged else ""
            self._log.info("\n-- %s%s --", group_key, marker)
            for name in imgs:
                issues = self.filename_issues(name)
                flag = f"  ← {', '.join(issues)}" if issues else ""
                self._log.info("  %s %s%s", "⚠" if issues else " ", name, flag)

    def global_id_counts(self) -> dict[str, dict[Any, int]]:
        """Per-group map *global_id* → number of shapes with that id (includes *__ungrouped__* if any)."""
        data = self.data
        pattern = self._pattern
        log = self._log
        image_names = list(data["images"].keys())
        groups, ungrouped = group_images(image_names, pattern)

        result: dict[str, dict[Any, int]] = {}

        for group_key, image_list in groups.items():
            gid_counts: dict[Any, int] = defaultdict(int)
            for image_name in image_list:
                shapes = data["images"][image_name].get("shapes", [])
                for shape in shapes:
                    gid = shape.get("global_id", None)
                    if gid is None:
                        log.warning("Global ID is None for shape %s in image %s", shape, image_name)
                        continue
                    gid_counts[gid] += 1
            result[group_key] = dict(gid_counts)

        if ungrouped:
            ungrouped_counts: dict[Any, int] = defaultdict(int)
            for image_name in ungrouped:
                for shape in data["images"][image_name].get("shapes", []):
                    gid = shape.get("global_id")
                    if gid is not None:
                        ungrouped_counts[gid] += 1
            result["__ungrouped__"] = dict(ungrouped_counts)

        return result

    def get_statistic(
        self,
        *,
        save: bool = True,
        save_plot: bool | None = None,
        counts: dict[str, dict[Any, int]] | None = None,
        json_out: Path | None = None,
        txt_out: Path | None = None,
        plot_out: Path | None = None,
        n_bins: int = 10,
        show_plot: bool = False,
        log_report: bool = True,
    ) -> dict[str, Any]:
        """
        Summarise per-*global_id* frequencies (same structure as :meth:`global_id_counts`).

        When *save* is True, writes ``dd.json`` next to the project unless *json_out* is set,
        and ``stats_report.txt`` (full text report) unless *txt_out* is set.

        The figure is written when *save_plot* is true (default: same as *save*), unless *plot_out* is set.
        """
        counts = counts if counts is not None else self.global_id_counts()
        do_plot = save if save_plot is None else save_plot

        if save:
            json_path = Path(json_out or self.json_path.with_name("global_counts.json"))
            serializable = {k: {str(gid): v for gid, v in inner.items()} for k, inner in counts.items()}
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2, ensure_ascii=False)
            self._log.info("Global counts saved to: %s", json_path)

        stats_payload = _build_stats_payload(counts)
        if log_report:
            for line in stats_payload["text_lines"]:
                self._log.info("%s", line)

        if save:
            txt_path = Path(txt_out or self.json_path.with_name("stats_report.txt"))
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(stats_payload["text_lines"]))
                f.write("\n")
            self._log.info("Text report saved to: %s", txt_path)

        if do_plot:
            fig_path = Path(plot_out or self.json_path.with_name("stats_visualization.png"))
            _render_statistics_figure(counts, fig_path, n_bins=n_bins, show=show_plot, log=self._log)

        return {"counts": counts, **stats_payload["metrics"], "text_lines": stats_payload["text_lines"]}


def _object_frequency_hist_bins(all_freqs: list[int]) -> tuple[list[str], list[int]]:
    """Bucket counts: 1..10 individually, 11-12, 13-15, 16+."""
    labels = [str(i) for i in range(1, 11)] + ["11-12", "13-15", "16+"]
    counts = [0] * len(labels)
    for f in all_freqs:
        x = int(f)
        if x < 1:
            continue
        if x <= 10:
            counts[x - 1] += 1
        elif x <= 12:
            counts[10] += 1
        elif x <= 15:
            counts[11] += 1
        else:
            counts[12] += 1
    return labels, counts


def _build_stats_payload(counts: dict[str, dict[Any, int]]) -> dict[str, Any]:
    import numpy as np
    from scipy import stats

    groups = _ordered_group_keys(counts.keys())
    inner_values = [list(counts[g].values()) for g in groups]
    all_freqs = [f for g in counts.values() for f in g.values()]

    lines: list[str] = []
    sep = "=" * 62

    if not all_freqs:
        lines.append(sep)
        lines.append("  ГЛОБАЛЬНАЯ СТАТИСТИКА (нет данных)")
        lines.append(sep)
        return {"text_lines": lines, "metrics": {"empty": True}}

    arr = np.array(all_freqs, dtype=float)
    group_sizes = [len(v) for v in inner_values]
    group_totals = [sum(v) for v in inner_values]
    group_means = [float(np.mean(v)) if v else float("nan") for v in inner_values]
    group_medians = [float(np.median(v)) if v else float("nan") for v in inner_values]
    group_stds = [float(np.std(v)) if v else float("nan") for v in inner_values]
    group_mins = [min(v) if v else 0 for v in inner_values]
    group_maxs = [max(v) if v else 0 for v in inner_values]

    # SciPy Shapiro–Wilk is limited to 5000 samples.
    if len(arr) >= 3:
        shapiro_sample = arr if len(arr) <= 5000 else np.random.default_rng(0).choice(arr, 5000, replace=False)
        shapiro_stat, shapiro_p = stats.shapiro(shapiro_sample)
    else:
        shapiro_stat, shapiro_p = float("nan"), float("nan")

    pcts = {p: float(np.percentile(arr, p)) for p in (10, 25, 50, 75, 90, 95, 99)}
    freq_counter = Counter(all_freqs)
    mode_val = freq_counter.most_common(1)[0]
    hist_labels, hist_counts_list = _object_frequency_hist_bins([int(x) for x in all_freqs])

    lines.append(sep)
    lines.append("  ГЛОБАЛЬНАЯ СТАТИСТИКА")
    lines.append(sep)
    lines.append(f"  Групп:                     {len(groups)}")
    lines.append(f"  Уникальных объектов:       {sum(group_sizes)}")
    lines.append(f"  Суммарная частота:         {int(sum(all_freqs))}")
    lines.append("")
    lines.append("  Частоты объектов (все группы):")
    lines.append(f"    Минимум:                 {arr.min()}")
    lines.append(f"    Максимум:                {arr.max()}")
    lines.append(f"    Размах:                  {arr.max() - arr.min()}")
    lines.append(f"    Среднее:                 {arr.mean():.4f}")
    lines.append(f"    Медиана:                 {float(np.median(arr)):.4f}")
    lines.append(f"    Мода:                    {mode_val[0]} (встречается {mode_val[1]} раз)")
    lines.append(f"    Стд. отклонение:         {arr.std():.4f}")
    lines.append(f"    Дисперсия:               {arr.var():.4f}")
    if arr.mean() != 0:
        lines.append(f"    Коэф. вариации:          {arr.std() / arr.mean() * 100:.1f}%")
    lines.append(f"    Асимметрия (skewness):   {stats.skew(arr):.4f}")
    lines.append(f"    Эксцесс (kurtosis):      {stats.kurtosis(arr):.4f}")
    lines.append("")
    lines.append("  Перцентили:")
    for p, v in pcts.items():
        lines.append(f"    P{p:>2}:  {v:.2f}")
    lines.append(f"    IQR (P75-P25):           {pcts[75] - pcts[25]:.2f}")
    lines.append("")
    lines.append("  Тест Шапиро-Уилка (нормальность):")
    lines.append(f"    W = {shapiro_stat:.4f},  p = {shapiro_p:.4f}")
    if not np.isnan(shapiro_p) and shapiro_p < 0.05:
        lines.append("    → распределение НЕ нормальное (p < 0.05)")
    else:
        lines.append("    → нет оснований отвергнуть нормальность (p ≥ 0.05)")
    lines.append("")
    lines.append("  Распределение объектов по частоте (число объектов в бине):")
    label_w = max(len(lb) for lb in hist_labels)
    for lb, c in zip(hist_labels, hist_counts_list):
        pct_str = f"{c / len(arr) * 100:5.1f}%"
        bar = "█" * int(c)
        lines.append(f"    {lb:>{label_w}}:  {bar:<15} {int(c):>4}  ({pct_str})")
    lines.append("")
    lines.append(sep)
    lines.append("  СТАТИСТИКА ПО ГРУППАМ")
    lines.append(sep)
    header = (
        f"  {'Группа':<12} {'Объектов':>9} {'Σ частот':>9} {'Среднее':>9} "
        f"{'Медиана':>9} {'Std':>7} {'Min':>5} {'Max':>5}"
    )
    lines.append(header)
    lines.append("  " + "-" * 60)
    for i, g in enumerate(groups):
        lines.append(
            f"  {g:<12} {group_sizes[i]:>9} {group_totals[i]:>9} "
            f"{group_means[i]:>9.2f} {group_medians[i]:>9.2f} "
            f"{group_stds[i]:>7.2f} {group_mins[i]:>5} {group_maxs[i]:>5}"
        )
    lines.append(sep)

    metrics = {
        "empty": False,
        "groups": groups,
        "all_freqs": arr.tolist(),
        "shapiro_stat": float(shapiro_stat) if not np.isnan(shapiro_stat) else None,
        "shapiro_p": float(shapiro_p) if not np.isnan(shapiro_p) else None,
        "percentiles": pcts,
        "mode": {"value": mode_val[0], "count": mode_val[1]},
        "histogram": {"bin_labels": hist_labels, "counts": hist_counts_list},
        "per_group": [
            {
                "group": g,
                "n_objects": group_sizes[i],
                "sum_freq": group_totals[i],
                "mean": group_means[i],
                "median": group_medians[i],
                "std": group_stds[i],
                "min": group_mins[i],
                "max": group_maxs[i],
            }
            for i, g in enumerate(groups)
        ],
    }
    return {"text_lines": lines, "metrics": metrics}


def _axis_hist_kde(
    ax: Any,
    arr: Any,
    *,
    n_bins: int,
    sns_module: Any,
) -> None:
    import numpy as np

    ax.hist(arr, bins=n_bins, color="#5B8DB8", edgecolor="white", linewidth=0.8, density=False, label="Количество")
    ax_twin = ax.twinx()
    sns_module.kdeplot(arr, ax=ax_twin, color="#E07B54", linewidth=1.8, label="KDE")
    ax_twin.set_ylabel("Плотность", fontsize=9)
    ax_twin.tick_params(labelsize=8)
    ax.axvline(arr.mean(), color="#E07B54", linestyle="--", linewidth=1.5, label=f"Среднее {arr.mean():.1f}")
    ax.axvline(np.median(arr), color="#6BAE75", linestyle=":", linewidth=1.5, label=f"Медиана {np.median(arr):.1f}")
    ax.set_title(f"Гистограмма частот ({n_bins} бинов) + KDE", fontsize=10)
    ax.set_xlabel("Частота объекта")
    ax.set_ylabel("Кол-во объектов")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax_twin.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")


def _axis_cdf_percentiles(ax: Any, arr: Any, pcts: dict[int, float]) -> None:
    import numpy as np

    sorted_arr = np.sort(arr)
    cdf = np.arange(1, len(sorted_arr) + 1) / len(sorted_arr)
    ax.step(sorted_arr, cdf, color="#5B8DB8", linewidth=1.8, where="post")
    ax.fill_between(sorted_arr, cdf, step="post", alpha=0.12, color="#5B8DB8")
    for p_label, p_val in [(25, pcts[25]), (50, pcts[50]), (75, pcts[75])]:
        p_cdf = p_label / 100
        ax.plot([arr.min(), p_val], [p_cdf, p_cdf], "--", color="gray", linewidth=0.8, alpha=0.7)
        ax.plot([p_val, p_val], [0, p_cdf], "--", color="gray", linewidth=0.8, alpha=0.7)
        ax.text(p_val + 0.1, p_cdf - 0.05, f"P{p_label}={p_val:.0f}", fontsize=8, color="gray")
    ax.set_title("Эмпирическая CDF", fontsize=10)
    ax.set_xlabel("Частота")
    ax.set_ylabel("F(x)")
    ax.set_ylim(0, 1.05)


def _render_statistics_figure(
    counts: dict[str, dict[Any, int]],
    output_path: Path,
    *,
    n_bins: int,
    show: bool,
    log: logging.Logger,
) -> None:
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.gridspec as gridspec
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    from scipy import stats

    groups = _ordered_group_keys(counts.keys())
    inner_values = [list(counts[g].values()) for g in groups]
    inner_for_dist = [v if v else [float("nan")] for v in inner_values]
    all_freqs = [f for g in counts.values() for f in g.values()]
    if not all_freqs:
        log.warning("Нет частот для визуализации.")
        return

    arr = np.array(all_freqs, dtype=float)
    pcts = {p: float(np.percentile(arr, p)) for p in (25, 50, 75)}
    sns.set_theme(style="whitegrid", palette="muted")

    n_groups = len(groups)
    if n_groups > _MANY_GROUPS_PLOT_THRESHOLD:
        _render_statistics_figure_many_groups(
            groups,
            arr,
            inner_values,
            pcts,
            n_bins=n_bins,
            show=show,
            log=log,
            output_path=output_path,
            sns_module=sns,
            gridspec_module=gridspec,
            plt_module=plt,
            stats_module=stats,
            np_module=np,
        )
        return

    group_sizes = [len(v) for v in inner_values]
    group_means = [float(np.mean(v)) if v else float("nan") for v in inner_values]
    group_stds = [float(np.std(v)) if v else 0.0 for v in inner_values]
    palette = sns.color_palette("Set2", max(len(groups), 1))

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(
        "Статистика распределения объектов по группам",
        fontsize=15,
        fontweight="bold",
        y=0.99,
    )
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.50, wspace=0.38)

    ax1 = fig.add_subplot(gs[0, :2])
    _axis_hist_kde(ax1, arr, n_bins=n_bins, sns_module=sns)

    ax2 = fig.add_subplot(gs[0, 2])
    (osm, osr), (slope, intercept, r) = stats.probplot(arr, dist="norm")
    ax2.plot(osm, osr, "o", color="#5B8DB8", markersize=4, alpha=0.8)
    ax2.plot(osm, slope * np.array(osm) + intercept, "--", color="#E07B54", linewidth=1.5)
    ax2.set_title(f"Q-Q plot (норм.)\nR²={r**2:.3f}", fontsize=10)
    ax2.set_xlabel("Теор. квантили")
    ax2.set_ylabel("Выборочные квантили")

    ax3 = fig.add_subplot(gs[1, 0])
    x = np.arange(len(groups))
    bars = ax3.bar(x, group_sizes, color=palette, edgecolor="white", linewidth=0.8)
    ax3.set_title("Объектов в группе", fontsize=10)
    ax3.set_ylabel("Кол-во объектов")
    ax3.set_xticks(x)
    ax3.set_xticklabels(groups, rotation=20, ha="right", fontsize=8)
    for bar, val in zip(bars, group_sizes):
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            str(val),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax4 = fig.add_subplot(gs[1, 1])
    bars4 = ax4.bar(
        x,
        group_means,
        color=palette,
        edgecolor="white",
        linewidth=0.8,
        yerr=group_stds,
        capsize=4,
        error_kw={"elinewidth": 1, "ecolor": "gray"},
    )
    ax4.set_title("Средняя частота ± std", fontsize=10)
    ax4.set_ylabel("Средняя частота")
    ax4.set_xticks(x)
    ax4.set_xticklabels(groups, rotation=20, ha="right", fontsize=8)
    for bar, val in zip(bars4, group_means):
        if not np.isnan(val):
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                f"{val:.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    ax5 = fig.add_subplot(gs[1, 2])
    bp = ax5.boxplot(
        inner_for_dist,
        patch_artist=True,
        notch=False,
        medianprops={"color": "black", "linewidth": 1.5},
        flierprops={"marker": "o", "markersize": 5, "alpha": 0.6},
    )
    for patch, color in zip(bp["boxes"], palette):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax5.set_xticks(np.arange(1, len(groups) + 1))
    ax5.set_xticklabels(groups, rotation=20, ha="right", fontsize=8)
    ax5.set_title("Box-plot по группам", fontsize=10)
    ax5.set_ylabel("Частота")

    ax6 = fig.add_subplot(gs[2, 0])
    vp = ax6.violinplot(inner_for_dist, showmeans=True, showmedians=True)
    for i, body in enumerate(vp["bodies"]):
        body.set_facecolor(palette[i % len(palette)])
        body.set_alpha(0.7)
    ax6.set_xticks(range(1, len(groups) + 1))
    ax6.set_xticklabels(groups, rotation=20, ha="right", fontsize=8)
    ax6.set_title("Violin-plot по группам", fontsize=10)
    ax6.set_ylabel("Частота")

    ax7 = fig.add_subplot(gs[2, 1])
    rng = np.random.default_rng(0)
    for i, g in enumerate(groups):
        freqs_g = list(counts[g].values())
        jitter = rng.uniform(-0.15, 0.15, len(freqs_g))
        ax7.scatter(
            [i + j for j in jitter],
            freqs_g,
            color=palette[i % len(palette)],
            s=40,
            alpha=0.8,
            zorder=3,
        )
        if freqs_g:
            ax7.hlines(float(np.mean(freqs_g)), i - 0.3, i + 0.3, colors=palette[i % len(palette)], linewidths=2, zorder=4)
    ax7.set_xticks(range(len(groups)))
    ax7.set_xticklabels(groups, rotation=20, ha="right", fontsize=8)
    ax7.set_title("Strip-plot (─ = среднее)", fontsize=10)
    ax7.set_ylabel("Частота")

    ax8 = fig.add_subplot(gs[2, 2])
    _axis_cdf_percentiles(ax8, arr, pcts)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    log.info("График сохранён: %s", output_path)
    if show:
        plt.show()
    plt.close(fig)


def _render_statistics_figure_many_groups(
    groups: list[str],
    arr: Any,
    inner_values: list[list[Any]],
    pcts: dict[int, float],
    *,
    n_bins: int,
    show: bool,
    log: logging.Logger,
    output_path: Path,
    sns_module: Any,
    gridspec_module: Any,
    plt_module: Any,
    stats_module: Any,
    np_module: Any,
) -> None:
    """Overview layout when there are too many groups for per-group categorical plots."""
    np = np_module
    plt = plt_module
    stats = stats_module
    gs = gridspec_module

    group_sizes = [len(v) for v in inner_values]
    group_means = np.array([float(np.mean(v)) if v else np.nan for v in inner_values], dtype=float)
    group_totals = np.array([sum(v) for v in inner_values], dtype=float)

    fig = plt.figure(figsize=(14, 11))
    fig.suptitle(
        f"Статистика по проекту ({len(arr)} объектов, {len(groups)} групп; "
        f"без помесячных bar/box — см. stats_report.txt)",
        fontsize=12,
        fontweight="bold",
        y=0.98,
    )
    gspec = gs.GridSpec(3, 2, figure=fig, height_ratios=[1.15, 1.0, 1.0], hspace=0.38, wspace=0.28)

    ax_hist = fig.add_subplot(gspec[0, :])
    _axis_hist_kde(ax_hist, arr, n_bins=n_bins, sns_module=sns_module)

    ax_qq = fig.add_subplot(gspec[1, 0])
    (osm, osr), (slope, intercept, r) = stats.probplot(arr, dist="norm")
    ax_qq.plot(osm, osr, "o", color="#5B8DB8", markersize=3, alpha=0.65)
    ax_qq.plot(osm, slope * np.array(osm) + intercept, "--", color="#E07B54", linewidth=1.5)
    ax_qq.set_title(f"Q-Q (норм.)  R²={r**2:.3f}", fontsize=10)
    ax_qq.set_xlabel("Теор. квантили")
    ax_qq.set_ylabel("Выборочные квантили")

    ax_cdf = fig.add_subplot(gspec[1, 1])
    _axis_cdf_percentiles(ax_cdf, arr, pcts)

    ax_sc = fig.add_subplot(gspec[2, 0])
    mask = ~np.isnan(group_means)
    sc = ax_sc.scatter(
        np.array(group_sizes, dtype=float)[mask],
        group_means[mask],
        c=group_totals[mask],
        cmap="viridis",
        s=28,
        alpha=0.65,
        edgecolors="white",
        linewidths=0.35,
    )
    plt.colorbar(sc, ax=ax_sc, label="Σ частот в группе")
    ax_sc.set_xlabel("Число объектов (global_id) в группе")
    ax_sc.set_ylabel("Средняя частота в группе")
    ax_sc.set_title("Группы: размер vs средняя частота (цвет = сумма частот)", fontsize=10)

    ax_gh = fig.add_subplot(gspec[2, 1])
    gm = group_means[mask]
    nb = min(48, max(12, len(groups) // 4))
    ax_gh.hist(gm, bins=nb, color="#6BAE75", edgecolor="white", linewidth=0.6)
    ax_gh.axvline(float(np.mean(gm)), color="#E07B54", linestyle="--", linewidth=1.2, label=f"среднее {np.mean(gm):.2f}")
    ax_gh.legend(fontsize=8)
    ax_gh.set_xlabel("Средняя частота по группе")
    ax_gh.set_ylabel("Число групп")
    ax_gh.set_title("Распределение средних частот между группами", fontsize=10)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    log.info("График сохранён: %s", output_path)
    if show:
        plt.show()
    plt.close(fig)

#!/usr/bin/env python3
"""Repeatable checks for the fictional demo posters.

Official templates are not opened and not modified. Numbers in the fixtures
are synthetic and must stay labeled as demo data.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def chrome_binary() -> str:
    """Use the stable binary.

    /usr/local/bin/google-chrome on the Cloud Agent image is a desktop wrapper.
    It pins remote-debugging-port 9222 and a shared profile, then appends the
    caller's flags. Headless dump-dom through that wrapper does not exit.
    """
    stable = Path("/usr/bin/google-chrome-stable")
    if stable.is_file():
        return str(stable)
    found = shutil.which("google-chrome")
    if found:
        return found
    raise SystemExit("未找到 google-chrome-stable 或 google-chrome")

REQUIRED_SNIPPETS = (
    "演示数据",
    "虚构",
    "合成",
    "卖方预估",
    "Whisper",
    "正式实际",
    "Beat",
    "核心经营",
    "前瞻",
    "卖方预测修正",
    "已有仓位",
    "新资金",
    "失效条件",
    "无真实持仓",
)

CASES = (
    {
        "name": "single-mobile",
        "file": "fixtures/demo/single-poster.html",
        "window": (1080, 1920),
        "page": (1080, 1920),
        "gutter": False,
        "screenshot": "demo_single_mobile_1080x1920.png",
    },
    {
        "name": "single-desktop",
        "file": "fixtures/demo/single-poster.html",
        "window": (1440, 1920),
        "page": (1080, 1920),
        "gutter": True,
        "screenshot": "demo_single_desktop_1440x1920.png",
    },
    {
        "name": "combined-mobile",
        "file": "fixtures/demo/combined-poster.html",
        "window": (1080, 1920),
        "page": (1080, 1920),
        "gutter": False,
        "screenshot": "demo_combined_mobile_1080x1920.png",
    },
    {
        "name": "combined-desktop",
        "file": "fixtures/demo/combined-poster.html",
        "window": (1440, 1920),
        "page": (1080, 1920),
        "gutter": True,
        "screenshot": "demo_combined_desktop_1440x1920.png",
    },
)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"{path} 不是 PNG")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def run_case(case: dict, out_dir: Path) -> dict:
    html_path = ROOT / case["file"]
    if not html_path.is_file():
        raise SystemExit(f"缺少夹具: {html_path}")
    width, height = case["window"]
    screenshot = out_dir / case["screenshot"]
    with tempfile.TemporaryDirectory(prefix="earnings-chrome-") as profile:
        cmd = [
            chrome_binary(),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--allow-file-access-from-files",
            f"--window-size={width},{height}",
            f"--user-data-dir={profile}",
            f"--screenshot={screenshot}",
            "--dump-dom",
            html_path.resolve().as_uri(),
        ]
        try:
            proc = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise SystemExit(f"Chrome 超过 30 秒未退出: {case['name']}") from exc
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"Chrome 退出码 {proc.returncode}: {case['name']}")
    match = re.search(
        r'<pre id="accept-report"[^>]*>(.*?)</pre>',
        proc.stdout,
        re.S,
    )
    if not match:
        sys.stderr.write(proc.stdout[-2000:])
        sys.stderr.write(proc.stderr[-2000:])
        raise SystemExit(f"没有读到验收报告: {case['name']}")
    report = json.loads(html.unescape(match.group(1)))
    page_text = proc.stdout
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in page_text]
    image_size = png_size(screenshot) if screenshot.is_file() else (0, 0)
    expect_page = case["page"]
    gutter_ok = True
    if case["gutter"]:
        gutter_ok = 160 <= report.get("pageLeft", -1) <= 200
    else:
        gutter_ok = abs(report.get("pageLeft", 99)) <= 2
    ok = (
        report.get("phase") == "fonts-ready"
        and report.get("demo") is True
        and report.get("fictional") is True
        and report.get("synthetic") is True
        and report.get("pageWidth") == expect_page[0]
        and report.get("pageHeight") == expect_page[1]
        and report.get("innerWidth") == width
        and report.get("overflows") == []
        and report.get("errors") == []
        and report.get("fontStatus") == "loaded"
        and not missing
        and image_size == (width, height)
        and gutter_ok
        and any(item.startswith("LXGW:") and item.endswith(":loaded") for item in report.get("fonts", []))
    )
    return {
        "name": case["name"],
        "ok": ok,
        "screenshot": str(screenshot),
        "imageSize": list(image_size),
        "expectedImage": [width, height],
        "page": [report.get("pageWidth"), report.get("pageHeight")],
        "expectedPage": list(expect_page),
        "pageLeft": report.get("pageLeft"),
        "gutterOk": gutter_ok,
        "phase": report.get("phase"),
        "fontStatus": report.get("fontStatus"),
        "overflows": report.get("overflows"),
        "errors": report.get("errors"),
        "missingSnippets": missing,
        "fonts": report.get("fonts"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="验收虚构财报海报夹具")
    parser.add_argument(
        "--out",
        default="/tmp/earnings-demo-preview",
        help="截图输出目录",
    )
    args = parser.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = [run_case(case, out_dir) for case in CASES]
    summary = {"ok": all(item["ok"] for item in results), "results": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

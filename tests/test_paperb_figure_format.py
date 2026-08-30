import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "paperB" / "render_figures.py"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")
    return struct.unpack(">II", header[16:24])


def pdf_text(path: Path) -> str:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise unittest.SkipTest("pdftotext is required for PDF text inspection")
    completed = subprocess.run(
        [executable, "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return " ".join(completed.stdout.split())


def blue_pixel_groups(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")

    offset = 8
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if depth != 8 or color_type not in (2, 6) or interlace != 0:
                raise AssertionError(f"Unsupported PNG format: {path}")
            channels = 3 if color_type == 2 else 4
        elif chunk_type == b"IDAT":
            compressed.extend(payload)
        elif chunk_type == b"IEND":
            break

    raw = zlib.decompress(compressed)
    stride = width * channels
    previous = bytearray(stride)
    dark_blue = 0
    supporting_blue = 0
    cursor = 0

    def paeth(left: int, above: int, upper_left: int) -> int:
        prediction = left + above - upper_left
        distances = (
            abs(prediction - left),
            abs(prediction - above),
            abs(prediction - upper_left),
        )
        return (left, above, upper_left)[distances.index(min(distances))]

    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor : cursor + stride]
        cursor += stride
        row = bytearray(stride)
        for index, value in enumerate(encoded):
            left = row[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            predictor = {
                0: 0,
                1: left,
                2: above,
                3: (left + above) // 2,
                4: paeth(left, above, upper_left),
            }[filter_type]
            row[index] = (value + predictor) & 0xFF
        for index in range(0, stride, channels):
            red, green, blue = row[index : index + 3]
            if blue - red >= 35 and blue - green >= 18 and red < 70:
                dark_blue += 1
            if blue - red >= 15 and blue - green >= 8 and red >= 70:
                supporting_blue += 1
        previous = row
    return dark_blue, supporting_blue


class PaperBFigureFormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.temp_dir.name)
        for suffix in (".pdf", ".png"):
            (cls.output_dir / f"figure1_theta_distribution_cutoff{suffix}").write_bytes(
                b"legacy combined figure"
            )
        completed = subprocess.run(
            [
                sys.executable,
                str(RENDERER),
                "--project-root",
                str(ROOT),
                "--output-dir",
                str(cls.output_dir),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_exported_pdfs_keep_ticks_but_remove_variable_names_and_other_text(self):
        expectations = {
            "figure1a_theta_distribution_cutoff.pdf": {
                "ticks": ["0.05"],
                "removed": ["Density", "Rank", "Empirical adaptation index", "Country-average", "Distribution of empirical theta", "Country-year distribution", "Countries ranked", "Histogram", "Kernel density", "Below cutoff", "At/above cutoff", "Dashed line", "Chile", "Italy", "Greece", "Japan"],
            },
            "figure1b_theta_country_rank_cutoff.pdf": {
                "ticks": ["0.05", "50"],
                "removed": ["Density", "Rank", "Empirical adaptation index", "Country-average", "Distribution of empirical theta", "Country-year distribution", "Countries ranked", "Histogram", "Kernel density", "Below cutoff", "At/above cutoff", "Dashed line"],
            },
            "figure2_mA_by_debt_wsdi.pdf": {
                "ticks": ["P10", "P90"],
                "removed": ["Marginal spread relief", "Current debt/GDP percentile", "WSDI percentile", "Empirical marginal spread relief", "By current debt/GDP", "By WSDI exposure", "held at its source-sample mean", "Raw values", "Dots: point estimates"],
            },
            "debt_marginal_effect_no_b.pdf": {
                "ticks": ["0.30", "0.20"],
                "removed": ["Empirical adaptation index", "Marginal effect on change in debt/GDP", "Debt/GDP change at", "Full controls", "Point estimate", "95% CI", "Dashed line"],
            },
            "readiness_marginal_effect_debt_cutoff_no_lag.pdf": {
                "ticks": ["0.30", "0.20"],
                "removed": ["Empirical adaptation index", "Marginal effect on readiness level", "Readiness at", "Cutoff inherited", "Point estimate", "95% CI", "Dashed line"],
            },
            "kink_marginal_effects_no_state.pdf": {
                "ticks": ["0.30", "0.20"],
                "removed": ["Empirical adaptation index", "Marginal effect on change in debt/GDP", "Marginal effect on readiness level", "Debt/GDP change at", "Readiness at", "Full controls", "Cutoff inherited", "Point estimate", "95% CI", "Dashed line"],
            },
        }

        for filename, expected in expectations.items():
            with self.subTest(filename=filename):
                path = self.output_dir / filename
                self.assertTrue(path.is_file(), filename)
                text = pdf_text(path)
                for label in expected["ticks"]:
                    self.assertIn(label, text)
                for label in expected["removed"]:
                    self.assertNotIn(label, text)

    def test_png_canvas_matches_square_panel_layouts(self):
        expected_ratios = {
            "debt_marginal_effect_no_b.png": 1.0,
            "readiness_marginal_effect_debt_cutoff_no_lag.png": 1.0,
            "figure1a_theta_distribution_cutoff.png": 1.0,
            "figure1b_theta_country_rank_cutoff.png": 1.0,
            "figure2_mA_by_debt_wsdi.png": 2.0,
            "kink_marginal_effects_no_state.png": 0.5,
        }

        for filename, expected_ratio in expected_ratios.items():
            with self.subTest(filename=filename):
                path = self.output_dir / filename
                self.assertTrue(path.is_file(), filename)
                width, height = png_size(path)
                self.assertAlmostEqual(width / height, expected_ratio, delta=0.08)

    def test_renderer_replaces_combined_figure1_with_two_standalone_figures(self):
        expected = {
            "figure1a_theta_distribution_cutoff.pdf",
            "figure1a_theta_distribution_cutoff.png",
            "figure1b_theta_country_rank_cutoff.pdf",
            "figure1b_theta_country_rank_cutoff.png",
        }
        actual = {path.name for path in self.output_dir.iterdir()}
        self.assertTrue(expected.issubset(actual))
        self.assertNotIn("figure1_theta_distribution_cutoff.pdf", actual)
        self.assertNotIn("figure1_theta_distribution_cutoff.png", actual)

    def test_country_rank_figure_labels_only_representative_countries(self):
        rank_path = self.output_dir / "figure1b_theta_country_rank_cutoff.pdf"
        distribution_path = self.output_dir / "figure1a_theta_distribution_cutoff.pdf"
        self.assertTrue(rank_path.is_file())
        self.assertTrue(distribution_path.is_file())
        rank_text = pdf_text(rank_path)
        distribution_text = pdf_text(distribution_path)
        for country in ("Chile", "Italy", "Greece", "Japan"):
            self.assertIn(country, rank_text)
            self.assertNotIn(country, distribution_text)

    def test_exported_pngs_use_dark_and_supporting_blue_tones(self):
        for path in sorted(self.output_dir.glob("*.png")):
            with self.subTest(filename=path.name):
                dark_blue, supporting_blue = blue_pixel_groups(path)
                self.assertGreater(dark_blue, 250)
                self.assertGreater(supporting_blue, 250)


if __name__ == "__main__":
    unittest.main()

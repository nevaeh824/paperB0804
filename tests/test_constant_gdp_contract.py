import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "data0804" / "build_invest_panel_weo.py"
ANALYSIS_CSV = ROOT / "data0804" / "invest_panel_weo.csv"
WEO_XLSX = ROOT / "data0804" / "WEOApr2026all.xlsx"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_invest_panel_weo", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class GDPControlContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def test_builder_reads_gdp_controls_from_weo(self):
        self.assertEqual(
            list(self.builder.WEO_FIELDS.items())[:4],
            [
                ("GGR_NGDP", "Revenue_gdp"),
                ("NGDP", "CurrentGDP"),
                ("NGDP_R", "ConstantGDP"),
                ("NGDPRPPPPC", "capitaGDP"),
            ],
        )

        weo_values, numeric_values, metadata, _ = self.builder.read_weo_values()
        self.assertIn(("AUS", 1995, "NGDP_R"), numeric_values)
        self.assertEqual(numeric_values[("AUS", 1995, "NGDP_R")], 1155.779)
        ngdp_r = metadata.loc[metadata["code"].eq("NGDP_R")]
        self.assertEqual(len(ngdp_r), 197)
        self.assertEqual(
            len({iso3 for iso3, _, code in numeric_values if code == "NGDP_R"}),
            196,
        )
        self.assertEqual(ngdp_r["unit"].drop_duplicates().tolist(), ["Domestic currency"])
        self.assertEqual(ngdp_r["scale"].drop_duplicates().tolist(), ["Billions"])
        self.assertIn(("AUS", 1995, "NGDPRPPPPC"), numeric_values)
        self.assertEqual(numeric_values[("AUS", 1995, "NGDPRPPPPC")], 39682.821)
        capita = metadata.loc[metadata["code"].eq("NGDPRPPPPC")]
        self.assertEqual(len(capita), 197)
        self.assertEqual(
            capita.loc[capita["scale"].ne(""), "scale"].drop_duplicates().tolist(),
            ["Units"],
        )
        self.builder.verify_weo_reconciliation(weo_values)

    def test_existing_constant_gdp_matches_weo_ngdp_r(self):
        workbook = load_workbook(
            WEO_XLSX,
            read_only=True,
            data_only=True,
            keep_links=False,
        )
        worksheet = workbook["Countries"]
        rows = worksheet.iter_rows(values_only=True)
        headers = [str(value).strip() if value is not None else "" for value in next(rows)]
        index = {name: position for position, name in enumerate(headers)}
        source = {}
        for row in rows:
            if row[index["INDICATOR.ID"]] != "NGDP_R":
                continue
            iso3 = str(row[index["COUNTRY.ID"]]).strip()
            for year in range(1995, 2024):
                value = row[index[str(year)]]
                if value not in (None, ""):
                    source[(iso3, year)] = float(value)
        workbook.close()

        output_rows = read_csv(ANALYSIS_CSV)
        output = {
            (row["iso3"], int(row["year"])): (
                None if row["ConstantGDP"] == "" else float(row["ConstantGDP"])
            )
            for row in output_rows
        }
        relevant_source = {key: source.get(key) for key in output}

        self.assertEqual(len(output), 1827)
        self.assertEqual(sum(value is not None for value in output.values()), 1825)
        self.assertEqual(
            {key for key, value in output.items() if value is None},
            {key for key, value in relevant_source.items() if value is None},
        )
        differences = [
            abs(value - relevant_source[key])
            for key, value in output.items()
            if value is not None
        ]
        self.assertEqual(max(differences), 0.0)
        self.assertEqual(sum(value <= 0 for value in output.values() if value is not None), 0)

    def test_existing_capita_gdp_matches_weo_ngdprppppc(self):
        _, numeric_values, _, _ = self.builder.read_weo_values()
        output_rows = read_csv(ANALYSIS_CSV)
        output = {
            (row["iso3"], int(row["year"])): (
                None if row["capitaGDP"] == "" else float(row["capitaGDP"])
            )
            for row in output_rows
        }
        expected = {
            key: numeric_values.get((*key, "NGDPRPPPPC"))
            for key in output
        }
        self.assertEqual(len(output), 1827)
        self.assertEqual(sum(value is not None for value in output.values()), 1823)
        self.assertEqual(
            {key for key, value in output.items() if value is None},
            {key for key, value in expected.items() if value is None},
        )
        differences = [
            abs(value - expected[key])
            for key, value in output.items()
            if value is not None
        ]
        self.assertEqual(max(differences), 0.0)
        self.assertEqual(sum(value <= 0 for value in output.values() if value is not None), 0)

    def test_add_weo_column_preserves_existing_rows_and_columns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "panel.csv"
            path.write_text(
                "iso3,year,ConstantGDP,tail\nAUS,1995,100,x\nSRB,1995,200,y\n",
                encoding="utf-8",
            )
            values = {("AUS", 1995, "NGDPRPPPPC"): "39682.821"}
            self.builder.add_weo_column(path, "NGDPRPPPPC", values)
            self.assertEqual(
                path.read_text(encoding="utf-8").splitlines(),
                [
                    "iso3,year,ConstantGDP,capitaGDP,tail",
                    "AUS,1995,100,39682.821,x",
                    "SRB,1995,200,,y",
                ],
            )

    def test_profile_omits_blank_weo_unit_components(self):
        _, _, metadata, source_country_codes = self.builder.read_weo_values()
        _, source_rows = self.builder.read_csv_rows(ANALYSIS_CSV)
        _, _, _, coverage, _ = self.builder.profile_output(
            source_rows,
            metadata,
            source_country_codes,
        )
        capita = next(row for row in coverage if row[0] == "`capitaGDP`")
        self.assertEqual(capita[4], "Units")

if __name__ == "__main__":
    unittest.main()

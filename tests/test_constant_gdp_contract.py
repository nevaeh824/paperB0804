import csv
import importlib.util
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "data0804" / "build_invest_panel_weo.py"
ANALYSIS_CSV = ROOT / "data0804" / "invest_panel_weo.csv"
WEO_XLSX = ROOT / "data0804" / "WEOApr2026all.xlsx"
WDI_RESERVES_CSV = ROOT / "data0804" / "API_FI.RES.TOTL.CD_DS2_en_csv_v2_14.csv"
VULNERABILITY_DELTA_CSV = (
    ROOT
    / "data0804/ndgain_countryindex_2026/resources/vulnerability/vulnerability_delta.csv"
)
READINESS_DELTA_CSV = (
    ROOT
    / "data0804/ndgain_countryindex_2026/resources/readiness/readiness_delta.csv"
)


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
                ("NGDPD", "CurrentGDP"),
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

    def test_current_gdp_matches_weo_ngdpd_and_reserves_use_usd_formula(self):
        workbook = load_workbook(
            WEO_XLSX, read_only=True, data_only=True, keep_links=False
        )
        worksheet = workbook["Countries"]
        rows = worksheet.iter_rows(values_only=True)
        headers = [str(value).strip() if value is not None else "" for value in next(rows)]
        index = {name: position for position, name in enumerate(headers)}
        ngdpd = {}
        for row in rows:
            if row[index["INDICATOR.ID"]] != "NGDPD":
                continue
            iso3 = str(row[index["COUNTRY.ID"]]).strip()
            for year in range(1995, 2024):
                value = row[index[str(year)]]
                if value not in (None, ""):
                    ngdpd[(iso3, year)] = Decimal(str(value))
        workbook.close()

        with WDI_RESERVES_CSV.open(encoding="utf-8-sig", newline="") as handle:
            raw_rows = csv.reader(handle)
            for header in raw_rows:
                if header and header[0] == "Country Name":
                    break
            reserve_rows = [dict(zip(header, row)) for row in raw_rows]
        reserve_usd = {
            (row["Country Code"], year): Decimal(row[str(year)])
            for row in reserve_rows
            if row["Indicator Code"] == "FI.RES.TOTL.CD"
            for year in range(1995, 2024)
            if row[str(year)] != ""
        }

        output_rows = read_csv(ANALYSIS_CSV)
        current_populated = 0
        reserves_populated = 0
        current_missing = set()
        reserves_missing = set()
        for row in output_rows:
            key = (row["iso3"], int(row["year"]))
            expected_current = ngdpd.get(key)
            if expected_current is None:
                self.assertEqual(row["CurrentGDP"], "")
                current_missing.add(key)
            else:
                self.assertEqual(Decimal(row["CurrentGDP"]), expected_current)
                current_populated += 1

            if expected_current is None or key not in reserve_usd:
                self.assertEqual(row["reserves"], "")
                reserves_missing.add(key)
            else:
                expected_reserves = (
                    reserve_usd[key] / Decimal("1e9") / expected_current * Decimal("100")
                )
                self.assertAlmostEqual(
                    float(row["reserves"]), float(expected_reserves), places=12
                )
                reserves_populated += 1

        self.assertEqual(current_populated, 1825)
        self.assertEqual(current_missing, {("SRB", 1995), ("SRB", 1996)})
        self.assertEqual(reserves_populated, 1757)
        self.assertEqual(len(reserves_missing), 70)
        self.assertEqual(
            {iso3 for iso3, _ in reserves_missing}, {"CIV", "HKG", "SRB", "TWN"}
        )

    def test_refresh_currentgdp_and_reserves_updates_only_requested_columns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "panel.csv"
            target.write_text(
                "iso3,year,CurrentGDP,reserves,tail\n"
                "AUS,1995,old,old,x\nSRB,1995,old,old,y\n",
                encoding="utf-8",
            )
            weo_values = {("AUS", 1995, "NGDPD"): "400"}
            reserve_values = {("AUS", 1995): "20000000000"}
            self.builder.refresh_currentgdp_and_reserves(
                target, weo_values, reserve_values
            )
            self.assertEqual(
                target.read_text(encoding="utf-8").splitlines(),
                [
                    "iso3,year,CurrentGDP,reserves,tail",
                    "AUS,1995,400,5,x",
                    "SRB,1995,,,y",
                ],
            )

    def test_reserves_formula_rejects_nonpositive_ngdpd(self):
        with self.assertRaisesRegex(ValueError, "NGDPD must be positive"):
            self.builder.calculate_reserves("0", "1000000000")

    def test_preservation_check_allows_only_reserves_recalculation(self):
        source = [{"iso3": "AUS", "year": "1995", "reserves": "old", "tail": "x"}]
        output = [{"iso3": "AUS", "year": "1995", "reserves": "5", "tail": "x"}]
        self.builder.verify_preservation(
            ["iso3", "year", "reserves", "tail"], source, output
        )
        output[0]["tail"] = "changed"
        with self.assertRaisesRegex(AssertionError, "tail"):
            self.builder.verify_preservation(
                ["iso3", "year", "reserves", "tail"], source, output
            )

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
        _, _, _, coverage, quality = self.builder.profile_output(
            source_rows,
            metadata,
            source_country_codes,
        )
        capita = next(row for row in coverage if row[0] == "`capitaGDP`")
        self.assertEqual(capita[4], "Units")
        self.assertTrue(quality["reserves_formula_missingness_matches"])
        self.assertLessEqual(quality["reserves_formula_max_difference"], 1e-12)
        self.assertEqual(quality["nonpositive_CurrentGDP"], 0)

    def test_delta_columns_equal_ndgain_source_values_times_100(self):
        output_rows = read_csv(ANALYSIS_CSV)
        self.assertEqual(len(output_rows), 1827)
        self.assertEqual(
            list(output_rows[0]).index("vulnerability_delta100"),
            list(output_rows[0]).index("vulnerability100") + 1,
        )
        self.assertEqual(
            list(output_rows[0]).index("readiness_delta100"),
            list(output_rows[0]).index("readiness100") + 1,
        )

        sources = {
            "vulnerability_delta100": VULNERABILITY_DELTA_CSV,
            "readiness_delta100": READINESS_DELTA_CSV,
        }
        target_keys = {(row["iso3"], int(row["year"])) for row in output_rows}
        self.assertEqual(len(target_keys), 1827)
        for output_name, source_path in sources.items():
            source_rows = read_csv(source_path)
            source = {
                (row["ISO3"], year): Decimal(row[str(year)]) * Decimal("100")
                for row in source_rows
                for year in range(1995, 2024)
                if row[str(year)] != ""
            }
            populated = 0
            missing_keys = set()
            for row in output_rows:
                key = (row["iso3"], int(row["year"]))
                actual = row[output_name]
                expected = source.get(key)
                if expected is None:
                    self.assertEqual(actual, "")
                    missing_keys.add(key)
                else:
                    self.assertEqual(Decimal(actual), expected)
                    populated += 1
            self.assertEqual(populated, 1769)
            self.assertEqual(len(missing_keys), 58)
            self.assertEqual({iso3 for iso3, _ in missing_keys}, {"HKG", "TWN"})

    def test_add_ndgain_delta_columns_preserves_existing_panel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            target = tmp / "panel.csv"
            vulnerability = tmp / "vulnerability.csv"
            readiness = tmp / "readiness.csv"
            target.write_text(
                "iso3,year,vulnerability100,readiness100,tail\n"
                "AUS,1995,30,60,x\nHKG,1995,40,70,y\n",
                encoding="utf-8",
            )
            vulnerability.write_text(
                "ISO3,Name,1995\nAUS,Australia,0.125\n",
                encoding="utf-8",
            )
            readiness.write_text(
                "ISO3,Name,1995\nAUS,Australia,-0.03125\n",
                encoding="utf-8",
            )
            self.builder.add_ndgain_delta_columns(
                target,
                {
                    "vulnerability_delta100": vulnerability,
                    "readiness_delta100": readiness,
                },
                years=range(1995, 1996),
            )
            self.assertEqual(
                target.read_text(encoding="utf-8").splitlines(),
                [
                    "iso3,year,vulnerability100,vulnerability_delta100,readiness100,readiness_delta100,tail",
                    "AUS,1995,30,12.5,60,-3.125,x",
                    "HKG,1995,40,,70,,y",
                ],
            )

    def test_ndgain_delta_reader_rejects_duplicate_iso3(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "duplicate.csv"
            source.write_text(
                "ISO3,Name,1995\nAUS,Australia,0.1\nAUS,Australia duplicate,0.2\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Duplicate ND-GAIN ISO3"):
                self.builder.read_ndgain_delta_values(
                    source, years=range(1995, 1996)
                )

if __name__ == "__main__":
    unittest.main()

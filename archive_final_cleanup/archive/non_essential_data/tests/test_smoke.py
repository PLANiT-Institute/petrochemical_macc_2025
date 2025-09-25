
import os
from petrochem.data_io import read_excel, baseline_total_mt, targets_map, build_timeseries, parse_links

def test_smoke():
    excel = os.path.join(os.path.dirname(__file__), "..", "examples", "kr_petchem_netzero_model_validated_v14.xlsx")
    sheets = read_excel(excel)
    years, tmap = targets_map(sheets, None)
    base = baseline_total_mt(sheets)
    techs, params = build_timeseries(sheets, years, ramp_default=0.2)
    groups, depends = parse_links(sheets)
    assert base >= 0 and len(years)>0 and len(techs)>0

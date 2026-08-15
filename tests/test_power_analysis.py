import importlib.util
from pathlib import Path

import pytest


def _power_module():
    path = Path("scripts/power_analysis.py")
    spec = importlib.util.spec_from_file_location("power_analysis", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_core_power_table_uses_640_evaluations():
    module = _power_module()
    table = module.build_power_table(32, 5)
    assert table["planned_evaluations"].eq(640).all()
    assert set(table["contrast"]) == {"main_effect", "interaction"}
    assert table.loc[
        table["contrast"].eq("interaction"),
        "mde_alpha_05_power_80",
    ].min() > table.loc[
        table["contrast"].eq("main_effect"),
        "mde_alpha_05_power_80",
    ].min()


def test_five_repetitions_improve_mde_with_diminishing_returns():
    module = _power_module()
    one = module.build_power_table(32, 1)
    five = module.build_power_table(32, 5)
    ten = module.build_power_table(32, 10)
    key = (one["outcome"].eq("fit_score")) & one["contrast"].eq("main_effect")
    mde_one = one.loc[key, "mde_alpha_05_power_80"].iloc[0]
    mde_five = five.loc[key, "mde_alpha_05_power_80"].iloc[0]
    mde_ten = ten.loc[key, "mde_alpha_05_power_80"].iloc[0]
    assert mde_five < mde_one
    assert (mde_one - mde_five) > (mde_five - mde_ten)
    assert mde_five == pytest.approx(0.246, abs=0.01)

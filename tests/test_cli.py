from pathlib import Path

import pytest

from expense_tracker.cli import main


def test_add_bad_amount_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["add", "-5", "food"], db_path=tmp_path / "t.db")
    assert code == 1
    assert "error" in capsys.readouterr().err


def test_add_text_amount_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["add", "abc", "food"], db_path=tmp_path / "t.db")
    assert code == 1
    assert "error" in capsys.readouterr().err


def test_add_then_list_shows_expense(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = tmp_path / "t.db"
    assert main(["add", "12.50", "food", "--date", "2026-11-10"], db_path=db) == 0
    assert main(["list"], db_path=db) == 0
    out = capsys.readouterr().out
    assert "12.50" in out
    assert "food" in out
    assert "2026-11-10" in out


def test_summary_shows_month_totals(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = tmp_path / "t.db"
    main(["add", "10.00", "food", "--date", "2026-11-01"], db_path=db)
    main(["add", "2.50", "food", "--date", "2026-11-30"], db_path=db)
    main(["add", "99.00", "rent", "--date", "2026-10-31"], db_path=db)
    capsys.readouterr()  # discard the "Added ..." lines

    assert main(["summary", "--month", "2026-11"], db_path=db) == 0
    out = capsys.readouterr().out
    assert "food: 12.50" in out
    assert "rent" not in out


def test_add_bad_date_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(
        ["add", "5", "food", "--date", "2026-13-01"], db_path=tmp_path / "t.db"
    )
    assert code == 1
    assert "error" in capsys.readouterr().err


def test_summary_bad_month_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["summary", "--month", "2026-13"], db_path=tmp_path / "t.db")
    assert code == 1
    assert "error" in capsys.readouterr().err


def test_delete_missing_id_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["delete", "999"], db_path=tmp_path / "t.db")
    assert code == 1
    assert "not found" in capsys.readouterr().err


def test_unknown_command_exits_2(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as e:
        main(["fly"], db_path=tmp_path / "t.db")
    assert e.value.code == 2

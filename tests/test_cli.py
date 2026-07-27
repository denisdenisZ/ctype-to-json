import json

import pytest

from ctype_to_json.cli import Pipeline, load_config, parse_args, verify_config


def make_ctx(headers_dir, config, **overrides):
    ctx = {
        "header": [str(headers_dir / "test_header.h")],
        "config": config,
        "out": None,
        "skip_unsupported": False,
        "emit_prober": False,
        "no_probe": False,
        "sizes": None,
        "debug": False,
    }
    ctx.update(overrides)
    return ctx


def test_parse_args_basic():
    args = parse_args(["-c", "config.toml", "-o", "out.json", "a.h", "b.h"])

    assert args.header == ["a.h", "b.h"]
    assert args.config == "config.toml"
    assert args.output == "out.json"
    assert not args.no_probe


def test_parse_args_mutually_exclusive_group_rejects_combo():
    with pytest.raises(SystemExit):
        parse_args(["--emit-prober", "--no-probe", "a.h"])


def test_load_config_reads_toml(fixtures_dir):
    config = load_config(str(fixtures_dir / "config.toml"))

    assert config["toolchain"]["cc"] == "gcc"
    assert config["parser"]["c_standard"] == "11"


def test_verify_config_requires_cc(fixtures_dir):
    with pytest.raises(SystemExit):
        verify_config(load_config(str(fixtures_dir / "config_missing_cc.toml")))


def test_verify_config_rejects_unsupported_standard(fixtures_dir):
    with pytest.raises(SystemExit):
        verify_config(load_config(str(fixtures_dir / "config_bad_std.toml")))


def test_verify_config_accepts_valid_config(fixtures_dir):
    verify_config(load_config(str(fixtures_dir / "config.toml")))


def test_pipeline_no_probe_outputs_parsed_data_without_sizes(
    headers_dir, fixtures_dir, capsys
):
    config = load_config(str(fixtures_dir / "config.toml"))
    ctx = make_ctx(headers_dir, config, no_probe=True)

    Pipeline(ctx).run()

    output = json.loads(capsys.readouterr().out)
    assert "size" not in output["ValueRange"]
    assert output["ValueRange"]["kind"] == "struct"


def test_pipeline_no_probe_writes_to_output_file(
    headers_dir, fixtures_dir, tmp_path
):
    config = load_config(str(fixtures_dir / "config.toml"))
    out_file = tmp_path / "out.json"
    ctx = make_ctx(headers_dir, config, no_probe=True, out=str(out_file))

    Pipeline(ctx).run()

    data = json.loads(out_file.read_text())
    assert "ControlConfig" in data


def test_pipeline_emit_prober_writes_c_source_named_after_output(
    headers_dir, fixtures_dir, tmp_path
):
    config = load_config(str(fixtures_dir / "config.toml"))
    out_file = tmp_path / "my_types.json"
    ctx = make_ctx(headers_dir, config, emit_prober=True, out=str(out_file))

    with pytest.raises(SystemExit) as exc_info:
        Pipeline(ctx).run()

    assert exc_info.value.code == 0
    prober_c = tmp_path / "my_types_prober.c"
    assert prober_c.exists()
    assert "sizeof(ValueRange)" in prober_c.read_text()


def test_pipeline_sizes_merges_precomputed_sizes_file(
    headers_dir, fixtures_dir, tmp_path
):
    config = load_config(str(fixtures_dir / "config.toml"))
    sizes_file = tmp_path / "sizes.txt"
    sizes_file.write_text(
        "ValueRange 12\n"
        "ValueRange.min_us 0\n"
        "ValueRange.min_us.size 4\n"
        "ValueRange.max_us 4\n"
        "ValueRange.max_us.size 4\n"
        "ValueRange.step_us 8\n"
        "ValueRange.step_us.size 4\n"
    )
    out_file = tmp_path / "out.json"
    ctx = make_ctx(
        headers_dir, config, sizes=str(sizes_file), out=str(out_file)
    )

    Pipeline(ctx).run()

    data = json.loads(out_file.read_text())
    assert data["ValueRange"]["size"] == 12


def test_pipeline_rejects_config_missing_cc(headers_dir, fixtures_dir):
    config = load_config(str(fixtures_dir / "config_missing_cc.toml"))
    ctx = make_ctx(headers_dir, config, no_probe=True)

    with pytest.raises(SystemExit):
        Pipeline(ctx).run()


def test_pipeline_skip_unsupported_drops_tainted_structs(
    headers_dir, fixtures_dir, capsys
):
    config = load_config(str(fixtures_dir / "config.toml"))
    ctx = make_ctx(
        headers_dir,
        config,
        header=[str(headers_dir / "unsupported_union.h")],
        no_probe=True,
        skip_unsupported=True,
    )

    Pipeline(ctx).run()

    captured = capsys.readouterr().out
    output = json.loads(captured[captured.index("{"):])
    assert "struct_with_union_field" not in output


def test_pipeline_normal_probe_end_to_end(
    headers_dir, fixtures_dir, has_gcc, capsys
):
    if not has_gcc:
        pytest.skip("gcc not available")

    config = load_config(str(fixtures_dir / "config.toml"))
    ctx = make_ctx(headers_dir, config)

    Pipeline(ctx).run()

    output = json.loads(capsys.readouterr().out)
    assert output["ValueRange"]["size"] == 12

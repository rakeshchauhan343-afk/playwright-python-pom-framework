import importlib


def load_config_reader():
    import utils.config_reader as config_reader

    return importlib.reload(config_reader)


def test_explicit_base_url_has_highest_precedence(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "qa")
    monkeypatch.setenv("QA_BASE_URL", "https://qa.example.test")
    monkeypatch.setenv("ORANGEHRM_URL", "https://legacy.example.test")
    monkeypatch.setenv("BASE_URL", "https://cli.example.test")

    config_reader = load_config_reader()

    assert config_reader.get_base_url() == "https://cli.example.test"


def test_environment_specific_url_is_supported(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("STAGING_BASE_URL", "https://staging.example.test")
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.setenv("ORANGEHRM_URL", "")

    config_reader = load_config_reader()

    assert config_reader.get_environment_name() == "staging"
    assert config_reader.get_base_url() == "https://staging.example.test"


def test_existing_yaml_default_remains_available(monkeypatch):
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.setenv("ORANGEHRM_URL", "")
    monkeypatch.setenv("ENVIRONMENT", "demo")

    config_reader = load_config_reader()

    assert config_reader.get_base_url() == "https://opensource-demo.orangehrmlive.com/"
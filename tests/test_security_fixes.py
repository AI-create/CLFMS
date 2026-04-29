from types import SimpleNamespace

from app.modules.auth import services as auth_services


def test_hash_otp_is_not_plaintext_and_is_deterministic():
    hashed_otp = auth_services._hash_otp("otp-hash@test.local", "123456")

    assert hashed_otp != "123456"
    assert len(hashed_otp) == 64
    assert hashed_otp == auth_services._hash_otp("otp-hash@test.local", "123456")


def test_otp_matches_supports_hashed_and_legacy_plaintext_entries():
    hashed_user = SimpleNamespace(
        email="legacy-otp@test.local",
        otp_code=auth_services._hash_otp("legacy-otp@test.local", "654321"),
    )
    plaintext_user = SimpleNamespace(email="legacy-otp@test.local", otp_code="654321")

    assert auth_services._otp_matches(hashed_user, "654321") is True
    assert auth_services._otp_matches(plaintext_user, "654321") is True
    assert auth_services._otp_matches(hashed_user, "000000") is False


def test_csp_disables_inline_scripts(test_client):
    response = test_client.get("/api/v1/health")

    assert response.status_code == 200
    csp = response.headers["Content-Security-Policy"]
    assert "script-src 'self';" in csp
    assert "script-src 'self' 'unsafe-inline'" not in csp
    assert "style-src 'self' 'unsafe-inline';" in csp

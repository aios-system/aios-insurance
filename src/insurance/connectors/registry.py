"""Insurance data connector configurations — 5 source systems.

Each connector defines how AIOS reads from an external system.
Passwords are stored as vault references, never in plaintext.
"""

from __future__ import annotations

from aios.data_platform.connectors import ConnectorConfig, ConnectorType


def get_connector_configs() -> list[ConnectorConfig]:
    """Return all 5 insurance connector configurations."""
    return [
        _guidewire_claims(),
        _duck_creek_policy(),
        _iso_claimsearch(),
        _edi_gateway(),
        _state_doi_reporting(),
    ]


def _guidewire_claims() -> ConnectorConfig:
    return ConnectorConfig(
        name="guidewire-claims",
        connector_type=ConnectorType.DATABASE,
        description="Claims management — policy holders, loss events, adjuster assignments",
        host="guidewire-db.insurance.internal",
        port=5432,
        database="ClaimsDB",
        username="aios_readonly",
        password_ref="vault://insurance/guidewire-password",
        extra_config={"driver": "postgresql", "ssl": True},
    )


def _duck_creek_policy() -> ConnectorConfig:
    return ConnectorConfig(
        name="duck-creek-policy",
        connector_type=ConnectorType.DATABASE,
        description="Policy administration — coverage details, endorsements, renewals",
        host="duckcreek-sql.insurance.internal",
        port=1433,
        database="PolicyAdmin",
        username="aios_reader",
        password_ref="vault://insurance/duckcreek-password",
        extra_config={"driver": "mssql"},
    )


def _iso_claimsearch() -> ConnectorConfig:
    return ConnectorConfig(
        name="iso-claimsearch",
        connector_type=ConnectorType.REST_API,
        description="Industry fraud database — cross-carrier claim history lookup",
        host="api.iso.com",
        extra_config={
            "base_path": "/claimsearch/v2/",
            "auth_type": "api_key",
            "api_key_ref": "vault://insurance/iso-api-key",
            "rate_limit": 100,
        },
    )


def _edi_gateway() -> ConnectorConfig:
    return ConnectorConfig(
        name="edi-gateway",
        connector_type=ConnectorType.REST_API,
        description="EDI 837/835 transaction processing — claims submission and remittance",
        host="edi-gateway.insurance.internal",
        extra_config={
            "base_path": "/api/v1/",
            "auth_type": "mutual_tls",
            "cert_ref": "vault://insurance/edi-cert",
        },
    )


def _state_doi_reporting() -> ConnectorConfig:
    return ConnectorConfig(
        name="state-doi-reporting",
        connector_type=ConnectorType.SFTP,
        description="Department of Insurance filings — regulatory submissions via SFTP",
        host="sftp.doi.state.gov",
        port=22,
        username="insurance_filing",
        password_ref="vault://insurance/doi-sftp-password",
        extra_config={"remote_dir": "/incoming/filings/"},
    )

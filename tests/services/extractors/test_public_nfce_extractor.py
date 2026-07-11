"""
Tests for the PublicNFCeExtractor.

These tests validate the complete extraction of NFC-e data from a real
public NFC-e HTML document.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.services.extractors.public_nfce_extractor import (
    PublicNFCeExtractor,
)

NFC_HTML_PATH = Path(__file__).resolve().parents[2] / "NFC.html"

def test_extract_complete_nfce_data_from_real_html() -> None:
    """
    Test complete NFC-e data extraction from a real HTML file.
    """

    html = NFC_HTML_PATH.read_text(encoding="utf-8")

    extractor = PublicNFCeExtractor()

    nfe_data = extractor.extract(html)

    assert (
        nfe_data.nfe_key
        == "42260609477652009061651010000629161601763233"
    )

    assert nfe_data.nfe_date == datetime(
        2026,
        6,
        26,
        15,
        3,
        17,
    )

    assert nfe_data.market_data.market_name == (
        "SDB COMERCIO DE ALIMENTOS LTDA"
    )
    assert nfe_data.market_data.cnpj == "09477652009061"
    assert nfe_data.market_data.market_street == (
        "SC401 RF JOSE CARLOS DAUX"
    )
    assert nfe_data.market_data.market_number == "9580"
    assert nfe_data.market_data.market_district == (
        "STO ANTONIO DE LISBOA"
    )
    assert nfe_data.market_data.market_city == "FLORIANOPOLIS"
    assert nfe_data.market_data.market_state == "SC"

    assert len(nfe_data.products_data) == 7

    first_product = nfe_data.products_data[0]

    assert first_product.name == "LEITE ITALAC INTEG 1L"
    assert first_product.product_code == "7898080640611"
    assert first_product.code_type == "EAN"
    assert first_product.quantity == Decimal("1")
    assert first_product.unit_price == Decimal("4.98")
    assert first_product.total_price == Decimal("4.98")

    fourth_product = nfe_data.products_data[3]

    assert fourth_product.name == "POKAN KG"
    assert fourth_product.product_code == "540"
    assert fourth_product.code_type == "INTERNAL"
    assert fourth_product.quantity == Decimal("0.49")
    assert fourth_product.unit_price == Decimal("4.98")
    assert fourth_product.total_price == Decimal("2.44")

    last_product = nfe_data.products_data[6]

    assert last_product.name == "LARANJA PERA KG"
    assert last_product.product_code == "182"
    assert last_product.code_type == "INTERNAL"
    assert last_product.quantity == Decimal("1.2")
    assert last_product.unit_price == Decimal("4.78")
    assert last_product.total_price == Decimal("5.74")
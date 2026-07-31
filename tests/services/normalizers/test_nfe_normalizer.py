"""Tests for the NFC-e data normalizer."""

from datetime import datetime
from decimal import Decimal

import pytest

from app.schemas.nfe_data import NFEData, NFEMarketData, NFEProductData
from app.services.normalizers.nfe_normalizer import NfeNormalizer


@pytest.fixture
def extracted_nfe_data() -> NFEData:
    """Return sample NFC-e data before normalization."""
    return NFEData(
        nfe_key="1234 5678 9012 3456 7890 1234 5678 9012 3456 7890 1234",
        nfe_date=datetime(2026, 6, 26, 15, 3, 17),
        market_data=NFEMarketData(
            cnpj="12.345.678/0001-90",
            market_name="  Market   Example LTDA  ",
            market_street="  Main   Street  ",
            market_number="  100  ",
            market_district="  Downtown  ",
            market_city="  Florianópolis  ",
            market_state=" sc ",
        ),
        products_data=[
            NFEProductData(
                product_code="7898 0806 4061 1",
                code_type="EAN",
                name="  WHOLE   MILK 1L  ",
                unit_price=Decimal("6.90"),
                total_price=Decimal("13.80"),
                quantity=Decimal("2"),
                ncm_code=None,
                brand="  Example   Brand  ",
                picture_url="  https://example.com/milk.jpg  ",
            ),
            NFEProductData(
                product_code="ABC-001",
                code_type="INTERNAL",
                name="  POKAN   KG  ",
                unit_price=Decimal("8.99"),
                total_price=Decimal("11.24"),
                quantity=Decimal("1.250"),
                ncm_code="08.05.21.00",
                brand=None,
                picture_url=None,
            ),
        ],
    )


def test_normalize_complete_nfe_data(
    extracted_nfe_data: NFEData,
) -> None:
    """Normalize all supported NFC-e fields."""
    normalized_data = NfeNormalizer.normalize(extracted_nfe_data)

    assert normalized_data.nfe_key == (
        "12345678901234567890123456789012345678901234"
    )
    assert normalized_data.nfe_date == datetime(2026, 6, 26, 15, 3, 17)

    assert normalized_data.market_data.cnpj == "12345678000190"
    assert normalized_data.market_data.market_name == "Market Example LTDA"
    assert normalized_data.market_data.market_street == "Main Street"
    assert normalized_data.market_data.market_number == "100"
    assert normalized_data.market_data.market_district == "Downtown"
    assert normalized_data.market_data.market_city == "Florianópolis"
    assert normalized_data.market_data.market_state == "SC"

    ean_product = normalized_data.products_data[0]

    assert ean_product.product_code == "7898080640611"
    assert ean_product.code_type == "EAN"
    assert ean_product.name == "WHOLE MILK 1L"
    assert ean_product.unit_price == Decimal("6.90")
    assert ean_product.total_price == Decimal("13.80")
    assert ean_product.quantity == Decimal("2")
    assert ean_product.ncm_code is None
    assert ean_product.brand == "Example Brand"
    assert ean_product.picture_url == "https://example.com/milk.jpg"

    internal_product = normalized_data.products_data[1]

    assert internal_product.product_code == "ABC-001"
    assert internal_product.code_type == "INTERNAL"
    assert internal_product.name == "POKAN KG"
    assert internal_product.unit_price == Decimal("8.99")
    assert internal_product.total_price == Decimal("11.24")
    assert internal_product.quantity == Decimal("1.250")
    assert internal_product.ncm_code == "08052100"
    assert internal_product.brand is None
    assert internal_product.picture_url is None


def test_normalize_ean_product_code() -> None:
    """Remove non-numeric characters from an EAN code."""
    normalized_code = NfeNormalizer._normalize_product_code(
        value="7898 0806-4061 1",
        code_type="EAN",
    )

    assert normalized_code == "7898080640611"


def test_normalize_internal_product_code() -> None:
    """Preserve meaningful characters in an internal product code."""
    normalized_code = NfeNormalizer._normalize_product_code(
        value="  ABC-001  ",
        code_type="INTERNAL",
    )

    assert normalized_code == "ABC-001"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("EAN", "EAN"),
        ("ean", "EAN"),
        (" EAN ", "EAN"),
        ("INTERNAL", "INTERNAL"),
        ("internal", "INTERNAL"),
        (" internal ", "INTERNAL"),
    ],
)
def test_normalize_supported_code_type(
    value: str,
    expected: str,
) -> None:
    """Normalize supported product code types."""
    assert NfeNormalizer._normalize_code_type(value) == expected


def test_normalize_unsupported_code_type() -> None:
    """Reject unsupported product code types."""
    with pytest.raises(
        ValueError,
        match="Unsupported product code type",
    ):
        NfeNormalizer._normalize_code_type("NCM")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12.345.678/0001-90", "12345678000190"),
        ("12345678000190", "12345678000190"),
        (" 12 345 678 0001 90 ", "12345678000190"),
    ],
)
def test_normalize_digits(
    value: str,
    expected: str,
) -> None:
    """Remove non-numeric characters from identifier fields."""
    assert NfeNormalizer._normalize_digits(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Market   Example  ", "Market Example"),
        ("Milk\nWhole\t1L", "Milk Whole 1L"),
        ("Product", "Product"),
    ],
)
def test_normalize_text(
    value: str,
    expected: str,
) -> None:
    """Remove unnecessary whitespace from text values."""
    assert NfeNormalizer._normalize_text(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("sc", "SC"),
        (" SC ", "SC"),
        ("sp", "SP"),
    ],
)
def test_normalize_state(
    value: str,
    expected: str,
) -> None:
    """Normalize Brazilian state abbreviations."""
    assert NfeNormalizer._normalize_state(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "S",
        "SCA",
        "Santa Catarina",
        "",
    ],
)
def test_normalize_invalid_state(value: str) -> None:
    """Reject invalid state abbreviation lengths."""
    with pytest.raises(
        ValueError,
        match="Market state must be a two-letter abbreviation",
    ):
        NfeNormalizer._normalize_state(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("8,90", Decimal("8.90")),
        ("R$ 8,90", Decimal("8.90")),
        ("1.234,56", Decimal("1234.56")),
        ("8.90", Decimal("8.90")),
        (10, Decimal("10")),
        (1.25, Decimal("1.25")),
        (Decimal("2.500"), Decimal("2.500")),
    ],
)
def test_normalize_decimal(
    value: Decimal | str | int | float,
    expected: Decimal,
) -> None:
    """Convert supported numeric formats to Decimal."""
    assert NfeNormalizer._normalize_decimal(value) == expected


def test_normalize_invalid_decimal() -> None:
    """Reject values that cannot be converted to Decimal."""
    with pytest.raises(
        ValueError,
        match="Invalid decimal value",
    ):
        NfeNormalizer._normalize_decimal("invalid")


def test_normalize_optional_text_returns_none() -> None:
    """Preserve missing optional text values."""
    assert NfeNormalizer._normalize_optional_text(None) is None


def test_normalize_empty_optional_text_returns_none() -> None:
    """Convert empty optional text values to None."""
    assert NfeNormalizer._normalize_optional_text("   ") is None


def test_normalize_optional_digits_returns_none() -> None:
    """Preserve missing optional numeric identifiers."""
    assert NfeNormalizer._normalize_optional_digits(None) is None


def test_normalize_empty_optional_digits_returns_none() -> None:
    """Convert optional values without digits to None."""
    assert NfeNormalizer._normalize_optional_digits("---") is None


def test_normalization_is_idempotent(
    extracted_nfe_data: NFEData,
) -> None:
    """Return the same result when normalization runs more than once."""
    first_result = NfeNormalizer.normalize(extracted_nfe_data)
    second_result = NfeNormalizer.normalize(first_result)

    assert second_result == first_result


def test_normalize_does_not_modify_original_data(
    extracted_nfe_data: NFEData,
) -> None:
    """Create normalized copies without mutating the extracted data."""
    original_market_name = extracted_nfe_data.market_data.market_name
    original_product_code = (
        extracted_nfe_data.products_data[0].product_code
    )

    normalized_data = NfeNormalizer.normalize(extracted_nfe_data)

    assert normalized_data is not extracted_nfe_data
    assert extracted_nfe_data.market_data.market_name == original_market_name
    assert (
        extracted_nfe_data.products_data[0].product_code
        == original_product_code
    )
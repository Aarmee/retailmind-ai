import os
import sys
import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# =========================================================
# 1. LOAD ENVIRONMENT
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Check your .env file."
    )


# =========================================================
# 2. GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=API_KEY)


# =========================================================
# 3. INVOICE DATA SCHEMA
# =========================================================

class InvoiceItem(BaseModel):
    product: Optional[str] = Field(default=None)
    quantity: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None)
    unit_price: Optional[float] = Field(default=None)
    item_total: Optional[float] = Field(default=None)


class InvoiceData(BaseModel):
    supplier: Optional[str] = Field(default=None)
    invoice_number: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)
    customer: Optional[str] = Field(default=None)

    items: list[InvoiceItem] = Field(default_factory=list)

    subtotal: Optional[float] = Field(default=None)
    discount: Optional[float] = Field(default=None)
    total: Optional[float] = Field(default=None)
    paid: Optional[float] = Field(default=None)
    due: Optional[float] = Field(default=None)


# =========================================================
# 4. GEMINI PROMPT
# =========================================================

PROMPT = """
You are an invoice information extraction system for a retail
automation application.

Analyze the supplied invoice image carefully.

The invoice may be:
- printed
- handwritten
- supermarket invoice
- kirana-shop bill
- thermal receipt
- tax invoice
- semi-structured document

Different invoices can have completely different layouts.

Do NOT assume a fixed position, table structure, column order,
or invoice format.

Extract only information that is visible in the invoice.

Extract:

- supplier
- invoice_number
- date
- customer
- items
    - product
    - quantity
    - unit
    - unit_price
    - item_total
- subtotal
- discount
- total
- paid
- due

IMPORTANT:

- Extract ALL identifiable products.
- Do not extract only the first product.
- Do not invent missing information.
- If a field is not visible or cannot be confidently identified,
  return null.
- Do not assume quantity = 1 unless clearly indicated.
- Do not confuse unit price and item total.
- Do not confuse subtotal, discount, total, paid and due.
- Preserve product names as they appear.
- Do not guess unclear product names.
- Keep separate invoice lines as separate items.
- Numbers must be numeric values.
- invoice_number must remain a string.
- Carefully inspect handwritten invoices.
- Base the answer only on the supplied image.
"""


# =========================================================
# 5. GEMINI EXTRACTION
# =========================================================

def extract_invoice(image_path: str) -> InvoiceData:

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Invoice image not found: {image_path}"
        )

    image_bytes = image_path.read_bytes()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(image_path.suffix.lower())

    if mime_type is None:
        raise ValueError(
            f"Unsupported image format: {image_path.suffix}"
        )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InvoiceData,
            temperature=0,
        ),
    )

    return InvoiceData.model_validate_json(response.text)


# =========================================================
# 6. NUMERIC VALIDATION
# =========================================================

def calculate_item_total(item: InvoiceItem) -> Optional[float]:
    """
    Calculate quantity × unit price when both values exist.
    """

    if item.quantity is None or item.unit_price is None:
        return None

    return round(item.quantity * item.unit_price, 2)


def validate_items(invoice: InvoiceData):
    """
    Check whether quantity × unit price agrees with item_total.

    We DO NOT automatically change the extracted value.
    We only report inconsistencies.
    """

    issues = []

    for index, item in enumerate(invoice.items, start=1):

        calculated = calculate_item_total(item)

        if calculated is None:
            continue

        if item.item_total is None:
            issues.append(
                f"Item {index} ({item.product}): "
                f"item total is missing; calculated value = {calculated}"
            )

        elif abs(calculated - item.item_total) > 0.01:
            issues.append(
                f"Item {index} ({item.product}): "
                f"quantity × unit price = {calculated}, "
                f"but extracted item total = {item.item_total}"
            )

    return issues


# =========================================================
# 7. SUBTOTAL CALCULATION
# =========================================================

def calculate_subtotal(invoice: InvoiceData) -> Optional[float]:
    """
    Calculate subtotal from invoice line totals.

    Only calculate it when every item has an item_total.
    """

    if not invoice.items:
        return None

    totals = []

    for item in invoice.items:

        if item.item_total is None:
            return None

        totals.append(item.item_total)

    return round(sum(totals), 2)


# =========================================================
# 8. TOTAL VALIDATION
# =========================================================

def validate_totals(invoice: InvoiceData):
    """
    Compare extracted totals with calculated values where possible.
    """

    issues = []

    calculated_subtotal = calculate_subtotal(invoice)

    # -----------------------------------------------------
    # Check subtotal
    # -----------------------------------------------------

    if calculated_subtotal is not None:

        if invoice.subtotal is None:

            issues.append(
                f"Subtotal missing; calculated subtotal = "
                f"{calculated_subtotal}"
            )

        elif abs(invoice.subtotal - calculated_subtotal) > 0.01:

            issues.append(
                f"Subtotal mismatch: extracted = "
                f"{invoice.subtotal}, calculated = "
                f"{calculated_subtotal}"
            )

    # -----------------------------------------------------
    # Check total using subtotal - discount
    # -----------------------------------------------------

    if (
        calculated_subtotal is not None
        and invoice.discount is not None
        and invoice.total is not None
    ):

        calculated_total = round(
            calculated_subtotal - invoice.discount,
            2
        )

        if abs(calculated_total - invoice.total) > 0.01:

            issues.append(
                f"Total mismatch: subtotal - discount = "
                f"{calculated_total}, extracted total = "
                f"{invoice.total}"
            )

    # -----------------------------------------------------
    # Check due amount
    # -----------------------------------------------------

    if (
        invoice.total is not None
        and invoice.paid is not None
        and invoice.due is not None
    ):

        calculated_due = round(
            invoice.total - invoice.paid,
            2
        )

        if abs(calculated_due - invoice.due) > 0.01:

            issues.append(
                f"Due mismatch: total - paid = "
                f"{calculated_due}, extracted due = "
                f"{invoice.due}"
            )

    return issues


# =========================================================
# 9. COMPLETE VALIDATION
# =========================================================

def validate_invoice(invoice: InvoiceData):

    issues = []

    # Validate individual products
    issues.extend(validate_items(invoice))

    # Validate totals
    issues.extend(validate_totals(invoice))

    calculated_subtotal = calculate_subtotal(invoice)

    return {
        "is_valid": len(issues) == 0,
        "calculated_subtotal": calculated_subtotal,
        "issues": issues,
    }


# =========================================================
# 10. DISPLAY
# =========================================================

def print_invoice(invoice: InvoiceData, validation):

    print("\n" + "=" * 60)
    print("EXTRACTED INVOICE")
    print("=" * 60)

    print(f"Supplier       : {invoice.supplier}")
    print(f"Invoice Number : {invoice.invoice_number}")
    print(f"Date           : {invoice.date}")
    print(f"Customer       : {invoice.customer}")

    print("\nITEMS")
    print("-" * 60)

    if not invoice.items:

        print("No items detected.")

    else:

        for i, item in enumerate(invoice.items, start=1):

            print(f"\nItem {i}")
            print(f"  Product     : {item.product}")
            print(f"  Quantity    : {item.quantity}")
            print(f"  Unit        : {item.unit}")
            print(f"  Unit Price  : {item.unit_price}")
            print(f"  Item Total  : {item.item_total}")

    print("\nTOTALS")
    print("-" * 60)

    print(f"Subtotal       : {invoice.subtotal}")
    print(f"Discount       : {invoice.discount}")
    print(f"Total          : {invoice.total}")
    print(f"Paid           : {invoice.paid}")
    print(f"Due            : {invoice.due}")

    print("\nVALIDATION")
    print("-" * 60)

    if validation["is_valid"]:

        print("Status         : VALID")

    else:

        print("Status         : REVIEW REQUIRED")

        for issue in validation["issues"]:
            print(f"  - {issue}")

    if validation["calculated_subtotal"] is not None:

        print(
            f"Calculated Subtotal : "
            f"{validation['calculated_subtotal']}"
        )

    print("=" * 60)


# =========================================================
# 11. MAIN
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "\nUsage:\n"
            "python gemini_invoice.py <invoice_image>\n"
        )

        sys.exit(1)

    image_path = sys.argv[1]

    try:

        # AI extraction
        invoice = extract_invoice(image_path)

        # Deterministic validation
        validation = validate_invoice(invoice)

        # Human-readable output
        print_invoice(invoice, validation)

        # Final JSON
        output = {
            "invoice": invoice.model_dump(),
            "validation": validation,
        }

        print("\nJSON OUTPUT")
        print("-" * 60)

        print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            )
        )

    except Exception as e:

        print("\nERROR:")
        print(str(e))

        sys.exit(1)
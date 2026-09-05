# 2. `invoice/README.md`

```markdown
# RetailMind AI – Invoice Extraction Module

## 1. Overview

The Invoice Extraction Module automatically extracts structured information from retail invoices.

Retail invoices can have different:

- Layouts
- Suppliers
- Product names
- Number of items
- Field positions
- Printed or handwritten formats

Therefore, the system does not depend on a fixed invoice template.

The module accepts an invoice image and extracts information such as:

- Supplier
- Invoice number
- Invoice date
- Customer
- Products
- Quantities
- Units
- Unit prices
- Item totals
- Subtotal
- Discount
- Total
- Paid amount
- Due amount

---

# 2. AI Approach

The module uses a multimodal AI-based information extraction approach.

```text
Invoice Image
      ↓
Gemini Vision
      ↓
Image Understanding
      ↓
Structured Information Extraction
      ↓
Pydantic Schema Validation
      ↓
Application-Level Validation
      ↓
Structured Invoice JSON
````

The model receives the invoice image directly and extracts the relevant information without requiring a predefined invoice layout.

---

# 3. Technologies Used

* Python
* Google Gemini API
* `google-genai`
* Pydantic
* Python-dotenv

The Gemini model currently used is:

```text
gemini-3.5-flash-lite
```

---

# 4. Why AI-Based Invoice Extraction?

Traditional invoice processing often depends on fixed coordinates or templates.

For example:

```text
Supplier → top-left
Invoice Number → top-right
Total → bottom-right
```

This approach fails when a different supplier uses a different layout.

RetailMind instead uses the visual content of the invoice to identify the meaning of the information.

Therefore:

```text
Different Invoice Layouts
          ↓
     AI Vision Model
          ↓
   Common Data Structure
```

This makes the extraction process more flexible for different retail invoices.

---

# 5. Structured Invoice Schema

The extracted invoice follows a common structure.

### Invoice-level fields

```text
supplier
invoice_number
date
customer
items
subtotal
discount
total
paid
due
```

### Item-level fields

Each invoice item can contain:

```text
product
quantity
unit
unit_price
item_total
```

Example:

```json
{
  "supplier": "XYZ Ltd.",
  "invoice_number": "489755",
  "date": "5/2/2015",
  "customer": "Shyam Agarwal",
  "items": [
    {
      "product": "Jeans",
      "quantity": 2,
      "unit": null,
      "unit_price": 750,
      "item_total": 1500
    }
  ],
  "subtotal": 2250,
  "discount": 225,
  "total": 2025,
  "paid": 500,
  "due": 1525
}
```

---

# 6. Pydantic Validation

Pydantic is used to enforce the expected output structure.

The model must return information according to the defined invoice schema.

This helps prevent unstructured responses and makes the extracted data easier for the backend to consume.

---

# 7. Application-Level Validation

AI extraction is followed by deterministic validation.

The validation layer checks whether the extracted values are mathematically consistent.

### Item Total

For each item:

```text
Expected Item Total =
Quantity × Unit Price
```

For example:

```text
Quantity = 2
Unit Price = 750

Expected Item Total = 2 × 750
                    = 1500
```

---

### Subtotal

The system can calculate:

```text
Calculated Subtotal =
Sum of Item Totals
```

---

### Total Validation

The system checks relationships between:

```text
Subtotal
Discount
Total
Paid
Due
```

If an extracted value does not match the calculated value, the system **flags the inconsistency instead of silently changing the invoice data**.

This is important because the original invoice may contain an actual mistake.

---

# 8. Example of Validation

Suppose the invoice contains:

```text
Product      : Handwash
Quantity     : 5
Unit Price   : 350
Item Total   : 350
```

The expected value is:

```text
5 × 350 = 1750
```

But the invoice says:

```text
Item Total = 350
```

The system flags this as an inconsistency instead of automatically changing `350` to `1750`.

This preserves the original invoice information while alerting the system that verification is required.

---

# 9. Project Structure

```text
invoice/
│
├── data/
│
├── models/
│   └── [previous LayoutLM experiments / models]
│
├── .env
├── .gitignore
├── gemini_invoice.py
├── validation.py
├── requirements.txt
└── README.md
```

The `models/` directory contains previous experimental LayoutLM work and can be retained as research/backup material.

The current production/demo extraction pipeline is implemented in:

```text
gemini_invoice.py
```

---

# 10. Setup

## Step 1 – Navigate to the Invoice Module

```powershell
cd invoice
```

---

## Step 2 – Activate the Virtual Environment

If using the shared project environment:

```powershell
..\venv\Scripts\activate
```

---

## Step 3 – Install Dependencies

```powershell
pip install -r requirements.txt
```

Required packages include:

```text
google-genai
pydantic
python-dotenv
```

---

# 11. Configure API Key

Create a `.env` file inside the `invoice` folder.

```text
GEMINI_API_KEY=your_api_key_here
```

Do not hardcode the API key inside Python files.

Do not commit the `.env` file to Git.

The `.gitignore` should contain:

```text
.env
```

---

# 12. Run Invoice Extraction

Run:

```powershell
python gemini_invoice.py
```

The script processes the configured invoice image and produces structured invoice information.

---

# 13. Supported Invoice Variations

The module has been tested with different invoice styles, including:

### Printed Retail Invoice

```text
Supplier
Invoice Number
Date
Customer
Products
Quantity
Price
Totals
```

### Supermarket Invoice

Contains a different layout and multiple products.

### Handwritten Supplier Bill

Contains handwritten information and may have missing or inconsistent values.

### Handwritten Kirana Bill

Contains retail products with different units such as:

```text
kg
box
100ml
```

The system attempts to extract available information and leaves unavailable fields as `null`.

---

# 14. Missing Information

If a field cannot be reliably extracted, it should remain:

```json
null
```

For example:

```json
{
  "customer": null,
  "subtotal": null
}
```

The system should not invent missing invoice information.

---

# 15. Important Design Principle

The module does not depend on hardcoded invoice coordinates or a single invoice template.

Instead:

```text
Invoice Image
      ↓
Visual Understanding
      ↓
Semantic Extraction
      ↓
Common JSON Structure
```

This allows invoices from different suppliers to be processed using the same extraction pipeline.

---

# 16. Integration with RetailMind Backend

The extracted invoice JSON can be sent to the backend API.

Example:

```text
Invoice Image
      ↓
AI Invoice Extraction
      ↓
Validation
      ↓
Structured JSON
      ↓
Backend API
      ↓
Inventory Database
```

The backend can then use the extracted product and quantity information to update inventory.

---

# 17. Limitations

* Handwritten invoices can be difficult to read.
* Poor image quality can reduce extraction accuracy.
* Ambiguous values may require manual verification.
* The module currently depends on the Gemini API.
* Product matching is handled separately from invoice extraction.

---

# 18. Future Improvements

Possible improvements include:

* Local OCR fallback
* Product-name matching with the retailer's inventory
* Better handwritten invoice processing
* Confidence scores for individual fields
* Automatic duplicate invoice detection
* Supplier-specific learning
* Local/open-source vision models

---

# 19. Summary

The Invoice Extraction Module converts different retail invoice images into a common structured format.

Its main purpose is to reduce manual data entry for small retailers while preserving the original invoice information and detecting inconsistencies.

```text
Different Invoice Formats
          ↓
       AI Vision
          ↓
 Structured Extraction
          ↓
     Validation
          ↓
      JSON Data
          ↓
 Inventory System
```

```

### One small recommendation

For your **capstone GitHub**, these READMEs are better than just having installation commands because they explain **what AI is actually being used and why**.

For the Voice README, emphasize **TF-IDF + Logistic Regression + Whisper**.

For the Invoice README, emphasize **multimodal image understanding + structured extraction + deterministic validation**.

That makes it much easier for your evaluator to see that the two modules are doing different AI tasks rather than simply calling APIs.
```

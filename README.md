# RetailMind AI

## AI-Powered Retail Automation Platform

RetailMind AI is a low-entry retail automation platform designed for
small retailers and micro-businesses.

The system aims to reduce manual business data entry by allowing
retailers to provide information through natural inputs such as
voice and invoices, which are transformed into structured business
records.

## Problem

Small retailers commonly manage sales, inventory, payments and credit
records through a combination of manual entry, invoices, notebooks
and payment records.

Existing retail management systems provide these functionalities,
but often require information to be entered into structured forms.

RetailMind AI focuses on reducing this data-entry burden.

## Proposed Solution

RetailMind AI follows the workflow:

Voice / Invoice / Payment Data
            ↓
      AI Understanding
            ↓
         Validation
            ↓
    Automatic Records
            ↓
     Business Insights

## Key Features

- AI-based voice sales capture
- Invoice and document information extraction
- Automatic inventory updates
- Cash, UPI and credit transaction tracking
- Payment reconciliation
- Per-item profit calculation
- Multilingual dashboard
- Natural-language business queries
- Demand forecasting
- Anomaly detection

## AI/ML Components

### Voice Processing
Speech recognition converts spoken business information into text.

### NLP
Natural Language Processing identifies the intent and entities
from voice-based business inputs.

Example:

"Sold 5 Maggi cash"

Product   → Maggi
Quantity  → 5
Payment   → Cash
Intent    → Sale

### Invoice Intelligence
OCR extracts relevant information such as:

- Product
- Quantity
- Price
- Supplier

### Machine Learning

Machine learning will be explored for:

- Demand forecasting
- Transaction anomaly detection

### Natural Language Queries

The system allows retailers to ask questions such as:

- Which product sold the most this month?
- Who has pending payments?
- What is my profit on a product?

## Technology Stack

### Frontend
- React.js
- Tailwind CSS

### Backend
- Node.js
- Express.js

### Database
- PostgreSQL

### AI/ML
- Python
- Whisper
- Tesseract / EasyOCR
- NLP libraries
- Scikit-learn / XGBoost

### GenAI
- Gemini API / Local LLM

### Deployment
- Docker

## Project Architecture

React.js
    ↓
Node.js + Express.js
    ↓
AI/ML Services
    ↓
PostgreSQL

AI/ML Services include:

- Speech Recognition
- NLP
- OCR
- Entity Extraction
- Entity Matching
- Forecasting
- Anomaly Detection

## Research Focus

The project focuses on studying whether a low-entry,
multimodal approach can reduce manual retail record-keeping effort
while maintaining reliable data accuracy.

The evaluation will consider:

- Data extraction accuracy
- Transaction accuracy
- Time required for recording
- Manual fields required
- Correction rate

## Project Structure

retailmind-ai/
│
├── frontend/
├── backend/
├── aiml/
│   ├── voice/
│   ├── ocr/
│   ├── nlp/
│   ├── forecasting/
│   └── anomaly_detection/
│
├── docs/
├── .gitignore
└── README.md

## Team Development

The project uses separate Git branches for parallel development.

main
  ↓
Stable integrated project

aiml
  ↓
AI/ML development

Other feature branches may be created as required.

AI/ML changes will be integrated into the main branch after
testing and review.

## Status

🚧 Currently under development.

## Project Type

Capstone Project

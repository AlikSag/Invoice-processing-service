import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

load_dotenv()

endpoint = os.getenv("DI_ENDPOINT")
key = os.getenv("DI_KEY")

if endpoint is None or key is None:
    raise ValueError("DI_ENDPOINT or DI_KEY is missing")

client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
)

def analyze_invoice(document_path: str):
    with open(document_path, "rb") as file:
        poller = client.begin_analyze_document(
            "prebuilt-invoice",
            file
        )
        result = poller.result()
    return result


def parse_invoice_result(result):
    document = result.documents[0]
    fields = document.fields

    invoice_id = fields.get("InvoiceId")
    invoice_date = fields.get("InvoiceDate")
    vendor_name = fields.get("VendorName")
    subtotal = fields.get("SubTotal")
    total_tax = fields.get("TotalTax")
    invoice_total = fields.get("InvoiceTotal")
    items_field = fields.get("Items")


    items = []

    if items_field:
        for item in items_field.value_array:
            item_fields = item.value_object

            description = item_fields.get("Description")
            quantity = item_fields.get("Quantity")
            unit_price = item_fields.get("UnitPrice")
            amount = item_fields.get("Amount")

            items.append(
                {
                    "description": (
                        description.value_string
                        if description
                        else None
                    ),
                    "quantity": (
                        quantity.value_number
                        if quantity
                        else None
                    ),
                    "unit_price": (
                        unit_price.value_currency.amount
                        if unit_price
                        else None
                    ),
                    "amount": (
                        amount.value_currency.amount
                        if amount
                        else None
                    ),
                }
            )
    return {
        "invoice_id": invoice_id.value_string if invoice_id else None,
        "invoice_date": str(invoice_date.value_date) if invoice_date else None,
        "vendor_name": vendor_name.value_string if vendor_name else None,
        "subtotal": subtotal.value_currency.amount if subtotal else None,
        "tax": total_tax.value_currency.amount if total_tax else None,
        "total": invoice_total.value_currency.amount if invoice_total else None,
        "currency": (
            invoice_total.value_currency.currency_code
            if invoice_total
            else None
        ),
        "items": items,
    }

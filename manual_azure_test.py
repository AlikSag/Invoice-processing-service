from app.azure_client import analyze_invoice, parse_invoice_result


def main():
    result = analyze_invoice("invoice.pdf")

    document = result.documents[0]
    fields = document.fields

    print(fields.keys())

    field = fields.get("InvoiceId")

    print(field)
    print(type(field))
    print(field.type)

    attributes = [
        name
        for name in dir(field)
        if name.startswith("value")
    ]

    print(attributes)


if __name__ == "__main__":
    main()

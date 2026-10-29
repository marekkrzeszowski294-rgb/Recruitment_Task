import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def load_sales(path):
    cleaned_sales = []
    rejected_rows = 0

    with path.open("r", encoding="utf-8-sig", newline="") as sales_file:
        reader = csv.DictReader(sales_file)
        required_columns = {"order_id", "product", "quantity", "price"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Plik sales.csv musi zawierać kolumny: "
                "order_id, product, quantity, price."
            )

        for row in reader:
            order_id = (row.get("order_id") or "").strip()
            product = (row.get("product") or "").strip()
            quantity_value = (row.get("quantity") or "").strip()
            price_value = (row.get("price") or "").strip()

            try:
                quantity = int(quantity_value)
                price = Decimal(price_value)
            except (ValueError, InvalidOperation):
                rejected_rows += 1
                continue

            if not order_id or not product or quantity <= 0 or price < 0:
                rejected_rows += 1
                continue

            cleaned_sales.append(
                {
                    "order_id": order_id,
                    "product": product,
                    "quantity": quantity,
                    "price": price,
                    "order_value": quantity * price,
                }
            )

    return cleaned_sales, rejected_rows


def generate_report(sales, rejected_rows):
    total_revenue = sum(
        (sale["order_value"] for sale in sales), start=Decimal("0")
    )
    product_totals = defaultdict(lambda: {"quantity": 0, "revenue": Decimal("0")})

    for sale in sales:
        product_total = product_totals[sale["product"]]
        product_total["quantity"] += sale["quantity"]
        product_total["revenue"] += sale["order_value"]

    report_lines = [
        "RAPORT SPRZEDAŻY",
        "=" * 40,
        f"Liczba poprawnych zamówień: {len(sales)}",
        f"Liczba odrzuconych wierszy: {rejected_rows}",
        f"Łączna wartość sprzedaży: {total_revenue:.2f} zł",
        "",
        "WARTOŚĆ ZAMÓWIEŃ",
        "-" * 40,
    ]

    report_lines.extend(
        f"Zamówienie {sale['order_id']} | {sale['product']} | "
        f"{sale['quantity']} szt. x {sale['price']:.2f} zł = "
        f"{sale['order_value']:.2f} zł"
        for sale in sales
    )

    report_lines.extend(["", "PODSUMOWANIE PRODUKTÓW", "-" * 40])
    report_lines.extend(
        f"{product}: {totals['quantity']} szt. | "
        f"{totals['revenue']:.2f} zł"
        for product, totals in sorted(product_totals.items())
    )

    return "\n".join(report_lines)


def main():
    data_directory = Path(__file__).resolve().parent
    sales_path = data_directory / "sales.csv"
    report_path = data_directory / "sales_report.txt"

    sales, rejected_rows = load_sales(sales_path)
    report = generate_report(sales, rejected_rows)
    report_path.write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\nRaport zapisano w pliku: {report_path}")


if __name__ == "__main__":
    main()
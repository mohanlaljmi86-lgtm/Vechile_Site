
from io import BytesIO
import pandas as pd


def trips_to_csv(trips):
    return (
        trips.drop(
            columns=["owner_id"],
            errors="ignore"
        )
        .to_csv(index=False)
        .encode("utf-8-sig")
    )


def trips_to_excel(trips):
    try:
        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            trips.drop(
                columns=["owner_id"],
                errors="ignore"
            ).to_excel(
                writer,
                index=False,
                sheet_name="Trip History"
            )

        return output.getvalue()

    except Exception:
        return None


def trip_pdf(trips):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer
        )
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        output = BytesIO()

        document = SimpleDocTemplate(
            output,
            pagesize=landscape(A4)
        )

        styles = getSampleStyleSheet()

        data = [[
            "Trip",
            "Vehicle",
            "Route",
            "Distance KM",
            "Total Cost ₹",
            "Per Person ₹"
        ]]

        for row in trips.to_dict("records"):

            data.append([
                str(row.get("trip_name", ""))[:24],
                str(row.get("vehicle", ""))[:22],
                str(row.get("route", ""))[:34],
                f'{float(row.get("distance_km", 0)):,.1f}',
                f'{float(row.get("total_cost", 0)):,.2f}',
                f'{float(row.get("per_person_cost", 0)):,.2f}'
            ])

        table = Table(
            data,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#14213d")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        document.build([
            Paragraph(
                "VehicleSaathi - Trip Report",
                styles["Title"]
            ),
            Spacer(1, 12),
            table
        ])

        return output.getvalue()

    except Exception:
        return None

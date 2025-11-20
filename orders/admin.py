# orders/admin.py
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum, Count, FloatField
from django.db.models.functions import TruncDate, Cast
from calendar import monthrange
import datetime as dt

from .models import Payment, Order, OrderProduct, SalesReport


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = (
        "payment",
        "user",
        "product",
        "quantity",
        "product_price",
        "ordered",
    )
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "full_name",
        "phone",
        "email",
        "city",
        "order_total",
        "tax",
        "status",
        "is_ordered",
        "created_at",
    ]
    list_filter = ["status", "is_ordered"]
    search_fields = [
        "order_number",
        "first_name",
        "last_name",
        "phone",
        "email",
    ]
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)

# ===========================
#  SALES DASHBOARD THEO THÁNG
# ===========================


class SalesReportAdmin(admin.ModelAdmin):
    """
    Dashboard doanh số theo tháng, lấy dữ liệu từ bảng Payment:
    - Payment.status = 'COMPLETED'
    - Sum(Payment.amount_paid) theo ngày trong tháng
    """

    # Đường dẫn template: templates/orders/sales_report.html
    change_list_template = "orders/sales_report.html"

    def get_queryset(self, request):
        # Không hiển thị list object
        return Order.objects.none()

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        today = timezone.localdate()

        # ---- Đọc năm / tháng từ query string (nếu có) ----
        year_param = request.GET.get("year")
        month_param = request.GET.get("month")

        try:
            selected_year = int(year_param) if year_param else today.year
        except (TypeError, ValueError):
            selected_year = today.year

        try:
            selected_month = int(month_param) if month_param else today.month
        except (TypeError, ValueError):
            selected_month = today.month

        if selected_month < 1 or selected_month > 12:
            selected_month = today.month

        # ---- Khoảng ngày trong tháng được chọn ----
        first_day = dt.date(selected_year, selected_month, 1)
        last_day = dt.date(
            selected_year,
            selected_month,
            monthrange(selected_year, selected_month)[1],
        )

        # ---- Query Payment (bảng orders_payment) ----
        payments_qs = Payment.objects.filter(
            status="COMPLETED",
            created_at__date__gte=first_day,
            created_at__date__lte=last_day,
        ).annotate(amount_float=Cast("amount_paid", FloatField()))

        # Tổng đơn & doanh thu gộp
        totals = payments_qs.aggregate(
            gross=Sum("amount_float"),
        )
        total_orders = payments_qs.count()
        gross_revenue = totals["gross"] or 0

        # Thuế: cộng từ các Order có payment nằm trong payments_qs
        orders_qs = Order.objects.filter(
            payment__in=payments_qs,
            is_ordered=True,
        )
        tax_total = orders_qs.aggregate(total=Sum("tax"))["total"] or 0
        net_revenue = gross_revenue - tax_total

        # ---- Doanh thu theo ngày ----
        revenue_by_day = (
            payments_qs.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                revenue=Sum("amount_float"),
                orders=Count("id"),
            )
            .order_by("day")
        )

        # Map day -> revenue, để fill đủ số ngày trong tháng
        num_days = monthrange(selected_year, selected_month)[1]
        rev_map = {
            row["day"].day: row["revenue"] or 0 for row in revenue_by_day
        }

        daily_labels = []
        daily_values = []
        for d in range(1, num_days + 1):
            daily_labels.append(str(d))  # "1", "2", ...
            daily_values.append(round(rev_map.get(d, 0), 2))

        # ---- Năm: 2025 -> 2030 ----
        years = list(range(2025, 2031))

        # ---- Tháng 1-12 để vẽ nút ----
        months = [
            {"number": 1, "label": "Tháng 1"},
            {"number": 2, "label": "Tháng 2"},
            {"number": 3, "label": "Tháng 3"},
            {"number": 4, "label": "Tháng 4"},
            {"number": 5, "label": "Tháng 5"},
            {"number": 6, "label": "Tháng 6"},
            {"number": 7, "label": "Tháng 7"},
            {"number": 8, "label": "Tháng 8"},
            {"number": 9, "label": "Tháng 9"},
            {"number": 10, "label": "Tháng 10"},
            {"number": 11, "label": "Tháng 11"},
            {"number": 12, "label": "Tháng 12"},
        ]

        extra_context = extra_context or {}
        extra_context.update(
            {
                "selected_year": selected_year,
                "selected_month": selected_month,
                "years": years,
                "months": months,
                "total_orders": total_orders,
                "gross_revenue": gross_revenue,
                "tax_total": tax_total,
                "net_revenue": net_revenue,
                "daily_labels": daily_labels,
                "daily_values": daily_values,
            }
        )

        # ==== QUAN TRỌNG: xoá year/month khỏi request.GET ====
        # để Django admin không coi chúng là filter và ném lỗi (redirect ?e=1)
        q = request.GET.copy()
        for key in ("year", "month"):
            if key in q:
                del q[key]
        request.GET = q

        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(SalesReport, SalesReportAdmin)

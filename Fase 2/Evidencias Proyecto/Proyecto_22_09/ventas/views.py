from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F
from django.utils.dateparse import parse_date
from .models import Venta, VentaItem
from .serializers import VentaSerializer, VentaReadSerializer
from django.http import HttpResponse

def lista(request):   return HttpResponse("Ventas: listado")
def crear(request):   return HttpResponse("Ventas: crear")
def detalle(request, pk): return HttpResponse(f"Ventas: detalle {pk}")
# ventas/views.py


class VentaListCreateView(generics.ListCreateAPIView):
    queryset = Venta.objets.call().select_related('cliente','usuario').prefetch_related('items__producto')
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        return VentaSerializer if self.request.method == 'POST' else VentaReadSerializer

# /api/ventas/resumen?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
class VentasResumenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        desde = parse_date(request.GET.get('desde') or '')
        hasta = parse_date(request.GET.get('hasta') or '')
        qs = Venta.objects.all()
        if desde: qs = qs.filter(creado_en__date__gte=desde)
        if hasta: qs = qs.filter(creado_en__date__lte=hasta)

        ingresos = qs.aggregate(m=Sum('total'))['m'] or 0
        total_ventas = qs.count()
        total_items = VentaItem.objects.filter(venta__in=qs).aggregate(s=Sum('cantidad'))['s'] or 0
        ticket_promedio = (ingresos / total_ventas) if total_ventas else 0

        return Response({
            'ingresos': float(ingresos),
            'total_ventas': total_ventas,
            'total_items': int(total_items),
            'ticket_promedio': float(ticket_promedio),
        })

# /api/ventas/top?desde=&hasta=&limit=5 (más vendidos)
class VentasTopProductosView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        desde = parse_date(request.GET.get('desde') or '')
        hasta = parse_date(request.GET.get('hasta') or '')
        limit = int(request.GET.get('limit') or 5)
        items = VentaItem.objects.select_related('producto')
        if desde: items = items.filter(venta__creado_en__date__gte=desde)
        if hasta: items = items.filter(venta__creado_en__date__lte=hasta)

        agg = (items
               .values('producto','producto__nombre')
               .annotate(unidades=Sum('cantidad'),
                         ingresos=Sum(F('cantidad')*F('precio_unitario')))
               .order_by('-unidades')[:limit])

        data = [{
            'producto': r['producto'],
            'nombre': r['producto__nombre'],
            'unidades': int(r['unidades'] or 0),
            'ingresos': float(r['ingresos'] or 0),
        } for r in agg]
        return Response(data)

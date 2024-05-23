from django.db.models import Sum

from products.models import GameDetail


class UpdateStock:
    def __init__(self, product):
        self.product = product
        sum_stocks = GameDetail.objects.filter(producto=self.product.first().pk,
                                               stock__gt=0).aggregate(Sum('stock'))
        product.update(stock=sum_stocks['stock__sum'])

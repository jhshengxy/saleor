#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/07/23 18:55
# @Author  : Shengxy
# @Site    : 
# @File    : feat_shopify.py
# @Software: PyCharm
import logging

from django.core.management.base import BaseCommand
from ...utils.shopify_products import feat_product_list,PASSWORD
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Recalculates the minimal variant prices for all products."

    def handle(self, *args, **options):
        if PASSWORD:
            feat_product_list()
        else:
            print('Please go to file product/utils/shopify_products.py set PASSWORD first')
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/07/23 18:55
# @Author  : Shengxy
# @Site    : 
# @File    : shopify_products.py
# @Software: PyCharm
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

import requests
import logging
import urllib
from decimal import Decimal
from ..models import Product, ProductVariant,ProductType,ProductImage,VariantImage

PASSWORD = ''
HOST = 'https://jhshengxy.myshopify.com/admin/api/2021-07/'
logger = logging.getLogger(__name__)

def send_request(url):
    headers = {
        "X-Shopify-Access-Token": PASSWORD,
        "Content-Type": "application/json"
    }
    r = requests.get(url=url,timeout=5,headers=headers)
    if r.status_code==200:
        try:
            res = r.json()
            return res
        except Exception as e:
            log.error(str(e))
            return {}
    else:
        return {}

def save_image_from_url(model, url):
    retry_count =1
    is_success = False
    while(retry_count<5):
        r = requests.get(url,timeout=5)

        if r.status_code==200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            img_temp.flush()

            model.image.save("image.jpg", File(img_temp), save=True)
            is_success= True
            break
        retry_count+=1

    return is_success


def feat_product_variants(product_obj:Product):
    url = f'{HOST}products/{product_obj.slug}.json'
    res = send_request(url)
    if res and "product" in res:
        # 处理veriants信息
        if  "variants" in res["product"]:
            for one in res["product"]["variants"]:
                var_obj = ProductVariant.objects.filter(sku=one['id']).first()
                if not var_obj:
                    var_obj = ProductVariant()
                    var_obj.sku=one['id']
                var_obj.name=one["title"]
                var_obj.product=product_obj
                if "price" in one and one["price"]:
                    var_obj.price_amount=Decimal(one["price"])
                else:
                    var_obj.price_amount=Decimal("0")
                
                var_obj.save()
        
        # 处理商品中的图片信息
        if 'images' in  res["product"] and len( res["product"]["images"])>0:
            for image in  res["product"]["images"]:
                image_obj = ProductImage.objects.filter(product=product_obj,alt=image['id']).first()
                if not image_obj:
                    image_obj = ProductImage()
                    image_obj.alt = image['id']
                    image_obj.product=product_obj
                        
                    img_download_resule = save_image_from_url(image_obj,image['src'])
                    image_obj.save()
                    if img_download_resule is False:
                        pass
                        #TODO 处理图片下载失败之后的日志写入以及再次下载

                # 将图片与变种信息相关联
                if 'variant_ids' in  image and len( image['variant_ids'])>0:
                    for one_id in  image['variant_ids']:
                        if not VariantImage.objects.filter(variant__sku=one_id,image=image_obj).exists():
                            variant_obj = ProductVariant.objects.filter(sku=one_id).first()
                            VariantImage.objects.create(variant=variant_obj,image=image_obj)
                        

def feat_product_list():
    fields = ['id','title','product_type','body_html','created_at',]
    url = f'{HOST}products.json/?fields={",".join(fields)}'

    res = send_request(url)
    if res and 'products' in res:
        for one in res['products']:
            product_type_obj,_ = ProductType.objects.get_or_create(name='test_type',slug='test_slug')
            if 'id' in one and one['id']:
                product_obj = Product.objects.filter(slug=one['id']).first()
                if not product_obj:
                    product_obj = Product()
                    product_obj.slug = one['id']
                
                product_obj.product_type=product_type_obj

                if 'title' in one:
                    product_obj.name=one['title']
                else:
                    product_obj.name=''

                if 'body_html' in one:
                    defalut_json = {"blocks": [{"key": "", "data": {}, "text": "", "type": "unstyled", "depth": 0, "entityRanges": [], "inlineStyleRanges": []}], "entityMap": {}}
                    defalut_json["blocks"][0]["text"]=one['body_html']
                    product_obj.description_json=defalut_json
                    product_obj.description=one['body_html']
                
                product_obj.save()
                # 获取variants信息
                feat_product_variants(product_obj)

                
                

                
import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts.charts import WordCloud, Pie
from pyecharts.globals import ChartType
from snapshot_selenium import snapshot as driver
from dao.init import get_mysql_config
from pyecharts import options as opts
from pyecharts.charts import Geo

def generate_word_cloud(data):
    word_count = {}
    for tag in data:
        if tag in word_count:
            word_count[tag] += 1
        else:
            word_count[tag] = 1

    word_cloud = (
        WordCloud()
        .add(series_name="职位标签", data_pair=list(word_count.items()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="职位标签词云图", pos_left="center",
                                      title_textstyle_opts=opts.TextStyleOpts(font_weight="bold")),
            graphic_opts=[
                opts.GraphicRect(
                    graphic_item=opts.GraphicItem(
                        left=0,
                        top=0,
                        z=0,
                        bounding="raw",
                        origin=[0, 0],
                    )
                ),
                opts.GraphicText(
                    graphic_item=opts.GraphicItem(left="center", top="middle", z=100),
                )
            ],
        )
    )

    word_cloud.width = "100%vh"
    word_cloud.height = "100vh"

    word_cloud.render('templates/word_cloud_chart.html')

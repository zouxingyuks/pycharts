from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType

def split_location(location):
    parts = location.split('·')
    return [part.strip() for part in parts]


# 在 generate_geo_chart 函数中添加地域分布图的生成逻辑
def generate_geo_chart(data):
    # 统计各个地区的数量
    location_counts = {}
    for result in data:
        location = result.location
        split_parts = split_location(location)
        for i, part in enumerate(split_parts):
            if i >= 2:  # 只处理前两个元素
                break
            if part in location_counts:
                location_counts[part] += 1
            else:
                location_counts[part] = 1

    # 创建 Geo 实例并设置地图类型
    geo = Geo()
    geo.add_schema(maptype="china")

    # 添加数据到 Geo 实例
    for part, count in location_counts.items():
        try:
            geo.get_coordinate(part)
            geo.add(
                series_name="地域分布",
                data_pair=[(part, count)],
                type_=ChartType.EFFECT_SCATTER,  # 散点图类型
                symbol_size=10,  # 散点大小
                label_opts=opts.LabelOpts(is_show=True),  # 显示标签
            )
        except Exception as e:
            print(f"坐标不存在: {part}, 错误原因: {str(e)}")

    # 设置全局配置项
    geo.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=max(location_counts.values()),  # 数据的最大值
            is_piecewise=True,  # 是否分段显示
        ),
    )

    # 渲染地域分布图并保存到文件
    geo.width = "100%vh"
    geo.height = "100vh"
    geo.render("templates/geo_chart.html")

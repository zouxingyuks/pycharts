import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts.charts import WordCloud, Pie
from pyecharts.globals import ChartType
from snapshot_selenium import snapshot as driver
from dao.init import get_mysql_config
from pyecharts import options as opts
from pyecharts.charts import Geo


def classify_salary(salary):
    if '·' in salary:
        salary_parts = salary.split('·')
        if len(salary_parts) == 2:
            salary_range = salary_parts[0].split('-')
            if len(salary_range) == 2:
                try:
                    low_salary = float(salary_range[0])
                    high_salary = float(salary_range[1].replace('K', ''))  # 移除额外字符
                    salary_multiplier = float(salary_parts[1].replace('薪', ''))
                    annual_salary = ((low_salary + high_salary) / 2) * salary_multiplier * 1000
                    return annual_salary
                except ValueError:
                    print(salary)
                    return None
    elif '元/天' in salary:
        salary = salary.replace('元/天', '')
        salary_range = salary.split('-')
        if len(salary_range) == 2:
            try:
                # 按一个月工作22天算
                low_salary = float(salary_range[0])
                high_salary = float(salary_range[1])
                daily_salary = (low_salary + high_salary) / 2
                annual_salary = daily_salary * 22 * 12
                return annual_salary
            except ValueError:
                print(salary)
                return None
    elif '元/时' in salary:
        salary = salary.replace('元/时', '')
        salary_range = salary.split('-')
        if len(salary_range) == 2:
            try:
                # 按一个月工作22天算，一天干10个小时算
                low_salary = float(salary_range[0])
                high_salary = float(salary_range[1])
                daily_salary = (low_salary + high_salary) / 2
                annual_salary = daily_salary * 22 * 12 * 10
                return annual_salary
            except ValueError:
                print(salary)
                return None
    elif '元/周' in salary:
        salary = salary.replace('元/周', '')
        salary_range = salary.split('-')
        if len(salary_range) == 2:
            try:
                # 按一个月工作 4 周算
                low_salary = float(salary_range[0])
                high_salary = float(salary_range[1])
                daily_salary = (low_salary + high_salary) / 2
                annual_salary = daily_salary * 12 * 4
                return annual_salary
            except ValueError:
                print(salary)
                return None
    elif '元/月' in salary:
        salary = salary.replace('元/月', '')
        salary_range = salary.split('-')
        if len(salary_range) == 2:
            try:
                low_salary = float(salary_range[0])
                high_salary = float(salary_range[1])
                monthly_salary = (low_salary + high_salary) / 2
                annual_salary = monthly_salary * 12 * 1000
                return annual_salary
            except ValueError:
                print(salary)
                return None
    else:
        salary_range = salary.split('-')
        if len(salary_range) == 2:
            try:
                low_salary = float(salary_range[0])
                high_salary = float(salary_range[1].replace('K', ''))  # 移除额外字符
                monthly_salary = (low_salary + high_salary) / 2
                annual_salary = monthly_salary * 12 * 1000
                return annual_salary
            except ValueError:
                print(salary)
                return None

    print(salary)
    return None


def generate_salary_pie(data):
    salary_ranges = {
        "10000以下": 0,
        "10000-50000": 0,
        "50000-100000": 0,
        "100000-200000": 0,
        "200000以上": 0
    }

    # 统计各个薪资范围的数量
    for salary in data:
        # print(data[salary])
        annual_salary = classify_salary(salary)
        if annual_salary is not None:
            if annual_salary < 10000:
                salary_ranges["10000以下"] += data[salary]
            elif 10000 <= annual_salary < 50000:
                salary_ranges["10000-50000"] += data[salary]
            elif 50000 <= annual_salary < 100000:
                salary_ranges["50000-100000"] += data[salary]
            elif 100000 <= annual_salary < 200000:
                salary_ranges["100000-200000"] += data[salary]
            else:
                salary_ranges["200000以上"] += data[salary]

    salary_pie = (
        Pie()
        .add(
            series_name="年薪分布饼状图",
            data_pair=[(key, value) for key, value in salary_ranges.items()],
            radius=["40%", "75%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="年薪分布饼状图",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_weight="bold"),
            ),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_top="middle",
                pos_right="5%",
                item_width=20,
                item_height=10,
            ),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c}", font_size=12, font_weight="bold")
        )
    )

    salary_pie.render('templates/salary_pie_chart.html')

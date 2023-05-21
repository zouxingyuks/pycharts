import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts.charts import WordCloud, Pie
from pyecharts.globals import ChartType
from snapshot_selenium import snapshot as driver
from dao.init import get_mysql_config
from pyecharts import options as opts
from pyecharts.charts import Geo
from salary_pie import *
from word_cloud import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
config = get_mysql_config()
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
db = SQLAlchemy(app)


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    job_tags = db.Column(db.String(255))
    company = db.Column(db.String(255))

    def __repr__(self):
        return f"<Job id={self.id} job_name={self.job_name} location={self.location} salary={self.salary} job_tags={self.job_tags} company={self.company}>"
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
            # print(part)

            if i < 2:  # 只处理前两个元素
                if part in location_counts:
                    location_counts[part] += 1
                else:
                    location_counts[part] = 1

    # 创建 Geo 实例并设置地图类型
    geo = Geo()
    geo.add_schema(maptype="china")

    # 添加数据到 Geo 实例
    geo.add(
        series_name="地域分布",
        data_pair=list(location_counts.items()),
        type_=ChartType.EFFECT_SCATTER,  # 散点图类型
        symbol_size=10,  # 散点大小
        label_opts=opts.LabelOpts(is_show=True),  # 显示标签
    )

    # 设置全局配置项
    geo.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=max(location_counts.values()),  # 数据的最大值
            is_piecewise=True,  # 是否分段显示
        ),
        title_opts=opts.TitleOpts(
            title="地域分布图",
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(font_weight="bold"),
        ),
    )

    # 渲染地域分布图并保存到文件
    geo.render("templates/geo_chart.html")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job = request.form.get('job')
        results = Job.query.filter(Job.job_name.ilike(f'%{job}%')).all()
        if 'word_cloud' in request.form:
            job_tags = [tag.strip() for result in results for tag in result.job_tags.split(',')]
            generate_word_cloud(job_tags)
            return render_template('word_cloud_chart.html')
        elif 'salary_pie' in request.form:
            salary_data = {}
            for result in results:
                salary = result.salary
                if salary in salary_data:
                    salary_data[salary] += 1
                else:
                    salary_data[salary] = 1

            generate_salary_pie(salary_data)
            return render_template('salary_pie_chart.html')
        elif 'geo_chart' in request.form:
            generate_geo_chart(results)
            return render_template('geo_chart.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

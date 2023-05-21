import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts.charts import WordCloud
from pyecharts.globals import ChartType
from snapshot_selenium import snapshot as driver
from dao.init import get_mysql_config
from pyecharts import options as opts

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

def generate_word_cloud(data):
    job_tags_chart = (
        WordCloud()
        .add(series_name="职位标签", data_pair=list(data.items()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="职位标签词云图", pos_left="center", title_textstyle_opts=opts.TextStyleOpts(font_weight="bold")),
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

    job_tags_chart.width = "100%vh"
    job_tags_chart.height = "100vh"

    job_tags_chart.render('templates/job_tags_chart.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job = request.form.get('job')
        results = Job.query.filter(Job.job_name.ilike(f'%{job}%')).all()
        job_tags = [tag.strip() for result in results for tag in result.job_tags.split(',')]

        job_tags_data = {tag: job_tags.count(tag) for tag in job_tags}

        generate_word_cloud(job_tags_data)

        return render_template('job_tags_chart.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

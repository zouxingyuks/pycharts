from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType

from dao.init import get_mysql_config
from salary_pie import generate_salary_pie
from word_cloud import generate_word_cloud
from geo_chart import  generate_geo_chart
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
config = get_mysql_config()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
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

import mysql.connector
import yaml
import os


def get_mysql_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.yaml')
    try:
        with open(config_file, encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config['mysql']
    except IOError:
        print('文件不存在,新建 config/config.yaml 文件...')
        config = {'mysql': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'jobs'
        }}
        with open('config/config.yaml', 'w') as f:
            yaml.dump(config, f)
        return config['mysql']

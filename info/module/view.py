from . import index_rule
import logging
@index_rule.route('/')
def index():
    logging.debug('这是一个debug日志')
    logging.info('这是一个info日志')
    logging.warning('这是一个warning日志')
    return '这是路由'
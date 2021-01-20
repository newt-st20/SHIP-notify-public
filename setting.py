DEBUG = True

# 本番環境ならデバッグモードにしない
if os.environ['RACK_ENV'] == 'production':
    DEBUG = False

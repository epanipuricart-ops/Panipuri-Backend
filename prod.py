from waitress import serve
import main
import config.config as cfg
serve(main.app, host=cfg.Flask['HOST'], port=cfg.Flask['PORT'])
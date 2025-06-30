logger = logging.getLogger(__name__)

# Logging setup
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'current')
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now(timezone('Asia/Kolkata')).strftime('%Y%m%d')
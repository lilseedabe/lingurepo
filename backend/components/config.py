import os
from dotenv import load_dotenv
from typing import Dict

def load_environment() -> Dict[str, str]:
    load_dotenv()
    required_vars = [
        'LINGUSTRUCT_LICENSE_KEY',
        'GROQ_API_KEY',
        'TOOLHOUSE_API_KEY',
        'REPO_NAME',
        'BRANCH_NAME'
    ]
    env = {var: os.getenv(var) for var in required_vars}
    missing = [var for var, value in env.items() if not value]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
    env['USER_ID'] = os.getenv('USER_ID', 'default_user')
    return env

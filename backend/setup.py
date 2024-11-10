from setuptools import setup, find_packages

setup(
    name='lingustruct',  # パッケージ名
    version='0.1.0',
    description='AI-supported system design framework optimized for usability.',
    author='Yasunori Abe',
    author_email='osusume-co@lilseed.jp',
    packages=find_packages(exclude=['templates_server', '*.enc']),  # 不要なファイルを除外
    license='Proprietary',  # 独自ライセンス
    install_requires=[
        'openai',
        'jsonschema',
        'fastapi',
        'uvicorn',
        'pydantic',
        'cryptography',  # 暗号化ライブラリ
        'requests',      # API通信に必要
        'weasyprint',    # PDF生成に必要
        'markdown'       # Markdown変換に必要
    ],
    include_package_data=False,  # セキュリティ強化のためパッケージ内データを除外
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

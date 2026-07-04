lint:
    isort --profile black .
    find . -name '*.py' -exec pyupgrade --py312-plus {} +
    autoflake -i --remove-all-unused-imports --ignore-init-module-imports --remove-duplicate-keys --remove-unused-variables -r .
    flake8 --extend-ignore=E501,B008,SIM113

format:
    black .
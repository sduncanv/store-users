from setuptools import setup


def get_requirements(filename="requirements.txt", write=False):

    repository_vars = ['REPOSITORY_USER', 'TOKEN']
    requirement = []

    variables = get_variables()

    with open('locked-requirements.txt', mode="r", encoding="utf-8") as lf:
        lines = lf.readlines()

    processed_lines = []
    for line in lines:
        processed_line = line

        if any(var in line for var in repository_vars):
            processed_line = line.replace(
                'REPOSITORY_USER', variables.get('REPOSITORY_USER')
            ).replace('TOKEN', variables.get('TOKEN'))

            if not write:
                if '#egg=' in processed_line:
                    parts = processed_line.split('#egg=')
                    processed_line = f'{parts[1].strip()} @ {parts[0].strip()}'

        processed_lines.append(processed_line)

    if write:
        with open(filename, 'w+') as f:
            f.writelines(processed_lines)

    return requirement


def get_variables():

    environment = {}

    with open(".env", mode="r") as f:
        lines = f.readlines()
        environment = dict(line.strip().split('=') for line in lines)

    return environment


if __name__ == "__main__":

    requirements = get_requirements()

    setup(
        name="store-users",
        version="1.0.0",
        description="This repository represents the logic of the users.",
        author="Samuel Duncan",
        author_email="srduncanv1217@gmail.com",
        url="https://github.com/sduncanv/store-users.git",
        packages=[
            'Users.Classes', 'Users.Models'
        ],
        package_dir={
            'Users.Classes': 'Classes', 'Users.Models': 'Models'
        },
        install_requires=requirements,
        python_requires=">=3.9",
        classifiers=[
            "Programming Language :: Python :: 3.9",
            "License :: OSI Approved :: MIT License",
        ],
    )

import setuptools


def get_environment():
    environment = {}
    env_filename = ".env"

    with open(env_filename, mode="r") as f:
        lines = f.readlines()
        environment = {
            line.strip().split('=')[0]: line.strip().split('=')[1]
            for line in lines
        }

    return environment


def get_requirements(filename="requirements.txt", write=False):

    # Defining placeholders
    env_vars = ['USERNAME', 'PASSWORD', 'TOKEN']
    indexes = []
    requirement_list = []
    requirements_lock = 'requirements-lock.txt'

    # Getting environment variables
    environment = get_environment()
    repo_user = environment.get('REPO_USER')
    repo_pass = environment.get('REPO_PASS')
    repo_token = environment.get('TOKEN')

    with open(requirements_lock, mode="r", encoding="utf-8") as req_lock:

        with open(filename, 'w+') as f:

            lines = req_lock.readlines()
            # Extracting indexes from lines containing placeholders
            indexes = [i for i, l in enumerate(lines)
                       for var in env_vars if var in l]

            f.seek(0)  # Setting file start

            for index, line in enumerate(lines):
                # Setting initial line content
                content = line

                if index in set(indexes):
                    # Replacing content placeholders with environment variables
                    content = line.replace(
                        'USERNAME', repo_user
                    ).replace(
                        'PASSWORD', repo_pass
                    ).replace(
                        'TOKEN', repo_token
                    )

                    if not write:
                        splitted = content.split('#egg=')
                        content = (
                            f'{splitted[1].strip()} @ {splitted[0].strip()}')

                # Rewriting line
                if write:
                    f.write(content)

                requirement_list.append(content)  # Storing requirement

    return requirement_list


if __name__ == "__main__":

    requirements = get_requirements()

    setuptools.setup(
        name="store-users",
        version="0.0.1",
        author="Samuel Duncan",
        author_email="srduncanv1217@gmail.com",
        url="https://github.com/sduncanv/store-users.git",
        project_urls={
            "Bug Tracker": "https://github.com/sduncanv/store-users.git",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: Other/Proprietary License",
            "Operating System :: OS Independent",
        ],
        package_dir={
            'Users.Classes': 'Classes',
            'Users.Models': 'Models'
        },
        packages=[
            'Users.Classes', 'Users.Models'
        ],
        python_requires=">=3.9",
        install_requires=requirements
    )

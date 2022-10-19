# The MIT License (MIT)
# Copyright © 2022 Opentensor Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import os
import sys
import pathlib
import pkg_resources
from typing import Optional
from setuptools import setup, find_packages

def read_requirements(path):
    with pathlib.Path(path).open() as requirements_txt:
        return [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]


requirements = read_requirements('requirements/prod.txt')
extra_requirements_dev = read_requirements('requirements/dev.txt')

package_data = {
    'subtensornodeapi': []
}

platform: Optional[str] = os.environ.get('BT_BUILD_TARGET') or sys.platform

# Check platform and remove unsupported subtensor node api binaries.
if platform == "linux" or platform == "linux2":
    # linux
    package_data['subtensornodeapi'].append('subtensor-node-api-linux')
elif platform == "darwin":
    # OS X
    package_data['subtensornodeapi'].append('subtensor-node-api-macos')
else: # e.g. platform == None
    # neither linux or macos
    # include neither binaries
    pass

setup(
    name='subtensornodeapi',
    version="0.0.1",
    description='subtensor-node-api for bittensor',
    long_description_content_type='text/markdown',
    url='https://github.com/opentensor/subtensor-node-api',
    author='bittensor.com',
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        'dev': extra_requirements_dev
    },
    include_package_data=True,
    author_email='',
    license='MIT',
    keywords=[
        'nlp',
        'crypto',
        'machine learning',
        'ml',
        'tao',
        'bittensor',
    ],
    python_requires='>=3.7'
)

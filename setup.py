import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.txt").read_text(encoding="utf-8") if (HERE / "README.txt").exists() else ""

setup(
	name="codefox",
	version="0.2.0",
	description="CodeFox CLI - code auditing and code review tool",
	long_description=README,
	long_description_content_type="text/plain",
	author="",
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		"typer",
		"rich",
		"python-dotenv",
		"GitPython",
		"google-genai",
	],
	entry_points={
		"console_scripts": [
			"codefox=codefox.main:cli",
		],
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.11",
)

